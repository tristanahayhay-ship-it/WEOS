import { useEffect, useRef, useCallback } from 'react'
import { useCountryStore } from '../../stores/countryStore'
import { useCountryEconomicStore } from '../../stores/countryEconomicStore'
import { useZoomStore } from '../../stores/zoomStore'
import { useGlobeViewStore } from '../../stores/globeViewStore'
import { useElementSize } from '../../hooks/useElementSize'
import { FlowRenderer } from '../../flows/FlowRenderer'
import type { FlowObject } from '../../flows/types'
import type { CityFlow, EconomicCity, CityFlowType } from '../../world/country/types'

// ── City flow → FlowObject conversion ────────────────────────────────────────

/** CSS + Three.js hex pairs for each city-flow type */
const FLOW_TYPE_COLORS: Record<CityFlowType, { css: string; hex: number }> = {
  capital:   { css: '#10b981', hex: 0x10b981 },  // emerald  — investment/government
  trade:     { css: '#3b82f6', hex: 0x3b82f6 },  // blue     — goods & services
  supply:    { css: '#f59e0b', hex: 0xf59e0b },  // amber    — supply chain
  logistics: { css: '#8b5cf6', hex: 0x8b5cf6 },  // violet   — logistics
}

const VALUE_MAX = 600  // normalise flow value to [0, 1]

function cityFlowToFlowObject(
  flow: CityFlow,
  cityMap: Map<string, EconomicCity>,
): FlowObject | null {
  const from = cityMap.get(flow.fromCityId)
  const to   = cityMap.get(flow.toCityId)
  if (!from || !to) return null

  const cfg = FLOW_TYPE_COLORS[flow.type]
  const thickness = Math.min(1, 0.3 + (flow.value / VALUE_MAX) * 0.7)

  return {
    id:            `cv3-${flow.id}`,
    startPoint:    [from.position.lon, from.position.lat],
    endPoint:      [to.position.lon,   to.position.lat],
    dataType:      flow.type === 'capital' ? 'capital' : flow.type === 'trade' ? 'trade' : 'supply-chain',
    value:         flow.value,
    color:         cfg.css,
    colorHex:      cfg.hex,
    thickness,
    animationSpeed: 0.9 + thickness * 0.5,
    displayPriority: Math.round(flow.value),
    lodRules:      { visibleAtLevels: [2] },
    visibilityState: 0,
  }
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

      if (currentLayer) {
        // Build a city lookup map
        const cityMap = new Map<string, EconomicCity>(currentLayer.cities.map((c) => [c.id, c]))

        // Upsert new flow objects
        for (const flow of currentLayer.flows) {
          const fo = cityFlowToFlowObject(flow, cityMap)
          if (!fo) continue
          renderer.upsertFlowObject(fo)
          fadeAlphasRef.current.set(fo.id, 0)
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
