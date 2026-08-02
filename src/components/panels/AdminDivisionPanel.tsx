import type { CSSProperties } from 'react'
import { useMemo, useState, useEffect } from 'react'
import { useZoomStore } from '../../stores/zoomStore'
import { useCountryStore } from '../../stores/countryStore'
import { getAdminData } from '../../view/adminDivisionMockData'
import type { AdministrativeDivision } from '../../view/types'

// ── Style tokens ──────────────────────────────────────────────────────────────

const EXIT_ANIMATION_MS = 260

const sectionBoxStyle: CSSProperties = {
  background: 'rgba(11,17,30,0.68)',
  borderColor: 'rgba(121,196,255,0.16)',
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <h3 className="mb-2 text-[11px] uppercase tracking-[0.2em]" style={{ color: 'rgba(121,196,255,0.7)' }}>
      {children}
    </h3>
  )
}

function LabelRow({ label, value, valueColor }: { label: string; value: string; valueColor?: string }) {
  return (
    <div className="flex items-center justify-between gap-3 py-1 text-xs">
      <span style={{ color: 'rgba(121,196,255,0.66)' }}>{label}</span>
      <span className="text-right" style={{ color: valueColor ?? '#d9efff' }}>{value}</span>
    </div>
  )
}

// ── Formatters ────────────────────────────────────────────────────────────────

function fmtB(v: number | null): string {
  if (v == null) return '—'
  if (v >= 1000) return `$${(v / 1000).toFixed(2)}T`
  return `$${v.toFixed(1)}B`
}

function fmtPop(v: number | null): string {
  if (v == null) return '—'
  if (v >= 1e9) return `${(v / 1e9).toFixed(2)}B`
  if (v >= 1e6) return `${(v / 1e6).toFixed(1)}M`
  if (v >= 1e3) return `${(v / 1e3).toFixed(0)}K`
  return String(v)
}

function outlookColor(outlook: AdministrativeDivision['outlook']): string {
  if (outlook === 'expanding')   return '#34d399'
  if (outlook === 'contracting') return '#f87171'
  return '#94a3b8'
}

// ── Division card ─────────────────────────────────────────────────────────────

function DivisionCard({
  division,
  rank,
}: {
  division: AdministrativeDivision
  rank: number
}) {
  return (
    <div
      className="mb-2 rounded-lg border p-2.5"
      style={sectionBoxStyle}
    >
      <div className="flex items-start justify-between gap-2 mb-1">
        <div className="flex items-center gap-2">
          <span className="text-[10px] w-4 shrink-0" style={{ color: 'rgba(121,196,255,0.45)' }}>
            {rank}
          </span>
          <span className="text-xs font-semibold" style={{ color: '#d9efff' }}>{division.name}</span>
        </div>
        <span
          className="text-[9px] uppercase tracking-[0.12em] rounded px-1.5 py-0.5 border shrink-0"
          style={{
            borderColor: `${outlookColor(division.outlook)}50`,
            color: outlookColor(division.outlook),
            background: `${outlookColor(division.outlook)}18`,
          }}
        >
          {division.outlook ?? '—'}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-x-3 gap-y-0.5 mt-1">
        {division.gdpUsdB != null && (
          <>
            <span className="text-[10px]" style={{ color: 'rgba(121,196,255,0.58)' }}>GDP</span>
            <span className="text-[10px]" style={{ color: '#d9efff' }}>{fmtB(division.gdpUsdB)}</span>
          </>
        )}
        {division.growthPercent != null && (
          <>
            <span className="text-[10px]" style={{ color: 'rgba(121,196,255,0.58)' }}>Growth</span>
            <span
              className="text-[10px]"
              style={{ color: division.growthPercent >= 0 ? '#34d399' : '#f87171' }}
            >
              {division.growthPercent >= 0 ? '+' : ''}{division.growthPercent.toFixed(1)}%
            </span>
          </>
        )}
        {division.population != null && (
          <>
            <span className="text-[10px]" style={{ color: 'rgba(121,196,255,0.58)' }}>Population</span>
            <span className="text-[10px]" style={{ color: '#d9efff' }}>{fmtPop(division.population)}</span>
          </>
        )}
        {division.infrastructureIndex != null && (
          <>
            <span className="text-[10px]" style={{ color: 'rgba(121,196,255,0.58)' }}>Infrastructure</span>
            <span className="text-[10px]" style={{ color: '#d9efff' }}>{division.infrastructureIndex.toFixed(0)}/100</span>
          </>
        )}
        {division.dominantSector != null && (
          <>
            <span className="text-[10px]" style={{ color: 'rgba(121,196,255,0.58)' }}>Top Sector</span>
            <span className="text-[10px]" style={{ color: '#a78bfa' }}>{division.dominantSector}</span>
          </>
        )}
        {division.netCapitalFlowUsdB != null && (
          <>
            <span className="text-[10px]" style={{ color: 'rgba(121,196,255,0.58)' }}>Net Capital</span>
            <span
              className="text-[10px]"
              style={{ color: division.netCapitalFlowUsdB >= 0 ? '#34d399' : '#f87171' }}
            >
              {division.netCapitalFlowUsdB >= 0 ? '+' : ''}{fmtB(division.netCapitalFlowUsdB)}
            </span>
          </>
        )}
      </div>
    </div>
  )
}

