import {
  BufferGeometry,
  ConeGeometry,
  Float32BufferAttribute,
  Group,
  Line,
  LineBasicMaterial,
  Mesh,
  MeshBasicMaterial,
  SphereGeometry,
} from 'three'
import { EARTH_RADIUS, projectLngLatToCartesian } from '../../utils/globe'
import { generateCountryInfrastructure, geoCirclePoints } from './CountryInfrastructureGenerator'
import type { Country } from '../../types/country'
import type {
  GeoPoint,
  GeoLine,
  CountryRiver,
  CountryAirport,
  CountrySeaport,
  CountryPark,
  CountryLanduse,
  LanduseType,
} from './types'

// ── Altitude constants ────────────────────────────────────────────────────────
// All above EARTH_RADIUS = 1.0, stacked to avoid z-fighting.

const ALT_LANDUSE  = EARTH_RADIUS + 0.0135
const ALT_PARK     = EARTH_RADIUS + 0.0145
const ALT_RIVER    = EARTH_RADIUS + 0.0155
const ALT_ROAD     = EARTH_RADIUS + 0.0165
const ALT_HIGHWAY  = EARTH_RADIUS + 0.0175
const ALT_RAILWAY  = EARTH_RADIUS + 0.0170
const ALT_SEAPORT  = EARTH_RADIUS + 0.022
const ALT_AIRPORT  = EARTH_RADIUS + 0.022

// ── Colours ───────────────────────────────────────────────────────────────────

const COLOR_ROAD     = '#7c8a9e'
const COLOR_HIGHWAY  = '#e2a84b'
const COLOR_RAILWAY  = '#c084fc'
const COLOR_RIVER    = '#38bdf8'
const COLOR_PARK     = '#22c55e'
const COLOR_AIRPORT  = '#f97316'
const COLOR_SEAPORT  = '#06b6d4'

