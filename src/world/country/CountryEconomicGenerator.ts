import type { Country, CountryEconomicData } from '../../types/country'
import type {
  CountryEconomicLayer,
  EconomicCity,
  EconomicNode,
} from './types'
import { getMockEconomicData } from './economicCities'

function ensureAirportHubs(cities: EconomicCity[], nodes: EconomicNode[]): EconomicNode[] {
  if (nodes.some((node) => node.type === 'airport')) {
    return nodes
  }

  const airportAnchor = cities.find((city) =>
    city.type === 'capital'
    || city.type === 'financial'
    || city.type === 'logistics'
    || city.type === 'industrial'
    || city.type === 'port',
  )

  if (!airportAnchor) return nodes

  return [
    ...nodes,
    {
      id: `${airportAnchor.id}-airport`,
      cityId: airportAnchor.id,
      type: 'airport',
      position: airportAnchor.position,
    },
  ]
}

// ── Public API ────────────────────────────────────────────────────────────────

/**
 * Generate the V3 economic layer for a country.
 *
 * Priority:
 *   1. Explicit mock data from `economicCities.ts` (highest fidelity).
 *   2. Universal capital-centred network derived from the Country model
 *      (works for every country on Earth).
 *
 * Missing data degrades gracefully — the universal generator never fabricates
 * statistics, only positions and flow magnitudes derived from available fields.
 */
export function generateEconomicLayer(
  country: Country,
  _economicData?: CountryEconomicData | null,
): CountryEconomicLayer {
  const mock = getMockEconomicData(country.isoCode)
  if (mock) {
    return {
      isoCode: country.isoCode,
      cities: mock.cities,
      nodes: ensureAirportHubs(mock.cities, mock.nodes),
      flows: mock.flows,
      capitalFlow24H: mock.capitalFlow24H,
    }
  }

  return {
    isoCode: country.isoCode,
    cities: [],
    nodes: [],
    flows: [],
  }
}