// ── Main export ───────────────────────────────────────────────────────────────

/**
 * AdminDivisionPanel — shown at Level 3 (Administrative Division View).
 *
 * Lists the administrative divisions of the selected country ranked by GDP.
 * Degrades gracefully when no admin data is available for the selected country.
 */
export default function AdminDivisionPanel() {
  const activeLevel      = useZoomStore((s) => s.activeLevel)
  const selectedCountry  = useCountryStore((s) => s.selectedCountry)

  const shouldBeVisible = activeLevel === 3

  const [isMounted, setIsMounted]       = useState(shouldBeVisible)
  const [isVisible, setIsVisible]       = useState(shouldBeVisible)

  useEffect(() => {
    if (shouldBeVisible) {
      setIsMounted(true)
      const frame = window.requestAnimationFrame(() => setIsVisible(true))
      return () => window.cancelAnimationFrame(frame)
    }

    setIsVisible(false)
    const timer = window.setTimeout(() => setIsMounted(false), EXIT_ANIMATION_MS)
    return () => window.clearTimeout(timer)
  }, [shouldBeVisible])

  const adminData = useMemo(
    () => selectedCountry ? getAdminData(selectedCountry.isoCode) : null,
    [selectedCountry],
  )

  const sortedDivisions = useMemo(() => {
    if (!adminData) return []
    return [...adminData.divisions].sort(
      (a, b) => (b.gdpUsdB ?? 0) - (a.gdpUsdB ?? 0),
    )
  }, [adminData])

  if (!isMounted) return null

  return (
    <aside
      className="pointer-events-auto absolute inset-3 z-20 flex w-auto flex-col overflow-hidden rounded-xl border sm:inset-auto sm:right-3 sm:top-3 sm:bottom-3 sm:w-[min(30rem,42vw)] sm:min-w-[18rem] sm:max-w-[92vw]"
      style={{
        background: 'rgba(7,12,22,0.82)',
        borderColor: 'rgba(121,196,255,0.22)',
        backdropFilter: 'blur(14px)',
        boxShadow: '0 14px 40px rgba(3,7,14,0.52)',
        transform: isVisible ? 'translateX(0)' : 'translateX(36px)',
        opacity: isVisible ? 1 : 0,
        transition: `opacity ${EXIT_ANIMATION_MS}ms ease, transform ${EXIT_ANIMATION_MS}ms ease`,
        pointerEvents: isVisible ? 'auto' : 'none',
      }}
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b px-4 py-3 shrink-0" style={{ borderColor: 'rgba(121,196,255,0.16)' }}>
        <div>
          <p className="text-[10px] uppercase tracking-[0.24em]" style={{ color: 'rgba(121,196,255,0.68)' }}>
            Regional Dashboard
          </p>
          <p className="text-xs" style={{ color: 'rgba(217,239,255,0.75)' }}>
            {selectedCountry
              ? `${selectedCountry.name} — Administrative Division View`
              : 'Select a country to see divisions'
            }
          </p>
        </div>
        <span
          className="text-[9px] uppercase tracking-[0.2em] rounded px-2 py-0.5 border"
          style={{ borderColor: 'rgba(121,196,255,0.3)', color: '#79c4ff', background: 'rgba(121,196,255,0.08)' }}
        >
          L3
        </span>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        {!selectedCountry && (
          <p className="text-xs mt-2" style={{ color: 'rgba(217,239,255,0.48)' }}>
            Zoom in to a country at Level 2 and select it, then zoom deeper to Level 3 to view
            administrative division intelligence.
          </p>
        )}

        {selectedCountry && !adminData && (
          <>
            <section className="mb-3 rounded-lg border p-3" style={sectionBoxStyle}>
              <SectionTitle>Country Context</SectionTitle>
              <LabelRow label="Country"   value={selectedCountry.name} />
              <LabelRow label="Capital"   value={selectedCountry.capital} />
              <LabelRow label="Continent" value={selectedCountry.continent} />
            </section>
            <p className="text-xs" style={{ color: 'rgba(217,239,255,0.42)' }}>
              Administrative division data is not yet available for {selectedCountry.name}.
              Division-level intelligence will be shown once data is connected.
            </p>
          </>
        )}

        {selectedCountry && adminData && sortedDivisions.length > 0 && (
          <>
            {/* Summary */}
            <section className="mb-3 rounded-lg border p-3" style={sectionBoxStyle}>
              <SectionTitle>Division Summary</SectionTitle>
              <LabelRow label="Country"    value={selectedCountry.name} />
              <LabelRow label="Divisions"  value={String(adminData.divisions.length)} />
              <LabelRow label="Intra-flows" value={String(adminData.intraFlows.length)} />
            </section>

            {/* Division rankings */}
            <section className="mb-1">
              <SectionTitle>Ranked by GDP</SectionTitle>
              {sortedDivisions.map((div, i) => (
                <DivisionCard key={div.id} division={div} rank={i + 1} />
              ))}
            </section>
          </>
        )}
      </div>
    </aside>
  )
}
