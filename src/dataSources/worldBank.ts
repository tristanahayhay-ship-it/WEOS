/**
 * World Bank Open Data Connector – Phase 6.2 (live data)
 *
 * Fetches GDP, GDP per capita, and Population for all countries using the
 * World Bank Open Data API. No API key required.
 *
 * Indicators:
 *   NY.GDP.MKTP.CD  – GDP, current USD  → stored as USD billions
 *   NY.GDP.PCAP.CD  – GDP per capita, current USD
 *   SP.POP.TOTL     – Population, total
 *
 * API reference: https://datahelpdesk.worldbank.org/knowledgebase/articles/898581
 */

import type { EconomicDataConnector, EconomicDataPoint, EconomicIndicatorCode, EconomicRawSnapshot } from '../types/economic'

const WB_BASE = 'https://api.worldbank.org/v2'
const PER_PAGE = 300

// Shape of a single World Bank indicator entry
interface WbEntry {
  country: { id: string; value: string }
  countryiso3code: string
  date: string
  value: number | null
}

// World Bank API response: a 2-element tuple [metadata, data[]]
type WbResponse = [{ pages: number; total: number }, WbEntry[] | null]

// Internal record produced by the live fetch
interface WorldBankLiveRecord {
  countryCode: string
  indicator: EconomicIndicatorCode
  value: number
  unit: string
  observedAt: string
  label: string
  wbIndicatorCode: string
}

async function fetchWbIndicator(
  indicatorCode: string,
): Promise<Map<string, { value: number | null; date: string }>> {
  const url =
    `${WB_BASE}/country/all/indicator/${indicatorCode}` +
    `?format=json&mrv=1&per_page=${PER_PAGE}`
  const res = await fetch(url)
  if (!res.ok) {
    throw new Error(`WorldBank: HTTP ${res.status} for indicator "${indicatorCode}"`)
  }
  const json = (await res.json()) as WbResponse
  const entries = json[1] ?? []
  const result = new Map<string, { value: number | null; date: string }>()
  for (const entry of entries) {
    // Skip aggregate/regional rows – only sovereign countries have a 3-letter ISO code
    if (!entry.countryiso3code || entry.countryiso3code.length !== 3) continue
    result.set(entry.country.id, { value: entry.value, date: entry.date })
  }
  return result
}

// Indicator definitions – order must match the Promise.all call below
const WB_INDICATOR_DEFS = [
  { wbCode: 'NY.GDP.MKTP.CD', indicator: 'gdp' as const, unit: 'USD billions', label: 'GDP (current US$)' },
  { wbCode: 'NY.GDP.PCAP.CD', indicator: 'gdpPerCapita' as const, unit: 'USD', label: 'GDP per capita (current US$)' },
  { wbCode: 'SP.POP.TOTL', indicator: 'population' as const, unit: 'people', label: 'Population, total' },
] as const

export const worldBankConnector: EconomicDataConnector<WorldBankLiveRecord> = {
  source: 'worldBank',

  fetchLatest: async (): Promise<EconomicRawSnapshot<WorldBankLiveRecord>> => {
    const fetchedAt = new Date().toISOString()

    const maps = await Promise.all(WB_INDICATOR_DEFS.map(({ wbCode }) => fetchWbIndicator(wbCode)))

    const records: WorldBankLiveRecord[] = []

    for (let i = 0; i < WB_INDICATOR_DEFS.length; i++) {
      const def = WB_INDICATOR_DEFS[i]
      const map = maps[i]

      for (const [countryCode, { value, date }] of map.entries()) {
        if (value === null) continue

        // GDP is returned in raw USD; normalise to billions
        const normalizedValue = def.indicator === 'gdp' ? value / 1e9 : value

        // World Bank `date` field is a year string (e.g. "2023")
        const observedAt = /^\d{4}$/.test(date) ? `${date}-01-01T00:00:00Z` : date

        records.push({
          countryCode,
          indicator: def.indicator,
          value: normalizedValue,
          unit: def.unit,
          observedAt,
          label: def.label,
          wbIndicatorCode: def.wbCode,
        })
      }
    }

    return { source: 'worldBank', fetchedAt, records, isMock: false }
  },

  normalize: (snapshot: EconomicRawSnapshot<WorldBankLiveRecord>): EconomicDataPoint[] =>
    snapshot.records.map((record) => ({
      key: `${snapshot.source}:${record.countryCode}:${record.indicator}`,
      countryCode: record.countryCode,
      indicator: record.indicator,
      value: record.value,
      unit: record.unit,
      observedAt: record.observedAt,
      source: snapshot.source,
      frequency: 'annual',
      isMock: snapshot.isMock,
      metadata: {
        label: record.label,
        wbIndicatorCode: record.wbIndicatorCode,
        provider: 'World Bank Open Data',
      },
    })),
}
