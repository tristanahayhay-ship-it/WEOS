/** A geographic point expressed as [longitude, latitude] in decimal degrees. */
export interface GeoPoint {
  lon: number
  lat: number
}

/** An ordered sequence of geographic points forming a polyline. */
export interface GeoLine {
  id: string
  points: GeoPoint[]
}

// ── Feature types ─────────────────────────────────────────────────────────────

export interface CountryHighway extends GeoLine {}
export interface CountryRoad extends GeoLine {}
export interface CountryRailway extends GeoLine {}

export interface CountryRiver extends GeoLine {
  /** Visual width in degrees (used to scale tube radius). */
  width: number
}

export interface CountryAirport {
  id: string
  position: GeoPoint
  isInternational: boolean
}

export interface CountrySeaport {
  id: string
  position: GeoPoint
}

export interface CountryPark {
  id: string
  center: GeoPoint
  /** Approximate radius in degrees (used for circle outline). */
  radiusDeg: number
}

export type LanduseType = 'forest' | 'agricultural' | 'urban' | 'desert' | 'wetland'

export interface CountryLanduse {
  id: string
  center: GeoPoint
  /** Approximate radius in degrees. */
  radiusDeg: number
  type: LanduseType
}

// ── Aggregate model ───────────────────────────────────────────────────────────

export interface CountryInfrastructure {
  isoCode: string
  highways: CountryHighway[]
  roads: CountryRoad[]
  railways: CountryRailway[]
  airports: CountryAirport[]
  seaports: CountrySeaport[]
  rivers: CountryRiver[]
  parks: CountryPark[]
  landuse: CountryLanduse[]
}

// ── Country View V3 ───────────────────────────────────────────────────────────

/** Economic role a city plays within its country */
export type CityType = 'capital' | 'financial' | 'industrial' | 'port' | 'logistics' | 'technology'

/** Type of economic node attached to a city */
export type EconomicNodeType =
  | 'financial_hub'
  | 'industrial_hub'
  | 'logistics_hub'
  | 'port'
  | 'airport'
  | 'tech_hub'
  | 'central_bank'
  | 'government'

/** Category of capital/goods flow between two cities */
export type CityFlowType = 'capital' | 'trade' | 'supply' | 'logistics'

/**
 * A named economic city within a country.
 * `importance` is in [0, 1]: 1 = primate city, lower = secondary.
 */
export interface EconomicCity {
  id: string
  name: string
  position: GeoPoint
  type: CityType
  /** Relative importance in [0, 1]; drives marker size and glow intensity */
  importance: number
  /** Total 24-hour capital flow volume in USD billions */
  volume24H?: number
  /** Net 24-hour flow in USD billions (positive = net inflow) */
  netFlow24H?: number
  /**
   * Pixel offset from the projected city dot for the floating city card.
   * Positive x = right, positive y = down.
   */
  cardOffset?: { x: number; y: number }
}

/**
 * An economic node co-located with or near a city.
 * Multiple nodes can exist per city.
 */
export interface EconomicNode {
  id: string
  cityId: string
  type: EconomicNodeType
  position: GeoPoint
}

/**
 * A directional flow between two cities.
 * `value` is an arbitrary economic magnitude (USD billions or index units).
 */
export interface CityFlow {
  id: string
  fromCityId: string
  toCityId: string
  type: CityFlowType
  /** Economic magnitude (USD billions or relative index) */
  value: number
  /** Visual color style — 'inflow' renders green, 'outflow' renders red */
  visualStyle?: 'inflow' | 'outflow'
}

/** Full V3 economic layer for one country */
export interface CountryEconomicLayer {
  isoCode: string
  cities: EconomicCity[]
  nodes: EconomicNode[]
  flows: CityFlow[]
  /** Aggregate 24-hour capital flow totals for the country */
  capitalFlow24H?: { inflowUsdB: number; outflowUsdB: number }
}
