import type { Country } from '../../types/country'
import { EARTH_RADIUS, projectLngLatToCartesian } from '../../utils/globe'
import type { CountryBoundaryGeometry } from '../../utils/countryGeometry'
import type { CountryAdminData } from '../../view/types'
import type { CountryEconomicLayer, CityType, CityFlowType, EconomicNodeType } from './types'

export type FlowState = 'inflow' | 'outflow' | 'neutral'
export type NodePriority = 'capital' | 'primary' | 'secondary' | 'tertiary'

export type NodeType =
  | 'capital'
  | 'financial_center'
  | 'industrial_center'
  | 'port'
  | 'airport'
  | 'logistics_hub'
  | 'trade_hub'
  | 'administrative_center'
  | 'production_zone'
  | 'consumption_zone'
  | 'special_economic_zone'

type FlowLocationType = Exclude<NodeType, 'capital'>

export type GeoPoint = {
  lat: number
  lng: number
}

export type GeoBoundary = {
  type: 'polygon' | 'multipolygon'
  coordinates: number[][][] | number[][][][]
}

export type CapitalNode = {
  id: string
  name: string
  lat: number
  lng: number
  flowState?: FlowState
  intensity?: number
  nodeType: 'capital'
  position: { lon: number; lat: number }
  priority: NodePriority
  priorityScore: number
}

export type AdministrativeDivision = {
  id: string
  name: string
  type: 'state' | 'province' | 'region' | 'district' | 'prefecture'
  boundary: GeoBoundary
  centroid: GeoPoint
}

export type FlowLocation = {
  id: string
  name: string
  type: FlowLocationType
  lat: number
  lng: number
  flowState: FlowState
  intensity: number
  nodeType: NodeType
  position: { lon: number; lat: number }
  priority: NodePriority
  priorityScore: number
}

export type FlowEdge = {
  id: string
  sourceId: string
  targetId: string
  flowState: FlowState
  intensity: number
  type: 'capital_flow' | 'trade' | 'investment' | 'credit' | 'logistics'
  fromId: string
  toId: string
  fromNodeType: NodeType
  toNodeType: NodeType
  state: FlowState
  value: number
  fromPoint: [number, number]
  toPoint: [number, number]
}

export type CountryGeoData = {
  countryId: string
  name: string
  boundary: GeoBoundary | null
  capital: CapitalNode
  divisions?: AdministrativeDivision[]
  flowLocations?: FlowLocation[]
}

type LegacyGeoBoundary = {
  id: string
  type: 'national' | 'administrative'
  rings: [number, number][][]
}

type LegacyAdministrativeDivision = {
  id: string
  name: string
  type: string
  center: [number, number]
  boundary: LegacyGeoBoundary | null
}

type LegacyCountryGeoData = {
  countryIsoCode: string
  nationalBoundary: LegacyGeoBoundary | null
  administrativeDivisions: LegacyAdministrativeDivision[]
}

export interface ResolvedCountryFlowModel {
  countryIsoCode: string
  country: CountryGeoData
  geo: LegacyCountryGeoData
  capital: CapitalNode
  flowLocations: FlowLocation[]
  renderFlowLocations: FlowLocation[]
  flowEdges: FlowEdge[]
  priorityLabelIds: string[]
  hiddenLocationIds: string[]
  capitalPosition: { x: number; y: number; z: number }
  divisionGeometry: GeoBoundary[]
  nodePositions: Record<string, { x: number; y: number; z: number }>
}

const LOCATION_TYPE_PRIORITY: Record<FlowLocation['nodeType'], number> = {
  capital: 1.0,
  financial_center: 0.93,
  trade_hub: 0.9,
  administrative_center: 0.78,
  industrial_center: 0.72,
  port: 0.68,
  airport: 0.64,
  logistics_hub: 0.6,
  production_zone: 0.52,
  consumption_zone: 0.48,
  special_economic_zone: 0.44,
}

interface ResolveCountryFlowParams {
  country: Country
  economicLayer: CountryEconomicLayer | null
  nationalBoundary?: GeoBoundary | null
  nationalBoundaryRings?: number[][][]
  adminData?: CountryAdminData | null
}

