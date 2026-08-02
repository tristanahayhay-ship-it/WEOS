import { useUIStore } from '../../stores/uiStore'
import { useCountryStore } from '../../stores/countryStore'
import { useZoomStore } from '../../stores/zoomStore'
import { isoToFlag } from '../../data/countries'
import type { TopbarTab, CountryTab } from '../../types/ui'

const GLOBAL_TABS: { id: TopbarTab; label: string }[] = [
  { id: 'global-view', label: 'GLOBAL VIEW' },
  { id: 'flows', label: 'FLOWS' },
  { id: 'sectors', label: 'SECTORS' },
  { id: 'nations', label: 'NATIONS' },
  { id: 'analytics', label: 'ANALYTICS' },
  { id: 'settings', label: 'SETTINGS' },
]

const COUNTRY_TABS: { id: CountryTab; label: string }[] = [
  { id: 'overview',       label: 'OVERVIEW' },
  { id: 'economy',        label: 'ECONOMY' },
  { id: 'markets',        label: 'MARKETS' },
  { id: 'trade',          label: 'TRADE' },
  { id: 'industry',       label: 'INDUSTRY' },
  { id: 'government',     label: 'GOVERNMENT' },
  { id: 'infrastructure', label: 'INFRASTRUCTURE' },
  { id: 'news',           label: 'NEWS' },
]

/** ISO → native / official country name for the country-view subtitle */
const LOCAL_NAMES: Record<string, string> = {
  JP: '日本国',
  CN: '中华人民共和国',
  US: 'United States of America',
  DE: 'Deutschland',
  GB: 'United Kingdom',
  FR: 'République française',
  IN: 'भारत गणराज्य',
  BR: 'República Federativa do Brasil',
  RU: 'Россия',
  KR: '대한민국',
  SG: 'Singapore',
  SA: 'المملكة العربية السعودية',
  AU: 'Australia',
  ZA: 'Suid-Afrika / South Africa',
  ES: 'Reino de España',
  TR: 'Türkiye Cumhuriyeti',
  MX: 'México',
  IT: 'Repubblica Italiana',
  CA: 'Canada',
  AR: 'República Argentina',
}

export default function Topbar() {
  const { activeTab, setActiveTab, activeCountryTab, setActiveCountryTab } = useUIStore()
  const selectedCountry = useCountryStore((s) => s.selectedCountry)
  const activeLevel = useZoomStore((s) => s.activeLevel)

  const isCountryView = activeLevel === 2 && selectedCountry !== null

  if (isCountryView && selectedCountry) {
    const localName = LOCAL_NAMES[selectedCountry.isoCode] ?? selectedCountry.englishName
    const flag = isoToFlag(selectedCountry.isoCode)

    return (
      <header
        className="flex flex-col shrink-0 border-b"
        style={{
          background: 'var(--weos-surface)',
          borderColor: 'var(--weos-border)',
        }}
      >
        {/* Country identity row */}
        <div className="flex items-center gap-3 px-4 py-2">
          <span className="text-3xl leading-none" aria-label={`Flag of ${selectedCountry.englishName}`}>
            {flag}
          </span>
          <div>
            <p
              className="text-xl font-bold leading-tight tracking-widest"
              style={{ color: '#d9efff' }}
            >
              {selectedCountry.name.toUpperCase()}
            </p>
            <p className="text-[11px] tracking-wide" style={{ color: 'rgba(121,196,255,0.65)' }}>
              {selectedCountry.name.toUpperCase()} / {localName}
            </p>
          </div>
        </div>

        {/* Country-specific tabs */}
        <nav
          className="flex border-t overflow-x-auto"
          style={{ borderColor: 'rgba(121,196,255,0.1)' }}
        >
          {COUNTRY_TABS.map((tab) => {
            const isActive = activeCountryTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveCountryTab(tab.id)}
                className="px-4 py-2 text-[11px] font-semibold tracking-widest whitespace-nowrap transition-colors border-b-2"
                style={{
                  color: isActive ? '#d9efff' : 'rgba(121,196,255,0.5)',
                  borderBottomColor: isActive ? 'var(--weos-accent)' : 'transparent',
                  background: 'transparent',
                }}
              >
                {tab.label}
              </button>
            )
          })}
        </nav>
      </header>
    )
  }

  return (
    <header
      className="flex items-center h-11 px-4 shrink-0 border-b"
      style={{
        background: 'var(--weos-surface)',
        borderColor: 'var(--weos-border)',
      }}
    >
      <span
        className="text-sm font-bold tracking-widest mr-6 shrink-0"
        style={{ color: 'var(--weos-accent)' }}
      >
        WEOS
      </span>

      <nav className="flex gap-1 overflow-x-auto">
        {GLOBAL_TABS.map((tab) => {
          const isActive = activeTab === tab.id
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className="px-3 py-1.5 text-xs font-semibold tracking-wider rounded transition-colors whitespace-nowrap"
              style={{
                background: isActive ? 'var(--weos-accent)' : 'transparent',
                color: isActive ? '#fff' : 'var(--weos-text-muted)',
              }}
            >
              {tab.label}
            </button>
          )
        })}
      </nav>
    </header>
  )
}
