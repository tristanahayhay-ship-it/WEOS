import { useEffect, useRef } from 'react'
import { useCountryStore } from '../../stores/countryStore'
import { useCountryEconomicStore } from '../../stores/countryEconomicStore'
import { useZoomStore } from '../../stores/zoomStore'
import { useGlobeViewStore } from '../../stores/globeViewStore'
import { projectToScreen } from '../../utils/projectToScreen'
import type { EconomicCity } from '../../world/country/types'

// ── Helpers ───────────────────────────────────────────────────────────────────

function formatUsdB(v: number): string {
  return `$\u00A0${Math.abs(v).toFixed(2)}B`
}

function formatNetFlow(v: number): string {
  return `${v >= 0 ? '+' : ''}${v.toFixed(2)}B`
}

/** Simple deterministic sparkline path (10 points) driven by a seed */
function makeSparkline(seed: number, trend: 'up' | 'down', amplitude = 6): string {
  const pts: [number, number][] = []
  let y = 20
  for (let i = 0; i < 10; i++) {
    const noise = Math.sin(seed * (i + 1) * 2.7) * amplitude
    const drift = trend === 'up' ? i * 1.5 : -i * 1.5
    y = Math.max(4, Math.min(36, 20 + noise + drift))
    pts.push([(i / 9) * 100, y])
  }
  return pts.map(([x, py], idx) => `${idx === 0 ? 'M' : 'L'}${x.toFixed(1)},${py.toFixed(1)}`).join(' ')
}

// ── City card ─────────────────────────────────────────────────────────────────

interface CityCardProps {
  city: EconomicCity
  domRef: (el: HTMLDivElement | null) => void
}

function CityCard({ city, domRef }: CityCardProps) {
  const { volume24H, netFlow24H, name, cardOffset } = city
  if (volume24H == null || netFlow24H == null) return null

  const offsetX = cardOffset?.x ?? 12
  const offsetY = cardOffset?.y ?? -22

  return (
    <div
      ref={domRef}
      className="absolute"
      style={{
        display: 'none', // shown by rAF after first position calculation
        transform: `translate(${offsetX}px, ${offsetY}px)`,
        zIndex: 18,
        pointerEvents: 'none',
      }}
    >
      <div
        className="rounded border px-2 py-1.5"
        style={{
          background: 'rgba(6, 10, 20, 0.85)',
          borderColor: 'rgba(121,196,255,0.22)',
          backdropFilter: 'blur(8px)',
          minWidth: 130,
          boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
        }}
      >
        <p
          className="text-[11px] font-bold tracking-[0.18em] mb-0.5"
          style={{ color: '#d9efff' }}
        >
          {name}
        </p>
        <p className="text-[9px] tracking-[0.14em] uppercase" style={{ color: 'rgba(121,196,255,0.6)' }}>
          NET FLOW{' '}
          <span style={{ color: netFlow24H >= 0 ? '#34d399' : '#f87171' }}>
            {formatNetFlow(netFlow24H)}
          </span>
        </p>
        <p className="text-[13px] font-semibold mt-0.5" style={{ color: '#34d399' }}>
          {formatUsdB(volume24H)}{' '}
          <span className="text-[9px] font-normal" style={{ color: 'rgba(121,196,255,0.5)' }}>
            (24H)
          </span>
        </p>
      </div>
    </div>
  )
}

// ── Capital Flow legend + sparkline ──────────────────────────────────────────

function CapitalFlowPanel({ inflowUsdB, outflowUsdB, isoCode }: {
  inflowUsdB: number
  outflowUsdB: number
  isoCode: string
}) {
  const seed = isoCode.split('').reduce((a, c) => a + c.charCodeAt(0), 0)
  const inflowPath = makeSparkline(seed, 'up')
  const outflowPath = makeSparkline(seed + 13, 'down', 5)

  return (
    <div
      className="absolute pointer-events-none"
      style={{ top: 12, left: 12, zIndex: 18, width: 232 }}
    >
      <div
        className="rounded-lg border px-3 py-2.5"
        style={{
          background: 'rgba(6, 10, 20, 0.88)',
          borderColor: 'rgba(121,196,255,0.2)',
          backdropFilter: 'blur(12px)',
          boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
        }}
      >
        {/* Title */}
        <p
          className="text-[10px] font-semibold tracking-[0.22em] uppercase mb-2"
          style={{ color: 'rgba(121,196,255,0.7)' }}
        >
          CAPITAL FLOW (24H)
        </p>

        {/* Inflow + Outflow row */}
        <div className="flex gap-3 mb-2">
          {/* Inflow */}
          <div className="flex-1">
            <p className="text-[9px] uppercase tracking-[0.2em] mb-0.5" style={{ color: '#34d399' }}>
              TOTAL INFLOW
            </p>
            <p className="text-[15px] font-bold leading-none" style={{ color: '#34d399' }}>
              {formatUsdB(inflowUsdB)}
            </p>
            <svg width="100%" height="24" viewBox="0 0 100 40" preserveAspectRatio="none" className="mt-1" aria-hidden="true">
              <path d={inflowPath} fill="none" stroke="#34d399" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>

          {/* Outflow */}
          <div className="flex-1">
            <p className="text-[9px] uppercase tracking-[0.2em] mb-0.5" style={{ color: '#f87171' }}>
              TOTAL OUTFLOW
            </p>
            <p className="text-[15px] font-bold leading-none" style={{ color: '#f87171' }}>
              {formatUsdB(outflowUsdB)}
            </p>
            <svg width="100%" height="24" viewBox="0 0 100 40" preserveAspectRatio="none" className="mt-1" aria-hidden="true">
              <path d={outflowPath} fill="none" stroke="#f87171" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
        </div>

        {/* Legend */}
        <div
          className="flex flex-col gap-0.5 border-t pt-2"
          style={{ borderColor: 'rgba(121,196,255,0.12)' }}
        >
          <LegendItem color="#34d399" type="dot" label="CAPITAL INFLOW" />
          <LegendItem color="#f87171" type="dot" label="CAPITAL OUTFLOW" />
          <LegendItem color="#fbbf24" type="dash" label="NET FLOW" />
        </div>
      </div>
    </div>
  )
}

