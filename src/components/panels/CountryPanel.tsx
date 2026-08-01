import { useCountryStore } from '../../stores/countryStore'
import { useRealtimeStore } from '../../stores/realtimeStore'
import { useZoomStore } from '../../stores/zoomStore'
import { ZOOM_LEVELS } from '../../zoom/levels'
import { isoToFlag, formatArea } from '../../data/countries'
import { ECONOMIC_DATA_BY_ISO } from '../../data/economicData'
import { buildRealtimeEconomicMap, getLatestRealtimeRecordsByIndicator } from '../../utils/realtimeEconomic'

const toTimestamp = (value: string): number => {
  const parsed = Date.parse(value)
  return Number.isNaN(parsed) ? -1 : parsed
}

const PANEL_LABELS: Record<string, string> = {
  isoCode:      'ISO CODE',
  capital:      'CAPITAL',
  continent:    'CONTINENT',
  area:         'AREA',
  population:   'POPULATION',
  gdp:          'GDP',
  gdpPerCapita: 'GDP PER CAPITA',
  inflation:    'INFLATION',
  interestRate: 'INTEREST RATE',
  unemployment: 'UNEMPLOYMENT',
  dataSource:   'DATA SOURCE',
  lastUpdated:  'LAST UPDATED',
  loadingState: 'LOADING STATE',
  errorState:   'ERROR STATE',
  currency:     'CURRENCY',
  timeZone:     'TIME ZONE',
}

function DataRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-0.5 py-2" style={{ borderBottom: '1px solid rgba(121,196,255,0.1)' }}>
      <span
        className="text-[10px] tracking-[0.18em] uppercase"
        style={{ color: 'rgba(121,196,255,0.55)' }}
      >
        {label}
      </span>
      <span className="text-sm" style={{ color: '#d9efff' }}>
        {value}
      </span>
    </div>
  )
}

