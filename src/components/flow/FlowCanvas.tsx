import { useEffect, useRef, useCallback } from 'react'
import { useFlowStore } from '../../stores/flowStore'
import { useRealtimeStore } from '../../stores/realtimeStore'
import { useGlobeViewStore } from '../../stores/globeViewStore'
import { useElementSize } from '../../hooks/useElementSize'
import { FlowRenderer } from '../../flows/FlowRenderer'
import type { FlowModel, FlowType } from '../../flows/types'
import type { EconomicDataPoint } from '../../types/economic'

const FLOW_VALUE_SCALE: Record<FlowType, number> = {
  trade: 50,
  investment: 250,
  debt: 1200,
  aid: 5000,
}

const getTimestamp = (value: string): number => {
  const parsed = Date.parse(value)
  return Number.isNaN(parsed) ? -1 : parsed
}

function buildGdpByCountry(records: Record<string, EconomicDataPoint>): Map<string, number> {
  const latestByCountry = new Map<string, { value: number; observedAt: number }>()

  for (const record of Object.values(records)) {
    if (record.indicator !== 'gdp' || record.value == null) continue

    const observedAt = getTimestamp(record.observedAt)
    const previous = latestByCountry.get(record.countryCode)
    if (!previous || observedAt >= previous.observedAt) {
      latestByCountry.set(record.countryCode, { value: record.value, observedAt })
    }
  }

  return new Map(
    Array.from(latestByCountry.entries()).map(([countryCode, latest]) => [countryCode, latest.value]),
  )
}

function withRealtimeEconomicValues(
  flows: FlowModel[],
  records: Record<string, EconomicDataPoint>,
): FlowModel[] {
  const gdpByCountry = buildGdpByCountry(records)

  return flows.map((flow) => {
    const sourceGdp = gdpByCountry.get(flow.sourceCountry)
    const targetGdp = gdpByCountry.get(flow.targetCountry)

    if (sourceGdp == null && targetGdp == null) return flow

    const singleCountryGdp = sourceGdp ?? targetGdp
    if (singleCountryGdp == null) return flow

    const baseValue = sourceGdp != null && targetGdp != null
      ? (sourceGdp + targetGdp) / 2
      : singleCountryGdp

    const scaledValue = Math.max(
      0.5,
      Math.round((baseValue / FLOW_VALUE_SCALE[flow.flowType]) * 100) / 100,
    )
    if (scaledValue === flow.value) return flow

    return {
      ...flow,
      value: scaledValue,
    }
  })
}

/**
 * FlowCanvas — a transparent WebGL canvas that overlays the globe and renders
 * animated 3D capital-flow arcs.
 *
 * Architecture:
 *  - Completely independent of GlobeEngine internals.
 *  - Reads GlobeFrameSnapshot from globeViewStore to synchronise camera matrices
 *    each frame, so arcs track the globe as the user orbits.
 *  - LOD path: reads FlowEngine snapshot via flowStore.tickLodEngine() each frame,
 *    upserts / removes flows in the renderer, and updates per-flow fade uniforms.
 *  - Legacy path: reads FlowStore for flow data, visible-type filter, and animation time.
 *  - Does NOT modify GlobeEngine, OverlayCanvas, or any Country Layer code.
 */
export default function FlowCanvas() {
  const { ref: containerRef, size } = useElementSize<HTMLDivElement>()
  const canvasRef   = useRef<HTMLCanvasElement | null>(null)
  const rendererRef = useRef<FlowRenderer | null>(null)
  const rafRef      = useRef<number>(0)
  const lastTimeRef = useRef<number>(performance.now())

  // Track which flow ids are currently in the renderer to diff against engine snapshot
  const activeIdsRef = useRef<Set<string>>(new Set())

  const isVisible    = useFlowStore((s) => s.isVisible)
  const tick         = useFlowStore((s) => s.tick)
  const flows        = useFlowStore((s) => s.flows)
  const visibleTypes = useFlowStore((s) => s.visibleTypes)
  const getFiltered  = useFlowStore((s) => s.getFilteredFlows)
  const tickLodEngine = useFlowStore((s) => s.tickLodEngine)
  const getLodEngine  = useFlowStore((s) => s.getLodEngine)
  const realtimeRecords = useRealtimeStore((s) => s.records)

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

  // ── Legacy flow data → geometry sync ─────────────────────────────────────
  // Re-run only when the flow list or visible-type filter changes.
  // This path is kept for the FlowPanel toggle UI (trade/investment/debt/aid).

  useEffect(() => {
    if (!rendererRef.current) return
    rendererRef.current.updateFlows(withRealtimeEconomicValues(getFiltered(), realtimeRecords))
  }, [flows, visibleTypes, getFiltered, realtimeRecords])

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

    // ── LOD engine integration ─────────────────────────────────────────────
    // Advance the engine's fade timers and retrieve the current frame's snapshot.

    const snapshot = tickLodEngine(delta)
    const engine   = getLodEngine()

    if (engine.hasChanged()) {
      // Geometry rebuild: add flows that appeared in the snapshot but aren't in
      // the renderer yet; remove flows that have completed their fade-out.
      const snapshotIds = new Set(snapshot.map((s) => s.flow.id))

      // Upsert incoming flows
      for (const { flow } of snapshot) {
        if (!activeIdsRef.current.has(flow.id)) {
          renderer.upsertFlowObject(flow)
          activeIdsRef.current.add(flow.id)
        }
      }

      // Remove flows that the engine has already disposed
      for (const id of activeIdsRef.current) {
        if (!snapshotIds.has(id)) {
          renderer.removeFlowObject(id)
          activeIdsRef.current.delete(id)
        }
      }
    }

    // Update per-flow fade alpha uniforms every frame (no geometry rebuild)
    for (const { flow, fadeAlpha } of snapshot) {
      renderer.setFlowFadeAlpha(flow.id, fadeAlpha)
    }

    renderer.render()
  }, [isVisible, tick, tickLodEngine, getLodEngine])

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
