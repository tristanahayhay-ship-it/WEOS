import type { Country, CountryEconomicData } from '../../types/country'
import { getCapitalCoordinate } from '../../data/capitalCoordinates'
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

function withResolvedCapitalCoordinates(country: Country, layer: CountryEconomicLayer): CountryEconomicLayer {
  const capitalCoordinate = getCapitalCoordinate(country.isoCode)
  if (!capitalCoordinate) return layer

  const capitalCity = layer.cities.find((city) => city.type === 'capital')
  if (!capitalCity) return layer

  const capitalPosition = { lon: capitalCoordinate.lng, lat: capitalCoordinate.lat }
  const capitalId = capitalCity.id

  return {
    ...layer,
    cities: layer.cities.map((city) => (
      city.id === capitalId
        ? { ...city, position: capitalPosition }
        : city
    )),
    nodes: layer.nodes.map((node) => (
      node.cityId === capitalId
        ? { ...node, position: capitalPosition }
        : node
    )),
  }
}

function generateUniversalCapitalLayer(
  country: Country,
  _economicData?: CountryEconomicData | null,
): CountryEconomicLayer {
  const capitalCoordinate = getCapitalCoordinate(country.isoCode)
  if (!capitalCoordinate) {
    return {
      isoCode: country.isoCode,
      cities: [],
      nodes: [],
      flows: [],
    }
  }

  const capitalId = `${country.isoCode.toLowerCase()}-capital`
  const capitalPosition = { lon: capitalCoordinate.lng, lat: capitalCoordinate.lat }

  return {
    isoCode: country.isoCode,
    cities: [
      {
        id: capitalId,
        name: country.capital,
        position: capitalPosition,
        type: 'capital',
        importance: 1.0,
      },
    ],
    nodes: [
      {
        id: `${capitalId}-government`,
        cityId: capitalId,
        type: 'government',
        position: capitalPosition,
      },
      {
        id: `${capitalId}-central-bank`,
        cityId: capitalId,
        type: 'central_bank',
        position: capitalPosition,
      },
    ],
    flows: [],
  }
}

// ── Public API ────────────────────────────────────────────────────────────────

/**
 * Generate the V3 economic layer for a country.
 *
 * Priority:
 *   1. Explicit mock data from `economicCities.ts` (highest fidelity).
 *   2. Universal capital-centred fallback resolved from factual capital coordinates.
 *
 * Missing data degrades gracefully — the universal generator uses real capital
 * coordinates when available and does not fabricate secondary node positions.
 */
export function generateEconomicLayer(
  country: Country,
  economicData?: CountryEconomicData | null,
): CountryEconomicLayer {
  const mock = getMockEconomicData(country.isoCode)
  if (mock) {
    const resolvedMock = withResolvedCapitalCoordinates(country, {
      isoCode: country.isoCode,
      cities: mock.cities,
      nodes: mock.nodes,
      flows: mock.flows,
      capitalFlow24H: mock.capitalFlow24H,
    })

    return {
      ...resolvedMock,
      nodes: ensureAirportHubs(resolvedMock.cities, resolvedMock.nodes),
    }
  }

  return generateUniversalCapitalLayer(country, economicData)
}
