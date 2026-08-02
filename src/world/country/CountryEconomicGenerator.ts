import type { Country } from '../../types/country'
import type { CountryEconomicLayer, EconomicCity, EconomicNode } from './types'
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
 * Returns mock data for countries that have entries in `economicCities.ts`;
 * returns an empty layer for all others.
 */
export function generateEconomicLayer(country: Country): CountryEconomicLayer {
  const mock = getMockEconomicData(country.isoCode)
  if (mock) {
    return {
      isoCode: country.isoCode,
      cities: mock.cities,
      nodes: ensureAirportHubs(mock.cities, mock.nodes),
      flows: mock.flows,
    }
  }
  return {
    isoCode: country.isoCode,
    cities: [],
    nodes: [],
    flows: [],
  }
}
