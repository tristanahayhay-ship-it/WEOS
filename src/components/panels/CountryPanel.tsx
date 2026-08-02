import { useEffect, useMemo, useState } from 'react'
import type { CSSProperties } from 'react'
import { isoToFlag, formatArea } from '../../data/countries'
import { useCountryStore } from '../../stores/countryStore'
import { useCountryEconomicStore } from '../../stores/countryEconomicStore'
import { useEconomicStore } from '../../stores/economicStore'
import { useRealtimeStore } from '../../stores/realtimeStore'
import { useZoomStore } from '../../stores/zoomStore'
import type { CountryEconomicData } from '../../types/country'
import type { EconomicDataPoint } from '../../types/economic'
import { buildRealtimeEconomicMap } from '../../utils/realtimeEconomic'
import type { CountryDashboardData, IndicatorGroup } from '../../data/countryDashboardMock'

const EXIT_ANIMATION_MS = 260

function formatNumber(value: number | null, suffix = '') {
  if (value == null) return '—'
  return `${value.toLocaleString('en-US')}${suffix}`
}

function formatMoneyUsdB(value: number | null) {
  if (value == null) return '—'
  if (value >= 1000) return `$${(value / 1000).toFixed(2)}T`
  return `$${value.toFixed(2)}B`
}

function formatRate(value: number | null) {
  if (value == null) return '—'
  return `${value.toFixed(2)}%`
}

function formatObservedAt(value: string | null) {
  if (!value) return null
  const parsed = Date.parse(value)
  if (Number.isNaN(parsed)) return null
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date(parsed))
}

function getNormalizedWidth(values: number[], current: number) {
  const max = Math.max(1, current, ...values)
  return Math.max(0.14, Math.min(current / max, 1))
}

function collectEconomicValues(
  records: ReadonlyMap<string, CountryEconomicData>,
  selector: (value: CountryEconomicData) => number | null,
) {
  const values: number[] = []
  for (const record of records.values()) {
    const next = selector(record)
    if (next != null && Number.isFinite(next)) {
      values.push(next)
    }
  }
  return values
}

function getLatestRecord(records: EconomicDataPoint[]) {
  return records.reduce<EconomicDataPoint | null>((latest, record) => {
    if (record.value == null) return latest
    if (!latest) return record
    return Date.parse(record.observedAt) >= Date.parse(latest.observedAt) ? record : latest
  }, null)
}

function MiniMetricChart({
  title,
  valueLabel,
  width,
  color,
  caption,
}: {
  title: string
  valueLabel: string
  width: number
  color: string
  caption?: string | null
}) {
  return (
    <div className="rounded-lg border p-2" style={sectionBoxStyle}>
      <div className="mb-1 flex items-baseline justify-between">
        <span className="text-[10px] uppercase tracking-[0.2em]" style={{ color: 'rgba(121,196,255,0.68)' }}>
          {title}
        </span>
        <span className="text-xs" style={{ color: '#d9efff' }}>
          {valueLabel}
        </span>
      </div>
      <svg width="100%" height="56" viewBox="0 0 240 56" preserveAspectRatio="none" role="img" aria-label={title}>
        <rect x="0" y="20" width="240" height="16" rx="8" fill="rgba(121,196,255,0.12)" />
        <rect x="0" y="20" width={240 * width} height="16" rx="8" fill={color} />
      </svg>
      {caption ? (
        <p className="mt-1 text-[10px]" style={{ color: 'rgba(217,239,255,0.52)' }}>{caption}</p>
      ) : null}
    </div>
  )
}

function LabelRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-3 py-1.5 text-xs">
      <span style={{ color: 'rgba(121,196,255,0.66)' }}>{label}</span>
      <span className="text-right" style={{ color: '#d9efff' }}>{value}</span>
    </div>
  )
}

const HEALTH_COLORS: Record<string, string> = {
  Strong: '#34d399',
  Stable: '#60a5fa',
  Watching: '#f59e0b',
}

const TREND_COLORS: Record<string, string> = {
  Upward: '#34d399',
  Flat: '#94a3b8',
  Cooling: '#f87171',
}

const RISK_COLORS: Record<string, string> = {
  Low: '#34d399',
  Medium: '#f59e0b',
  High: '#f87171',
}

const FLOW_COLORS: Record<string, string> = {
  Inflow: '#34d399',
  Balanced: '#60a5fa',
  Outflow: '#f87171',
}

