import { createSeededRandom, hashString } from '../procedural/random'
import type { Country } from '../../types/country'
import type {
  GeoPoint,
  CityType,
  EconomicNodeType,
  EconomicCity,
  EconomicNode,
  CityFlow,
  CityFlowType,
  CountryEconomicLayer,
} from './types'
import { getMockEconomicData } from './economicCities'

// ── Colour / config ──────────────────────────────────────────────────────────

const CITY_FLOW_TYPES: CityFlowType[] = ['capital', 'trade', 'supply', 'logistics']

// ── Procedural fallback generator ────────────────────────────────────────────

/** City archetype templates used when no mock data is available */
const CITY_ARCHETYPES: Array<{ type: CityType; importance: number; nodeTypes: EconomicNodeType[] }> = [
  { type: 'capital',    importance: 1.0,  nodeTypes: ['government', 'central_bank'] },
  { type: 'financial',  importance: 0.88, nodeTypes: ['financial_hub'] },
  { type: 'industrial', importance: 0.72, nodeTypes: ['industrial_hub'] },
  { type: 'port',       importance: 0.70, nodeTypes: ['port'] },
  { type: 'logistics',  importance: 0.65, nodeTypes: ['logistics_hub'] },
  { type: 'technology', importance: 0.75, nodeTypes: ['tech_hub'] },
]

function proceduralCities(country: Country): CountryEconomicLayer {
  const seed = country.numericCode ^ hashString(country.isoCode) ^ 0xdeadbeef
  const rng = createSeededRandom(seed)

  const [centerLon, centerLat] = country.center
  const radiusDeg = Math.max(0.8, Math.min(18, Math.sqrt(country.area / Math.PI) / 111))
  const cosLat = Math.cos((centerLat * Math.PI) / 180) || 0.001

  // Number of cities: 2 (tiny nations) to 6 (large nations)
  const cityCount = Math.min(6, Math.max(2, 2 + Math.floor(Math.log10(country.area + 1) - 2)))

  const cities: EconomicCity[] = []
  const nodes: EconomicNode[] = []

  for (let i = 0; i < cityCount; i += 1) {
    const archetype = CITY_ARCHETYPES[i % CITY_ARCHETYPES.length]!
    const angle = (i / cityCount) * Math.PI * 2 + rng() * 0.5
    const dist = i === 0 ? 0 : (0.2 + rng() * 0.6) * radiusDeg
    const pos: GeoPoint = {
      lon: centerLon + (dist * Math.cos(angle)) / cosLat,
      lat: centerLat + dist * Math.sin(angle),
    }
    const city: EconomicCity = {
      id: `${country.isoCode.toLowerCase()}-city-${i}`,
      name: i === 0 ? country.capital : `${archetype.type.charAt(0).toUpperCase() + archetype.type.slice(1)} Hub ${i}`,
      position: pos,
      type: archetype.type,
      importance: archetype.importance - rng() * 0.1,
    }
    cities.push(city)

    for (const nodeType of archetype.nodeTypes) {
      const nodeOffset = 0.04 * radiusDeg
      nodes.push({
        id: `${city.id}-${nodeType}`,
        cityId: city.id,
        type: nodeType,
        position: {
          lon: pos.lon + (rng() - 0.5) * nodeOffset / cosLat,
          lat: pos.lat + (rng() - 0.5) * nodeOffset,
        },
      })
    }
  }

  // Flows: each city connects to 1-2 nearest others
  const flows: CityFlow[] = []
  const seen = new Set<string>()

  for (let i = 0; i < cities.length; i += 1) {
    const from = cities[i]!
    // Sort other cities by distance
    const others = cities
      .map((c, j) => ({ j, d: Math.hypot(c.position.lon - from.position.lon, c.position.lat - from.position.lat) }))
      .filter((o) => o.j !== i)
      .sort((a, b) => a.d - b.d)

    const connections = Math.min(2, others.length)
    for (let k = 0; k < connections; k += 1) {
      const j = others[k]!.j
      const key = `${Math.min(i, j)}-${Math.max(i, j)}`
      if (seen.has(key)) continue
      seen.add(key)

      const flowType = CITY_FLOW_TYPES[Math.floor(rng() * CITY_FLOW_TYPES.length)] ?? 'trade'
      flows.push({
        id: `${country.isoCode.toLowerCase()}-flow-${i}-${j}`,
        fromCityId: from.id,
        toCityId: cities[j]!.id,
        type: flowType,
        value: 50 + Math.floor(rng() * 250),
      })
    }
  }

  return { isoCode: country.isoCode, cities, nodes, flows }
}

// ── Public API ────────────────────────────────────────────────────────────────

/**
 * Generate the V3 economic layer for a country.
 *
 * Returns mock data for countries that have entries in `economicCities.ts`;
 * falls back to a deterministic procedural generator for all others.
 */
export function generateEconomicLayer(country: Country): CountryEconomicLayer {
  const mock = getMockEconomicData(country.isoCode)
  if (mock) {
    return { isoCode: country.isoCode, ...mock }
  }
  return proceduralCities(country)
}
