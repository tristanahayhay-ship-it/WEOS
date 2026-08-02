import type { Country } from '../../types/country'
import type { CountryAdminData } from '../../view/types'
import type { CountryEconomicLayer, CityType, EconomicNodeType } from './types'

export type FlowState = 'inflow' | 'outflow' | 'neutral'

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

export interface GeoBoundary {
  id: string
  type: 'national' | 'administrative'
  rings: [number, number][][]
}

export interface AdministrativeDivision {
  id: string
  name: string
  type: string
  center: [number, number]
  boundary: GeoBoundary | null
}

export interface CapitalNode {
  id: string
  name: string
  nodeType: 'capital'
  position: { lon: number; lat: number }
}

export interface FlowLocation {
  id: string
  name: string
  nodeType: NodeType
  position: { lon: number; lat: number }
  flowState: FlowState
  intensity: number
}

export interface FlowEdge {
  id: string
  fromId: string
  toId: string
  fromNodeType: NodeType
  toNodeType: NodeType
  state: FlowState
  intensity: number
  value: number
}

export interface CountryGeoData {
  countryIsoCode: string
  nationalBoundary: GeoBoundary | null
  administrativeDivisions: AdministrativeDivision[]
}

export interface ResolvedCountryFlowModel {
  countryIsoCode: string
  geo: CountryGeoData
  capital: CapitalNode
  flowLocations: FlowLocation[]
  flowEdges: FlowEdge[]
  priorityLabelIds: string[]
}

interface ResolveCountryFlowParams {
  country: Country
  economicLayer: CountryEconomicLayer | null
  nationalBoundaryRings?: number[][][]
  adminData?: CountryAdminData | null
}

function mapNodeType(nodeType: EconomicNodeType): NodeType {
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

function mapCityType(cityType: CityType): NodeType | null {
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

function clamp01(n: number): number {
  return Math.max(0, Math.min(1, n))
}

export function resolveCountryFlowModel({
  country,
  economicLayer,
  nationalBoundaryRings = [],
  adminData = null,
}: ResolveCountryFlowParams): ResolvedCountryFlowModel | null {
  if (!economicLayer) return null

  const capitalCity = economicLayer.cities.find((city) => city.type === 'capital')
  if (!capitalCity) return null

  const capital: CapitalNode = {
    id: capitalCity.id,
    name: capitalCity.name,
    nodeType: 'capital',
    position: capitalCity.position,
  }

  const locationsById = new Map<string, FlowLocation>()

  for (const node of economicLayer.nodes) {
    if (node.cityId === capital.id) continue
    locationsById.set(node.cityId, {
      id: node.cityId,
      name: economicLayer.cities.find((city) => city.id === node.cityId)?.name ?? node.cityId,
      nodeType: mapNodeType(node.type),
      position: node.position,
      flowState: 'neutral',
      intensity: 0,
    })
  }

  for (const city of economicLayer.cities) {
    if (city.id === capital.id || locationsById.has(city.id)) continue
    const mappedType = mapCityType(city.type)
    if (!mappedType) continue
    locationsById.set(city.id, {
      id: city.id,
      name: city.name,
      nodeType: mappedType,
      position: city.position,
      flowState: 'neutral',
      intensity: 0,
    })
  }

  const netByLocationId = new Map<string, number>()
  for (const flow of economicLayer.flows) {
    const amount = Math.max(0, flow.value)
    if (amount <= 0) continue

    if (flow.toCityId === capital.id && locationsById.has(flow.fromCityId)) {
      netByLocationId.set(flow.fromCityId, (netByLocationId.get(flow.fromCityId) ?? 0) + amount)
      continue
    }

    if (flow.fromCityId === capital.id && locationsById.has(flow.toCityId)) {
      netByLocationId.set(flow.toCityId, (netByLocationId.get(flow.toCityId) ?? 0) - amount)
      continue
    }

    if (flow.visualStyle === 'inflow' && locationsById.has(flow.fromCityId)) {
      netByLocationId.set(flow.fromCityId, (netByLocationId.get(flow.fromCityId) ?? 0) + amount)
      continue
    }

    if (flow.visualStyle === 'outflow' && locationsById.has(flow.toCityId)) {
      netByLocationId.set(flow.toCityId, (netByLocationId.get(flow.toCityId) ?? 0) - amount)
      continue
    }
  }

  let maxMagnitude = 0
  for (const value of netByLocationId.values()) {
    maxMagnitude = Math.max(maxMagnitude, Math.abs(value))
  }
  const scale = maxMagnitude > 0 ? maxMagnitude : 1

  const flowLocations: FlowLocation[] = []
  const flowEdges: FlowEdge[] = []

  for (const location of locationsById.values()) {
    const net = netByLocationId.get(location.id) ?? 0
    const magnitude = Math.abs(net)
    const intensity = clamp01(magnitude / scale)

    const state: FlowState = net > 0 ? 'inflow' : net < 0 ? 'outflow' : 'neutral'
    flowLocations.push({ ...location, flowState: state, intensity })

    if (magnitude <= 0) continue

    flowEdges.push({
      id: `${country.isoCode.toLowerCase()}-${location.id}-capital`,
      fromId: state === 'inflow' ? location.id : capital.id,
      toId: state === 'inflow' ? capital.id : location.id,
      fromNodeType: state === 'inflow' ? location.nodeType : 'capital',
      toNodeType: state === 'inflow' ? 'capital' : location.nodeType,
      state,
      intensity,
      value: magnitude,
    })
  }

  const geo: CountryGeoData = {
    countryIsoCode: country.isoCode,
    nationalBoundary: nationalBoundaryRings.length > 0
      ? {
          id: `${country.isoCode.toLowerCase()}-national-boundary`,
          type: 'national',
          rings: nationalBoundaryRings as [number, number][][],
        }
      : null,
    administrativeDivisions: (adminData?.divisions ?? []).map((division) => ({
      id: division.id,
      name: division.name,
      type: division.type,
      center: division.center,
      boundary: division.boundaryRings && division.boundaryRings.length > 0
        ? {
            id: `${division.id}-boundary`,
            type: 'administrative',
            rings: division.boundaryRings as [number, number][][],
          }
        : null,
    })),
  }

  const priorityLabelIds = [
    capital.id,
    ...flowLocations
      .slice()
      .sort((a, b) => b.intensity - a.intensity)
      .slice(0, 4)
      .map((loc) => loc.id),
  ]

  return {
    countryIsoCode: country.isoCode,
    geo,
    capital,
    flowLocations,
    flowEdges,
    priorityLabelIds,
  }
}