function SummaryBadge({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div className="flex flex-col items-center rounded-md border p-2 text-center" style={{ background: 'rgba(11,17,30,0.7)', borderColor: 'rgba(121,196,255,0.14)' }}>
      <span className="text-[9px] uppercase tracking-[0.18em] mb-1" style={{ color: 'rgba(121,196,255,0.6)' }}>{label}</span>
      <span className="text-xs font-semibold" style={{ color }}>{value}</span>
    </div>
  )
}

function SparklineChart({ points, color, height = 40 }: { points: { label: string; value: number }[]; color: string; height?: number }) {
  if (points.length < 2) return null
  const values = points.map((p) => p.value)
  const min = Math.min(...values)
  const max = Math.max(...values)
  const range = max - min || 1
  const w = 240
  const step = w / (points.length - 1)
  const pathD = points.map((p, i) => {
    const x = i * step
    const y = height - ((p.value - min) / range) * (height - 6) - 3
    return `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`
  }).join(' ')
  return (
    <svg width="100%" height={height} viewBox={`0 0 ${w} ${height}`} preserveAspectRatio="none" aria-hidden="true">
      <path d={pathD} fill="none" stroke={color} strokeWidth="1.8" strokeLinejoin="round" strokeLinecap="round" />
    </svg>
  )
}

function SparklineCard({ title, valueLabel, points, color }: { title: string; valueLabel: string; points: { label: string; value: number }[]; color: string }) {
  return (
    <div className="rounded-lg border p-2" style={sectionBoxStyle}>
      <div className="mb-1 flex items-baseline justify-between">
        <span className="text-[10px] uppercase tracking-[0.2em]" style={{ color: 'rgba(121,196,255,0.68)' }}>{title}</span>
        <span className="text-xs" style={{ color: '#d9efff' }}>{valueLabel}</span>
      </div>
      <SparklineChart points={points} color={color} />
    </div>
  )
}

function SectorBar({ name, share }: { name: string; share: number }) {
  return (
    <div className="mb-1.5">
      <div className="flex justify-between text-[10px] mb-0.5">
        <span style={{ color: 'rgba(217,239,255,0.72)' }}>{name}</span>
        <span style={{ color: '#d9efff' }}>{share}%</span>
      </div>
      <div className="w-full rounded-full h-1.5" style={{ background: 'rgba(121,196,255,0.12)' }}>
        <div className="h-1.5 rounded-full" style={{ width: `${share}%`, background: 'rgba(96,165,250,0.7)' }} />
      </div>
    </div>
  )
}

const NEWS_CATEGORY_COLORS: Record<string, string> = {
  economic: '#34d399',
  policy: '#a78bfa',
  market: '#60a5fa',
}

const sectionBoxStyle: CSSProperties = {
  background: 'rgba(11, 17, 30, 0.68)',
  borderColor: 'rgba(121,196,255,0.16)',
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <h3 className="mb-2 text-[11px] uppercase tracking-[0.2em]" style={{ color: 'rgba(121,196,255,0.7)' }}>
      {children}
    </h3>
  )
}

/**
 * Renders a single indicator group cluster.
 * Hidden automatically when the group has no metrics.
 */
function IndicatorGroupSection({ group }: { group: IndicatorGroup }) {
  if (group.metrics.length === 0) return null
  return (
    <div className="rounded-md border px-3 py-2" style={sectionBoxStyle}>
      <p className="mb-1.5 text-[10px] uppercase tracking-[0.18em]" style={{ color: 'rgba(121,196,255,0.6)' }}>
        {group.title}
      </p>
      {group.metrics.map((metric) => (
        <div key={metric.label} className="flex items-center justify-between gap-2 py-0.5 text-[11px]">
          <span style={{ color: 'rgba(121,196,255,0.6)' }}>{metric.label}</span>
          <span style={{ color: metric.color ?? '#d9efff' }}>{metric.value}</span>
        </div>
      ))}
    </div>
  )
}