function mapNodeType(nodeType: EconomicNodeType): FlowLocationType {
  switch (nodeType) {
    case 'financial_hub': return 'financial_center'
    case 'industrial_hub': return 'industrial_center'
    case 'port': return 'port'
    case 'airport': return 'airport'
    case 'logistics_hub': return 'logistics_hub'
    case 'tech_hub': return 'trade_hub'
    case 'government':
    case 'central_bank':
      return 'administrative_center'
    case 'trade_hub': return 'trade_hub'
    case 'financial_center': return 'financial_center'
    case 'industrial_center': return 'industrial_center'
    case 'administrative_center': return 'administrative_center'
    case 'production_zone': return 'production_zone'
    case 'consumption_zone': return 'consumption_zone'
    case 'special_economic_zone': return 'special_economic_zone'
  }
}

function mapCityType(cityType: CityType): FlowLocationType | null {
  switch (cityType) {
    case 'financial': return 'financial_center'
    case 'industrial': return 'industrial_center'
    case 'port': return 'port'
    case 'logistics': return 'logistics_hub'
    case 'technology': return 'production_zone'
    case 'capital':
      return null
  }
}

function mapFlowType(type: CityFlowType): FlowEdge['type'] {
  switch (type) {
    case 'capital': return 'capital_flow'
    case 'logistics': return 'logistics'
    case 'trade': return 'trade'
    case 'supply': return 'credit'
  }
}

function clamp01(n: number): number {
  return Math.max(0, Math.min(1, n))
}

function isValidLngLat(lng: number, lat: number): boolean {
  return Number.isFinite(lng) && Number.isFinite(lat) && lng >= -180 && lng <= 180 && lat >= -90 && lat <= 90
}

function nodePriorityFromType(nodeType: FlowLocation['nodeType'], intensity: number): { priority: NodePriority; score: number } {
  const base = LOCATION_TYPE_PRIORITY[nodeType] ?? 0.4
  const score = clamp01(base * 0.7 + intensity * 0.3)
  if (score >= 0.82) return { priority: 'primary', score }
  if (score >= 0.6) return { priority: 'secondary', score }
  return { priority: 'tertiary', score }
}

function normalizeBoundary(
  boundary?: GeoBoundary | CountryBoundaryGeometry | null,
  nationalBoundaryRings: number[][][] = [],
): GeoBoundary | null {
  if (boundary) {
    return {
      type: boundary.type,
      coordinates: boundary.coordinates,
    }
  }

  if (nationalBoundaryRings.length === 0) return null
  return {
    type: 'polygon',
    coordinates: nationalBoundaryRings,
  }
}

export function flattenGeoBoundaryRings(boundary: GeoBoundary | null): [number, number][][] {
  if (!boundary) return []
  if (boundary.type === 'polygon') {
    return boundary.coordinates as [number, number][][]
  }

  return (boundary.coordinates as [number, number][][][]).flatMap((polygon) => polygon)
}

function toLegacyBoundary(
  id: string,
  type: 'national' | 'administrative',
  boundary: GeoBoundary | null,
): LegacyGeoBoundary | null {
  if (!boundary) return null
  return {
    id,
    type,
    rings: flattenGeoBoundaryRings(boundary),
  }
}

function toDivisionBoundary(boundaryRings?: [number, number][][]): GeoBoundary | null {
  if (!boundaryRings || boundaryRings.length === 0) return null
  return {
    type: 'polygon',
    coordinates: boundaryRings,
  }
}

function buildNodePosition(lng: number, lat: number, altitude: number) {
  const [x, y, z] = projectLngLatToCartesian(lng, lat, altitude)
  return { x, y, z }
}

