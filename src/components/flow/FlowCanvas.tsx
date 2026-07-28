import { useEffect, useRef, useCallback } from 'react'
import { useFlowStore } from '../../stores/flowStore'
import { useGlobeViewStore } from '../../stores/globeViewStore'
import { useElementSize } from '../../hooks/useElementSize'
import { FlowRenderer } from '../../flows/FlowRenderer'

/**
 * FlowCanvas — a transparent WebGL canvas that overlays the globe and renders
 * animated 3D capital-flow arcs.
 *
 * Architecture:
 *  - Completely independent of GlobeEngine internals.
 *  - Reads GlobeFrameSnapshot from globeViewStore to synchronise camera matrices
 *    each frame, so arcs track the globe as the user orbits.
 *  - Reads FlowStore for flow data, visible-type filter, and animation time.
 *  - Does NOT modify GlobeEngine, OverlayCanvas, or any Country Layer code.
 */
export default function FlowCanvas() {
  const { ref: containerRef, size } = useElementSize<HTMLDivElement>()
  const canvasRef   = useRef<HTMLCanvasElement | null>(null)
  const rendererRef = useRef<FlowRenderer | null>(null)
  const rafRef      = useRef<number>(0)
  const lastTimeRef = useRef<number>(performance.now())

  const isVisible    = useFlowStore((s) => s.isVisible)
  const tick         = useFlowStore((s) => s.tick)
  const flows        = useFlowStore((s) => s.flows)
  const visibleTypes = useFlowStore((s) => s.visibleTypes)
  const getFiltered  = useFlowStore((s) => s.getFilteredFlows)

  // ── Renderer bootstrap ────────────────────────────────────────────────────

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || rendererRef.current) return

    rendererRef.current = new FlowRenderer(canvas)

    return () => {
      rendererRef.current?.dispose()
      rendererRef.current = null
    }
  }, [])

  // ── Resize ────────────────────────────────────────────────────────────────

  useEffect(() => {
    if (!size || !rendererRef.current) return
    rendererRef.current.resize(size.width, size.height)
  }, [size])

  // ── Flow data → geometry sync ─────────────────────────────────────────────
  // Re-run only when the flow list or visible-type filter changes.

  useEffect(() => {
    if (!rendererRef.current) return
    rendererRef.current.updateFlows(getFiltered())
  }, [flows, visibleTypes, getFiltered])

  // ── Animation loop ────────────────────────────────────────────────────────

  const animate = useCallback(() => {
    rafRef.current = requestAnimationFrame(animate)

    const now   = performance.now()
    const delta = (now - lastTimeRef.current) / 1000
    lastTimeRef.current = now

    const renderer = rendererRef.current
    if (!renderer) return

    tick(delta)

    if (!isVisible) return

    const frame = useGlobeViewStore.getState().frame
    if (!frame) return

    renderer.syncCamera(frame)
    renderer.setTime(useFlowStore.getState().animationTime)
    renderer.render()
  }, [isVisible, tick])

  useEffect(() => {
    rafRef.current = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(rafRef.current)
  }, [animate])

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div
      ref={containerRef}
      className="pointer-events-none absolute inset-0 w-full h-full"
      style={{ zIndex: 10 }}
      aria-hidden="true"
    >
      <canvas
        ref={canvasRef}
        className="w-full h-full block"
        style={{ opacity: isVisible ? 1 : 0, transition: 'opacity 0.3s' }}
      />
    </div>
  )
}