function DashboardSections({ dashboard }: { dashboard: CountryDashboardData }) {
  return (
    <>
      {/* Summary badges */}
      <section className="mb-3 rounded-lg border p-3" style={sectionBoxStyle}>
        <SectionTitle>Economic Summary</SectionTitle>
        <div className="grid grid-cols-2 gap-1.5">
          <SummaryBadge label="Health" value={dashboard.summary.economicHealth} color={HEALTH_COLORS[dashboard.summary.economicHealth] ?? '#d9efff'} />
          <SummaryBadge label="Growth" value={dashboard.summary.growthTrend} color={TREND_COLORS[dashboard.summary.growthTrend] ?? '#d9efff'} />
          <SummaryBadge label="Risk" value={dashboard.summary.riskLevel} color={RISK_COLORS[dashboard.summary.riskLevel] ?? '#d9efff'} />
          <SummaryBadge label="Capital" value={dashboard.summary.capitalFlowStatus} color={FLOW_COLORS[dashboard.summary.capitalFlowStatus] ?? '#d9efff'} />
        </div>
      </section>

      {/* Macro dashboard metrics */}
      <section className="mb-3 rounded-lg border p-3" style={sectionBoxStyle}>
        <SectionTitle>Key Indicators</SectionTitle>
        <LabelRow label="GDP Growth" value={`${dashboard.gdpGrowthPercent.toFixed(2)}%`} />
        <LabelRow label="PMI" value={dashboard.pmi.toFixed(1)} />
        <LabelRow label="Public Debt / GDP" value={`${dashboard.publicDebtPercentGdp.toFixed(1)}%`} />
        <LabelRow label="FX Reserves" value={formatMoneyUsdB(dashboard.fxReservesUsdB)} />
        <LabelRow label="Credit Rating" value={dashboard.creditRating} />
        <LabelRow label="Exports" value={formatMoneyUsdB(dashboard.exportsUsdB)} />
        <LabelRow label="Imports" value={formatMoneyUsdB(dashboard.importsUsdB)} />
        <LabelRow
          label="Trade Balance"
          value={`${dashboard.exportsUsdB - dashboard.importsUsdB >= 0 ? '+' : ''}${formatMoneyUsdB(dashboard.exportsUsdB - dashboard.importsUsdB)}`}
        />
      </section>

      {/* Sparkline charts */}
      <section className="mb-3 rounded-lg border p-3" style={sectionBoxStyle}>
        <SectionTitle>Historical Trends</SectionTitle>
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
          <SparklineCard title="GDP" valueLabel={`${dashboard.gdpGrowthPercent.toFixed(1)}% growth`} points={dashboard.gdpChart} color="#34d399" />
          <SparklineCard title="Inflation" valueLabel={formatRate(dashboard.inflationPercent)} points={dashboard.inflationChart} color="#f59e0b" />
          <SparklineCard title="Interest Rate" valueLabel={formatRate(dashboard.interestRatePercent)} points={dashboard.interestRateChart} color="#22c55e" />
          <SparklineCard title="Trade Balance" valueLabel="6-month" points={dashboard.tradeBalanceChart} color="#60a5fa" />
        </div>
      </section>

      {/* Sectors */}
      <section className="mb-3 rounded-lg border p-3" style={sectionBoxStyle}>
        <SectionTitle>Economic Sectors</SectionTitle>
        {dashboard.sectors.map((sector) => (
          <SectorBar key={sector.name} name={sector.name} share={sector.sharePercent} />
        ))}
      </section>

      {/* Top companies */}
      <section className="mb-3 rounded-lg border p-3" style={sectionBoxStyle}>
        <SectionTitle>Top Companies</SectionTitle>
        {dashboard.topCompanies.map((company) => (
          <div key={company.name} className="flex items-start justify-between gap-2 py-1.5 border-b last:border-0" style={{ borderColor: 'rgba(121,196,255,0.1)' }}>
            <div>
              <p className="text-[11px]" style={{ color: '#d9efff' }}>{company.name}</p>
              <p className="text-[10px]" style={{ color: 'rgba(121,196,255,0.6)' }}>{company.industry} · {company.headquarters}</p>
            </div>
            <span className="text-[11px] shrink-0" style={{ color: '#34d399' }}>{formatMoneyUsdB(company.marketCapUsdB)}</span>
          </div>
        ))}
      </section>

      {/* Indicator groups — only rendered groups with available data are shown */}
      {dashboard.indicatorGroups && dashboard.indicatorGroups.length > 0 ? (
        <section className="mb-3 rounded-lg border p-3" style={sectionBoxStyle}>
          <SectionTitle>Economic Indicators</SectionTitle>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            {dashboard.indicatorGroups.map((group) => (
              <IndicatorGroupSection key={group.id} group={group} />
            ))}
          </div>
        </section>
      ) : null}

      {/* News feed */}
      <section className="mb-3 rounded-lg border p-3" style={sectionBoxStyle}>
        <SectionTitle>Latest News</SectionTitle>
        {dashboard.news.map((item) => (
          <div key={item.title} className="mb-2 last:mb-0">
            <div className="flex items-center gap-1.5 mb-0.5">
              <span
                className="text-[9px] uppercase tracking-[0.15em] rounded px-1 py-0.5"
                style={{
                  color: NEWS_CATEGORY_COLORS[item.category] ?? '#d9efff',
                  background: 'rgba(121,196,255,0.1)',
                }}
              >
                {item.category}
              </span>
              <span className="text-[10px]" style={{ color: 'rgba(217,239,255,0.45)' }}>{item.time}</span>
            </div>
            <p className="text-[11px] leading-snug" style={{ color: 'rgba(217,239,255,0.85)' }}>{item.title}</p>
            <p className="text-[10px] mt-0.5" style={{ color: 'rgba(121,196,255,0.5)' }}>{item.source}</p>
          </div>
        ))}
      </section>
    </>
  )
}

