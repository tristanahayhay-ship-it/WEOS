import type { Country, CountryEconomicData } from '../../types/country'
import type {
  CountryEconomicLayer,
  EconomicCity,
  EconomicNode,
  CityFlow,
  CityType,
  EconomicNodeType,
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

// ── Universal fallback generator ──────────────────────────────────────────────

/**
 * Hub archetype: defines the role, node type, and compass offset of each
 * algorithmically placed hub around the capital.
 */
interface HubArchetype {
  suffix: string
  cityType: CityType
  nodeType: EconomicNodeType
  /** Compass bearing in degrees (0 = north, clockwise) */
  bearing: number
  /** Importance in [0, 1] */
  importance: number
}

const HUB_ARCHETYPES: HubArchetype[] = [
  { suffix: 'fin',  cityType: 'financial',  nodeType: 'financial_hub',  bearing:  30, importance: 0.88 },
  { suffix: 'port', cityType: 'port',        nodeType: 'port',           bearing: 120, importance: 0.80 },
  { suffix: 'ind',  cityType: 'industrial',  nodeType: 'industrial_hub', bearing: 200, importance: 0.74 },
  { suffix: 'log',  cityType: 'logistics',   nodeType: 'logistics_hub',  bearing: 280, importance: 0.68 },
  { suffix: 'reg',  cityType: 'logistics',   nodeType: 'logistics_hub',  bearing: 160, importance: 0.62 },
]

/**
 * Return the angular spread (degrees) to use when placing hubs around the
 * capital, scaled logarithmically by country area (km²).
 */
function hubSpreadDeg(areaSqKm: number): number {
  if (areaSqKm <= 0) return 1.5
  // Clamp between 0.5° (micro-states) and 14° (Russia-scale)
  const raw = Math.log10(Math.max(areaSqKm, 1)) * 1.4 - 4.4
  return Math.max(0.5, Math.min(14, raw))
}

/** Convert bearing + distance to a [lon, lat] offset from an origin point. */
function offsetPoint(
  originLon: number,
  originLat: number,
  bearingDeg: number,
  distanceDeg: number,
): { lon: number; lat: number } {
  const bearRad = (bearingDeg * Math.PI) / 180
  const latOffset = Math.cos(bearRad) * distanceDeg
  // Adjust lon offset for latitude compression
  const cosLat = Math.cos((originLat * Math.PI) / 180)
  const lonOffset = (Math.sin(bearRad) * distanceDeg) / Math.max(cosLat, 0.1)
  return {
    lon: originLon + lonOffset,
    lat: Math.max(-85, Math.min(85, originLat + latOffset)),
  }
}

/**
 * Derive base flow magnitude (USD B) from economic data or country area.
 * Used to scale hub-to-hub flows realistically.
 */
function baseFlowValue(economicData: CountryEconomicData | null, areaSqKm: number): number {
  if (economicData?.gdpUsd != null && economicData.gdpUsd > 0) {
    // Roughly 5-15% of annual GDP as daily/periodic flow intensity
    return Math.max(10, Math.min(500, economicData.gdpUsd * 0.08))
  }
  // Fallback from area proxy
  return Math.max(10, Math.min(120, Math.sqrt(areaSqKm) * 0.012))
}

/**
 * Build a capital-centered economic flow network for any country that lacks
 * explicit mock data.
 *
 * The capital is placed at `country.center` (the best available approximation)
 * and 3–5 secondary hubs are placed at radial offsets scaled to the country's
 * area. Flows radiate outward from the capital (visualStyle: 'outflow') and
 * return from major hubs back to the capital (visualStyle: 'inflow').
 */
function generateUniversalLayer(
  country: Country,
  economicData: CountryEconomicData | null,
): CountryEconomicLayer {
  const iso = country.isoCode.toLowerCase()
  const [capLon, capLat] = country.center
  const spread = hubSpreadDeg(country.area)
  const baseValue = baseFlowValue(economicData, country.area)

  // ── Capital city ──────────────────────────────────────────────────────────
  const capitalId = `${iso}-cap`
  const capitalCity: EconomicCity = {
    id: capitalId,
    name: country.capital,
    position: { lon: capLon, lat: capLat },
    type: 'capital',
    importance: 1.0,
    volume24H: baseValue * 2.2,
    netFlow24H: baseValue * 0.3,
    cardOffset: { x: 12, y: -42 },
  }

  const capitalNode: EconomicNode = {
    id: `${capitalId}-gov`,
    cityId: capitalId,
    type: 'government',
    position: { lon: capLon, lat: capLat },
  }

  // ── Secondary hubs ────────────────────────────────────────────────────────
  // For very small countries keep only the most important archetypes
  const archetypeCount = spread < 1 ? 2 : spread < 3 ? 3 : spread < 6 ? 4 : 5
  const selectedArchetypes = HUB_ARCHETYPES.slice(0, archetypeCount)

  const hubCities: EconomicCity[] = selectedArchetypes.map((arch, i) => {
    const pos = offsetPoint(capLon, capLat, arch.bearing, spread * (0.55 + i * 0.05))
    const hubId = `${iso}-${arch.suffix}`
    return {
      id: hubId,
      name: `${arch.cityType.charAt(0).toUpperCase() + arch.cityType.slice(1)} Hub`,
      position: pos,
      type: arch.cityType,
      importance: arch.importance,
      volume24H: baseValue * arch.importance,
      netFlow24H: baseValue * arch.importance * 0.15,
    }
  })

  const hubNodes: EconomicNode[] = selectedArchetypes.map((arch, i) => {
    const hub = hubCities[i]
    return {
      id: `${hub.id}-node`,
      cityId: hub.id,
      type: arch.nodeType,
      position: hub.position,
    }
  })

  // Central bank node co-located with capital
  const centralBankNode: EconomicNode = {
    id: `${capitalId}-cb`,
    cityId: capitalId,
    type: 'central_bank',
    position: { lon: capLon + 0.02, lat: capLat + 0.02 },
  }

  // ── Flows ─────────────────────────────────────────────────────────────────
  const flows: CityFlow[] = []

  // Capital → each hub (outflow = red/orange)
  hubCities.forEach((hub, i) => {
    const arch = selectedArchetypes[i]
    const flowType = arch.cityType === 'port' ? 'trade'
      : arch.cityType === 'industrial' ? 'supply'
      : arch.cityType === 'logistics' ? 'logistics'
      : 'capital'
    flows.push({
      id: `${iso}-out-${i}`,
      fromCityId: capitalId,
      toCityId: hub.id,
      type: flowType,
      value: baseValue * arch.importance,
      visualStyle: 'outflow',
    })
  })

  // Two strongest hubs → capital (inflow = green)
  hubCities.slice(0, 2).forEach((hub, i) => {
    const arch = selectedArchetypes[i]
    const flowType = arch.cityType === 'port' ? 'trade'
      : arch.cityType === 'industrial' ? 'supply'
      : 'capital'
    flows.push({
      id: `${iso}-in-${i}`,
      fromCityId: hub.id,
      toCityId: capitalId,
      type: flowType,
      value: baseValue * arch.importance * 0.7,
      visualStyle: 'inflow',
    })
  })

  // ── Aggregate capital flow totals ─────────────────────────────────────────
  const inflowUsdB  = flows.filter((f) => f.visualStyle === 'inflow').reduce((s, f) => s + f.value, 0)
  const outflowUsdB = flows.filter((f) => f.visualStyle === 'outflow').reduce((s, f) => s + f.value, 0)

  const allCities = [capitalCity, ...hubCities]
  const allNodes  = ensureAirportHubs(allCities, [capitalNode, centralBankNode, ...hubNodes])

  return {
    isoCode: country.isoCode,
    cities:  allCities,
    nodes:   allNodes,
    flows,
    capitalFlow24H: { inflowUsdB, outflowUsdB },
  }
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
  economicData?: CountryEconomicData | null,
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

  return generateUniversalLayer(country, economicData ?? null)
}
