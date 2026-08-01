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
