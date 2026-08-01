import { useEffect, useMemo, useState } from 'react'
import type { CSSProperties } from 'react'
import { useCountryStore } from '../../stores/countryStore'
import { useZoomStore } from '../../stores/zoomStore'
import { isoToFlag, formatArea } from '../../data/countries'
import { ECONOMIC_DATA_BY_ISO } from '../../data/economicData'
import { buildCountryDashboardMock } from '../../data/countryDashboardMock'

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

function MiniChart({
  title,
  series,
  color,
  unit = '',
}: {
  title: string
  series: Array<{ label: string; value: number }>
  color: string
  unit?: string
}) {
  const width = 240
  const height = 68
  const padded = 8
  const values = series.map((point) => point.value)
  const min = Math.min(...values)
  const max = Math.max(...values)
  const range = max - min || 1

  const points = series
    .map((point, index) => {
      const x = padded + (index * (width - padded * 2)) / Math.max(series.length - 1, 1)
      const y = height - padded - ((point.value - min) / range) * (height - padded * 2)
      return `${x},${y}`
    })
    .join(' ')

  return (
    <div className="rounded-lg border p-2" style={sectionBoxStyle}>
      <div className="mb-1 flex items-baseline justify-between">
        <span className="text-[10px] uppercase tracking-[0.2em]" style={{ color: 'rgba(121,196,255,0.68)' }}>
          {title}
        </span>
        <span className="text-xs" style={{ color: '#d9efff' }}>
          {series[series.length - 1]?.value.toFixed(2)}{unit}
        </span>
      </div>
      <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none" role="img" aria-label={title}>
        <polyline fill="none" stroke={color} strokeWidth="2" points={points} />
      </svg>
      <div className="mt-1 flex justify-between text-[10px]" style={{ color: 'rgba(217,239,255,0.52)' }}>
        <span>{series[0]?.label}</span>
        <span>{min.toFixed(1)}{unit}</span>
        <span>{max.toFixed(1)}{unit}</span>
        <span>{series[series.length - 1]?.label}</span>
      </div>
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

const sectionBoxStyle: CSSProperties = {
  background: 'rgba(11, 17, 30, 0.68)',
  borderColor: 'rgba(121,196,255,0.16)',
}

export default function CountryPanel() {
  const selectedCountry = useCountryStore((s) => s.selectedCountry)
  const isPanelOpen = useCountryStore((s) => s.isPanelOpen)
  const closePanel = useCountryStore((s) => s.closePanel)
  const activeLevel = useZoomStore((s) => s.activeLevel)

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

  const economic = displayCountry ? ECONOMIC_DATA_BY_ISO.get(displayCountry.isoCode) ?? null : null
  const dashboard = useMemo(
    () => (displayCountry ? buildCountryDashboardMock(displayCountry, economic) : null),
    [displayCountry, economic],
  )

  if (!isMounted || !displayCountry || !dashboard) return null

  return (
    <aside
      className="absolute right-3 top-3 bottom-3 z-20 flex w-[min(30rem,42vw)] min-w-[18rem] max-w-[92vw] flex-col overflow-hidden rounded-xl border"
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
            Country Command Center
          </p>
          <p className="text-xs" style={{ color: 'rgba(217,239,255,0.75)' }}>Country View V4</p>
        </div>
        <button
          type="button"
          onClick={closePanel}
          className="h-7 w-7 rounded text-sm"
          style={{ color: 'rgba(121,196,255,0.88)', background: 'rgba(17, 25, 42, 0.74)' }}
          aria-label="Close Country Command Center"
        >
          ✕
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4">
        <section className="mb-3 rounded-lg border p-3" style={sectionBoxStyle}>
          <div className="mb-2 flex items-start gap-3">
            <span className="text-4xl" aria-label={`Flag of ${displayCountry.englishName}`}>{isoToFlag(displayCountry.isoCode)}</span>
            <div>
              <h2 className="text-lg font-semibold" style={{ color: '#d9efff' }}>{displayCountry.name}</h2>
              <p className="text-xs" style={{ color: 'rgba(217,239,255,0.58)' }}>{displayCountry.capital} • {displayCountry.continent}</p>
            </div>
          </div>
          <LabelRow label="Population" value={formatNumber(economic?.population ?? null)} />
          <LabelRow label="Area" value={formatArea(displayCountry.area)} />
          <LabelRow label="GDP" value={formatMoneyUsdB(economic?.gdpUsd ?? null)} />
          <LabelRow label="GDP per Capita" value={economic?.gdpPerCapitaUsd == null ? '—' : `$${Math.round(economic.gdpPerCapitaUsd).toLocaleString('en-US')}`} />
          <LabelRow label="GDP Growth" value={formatRate(dashboard.gdpGrowthPercent)} />
          <LabelRow label="Inflation" value={formatRate(dashboard.inflationPercent)} />
          <LabelRow label="Interest Rate" value={formatRate(dashboard.interestRatePercent)} />
          <LabelRow label="Unemployment" value={formatRate(dashboard.unemploymentPercent)} />
          <LabelRow label="PMI" value={dashboard.pmi.toFixed(1)} />
          <LabelRow label="Public Debt" value={formatRate(dashboard.publicDebtPercentGdp)} />
          <LabelRow label="Exports" value={formatMoneyUsdB(dashboard.exportsUsdB)} />
          <LabelRow label="Imports" value={formatMoneyUsdB(dashboard.importsUsdB)} />
          <LabelRow label="FX Reserves" value={formatMoneyUsdB(dashboard.fxReservesUsdB)} />
          <LabelRow label="Credit Rating" value={dashboard.creditRating} />
        </section>

        <section className="mb-3 grid grid-cols-1 gap-2 sm:grid-cols-2">
          <MiniChart title="GDP Chart" series={dashboard.gdpChart} color="#34d399" unit="B" />
          <MiniChart title="Inflation Chart" series={dashboard.inflationChart} color="#f59e0b" unit="%" />
          <MiniChart title="Interest Rate Chart" series={dashboard.interestRateChart} color="#60a5fa" unit="%" />
          <MiniChart title="Trade Balance Chart" series={dashboard.tradeBalanceChart} color="#a78bfa" unit="B" />
        </section>

        <section className="mb-3 rounded-lg border p-3" style={sectionBoxStyle}>
          <h3 className="mb-2 text-[11px] uppercase tracking-[0.2em]" style={{ color: 'rgba(121,196,255,0.7)' }}>Top Companies</h3>
          <div className="space-y-2">
            {dashboard.topCompanies.map((company) => (
              <div key={company.name} className="rounded border px-2 py-2 text-xs" style={{ borderColor: 'rgba(121,196,255,0.16)' }}>
                <div className="font-medium" style={{ color: '#d9efff' }}>{company.name}</div>
                <div className="mt-1 grid grid-cols-3 gap-2" style={{ color: 'rgba(217,239,255,0.62)' }}>
                  <span>Cap: ${company.marketCapUsdB.toFixed(1)}B</span>
                  <span>{company.industry}</span>
                  <span>{company.headquarters}</span>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="mb-3 rounded-lg border p-3" style={sectionBoxStyle}>
          <h3 className="mb-2 text-[11px] uppercase tracking-[0.2em]" style={{ color: 'rgba(121,196,255,0.7)' }}>Economic Sectors</h3>
          <div className="space-y-2">
            {dashboard.sectors.map((sector) => (
              <div key={sector.name}>
                <div className="mb-1 flex items-center justify-between text-xs">
                  <span style={{ color: '#d9efff' }}>{sector.name}</span>
                  <span style={{ color: 'rgba(217,239,255,0.62)' }}>{sector.sharePercent}%</span>
                </div>
                <div className="h-1.5 rounded" style={{ background: 'rgba(121,196,255,0.15)' }}>
                  <div className="h-full rounded" style={{ width: `${sector.sharePercent}%`, background: '#60a5fa' }} />
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="mb-3 rounded-lg border p-3" style={sectionBoxStyle}>
          <h3 className="mb-2 text-[11px] uppercase tracking-[0.2em]" style={{ color: 'rgba(121,196,255,0.7)' }}>News Panel</h3>
          <div className="space-y-2 text-xs">
            {dashboard.news.map((item) => (
              <div key={`${item.category}-${item.title}`} className="rounded border p-2" style={{ borderColor: 'rgba(121,196,255,0.14)' }}>
                <p className="mb-1 uppercase tracking-[0.16em]" style={{ color: 'rgba(121,196,255,0.65)' }}>{item.category}</p>
                <p style={{ color: '#d9efff' }}>{item.title}</p>
                <p className="mt-1" style={{ color: 'rgba(217,239,255,0.56)' }}>{item.source} • {item.time}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-lg border p-3" style={sectionBoxStyle}>
          <h3 className="mb-2 text-[11px] uppercase tracking-[0.2em]" style={{ color: 'rgba(121,196,255,0.7)' }}>Country Summary</h3>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="rounded border p-2" style={{ borderColor: 'rgba(121,196,255,0.16)' }}>
              <p style={{ color: 'rgba(121,196,255,0.62)' }}>Economic Health</p>
              <p style={{ color: '#d9efff' }}>{dashboard.summary.economicHealth}</p>
            </div>
            <div className="rounded border p-2" style={{ borderColor: 'rgba(121,196,255,0.16)' }}>
              <p style={{ color: 'rgba(121,196,255,0.62)' }}>Growth Trend</p>
              <p style={{ color: '#d9efff' }}>{dashboard.summary.growthTrend}</p>
            </div>
            <div className="rounded border p-2" style={{ borderColor: 'rgba(121,196,255,0.16)' }}>
              <p style={{ color: 'rgba(121,196,255,0.62)' }}>Risk Level</p>
              <p style={{ color: '#d9efff' }}>{dashboard.summary.riskLevel}</p>
            </div>
            <div className="rounded border p-2" style={{ borderColor: 'rgba(121,196,255,0.16)' }}>
              <p style={{ color: 'rgba(121,196,255,0.62)' }}>Capital Flow Status</p>
              <p style={{ color: '#d9efff' }}>{dashboard.summary.capitalFlowStatus}</p>
            </div>
          </div>
        </section>
      </div>
    </aside>
  )
}