const LANDUSE_COLORS: Record<LanduseType, string> = {
  forest:       '#166534',
  agricultural: '#a3e635',
  urban:        '#94a3b8',
  desert:       '#d97706',
  wetland:      '#0e7490',
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function geoPointsToFloat32(points: GeoPoint[], altitude: number): Float32Array {
  const arr: number[] = []
  for (const p of points) {
    const [x, y, z] = projectLngLatToCartesian(p.lon, p.lat, altitude)
    arr.push(x, y, z)
  }
  return new Float32Array(arr)
}

function addLine(
  group: Group,
  points: GeoPoint[],
  altitude: number,
  color: string,
  opacity: number,
): void {
  if (points.length < 2) return
  const positions = geoPointsToFloat32(points, altitude)
  const geo = new BufferGeometry()
  geo.setAttribute('position', new Float32BufferAttribute(positions, 3))
  group.add(new Line(geo, new LineBasicMaterial({ color, opacity, transparent: opacity < 1 })))
}

function addCircle(
  group: Group,
  center: GeoPoint,
  radiusDeg: number,
  altitude: number,
  color: string,
  opacity: number,
): void {
  const pts = geoCirclePoints(center, radiusDeg, 32)
  addLine(group, pts, altitude, color, opacity)
}

function addMarker(
  group: Group,
  position: GeoPoint,
  altitude: number,
  color: string,
  radius: number,
): void {
  const [x, y, z] = projectLngLatToCartesian(position.lon, position.lat, altitude)
  const mesh = new Mesh(
    new SphereGeometry(radius, 7, 7),
    new MeshBasicMaterial({ color }),
  )
  mesh.position.set(x, y, z)
  group.add(mesh)
}

// ── Layer builders ────────────────────────────────────────────────────────────

function addLanduse(group: Group, zones: CountryLanduse[]): void {
  for (const zone of zones) {
    const color = LANDUSE_COLORS[zone.type]
    addCircle(group, zone.center, zone.radiusDeg, ALT_LANDUSE, color, 0.3)
  }
}

function addParks(group: Group, parks: CountryPark[]): void {
  for (const park of parks) {
    addCircle(group, park.center, park.radiusDeg, ALT_PARK, COLOR_PARK, 0.55)
  }
}

function addRivers(group: Group, rivers: CountryRiver[]): void {
  for (const river of rivers) {
    addLine(group, river.points, ALT_RIVER, COLOR_RIVER, 0.8)
  }
}

function addRoads(group: Group, roads: GeoLine[]): void {
  for (const road of roads) {
    addLine(group, road.points, ALT_ROAD, COLOR_ROAD, 0.6)
  }
}

function addHighways(group: Group, highways: GeoLine[]): void {
  for (const hwy of highways) {
    addLine(group, hwy.points, ALT_HIGHWAY, COLOR_HIGHWAY, 0.85)
  }
}

function addRailways(group: Group, railways: GeoLine[]): void {
  for (const rail of railways) {
    addLine(group, rail.points, ALT_RAILWAY, COLOR_RAILWAY, 0.7)
  }
}

function addSeaports(group: Group, seaports: CountrySeaport[]): void {
  for (const port of seaports) {
    addMarker(group, port.position, ALT_SEAPORT, COLOR_SEAPORT, 0.0045)

    // Anchor ring
    addCircle(group, port.position, 0.15, ALT_SEAPORT, COLOR_SEAPORT, 0.4)
  }
}

function addAirports(group: Group, airports: CountryAirport[]): void {
  for (const airport of airports) {
    addMarker(group, airport.position, ALT_AIRPORT, COLOR_AIRPORT, airport.isInternational ? 0.006 : 0.004)

    // Runway indicator: two short lines in a cross
    const cosLat = Math.cos((airport.position.lat * Math.PI) / 180) || 0.001
    const r = airport.isInternational ? 0.2 : 0.12
    for (const angle of [0, Math.PI / 2]) {
      const from: GeoPoint = {
        lon: airport.position.lon - (r * Math.cos(angle)) / cosLat,
        lat: airport.position.lat - r * Math.sin(angle),
      }
      const to: GeoPoint = {
        lon: airport.position.lon + (r * Math.cos(angle)) / cosLat,
        lat: airport.position.lat + r * Math.sin(angle),
      }
      addLine(group, [from, to], ALT_AIRPORT, COLOR_AIRPORT, 0.5)
    }
  }
}

// ── Cone marker for seaport anchor (decorative) ──────────────────────────────

function addSeaportMast(group: Group, seaport: CountrySeaport): void {
  const [x, y, z] = projectLngLatToCartesian(
    seaport.position.lon,
    seaport.position.lat,
    ALT_SEAPORT + 0.004,
  )
  const mast = new Mesh(
    new ConeGeometry(0.0015, 0.006, 5),
    new MeshBasicMaterial({ color: COLOR_SEAPORT }),
  )
  // Point the cone outward from the globe center
  const len = Math.sqrt(x * x + y * y + z * z)
  mast.position.set(x, y, z)
  mast.lookAt(0, 0, 0)
  mast.rotateX(Math.PI)
  void len
  group.add(mast)
}

// ── Public API ────────────────────────────────────────────────────────────────

/**
 * Generate and append Country View V2 infrastructure geometry to `group`.
 * Rendering order (bottom → top): landuse, parks, rivers, roads, highways,
 * railways, seaports, airports.
 *
 * The function only appends; clearing is the caller's responsibility.
 */
export function addCountryInfrastructure(group: Group, country: Country): void {
  const infra = generateCountryInfrastructure(country)

  addLanduse(group, infra.landuse)
  addParks(group, infra.parks)
  addRivers(group, infra.rivers)
  addRoads(group, infra.roads)
  addHighways(group, infra.highways)
  addRailways(group, infra.railways)

  for (const port of infra.seaports) {
    addSeaportMast(group, port)
  }
  addSeaports(group, infra.seaports)
  addAirports(group, infra.airports)
}
