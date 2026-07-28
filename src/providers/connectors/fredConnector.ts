/**
 * FRED (Federal Reserve Economic Data) Connector (framework stub)
 *
 * This connector is scaffolded and ready to be activated.
 * It currently returns an empty map because:
 *  1. FRED requires an API key (set VITE_FRED_API_KEY in your .env file).
 *  2. FRED is primarily US-centric; global country data is limited.
 *
 * To activate:
 *  1. Register for a free FRED API key at https://fred.stlouisfed.org/docs/api/api_key.html
 *  2. Add VITE_FRED_API_KEY=<your-key> to your .env.local file.
 *  3. Implement `fetchAll()` below using the FRED REST API:
 *     https://fred.stlouisfed.org/docs/api/fred/
 *
 * Example FRED series IDs (US-only):
 *   GDP        — Gross Domestic Product (USD billions, SAAR)
 *   CPIAUCSL   — Consumer Price Index (inflation proxy)
 *   FEDFUNDS   — Effective Federal Funds Rate
 *   POPTHM     — US Population (thousands)
 *
 * See docs/data-provider-layer.md for instructions on adding a new provider.
 */

import type { EconomicDataProvider, PartialEconomicData } from '../types'

export class FredConnector implements EconomicDataProvider {
  readonly name = 'FRED'
  readonly requiresApiKey = true

  async fetchAll(): Promise<Map<string, PartialEconomicData>> {
    // ProviderManager skips connectors where requiresApiKey === true
    // and no key is configured, so this method is only called when a key exists.
    //
    // Stub: return empty map until a full implementation is added.
    // Real implementation example (set VITE_FRED_API_KEY in .env.local first):
    //
    //   const key = (import.meta.env as Record<string, string>)['VITE_FRED_API_KEY'] ?? ''
    //   const url = `https://api.stlouisfed.org/fred/series/observations?series_id=GDP&api_key=${key}&file_type=json&sort_order=desc&limit=1`
    //   const res = await fetch(url)
    //   if (!res.ok) return new Map()
    //   // FRED only covers US; return a single "US" entry
    //   const json = await res.json()
    //   const gdpUsd = parseFloat(json.observations[0].value) // already in USD billions
    //   return new Map([['US', { gdpUsd }]])
    //
    return new Map<string, PartialEconomicData>()
  }
}
