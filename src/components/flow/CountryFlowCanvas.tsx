import { useEffect, useRef, useCallback } from 'react'
import { useCountryStore } from '../../stores/countryStore'
import { useCountryEconomicStore } from '../../stores/countryEconomicStore'
import { useZoomStore } from '../../stores/zoomStore'
import { useGlobeViewStore } from '../../stores/globeViewStore'
import { useElementSize } from '../../hooks/useElementSize'
import { FlowRenderer } from '../../flows/FlowRenderer'
import type { FlowObject } from '../../flows/types'
import type { NodeType, FlowState } from '../../world/country/countryFlowModel'
import { resolveCountryFlowModel } from '../../world/country/countryFlowModel'

// ── City flow → FlowObject conversion ────────────────────────────────────────

function colorForFlowState(state: FlowState, nodeType: NodeType): { css: string; hex: number } {
  if (state === 'inflow') {
    const blueTypes: NodeType[] = ['port', 'airport', 'trade_hub', 'logistics_hub']
    return blueTypes.includes(nodeType)
      ? { css: '#3b82f6', hex: 0x3b82f6 }
      : { css: '#10b981', hex: 0x10b981 }
  }
  if (state === 'outflow') {
    const orangeTypes: NodeType[] = ['industrial_center', 'production_zone', 'consumption_zone']
    return orangeTypes.includes(nodeType)
      ? { css: '#f97316', hex: 0xf97316 }
      : { css: '#ef4444', hex: 0xef4444 }
  }
  return { css: '#64748b', hex: 0x64748b }
}

// ── Component ─────────────────────────────────────────────────────────────────

/**
 * CountryFlowCanvas — animated arc canvas for Country View V3.
 *
 * Renders directional capital/trade/supply/logistics flows between a country's
 * economic cities.  Only visible when zoom level === 2 AND a country is selected.
 *
 * Architecture mirrors FlowCanvas but is self-contained:
 *  - Maintains its own FlowRenderer instance.
 *  - Reads the CountryEconomicStore for city flow data.
 *  - Rebuilds geometry only when the active country changes.
 *  - Drives per-flow fade uniforms every frame for smooth fade-in.
 *  - CSS opacity transitions handle level-based LOD show/hide.
 */
export default function CountryFlowCanvas() {
  const { ref: containerRef, size } = useElementSize<HTMLDivElement>()
  const canvasRef   = useRef<HTMLCanvasElement | null>(null)
  const rendererRef = useRef<FlowRenderer | null>(null)
  const rafRef      = useRef<number>(0)
  const timeRef     = useRef<number>(0)
  const lastTimeRef = useRef<number>(performance.now())

  /** ISO code of the country whose geometry is currently loaded */
  const loadedIsoRef = useRef<string>('')
  /** Fade alphas driven manually (no FlowEngine — simpler for single-country flows) */
  const fadeAlphasRef = useRef<Map<string, number>>(new Map())

  const selectedCountry  = useCountryStore((s) => s.selectedCountry as import('../../types/country').Country | null)
  const loadForCountry   = useCountryEconomicStore((s) => s.loadForCountry)
  const activeLevel      = useZoomStore((s) => s.activeLevel)

  const isVisible = activeLevel === 2 && selectedCountry !== null

  // ── Load economic layer when country changes ──────────────────────────────

  useEffect(() => {
    if (selectedCountry) {
      loadForCountry(selectedCountry)
    }
  }, [selectedCountry, loadForCountry])

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

  // ── Animation loop ────────────────────────────────────────────────────────

  const animate = useCallback(() => {
    rafRef.current = requestAnimationFrame(animate)

    const now   = performance.now()
    const delta = Math.min((now - lastTimeRef.current) / 1000, 0.1)
    lastTimeRef.current = now
    timeRef.current += delta

    const renderer = rendererRef.current
    if (!renderer) return

    // ── Rebuild geometry when country changes ──────────────────────────────
    const currentLayer = useCountryEconomicStore.getState().layer
    const currentIso   = currentLayer?.isoCode ?? ''

    if (currentIso !== loadedIsoRef.current) {
      loadedIsoRef.current = currentIso

      // Remove all previous flow arcs before clearing the alpha map
      const previousIds = Array.from(fadeAlphasRef.current.keys())
      for (const id of previousIds) {
        renderer.removeFlowObject(id)
      }
      fadeAlphasRef.current.clear()

      const currentCountry = useCountryStore.getState().selectedCountry
      if (currentLayer && currentCountry) {
        const model = resolveCountryFlowModel({
          country: currentCountry,
          economicLayer: currentLayer,
        })

        if (model) {
          const nodeTypeById = new Map<string, NodeType>([
            [model.capital.id, 'capital'],
            ...model.renderFlowLocations.map((location) => [location.id, location.nodeType] as [string, NodeType]),
          ])
          const nodePriorityById = new Map<string, number>([
            [model.capital.id, model.capital.priorityScore],
            ...model.renderFlowLocations.map((location) => [location.id, location.priorityScore] as [string, number]),
          ])

          for (const edge of model.flowEdges) {
            const start = edge.fromPoint
            const end = edge.toPoint
            const nonCapitalId = edge.fromId === model.capital.id ? edge.toId : edge.fromId
            const nodeType = nodeTypeById.get(nonCapitalId) ?? 'trade_hub'
            const color = colorForFlowState(edge.state, nodeType)
            const thickness = 0.25 + edge.intensity * 0.75
            const priority = nodePriorityById.get(nonCapitalId) ?? 0

            const flowObject: FlowObject = {
              id: `country-flow-${edge.id}`,
              startPoint: start,
              endPoint: end,
              dataType: nodeType === 'capital' ? 'capital' : nodeType === 'trade_hub' ? 'trade' : 'supply-chain',
              value: edge.value,
              color: color.css,
              colorHex: color.hex,
              thickness,
              animationSpeed: 0.8 + edge.intensity * 0.9,
              displayPriority: Math.round(edge.value * (0.7 + priority * 0.3)),
              lodRules: { visibleAtLevels: [2] },
              visibilityState: 0,
            }
            renderer.upsertFlowObject(flowObject)
            fadeAlphasRef.current.set(flowObject.id, 0)
          }
        }
      }
    }

    if (!isVisible) {
      // Fade all alphas toward 0 when hidden
      for (const [id, alpha] of fadeAlphasRef.current) {
        const next = Math.max(0, alpha - delta * 2)
        fadeAlphasRef.current.set(id, next)
        renderer.setFlowFadeAlpha(id, next)
      }
      return
    }

    const frame = useGlobeViewStore.getState().frame
    if (!frame) return

    renderer.syncCamera(frame)
    renderer.setTime(timeRef.current)

    // Advance per-flow fade-in
    const FADE_IN_SPEED = 1.5
    for (const [id, alpha] of fadeAlphasRef.current) {
      const next = Math.min(1, alpha + delta * FADE_IN_SPEED)
      fadeAlphasRef.current.set(id, next)
      renderer.setFlowFadeAlpha(id, next)
    }

    renderer.render()
  }, [isVisible])

  useEffect(() => {
    rafRef.current = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(rafRef.current)
  }, [animate])

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div
      ref={containerRef}
      className="pointer-events-none absolute inset-0 w-full h-full"
      style={{ zIndex: 11 }}
      aria-hidden="true"
    >
      <canvas
        ref={canvasRef}
        className="w-full h-full block"
        style={{
          opacity:    isVisible ? 1 : 0,
          transition: 'opacity 0.5s ease',
        }}
      />
    </div>
  )
}
