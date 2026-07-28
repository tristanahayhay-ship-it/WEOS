/**
 * IMF DataMapper Connector (framework stub)
 *
 * This connector is scaffolded and ready to be activated.
 * It currently returns an empty map so the system falls back to
 * the next provider in the chain.
 *
 * To activate: implement `fetchAll()` using the IMF DataMapper REST API:
 *   https://www.imf.org/external/datamapper/api/v1/
 *
 * Useful indicators:
 *   NGDP_RPCH  — Real GDP growth (%)
 *   PCPIPCH    — Inflation, average consumer prices (%)
 *   FPOLM_PA   — Monetary policy-related interest rate (%)
 *
 * Note: The IMF API uses ISO alpha-3 country codes.
 *       Map alpha-2 → alpha-3 using the countries data in `src/data/countries.ts`.
 *
 * No API key required for the IMF DataMapper REST API.
 * Some endpoints may have CORS restrictions when called from a browser.
 * Consider routing through a serverless proxy in production if CORS is an issue.
 */

import type { EconomicDataProvider, PartialEconomicData } from '../types'

export class ImfConnector implements EconomicDataProvider {
  readonly name = 'IMF'
  readonly requiresApiKey = false

  async fetchAll(): Promise<Map<string, PartialEconomicData>> {
    // Stub: return empty map.
    // Real implementation example (not activated):
    //
    //   const url = 'https://www.imf.org/external/datamapper/api/v1/PCPIPCH?periods=2023'
    //   const res = await fetch(url)
    //   if (!res.ok) return new Map()
    //   const json = await res.json() as ImfResponse
    //   // parse json.values.PCPIPCH and map alpha-3 → alpha-2
    //   ...
    //
    return new Map<string, PartialEconomicData>()
  }
}