function LegendItem({ color, type, label }: { color: string; type: 'dot' | 'dash'; label: string }) {
  return (
    <div className="flex items-center gap-1.5">
      {type === 'dot' ? (
        <span
          style={{
            display: 'inline-block',
            width: 7,
            height: 7,
            borderRadius: '50%',
            background: color,
            flexShrink: 0,
          }}
        />
      ) : (
        <svg width="14" height="3" viewBox="0 0 14 3" aria-hidden="true" style={{ flexShrink: 0 }}>
          <line x1="0" y1="1.5" x2="14" y2="1.5" stroke={color} strokeWidth="2" strokeDasharray="4 2" />
        </svg>
      )}
      <span className="text-[9px] tracking-[0.18em] uppercase" style={{ color: 'rgba(217,239,255,0.55)' }}>
        {label}
      </span>
    </div>
  )
}

// ── Main component ────────────────────────────────────────────────────────────

/**
 * CountryFlowHUD — overlaid on top of the globe when in Country View (zoom level 2).
 *
 * Renders two elements:
 *  1. A floating "Capital Flow (24H)" panel (top-left) showing total inflow /
 *     outflow and a legend.
 *  2. Per-city info cards positioned at the projected screen coordinates of
 *     each city, updated every animation frame without triggering React re-renders.
 */
export default function CountryFlowHUD() {
  const selectedCountry = useCountryStore((s) => s.selectedCountry)
  const activeLevel = useZoomStore((s) => s.activeLevel)
  const layer = useCountryEconomicStore((s) => s.layer)

  const isVisible = activeLevel === 2 && selectedCountry !== null

  // Map: city id → DOM element ref for position updates
  const cardDomRefs = useRef<Map<string, HTMLDivElement>>(new Map())
  const rafRef = useRef<number>(0)

  // rAF loop: update city-card DOM positions directly — no React re-renders
  useEffect(() => {
    if (!isVisible) {
      // Hide all cards when not in country view
      for (const el of cardDomRefs.current.values()) {
        el.style.display = 'none'
      }
      return
    }

    const tick = () => {
      rafRef.current = requestAnimationFrame(tick)
      const frame = useGlobeViewStore.getState().frame
      if (!frame || !layer) return

      for (const city of layer.cities) {
        if (city.volume24H == null || city.netFlow24H == null) continue
        const el = cardDomRefs.current.get(city.id)
        if (!el) continue

        const pos = projectToScreen(city.position.lon, city.position.lat, frame)
        if (!pos) {
          el.style.display = 'none'
          continue
        }

        el.style.display = 'block'
        el.style.left = `${pos.x}px`
        el.style.top = `${pos.y}px`
      }
    }

    rafRef.current = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(rafRef.current)
  }, [isVisible, layer])

  if (!isVisible || !selectedCountry) return null

  const flow24H = layer?.capitalFlow24H

  const citiesToCard = layer?.cities.filter((c) => c.volume24H != null && c.netFlow24H != null) ?? []

  return (
    <>
      {/* Capital Flow (24H) panel */}
      {flow24H && (
        <CapitalFlowPanel
          inflowUsdB={flow24H.inflowUsdB}
          outflowUsdB={flow24H.outflowUsdB}
          isoCode={selectedCountry.isoCode}
        />
      )}

      {/* City overlay cards — positioned via rAF, absolutely inside <main> */}
      {citiesToCard.map((city) => (
        <CityCard
          key={city.id}
          city={city}
          domRef={(el) => {
            if (el) {
              cardDomRefs.current.set(city.id, el)
            } else {
              cardDomRefs.current.delete(city.id)
            }
          }}
        />
      ))}
    </>
  )
}
