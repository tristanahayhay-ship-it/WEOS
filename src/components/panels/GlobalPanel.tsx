import type { CSSProperties } from 'react'
import { useMemo } from 'react'
import { useZoomStore } from '../../stores/zoomStore'
import { WORLD_MOCK_DATA } from '../../view/worldMockData'
import { resolveResolvedViewModel } from '../../view/resolver'
import type { ViewState, DashboardSection, DashboardRankEntry } from '../../view/types'
import type { Continent } from '../../types/country'

// ── Style tokens ──────────────────────────────────────────────────────────────

const panelStyle: CSSProperties = {
  background: 'rgba(7,12,22,0.82)',
  borderColor: 'rgba(121,196,255,0.22)',
  backdropFilter: 'blur(14px)',
  boxShadow: '0 14px 40px rgba(3,7,14,0.52)',
}

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

function RankTable({ rows }: { rows: DashboardRankEntry[] }) {
  return (
    <div>
      {rows.map((row) => (
        <div
          key={row.name}
          className="flex items-center gap-2 py-1 border-b last:border-0 text-xs"
          style={{ borderColor: 'rgba(121,196,255,0.1)' }}
        >
          <span className="w-4 shrink-0 text-right" style={{ color: 'rgba(121,196,255,0.45)' }}>
            {row.rank}
          </span>
          <span className="flex-1" style={{ color: 'rgba(217,239,255,0.85)' }}>{row.name}</span>
          <span style={{ color: '#34d399' }}>{row.value}</span>
        </div>
      ))}
    </div>
  )
}

function DashboardSectionCard({ section }: { section: DashboardSection }) {
  return (
    <section className="mb-3 rounded-lg border p-3" style={sectionBoxStyle}>
      <SectionTitle>{section.title}</SectionTitle>
      {section.metrics?.map((m) => (
        <LabelRow key={m.label} label={m.label} value={m.value} valueColor={m.color} />
      ))}
      {section.rankings && <RankTable rows={section.rankings} />}
    </section>
  )
}

// ── Continent breadcrumbs ─────────────────────────────────────────────────────

const CONTINENT_CENTERS: Array<{ name: Continent; label: string }> = [
  { name: 'North America', label: 'N. America' },
  { name: 'South America', label: 'S. America' },
  { name: 'Europe',        label: 'Europe'     },
  { name: 'Africa',        label: 'Africa'     },
  { name: 'Asia',          label: 'Asia'       },
  { name: 'Oceania',       label: 'Oceania'    },
]

function ContinentSelector({
  active,
}: {
  active: Continent | null
}) {
  return (
    <div className="flex flex-wrap gap-1 mb-3">
      {CONTINENT_CENTERS.map(({ name, label }) => {
        const isActive = name === active
        return (
          <span
            key={name}
            className="text-[9px] uppercase tracking-[0.12em] rounded px-1.5 py-0.5 border"
            style={{
              borderColor: isActive ? 'rgba(121,196,255,0.6)' : 'rgba(121,196,255,0.2)',
              color: isActive ? '#79c4ff' : 'rgba(121,196,255,0.45)',
              background: isActive ? 'rgba(121,196,255,0.1)' : 'transparent',
            }}
          >
            {label}
          </span>
        )
      })}
    </div>
  )
}

// ── Main export ───────────────────────────────────────────────────────────────

/**
 * GlobalPanel — shown at Level 0 (Global) and Level 1 (Continent).
 *
 * Renders the resolved dashboard model for the current scope.
 * Data-driven: sections are omitted when data is unavailable.
 */
export default function GlobalPanel() {
  const activeLevel     = useZoomStore((s) => s.activeLevel)
  const isVisible       = activeLevel === 0 || activeLevel === 1

  // Derive a minimal ViewState from the zoom level.
  // Continent selection at level 1 is inferred from the globe; for now we
  // show the global view at both levels — users can zoom into a continent.
  const viewState = useMemo<ViewState>(
    () => ({
      level: activeLevel as ViewState['level'],
      activeContinent: null,
      activeCountryIso: null,
      activeDivisionId: null,
    }),
    [activeLevel],
  )

  const model = useMemo(
    () => resolveResolvedViewModel(viewState, WORLD_MOCK_DATA),
    [viewState],
  )

  if (!isVisible) return null

  const levelLabel = activeLevel === 0 ? 'Global View' : 'Continent View'
  const levelSubtitle = activeLevel === 0
    ? 'World-scale economic intelligence'
    : 'Continental capital flow network'

  return (
    <aside
      className="pointer-events-auto absolute inset-3 z-20 flex w-auto flex-col overflow-hidden rounded-xl border sm:inset-auto sm:left-3 sm:top-3 sm:bottom-3 sm:w-[min(28rem,38vw)] sm:min-w-[16rem] sm:max-w-[92vw]"
      style={panelStyle}
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b px-4 py-3 shrink-0" style={{ borderColor: 'rgba(121,196,255,0.16)' }}>
        <div>
          <p className="text-[10px] uppercase tracking-[0.24em]" style={{ color: 'rgba(121,196,255,0.68)' }}>
            {levelLabel}
          </p>
          <p className="text-xs" style={{ color: 'rgba(217,239,255,0.75)' }}>{levelSubtitle}</p>
        </div>
        <span
          className="text-[9px] uppercase tracking-[0.2em] rounded px-2 py-0.5 border"
          style={{ borderColor: 'rgba(121,196,255,0.3)', color: '#79c4ff', background: 'rgba(121,196,255,0.08)' }}
        >
          L{activeLevel}
        </span>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        {activeLevel === 1 && (
          <ContinentSelector active={null} />
        )}

        {model.dashboard.sections.map((section) => (
          <DashboardSectionCard key={section.id} section={section} />
        ))}

        {model.dashboard.sections.length === 0 && (
          <p className="text-xs mt-4" style={{ color: 'rgba(217,239,255,0.45)' }}>
            No data available for this view.
          </p>
        )}
      </div>
    </aside>
  )
}
