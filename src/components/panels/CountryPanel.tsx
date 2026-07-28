import { useCountryStore } from '../../stores/countryStore'
import { isoToFlag, formatArea } from '../../data/countries'

const PANEL_LABELS: Record<string, string> = {
  isoCode:   'ISO CODE',
  capital:   'CAPITAL',
  continent: 'CONTINENT',
  area:      'AREA',
  population:'POPULATION',
  gdp:       'GDP',
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

  if (!isPanelOpen || !selectedCountry) return null

  const flag = isoToFlag(selectedCountry.isoCode)

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
        <DataRow label={PANEL_LABELS.isoCode}    value={`${selectedCountry.isoCode} / ${selectedCountry.iso3Code}`} />
        <DataRow label={PANEL_LABELS.capital}    value={selectedCountry.capital} />
        <DataRow label={PANEL_LABELS.continent}  value={selectedCountry.continent} />
        <DataRow label={PANEL_LABELS.area}       value={formatArea(selectedCountry.area)} />
        <DataRow label={PANEL_LABELS.population} value="—" />
        <DataRow label={PANEL_LABELS.gdp}        value="—" />
      </div>

      {/* Footer note */}
      <div
        className="px-4 py-2 text-[10px]"
        style={{
          color: 'rgba(121,196,255,0.35)',
          borderTop: '1px solid rgba(121,196,255,0.1)',
        }}
      >
        Population &amp; GDP available in a future phase
      </div>
    </aside>
  )
}