export function resolveCountryFlowModel({
  country,
  economicLayer,
  nationalBoundary,
  nationalBoundaryRings = [],
  adminData = null,
}: ResolveCountryFlowParams): ResolvedCountryFlowModel | null {
  if (!economicLayer) return null

  const capitalCity = economicLayer.cities.find((city) => city.type === 'capital')
  if (!capitalCity) return null
  if (!isValidLngLat(capitalCity.position.lon, capitalCity.position.lat)) return null

  const capitalNetFlow = capitalCity.netFlow24H ?? 0
  const capital: CapitalNode = {
    id: capitalCity.id,
    name: country.capital || capitalCity.name,
    lat: capitalCity.position.lat,
    lng: capitalCity.position.lon,
    flowState: capitalNetFlow > 0 ? 'inflow' : capitalNetFlow < 0 ? 'outflow' : 'neutral',
    intensity: capitalCity.volume24H != null && capitalCity.volume24H > 0
      ? clamp01(Math.abs(capitalNetFlow) / capitalCity.volume24H)
      : 1,
    nodeType: 'capital',
    position: capitalCity.position,
    priority: 'capital',
    priorityScore: 1,
  }

  const locationsById = new Map<string, Omit<FlowLocation, 'flowState' | 'intensity' | 'priority' | 'priorityScore'>>()

  for (const node of economicLayer.nodes) {
    if (node.cityId === capital.id) continue
    if (!isValidLngLat(node.position.lon, node.position.lat)) continue
    locationsById.set(node.cityId, {
      id: node.cityId,
      name: economicLayer.cities.find((city) => city.id === node.cityId)?.name ?? node.cityId,
      type: mapNodeType(node.type),
      lat: node.position.lat,
      lng: node.position.lon,
      nodeType: mapNodeType(node.type),
      position: node.position,
    })
  }

  for (const city of economicLayer.cities) {
    if (city.id === capital.id || locationsById.has(city.id)) continue
    if (!isValidLngLat(city.position.lon, city.position.lat)) continue
    const mappedType = mapCityType(city.type)
    if (!mappedType) continue
    locationsById.set(city.id, {
      id: city.id,
      name: city.name,
      type: mappedType,
      lat: city.position.lat,
      lng: city.position.lon,
      nodeType: mappedType,
      position: city.position,
    })
  }

  const netByLocationId = new Map<string, number>()
  const flowTypeByLocationId = new Map<string, FlowEdge['type']>()

  for (const flow of economicLayer.flows) {
    const amount = Math.max(0, flow.value)
    if (amount <= 0) continue

    if (flow.toCityId === capital.id && locationsById.has(flow.fromCityId)) {
      netByLocationId.set(flow.fromCityId, (netByLocationId.get(flow.fromCityId) ?? 0) + amount)
      flowTypeByLocationId.set(flow.fromCityId, mapFlowType(flow.type))
      continue
    }

    if (flow.fromCityId === capital.id && locationsById.has(flow.toCityId)) {
      netByLocationId.set(flow.toCityId, (netByLocationId.get(flow.toCityId) ?? 0) - amount)
      flowTypeByLocationId.set(flow.toCityId, mapFlowType(flow.type))
      continue
    }

    if (flow.visualStyle === 'inflow' && locationsById.has(flow.fromCityId)) {
      netByLocationId.set(flow.fromCityId, (netByLocationId.get(flow.fromCityId) ?? 0) + amount)
      flowTypeByLocationId.set(flow.fromCityId, mapFlowType(flow.type))
      continue
    }

    if (flow.visualStyle === 'outflow' && locationsById.has(flow.toCityId)) {
      netByLocationId.set(flow.toCityId, (netByLocationId.get(flow.toCityId) ?? 0) - amount)
      flowTypeByLocationId.set(flow.toCityId, mapFlowType(flow.type))
      continue
    }
  }

  let maxMagnitude = 0
  for (const value of netByLocationId.values()) {
    maxMagnitude = Math.max(maxMagnitude, Math.abs(value))
  }
  const scale = maxMagnitude > 0 ? maxMagnitude : 1

  const flowLocations: FlowLocation[] = []
  const flowEdgesAll: FlowEdge[] = []

  for (const location of locationsById.values()) {
    const net = netByLocationId.get(location.id) ?? 0
    const magnitude = Math.abs(net)
    const intensity = clamp01(magnitude / scale)

    const state: FlowState = net > 0 ? 'inflow' : net < 0 ? 'outflow' : 'neutral'
    const priorityMeta = nodePriorityFromType(location.nodeType, intensity)
    flowLocations.push({
      ...location,
      flowState: state,
      intensity,
      priority: priorityMeta.priority,
      priorityScore: priorityMeta.score,
    })

    if (magnitude <= 0) continue

    const fromId = state === 'inflow' ? location.id : capital.id
    const toId = state === 'inflow' ? capital.id : location.id
    const fromNodeType = state === 'inflow' ? location.nodeType : 'capital'
    const toNodeType = state === 'inflow' ? 'capital' : location.nodeType

    flowEdgesAll.push({
      id: `${country.isoCode.toLowerCase()}-${location.id}-capital`,
      sourceId: fromId,
      targetId: toId,
      flowState: state,
      intensity,
      type: flowTypeByLocationId.get(location.id) ?? 'capital_flow',
      fromId,
      toId,
      fromNodeType,
      toNodeType,
      state,
      value: magnitude,
      fromPoint: [state === 'inflow' ? location.lng : capital.lng, state === 'inflow' ? location.lat : capital.lat],
      toPoint: [state === 'inflow' ? capital.lng : location.lng, state === 'inflow' ? capital.lat : location.lat],
    })
  }

  const sortedByPriority = flowLocations
    .slice()
    .sort((a, b) => (b.priorityScore - a.priorityScore) || (b.intensity - a.intensity))

  const RENDER_LOCATION_LIMIT = 18
  const hasDenseData = sortedByPriority.length > RENDER_LOCATION_LIMIT
  const renderFlowLocations = hasDenseData
    ? sortedByPriority.slice(0, RENDER_LOCATION_LIMIT)
    : sortedByPriority
  const renderLocationIds = new Set(renderFlowLocations.map((location) => location.id))
  const hiddenLocationIds = hasDenseData
    ? sortedByPriority.slice(RENDER_LOCATION_LIMIT).map((location) => location.id)
    : []
  const flowEdges = flowEdgesAll.filter((edge) => (
    (edge.fromId === capital.id || renderLocationIds.has(edge.fromId))
    && (edge.toId === capital.id || renderLocationIds.has(edge.toId))
  ))

  const resolvedBoundary = normalizeBoundary(nationalBoundary, nationalBoundaryRings)
  const divisions = (adminData?.divisions ?? [])
    .map((division) => {
      const boundary = toDivisionBoundary(division.boundaryRings)
      if (!boundary) return null
      if (
        division.type !== 'state'
        && division.type !== 'province'
        && division.type !== 'region'
        && division.type !== 'district'
        && division.type !== 'prefecture'
      ) {
        return null
      }

      return {
        id: division.id,
        name: division.name,
        type: division.type,
        boundary,
        centroid: {
          lng: division.center[0],
          lat: division.center[1],
        },
      } satisfies AdministrativeDivision
    })
    .filter((division): division is AdministrativeDivision => division !== null)

  const countryData: CountryGeoData = {
    countryId: country.isoCode,
    name: country.name,
    boundary: resolvedBoundary,
    capital,
    divisions: divisions.length > 0 ? divisions : undefined,
    flowLocations: flowLocations.length > 0 ? flowLocations : undefined,
  }

  const priorityLabelIds = [
    capital.id,
    ...renderFlowLocations
      .slice()
      .sort((a, b) => (b.priorityScore - a.priorityScore) || (b.intensity - a.intensity))
      .slice(0, 4)
      .map((loc) => loc.id),
  ]

  const nodePositions: Record<string, { x: number; y: number; z: number }> = {
    [capital.id]: buildNodePosition(capital.lng, capital.lat, EARTH_RADIUS + 0.028),
  }
  for (const location of flowLocations) {
    nodePositions[location.id] = buildNodePosition(location.lng, location.lat, EARTH_RADIUS + 0.028)
  }

  return {
    countryIsoCode: country.isoCode,
    country: countryData,
    geo: {
      countryIsoCode: country.isoCode,
      nationalBoundary: toLegacyBoundary(
        `${country.isoCode.toLowerCase()}-national-boundary`,
        'national',
        resolvedBoundary,
      ),
      administrativeDivisions: divisions.map((division) => ({
        id: division.id,
        name: division.name,
        type: division.type,
        center: [division.centroid.lng, division.centroid.lat],
        boundary: toLegacyBoundary(`${division.id}-boundary`, 'administrative', division.boundary),
      })),
    },
    capital,
    flowLocations,
    renderFlowLocations,
    flowEdges,
    priorityLabelIds,
    hiddenLocationIds,
    capitalPosition: nodePositions[capital.id],
    divisionGeometry: divisions.map((division) => division.boundary),
    nodePositions,
  }
}