export default function CountryPanel() {
  const selectedCountry = useCountryStore((s) => s.selectedCountry)
  const isPanelOpen = useCountryStore((s) => s.isPanelOpen)
  const closePanel = useCountryStore((s) => s.closePanel)
  const activeLevel = useZoomStore((s) => s.activeLevel)
  const records = useRealtimeStore((s) => s.records)
  const sourceState = useRealtimeStore((s) => s.sourceState)
  const lastPipelineRunAt = useRealtimeStore((s) => s.lastPipelineRunAt)

  if (!ZOOM_LEVELS[activeLevel].panel.showCountryPanel || !isPanelOpen || !selectedCountry) return null

  const flag = isoToFlag(selectedCountry.isoCode)
  const realtimeEconomicData = buildRealtimeEconomicMap(records, ECONOMIC_DATA_BY_ISO)
  const econ =
    realtimeEconomicData.get(selectedCountry.isoCode) ??
    ECONOMIC_DATA_BY_ISO.get(selectedCountry.isoCode) ??
    null
  const latestByIndicator = getLatestRealtimeRecordsByIndicator(records, selectedCountry.isoCode)
  const unemployment = latestByIndicator.unemployment?.value ?? null

  const activeSourceIds = Array.from(
    new Set(
      Object.values(latestByIndicator)
        .map((record) => record.source)
        .filter((source): source is keyof typeof sourceState => source != null),
    ),
  )

  const dataSource = activeSourceIds.length > 0
    ? activeSourceIds
      .map((source) => sourceState[source].sourceName || source)
      .join(', ')
    : 'Placeholder'

  const sourceStates = activeSourceIds.length > 0
    ? activeSourceIds.map((source) => sourceState[source])
    : Object.values(sourceState)

  const lastUpdated = sourceStates
    .map((state) => state.lastUpdatedAt)
    .filter((value): value is string => value != null)
    .reduce<string | null>((latest, current) => {
      if (!latest) return current
      return toTimestamp(current) >= toTimestamp(latest) ? current : latest
    }, null) ?? lastPipelineRunAt

  const isLoading = sourceStates.some(
    (state) =>
      state.loading ||
      state.connectorStatus === 'fetching' ||
      state.connectorStatus === 'retrying',
  )

  const errorState = sourceStates
    .map((state) => state.error ?? state.lastError)
    .find((message): message is string => message != null) ?? null

  const fmt = (n: number | null, suffix = '') =>
    n == null ? '—' : n.toLocaleString('en-US') + suffix

  const BILLION = 1_000
  const fmtGdp = (n: number | null) => {
    if (n == null) return '—'
    if (n >= BILLION) return `$${(n / BILLION).toFixed(2)}T`
    return `$${n.toFixed(2)}B`
  }

  const fmtGdpPerCapita = (n: number | null) =>
    n == null ? '—' : `$${n.toLocaleString('en-US')}`

  const fmtRate = (n: number | null) =>
    n == null ? '—' : `${n.toFixed(2)}%`

  const fmtLastUpdated = (value: string | null) => {
    if (!value) return '—'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return value
    return date.toLocaleString('en-US')
  }

  return (
    <aside
      className="absolute right-0 top-0 h-full w-72 flex flex-col overflow-hidden"
      style={{
        background: 'rgba(8, 13, 24, 0.88)',
        borderLeft: '1px solid rgba(121,196,255,0.18)',
        backdropFilter: 'blur(12px)',
        zIndex: 20,
      }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between px-4 py-3"
        style={{ borderBottom: '1px solid rgba(121,196,255,0.18)' }}
      >
        <span
          className="text-[10px] tracking-[0.3em] uppercase"
          style={{ color: 'rgba(121,196,255,0.6)' }}
        >
          Country Info
        </span>
        <button
          type="button"
          onClick={closePanel}
          className="flex items-center justify-center w-6 h-6 rounded transition-opacity hover:opacity-70"
          style={{ color: 'rgba(121,196,255,0.6)' }}
          aria-label="Close country panel"
        >
          ✕
        </button>
      </div>

      {/* Flag + name */}
      <div
        className="px-4 py-4 flex flex-col gap-2"
        style={{ borderBottom: '1px solid rgba(121,196,255,0.12)' }}
      >
        <span className="text-5xl leading-none select-none" aria-label={`Flag of ${selectedCountry.englishName}`}>
          {flag}
        </span>
        <h2 className="text-lg font-semibold leading-tight" style={{ color: '#d9efff' }}>
          {selectedCountry.name}
        </h2>
        {selectedCountry.englishName !== selectedCountry.name && (
          <p className="text-xs" style={{ color: 'rgba(217,239,255,0.5)' }}>
            {selectedCountry.englishName}
          </p>
        )}
      </div>

      {/* Data rows */}
      <div className="flex-1 overflow-y-auto px-4 py-1">
        <DataRow label={PANEL_LABELS.isoCode}      value={`${selectedCountry.isoCode} / ${selectedCountry.iso3Code}`} />
        <DataRow label={PANEL_LABELS.capital}      value={selectedCountry.capital} />
        <DataRow label={PANEL_LABELS.continent}    value={selectedCountry.continent} />
        <DataRow label={PANEL_LABELS.area}         value={formatArea(selectedCountry.area)} />
        <DataRow label={PANEL_LABELS.population}   value={econ ? fmt(econ.population) : '—'} />
        <DataRow label={PANEL_LABELS.gdp}          value={econ ? fmtGdp(econ.gdpUsd) : '—'} />
        <DataRow label={PANEL_LABELS.gdpPerCapita} value={econ ? fmtGdpPerCapita(econ.gdpPerCapitaUsd) : '—'} />
        <DataRow label={PANEL_LABELS.inflation}    value={econ ? fmtRate(econ.inflationPercent) : '—'} />
        <DataRow label={PANEL_LABELS.interestRate} value={econ ? fmtRate(econ.interestRatePercent) : '—'} />
        <DataRow label={PANEL_LABELS.unemployment} value={fmtRate(unemployment)} />
        <DataRow label={PANEL_LABELS.dataSource}   value={dataSource} />
        <DataRow label={PANEL_LABELS.lastUpdated}  value={fmtLastUpdated(lastUpdated)} />
        <DataRow label={PANEL_LABELS.loadingState} value={isLoading ? 'Refreshing' : 'Idle'} />
        {errorState && <DataRow label={PANEL_LABELS.errorState} value={errorState} />}
        <DataRow label={PANEL_LABELS.currency}     value={econ && econ.currency ? `${econ.currency}${econ.currencyCode ? ` (${econ.currencyCode})` : ''}` : '—'} />
        <DataRow label={PANEL_LABELS.timeZone}     value={econ && econ.timeZones.length > 0 ? econ.timeZones[0] : '—'} />
      </div>
    </aside>
  )
}