export default function CountryPanel() {
  const selectedCountry = useCountryStore((s) => s.selectedCountry)
  const isPanelOpen = useCountryStore((s) => s.isPanelOpen)
  const closePanel = useCountryStore((s) => s.closePanel)
  const activeLevel = useZoomStore((s) => s.activeLevel)
  const economicRecords = useEconomicStore((s) => s.data)
  const realtimeRecords = useRealtimeStore((s) => s.records)
  const dashboard = useCountryEconomicStore((s) => s.dashboard)
  const countryEconomicLayer = useCountryEconomicStore((s) => s.layer)
  const loadCountryEconomicLayer = useCountryEconomicStore((s) => s.loadForCountry)

  const shouldBeVisible = activeLevel === 2 && isPanelOpen && selectedCountry !== null
  const [isMounted, setIsMounted] = useState(shouldBeVisible)
  const [isVisible, setIsVisible] = useState(shouldBeVisible)
  const [displayCountry, setDisplayCountry] = useState(selectedCountry)

  useEffect(() => {
    if (shouldBeVisible && selectedCountry) {
      setDisplayCountry(selectedCountry)
      setIsMounted(true)
      const frame = window.requestAnimationFrame(() => setIsVisible(true))
      return () => window.cancelAnimationFrame(frame)
    }

    setIsVisible(false)
    const timer = window.setTimeout(() => {
      setIsMounted(false)
      setDisplayCountry(null)
    }, EXIT_ANIMATION_MS)
    return () => window.clearTimeout(timer)
  }, [shouldBeVisible, selectedCountry])

  useEffect(() => {
    if (displayCountry) {
      loadCountryEconomicLayer(displayCountry)
    }
  }, [displayCountry, loadCountryEconomicLayer])

  const liveRecords = useMemo(
    () => Object.values(realtimeRecords).filter((record) => !record.isMock),
    [realtimeRecords],
  )
  const liveRecordsByKey = useMemo(
    () => Object.fromEntries(liveRecords.map((record) => [record.key, record])),
    [liveRecords],
  )
  const mergedEconomicRecords = useMemo(
    () => buildRealtimeEconomicMap(liveRecordsByKey, economicRecords),
    [liveRecordsByKey, economicRecords],
  )
  const economic = displayCountry ? mergedEconomicRecords.get(displayCountry.isoCode) ?? null : null

  const liveRecordsForCountry = useMemo(() => {
    if (!displayCountry) return []
    return liveRecords.filter((record) => record.countryCode === displayCountry.isoCode)
  }, [displayCountry, liveRecords])

  const unemploymentRecord = useMemo(
    () => getLatestRecord(liveRecordsForCountry.filter((record) => record.indicator === 'unemployment')),
    [liveRecordsForCountry],
  )
  const macroMetrics = useMemo(() => {
    if (!displayCountry) return []

    const rows: Array<{ label: string; value: string }> = [
      { label: 'Population', value: formatNumber(economic?.population ?? null) },
      { label: 'Area', value: formatArea(displayCountry.area) },
      { label: 'GDP', value: formatMoneyUsdB(economic?.gdpUsd ?? null) },
      {
        label: 'GDP per Capita',
        value: economic?.gdpPerCapitaUsd == null ? '—' : `$${Math.round(economic.gdpPerCapitaUsd).toLocaleString('en-US')}`,
      },
      { label: 'Inflation', value: formatRate(economic?.inflationPercent ?? null) },
      { label: 'Interest Rate', value: formatRate(economic?.interestRatePercent ?? null) },
    ]

    if (unemploymentRecord?.value != null) {
      rows.push({ label: 'Unemployment', value: formatRate(unemploymentRecord.value) })
    }

    return rows.filter((row) => row.value !== '—')
  }, [displayCountry, economic, unemploymentRecord])

  const gdpValues = useMemo(
    () => collectEconomicValues(mergedEconomicRecords, (record) => record.gdpUsd),
    [mergedEconomicRecords],
  )
  const gdpPerCapitaValues = useMemo(
    () => collectEconomicValues(mergedEconomicRecords, (record) => record.gdpPerCapitaUsd),
    [mergedEconomicRecords],
  )
  const populationValues = useMemo(
    () => collectEconomicValues(mergedEconomicRecords, (record) => record.population),
    [mergedEconomicRecords],
  )
  const inflationValues = useMemo(
    () => collectEconomicValues(mergedEconomicRecords, (record) => record.inflationPercent),
    [mergedEconomicRecords],
  )
  const interestRateValues = useMemo(
    () => collectEconomicValues(mergedEconomicRecords, (record) => record.interestRatePercent),
    [mergedEconomicRecords],
  )
  const unemploymentValues = useMemo(
    () => liveRecords
      .filter((record) => record.indicator === 'unemployment' && record.value != null)
      .map((record) => record.value as number),
    [liveRecords],
  )

  const miniCharts = useMemo(() => {
    if (!economic) return []

    const charts: Array<{ title: string; valueLabel: string; width: number; color: string; caption?: string | null }> = []

    if (economic.gdpUsd != null) {
      charts.push({
        title: 'GDP',
        valueLabel: formatMoneyUsdB(economic.gdpUsd),
        width: getNormalizedWidth(gdpValues, economic.gdpUsd),
        color: '#34d399',
      })
    }

    if (economic.gdpPerCapitaUsd != null) {
      charts.push({
        title: 'GDP per Capita',
        valueLabel: `$${Math.round(economic.gdpPerCapitaUsd).toLocaleString('en-US')}`,
        width: getNormalizedWidth(gdpPerCapitaValues, economic.gdpPerCapitaUsd),
        color: '#60a5fa',
      })
    }

    if (economic.population != null) {
      charts.push({
        title: 'Population',
        valueLabel: formatNumber(economic.population),
        width: getNormalizedWidth(populationValues, economic.population),
        color: '#a78bfa',
      })
    }

    if (economic.inflationPercent != null) {
      charts.push({
        title: 'Inflation',
        valueLabel: formatRate(economic.inflationPercent),
        width: getNormalizedWidth(inflationValues, economic.inflationPercent),
        color: '#f59e0b',
      })
    }

    if (economic.interestRatePercent != null) {
      charts.push({
        title: 'Interest Rate',
        valueLabel: formatRate(economic.interestRatePercent),
        width: getNormalizedWidth(interestRateValues, economic.interestRatePercent),
        color: '#22c55e',
      })
    }

    if (unemploymentRecord?.value != null) {
      charts.push({
        title: 'Unemployment',
        valueLabel: formatRate(unemploymentRecord.value),
        width: getNormalizedWidth(unemploymentValues, unemploymentRecord.value),
        color: '#fb7185',
        caption: formatObservedAt(unemploymentRecord.observedAt),
      })
    }

    return charts
  }, [
    economic,
    gdpPerCapitaValues,
    gdpValues,
    inflationValues,
    interestRateValues,
    populationValues,
    unemploymentRecord,
    unemploymentValues,
  ])

  const capitalFlowSummary = useMemo(() => {
    if (!displayCountry || !countryEconomicLayer || countryEconomicLayer.isoCode !== displayCountry.isoCode) return []

    let capitalLinks = 0
    let capitalMagnitude = 0
    let tradeLinks = 0
    let tradeMagnitude = 0

    for (const flow of countryEconomicLayer.flows) {
      if (flow.type === 'capital') {
        capitalLinks += 1
        capitalMagnitude += flow.value
      }

      if (flow.type === 'trade') {
        tradeLinks += 1
        tradeMagnitude += flow.value
      }
    }

    const rows: Array<{ label: string; value: string }> = []
    if (capitalLinks > 0) {
      rows.push({
        label: 'Capital Flows',
        value: `${capitalLinks} links • ${Math.round(capitalMagnitude).toLocaleString('en-US')} intensity`,
      })
    }
    if (tradeLinks > 0) {
      rows.push({
        label: 'Trade Network',
        value: `${tradeLinks} links • ${Math.round(tradeMagnitude).toLocaleString('en-US')} intensity`,
      })
    }

    return rows
  }, [countryEconomicLayer, displayCountry])

  if (!isMounted || !displayCountry) return null

  return (
    <aside
      className="absolute inset-3 z-20 flex w-auto flex-col overflow-hidden rounded-xl border sm:inset-auto sm:right-3 sm:top-3 sm:bottom-3 sm:w-[min(30rem,42vw)] sm:min-w-[18rem] sm:max-w-[92vw]"
      style={{
        background: 'rgba(7, 12, 22, 0.82)',
        borderColor: 'rgba(121,196,255,0.22)',
        backdropFilter: 'blur(14px)',
        boxShadow: '0 14px 40px rgba(3,7,14,0.52)',
        transform: isVisible ? 'translateX(0)' : 'translateX(36px)',
        opacity: isVisible ? 1 : 0,
        transition: `opacity ${EXIT_ANIMATION_MS}ms ease, transform ${EXIT_ANIMATION_MS}ms ease`,
        pointerEvents: isVisible ? 'auto' : 'none',
      }}
    >
      <div className="flex items-center justify-between border-b px-4 py-3" style={{ borderColor: 'rgba(121,196,255,0.16)' }}>
        <div>
          <p className="text-[10px] uppercase tracking-[0.24em]" style={{ color: 'rgba(121,196,255,0.68)' }}>
            National Dashboard
          </p>
          <p className="text-xs" style={{ color: 'rgba(217,239,255,0.75)' }}>Country View Final</p>
        </div>
        <button
          type="button"
          onClick={closePanel}
          className="h-7 w-7 rounded text-sm"
          style={{ color: 'rgba(121,196,255,0.88)', background: 'rgba(17, 25, 42, 0.74)' }}
          aria-label="Close country dashboard"
        >
          ✕
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4">
        {/* Country identity */}
        <section className="mb-3 rounded-lg border p-3" style={sectionBoxStyle}>
          <div className="mb-2 flex items-start gap-3">
            <span className="text-4xl" aria-label={`Flag of ${displayCountry.englishName}`}>{isoToFlag(displayCountry.isoCode)}</span>
            <div>
              <h2 className="text-lg font-semibold" style={{ color: '#d9efff' }}>{displayCountry.name}</h2>
              <p className="text-xs" style={{ color: 'rgba(217,239,255,0.58)' }}>{displayCountry.capital} • {displayCountry.continent}</p>
            </div>
          </div>
          {macroMetrics.length > 0 ? (
            macroMetrics.map((metric) => <LabelRow key={metric.label} label={metric.label} value={metric.value} />)
          ) : (
            <p className="text-xs" style={{ color: 'rgba(217,239,255,0.58)' }}>
              Macro data will appear here as structured country data becomes available.
            </p>
          )}
        </section>

        {/* Realtime bar charts — from live economic store */}
        {miniCharts.length > 0 ? (
          <section className="mb-3 rounded-lg border p-3" style={sectionBoxStyle}>
            <SectionTitle>Live Metrics</SectionTitle>
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
              {miniCharts.map((chart) => (
                <MiniMetricChart
                  key={chart.title}
                  title={chart.title}
                  valueLabel={chart.valueLabel}
                  width={chart.width}
                  color={chart.color}
                  caption={chart.caption}
                />
              ))}
            </div>
          </section>
        ) : null}

        {/* Capital flow summary — from 3D economic layer */}
        {capitalFlowSummary.length > 0 ? (
          <section className="mb-3 rounded-lg border p-3" style={sectionBoxStyle}>
            <SectionTitle>Capital Flow Summary</SectionTitle>
            {capitalFlowSummary.map((item) => <LabelRow key={item.label} label={item.label} value={item.value} />)}
          </section>
        ) : null}

        {/* Full dashboard sections — rendered once dashboard data is available */}
        {dashboard ? <DashboardSections dashboard={dashboard} /> : null}
      </div>
    </aside>
  )
}
