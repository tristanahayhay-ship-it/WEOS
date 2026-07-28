/**
 * World Bank Open Data Connector
 *
 * Fetches Population and GDP for all countries in a single batch request.
 * No API key required — the World Bank API is publicly accessible.
 *
 * Indicators used:
 *   SP.POP.TOTL  — Population, total
 *   NY.GDP.MKTP.CD — GDP, current USD (converted to billions internally)
 *
 * API reference: https://datahelpdesk.worldbank.org/knowledgebase/articles/898581
 */

import type { EconomicDataProvider, PartialEconomicData } from '../types'

const WB_BASE = 'https://api.worldbank.org/v2'
const PER_PAGE = 300

/** Shape of a single World Bank indicator data entry */
interface WbEntry {
  country: { id: string; value: string }
  countryiso3code: string
  value: number | null
}

/** World Bank API response: a 2-element tuple [metadata, data[]] */
type WbResponse = [{ pages: number; total: number }, WbEntry[] | null]

/**
 * Fetch a single indicator for all countries.
 * Returns a map from ISO alpha-2 code → numeric value (or null).
 * Aggregate/regional entries (no valid ISO 3-letter code) are filtered out.
 */
async function fetchIndicator(
  indicatorCode: string,
): Promise<Map<string, number | null>> {
  const url =
    `${WB_BASE}/country/all/indicator/${indicatorCode}` +
    `?format=json&mrv=1&per_page=${PER_PAGE}`

  const res = await fetch(url)
  if (!res.ok) {
    throw new Error(
      `WorldBank: HTTP ${res.status} for indicator "${indicatorCode}"`,
    )
  }

  const json = (await res.json()) as WbResponse
  const entries = json[1] ?? []

  const result = new Map<string, number | null>()
  for (const entry of entries) {
    // Skip aggregates: only 3-letter ISO codes are sovereign countries
    if (!entry.countryiso3code || entry.countryiso3code.length !== 3) continue
    result.set(entry.country.id, entry.value)
  }
  return result
}

export class WorldBankConnector implements EconomicDataProvider {
  readonly name = 'WorldBank'
  readonly requiresApiKey = false

  async fetchAll(): Promise<Map<string, PartialEconomicData>> {
    // Fetch Population and GDP in parallel
    const [popMap, gdpMap] = await Promise.all([
      fetchIndicator('SP.POP.TOTL'),    // Population, total
      fetchIndicator('NY.GDP.MKTP.CD'), // GDP, current USD
    ])

    const result = new Map<string, PartialEconomicData>()
    const allIsoCodes = new Set([...popMap.keys(), ...gdpMap.keys()])

    for (const isoCode of allIsoCodes) {
      // Use `?? null` to normalise "key absent" and "key present with null value"
      // to the same null, then only include non-null values in the partial so
      // valid placeholder data is never overwritten with null.
      const population = popMap.get(isoCode) ?? null
      const gdpRawUsd = gdpMap.get(isoCode) ?? null

      const partial: PartialEconomicData = {}

      if (population !== null) partial.population = population
      if (gdpRawUsd !== null) {
        // World Bank returns GDP in raw USD; our schema stores billions
        partial.gdpUsd = gdpRawUsd / 1e9
        // Derive GDP per capita when population is also available
        if (population !== null && population > 0) {
          partial.gdpPerCapitaUsd = Math.round(gdpRawUsd / population)
        }
      }

      if (Object.keys(partial).length > 0) {
        result.set(isoCode, partial)
      }
    }

    return result
  }
}
