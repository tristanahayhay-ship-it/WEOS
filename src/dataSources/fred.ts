/**
 * FRED (Federal Reserve Economic Data) Connector – Phase 6.2 (live data)
 *
 * Fetches US-centric economic indicators from the St. Louis Fed's public REST API.
 * An API key is required (free registration at https://fred.stlouisfed.org/docs/api/api_key.html).
 * Set VITE_FRED_API_KEY in your .env.local file to activate this connector.
 *
 * Without a key, this connector returns an empty snapshot (isMock: false, 0 records).
 * The DataPipeline treats 0 records gracefully – the store is simply not updated.
 *
 * ⚠️  Security note: This connector runs in the browser. The VITE_FRED_API_KEY value
 *    is embedded into the compiled JS bundle at build time and is therefore visible to
 *    anyone who inspects the bundle. FRED keys are free-tier and carry no billing risk,
 *    but if tighter control is needed a server-side proxy should be introduced in a
 *    future phase. This limitation is accepted for Phase 6.2.
 *
 *   CPIAUCSL_PC1  – CPI percent change from year ago (inflation %)
 *   FEDFUNDS      – Effective Federal Funds Rate (interest rate %)
 *   UNRATE        – Unemployment Rate (%)
 *   GDP           – Gross Domestic Product (USD billions, SAAR)
 *
 * All series are US-only.
 */

import type { EconomicDataConnector, EconomicDataPoint, EconomicIndicatorCode, EconomicRawSnapshot } from '../types/economic'

// Shape of a single FRED observation
interface FredObservation {
  date: string
  value: string
}

interface FredApiResponse {
  observations: FredObservation[]
}

// Internal record produced by the live fetch
interface FredLiveRecord {
  seriesId: string
  countryCode: 'US'
  observedAt: string
  value: number
  unit: string
  indicator: EconomicIndicatorCode
}

const FRED_SERIES_DEFS = [
  { seriesId: 'CPIAUCSL_PC1', indicator: 'inflation' as const, unit: 'percent', label: 'CPI YoY Change (%)' },
  { seriesId: 'FEDFUNDS', indicator: 'interestRate' as const, unit: 'percent', label: 'Effective Federal Funds Rate' },
  { seriesId: 'UNRATE', indicator: 'unemployment' as const, unit: 'percent', label: 'Unemployment Rate' },
  { seriesId: 'GDP', indicator: 'gdp' as const, unit: 'USD billions', label: 'GDP (SAAR)' },
] as const

const FRED_BASE = 'https://api.stlouisfed.org/fred'

async function fetchLatestObservation(
  apiKey: string,
  seriesId: string,
): Promise<{ date: string; value: number } | null> {
  const url =
    `${FRED_BASE}/series/observations` +
    `?series_id=${seriesId}` +
    `&api_key=${apiKey}` +
    `&file_type=json` +
    `&sort_order=desc` +
    `&limit=1`

  const res = await fetch(url)
  if (!res.ok) return null

  const json = (await res.json()) as FredApiResponse
  const obs = json.observations?.[0]
  if (!obs || obs.value === '.') return null

  const value = parseFloat(obs.value)
  if (isNaN(value)) return null

  return { date: obs.date, value }
}

export const fredConnector: EconomicDataConnector<FredLiveRecord> = {
  source: 'fred',

  fetchLatest: async (): Promise<EconomicRawSnapshot<FredLiveRecord>> => {
    const apiKey = (import.meta.env as Record<string, string>)['VITE_FRED_API_KEY'] ?? ''
    const fetchedAt = new Date().toISOString()

    if (!apiKey) {
      // No API key – return an empty live snapshot; DataPipeline handles 0 records gracefully
      return { source: 'fred', fetchedAt, records: [], isMock: false }
    }

    const settled = await Promise.allSettled(
      FRED_SERIES_DEFS.map(async (def) => {
        const obs = await fetchLatestObservation(apiKey, def.seriesId)
        if (!obs) return null
        const record: FredLiveRecord = {
          seriesId: def.seriesId,
          countryCode: 'US',
          observedAt: `${obs.date}T00:00:00Z`,
          value: obs.value,
          unit: def.unit,
          indicator: def.indicator,
        }
        return record
      }),
    )

    const records: FredLiveRecord[] = []
    for (const result of settled) {
      if (result.status === 'fulfilled' && result.value !== null) {
        records.push(result.value)
      }
    }

    return { source: 'fred', fetchedAt, records, isMock: false }
  },

  normalize: (snapshot: EconomicRawSnapshot<FredLiveRecord>): EconomicDataPoint[] =>
    snapshot.records.map((record) => ({
      key: `${snapshot.source}:${record.countryCode}:${record.indicator}`,
      countryCode: record.countryCode,
      indicator: record.indicator,
      value: record.value,
      unit: record.unit,
      observedAt: record.observedAt,
      source: snapshot.source,
      frequency: 'monthly',
      isMock: snapshot.isMock,
      metadata: {
        seriesId: record.seriesId,
        provider: 'FRED (Federal Reserve Economic Data)',
      },
    })),
}
