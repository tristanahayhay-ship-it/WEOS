import { createSeededRandom, hashString } from '../procedural/random'
import type { SeededRandom } from '../procedural/random'
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
  CountryInfrastructure,
} from './types'

// ── Geometry helpers ──────────────────────────────────────────────────────────

/**
 * Interpolate N equally-spaced points along the great circle between two
 * geographic points. `steps` must be >= 2 (returns endpoints only when 2).
 */
function interpolateGeoArc(from: GeoPoint, to: GeoPoint, steps: number): GeoPoint[] {
  const pts: GeoPoint[] = []
  for (let i = 0; i < steps; i += 1) {
    const t = i / (steps - 1)
    pts.push({ lon: from.lon + (to.lon - from.lon) * t, lat: from.lat + (to.lat - from.lat) * t })
  }
  return pts
}

/**
 * Build a line from `from` to `to`, adding intermediate samples so that the
 * line visually follows the sphere surface.
 */
function geoLineBetween(id: string, from: GeoPoint, to: GeoPoint): GeoLine {
  const dLon = Math.abs(to.lon - from.lon)
  const dLat = Math.abs(to.lat - from.lat)
  const dist = Math.sqrt(dLon * dLon + dLat * dLat)
  const steps = Math.max(2, Math.ceil(dist / 1.5) + 1)
  return { id, points: interpolateGeoArc(from, to, steps) }
}

/** Generate a ring of N evenly-spaced points around a geographic center. */
function geoCirclePoints(center: GeoPoint, radiusDeg: number, n: number): GeoPoint[] {
  const cosLat = Math.cos((center.lat * Math.PI) / 180) || 0.001
  const pts: GeoPoint[] = []
  for (let i = 0; i <= n; i += 1) {
    const angle = (i / n) * Math.PI * 2
    pts.push({
      lon: center.lon + (radiusDeg * Math.cos(angle)) / cosLat,
      lat: center.lat + radiusDeg * Math.sin(angle),
    })
  }
  return pts
}

// ── Hub generation ────────────────────────────────────────────────────────────

function generateHubs(center: GeoPoint, radiusDeg: number, count: number, rng: SeededRandom): GeoPoint[] {
  const cosLat = Math.cos((center.lat * Math.PI) / 180) || 0.001
  const hubs: GeoPoint[] = [{ ...center }]

  while (hubs.length < count) {
    const angle = rng() * Math.PI * 2
    const dist = (0.15 + rng() * 0.65) * radiusDeg
    hubs.push({
      lon: center.lon + (dist * Math.cos(angle)) / cosLat,
      lat: center.lat + dist * Math.sin(angle),
    })
  }

  return hubs
}

// ── Road & highway network ────────────────────────────────────────────────────

function generateRoads(hubs: GeoPoint[], connectionsPerHub: number): GeoLine[] {
  const seen = new Set<string>()
  const lines: GeoLine[] = []

  for (let i = 0; i < hubs.length; i += 1) {
    const distances: Array<{ idx: number; d: number }> = []
    const h = hubs[i]!
    for (let j = 0; j < hubs.length; j += 1) {
      if (i === j) continue
      const dx = hubs[j]!.lon - h.lon
      const dy = hubs[j]!.lat - h.lat
      distances.push({ idx: j, d: dx * dx + dy * dy })
    }
    distances.sort((a, b) => a.d - b.d)

    for (let k = 0; k < Math.min(connectionsPerHub, distances.length); k += 1) {
      const j = distances[k]!.idx
      const key = [Math.min(i, j), Math.max(i, j)].join('-')
      if (seen.has(key)) continue
      seen.add(key)
      lines.push(geoLineBetween(`road-${key}`, hubs[i]!, hubs[j]!))
    }
  }

  return lines
}

function generateHighways(hubs: GeoPoint[]): GeoLine[] {
  if (hubs.length < 2) return []

  // Sort hubs by longitude to form a west-east spine
  const sorted = [...hubs].sort((a, b) => a.lon - b.lon)
  const lines: GeoLine[] = []

  for (let i = 0; i < sorted.length - 1; i += 1) {
    lines.push(geoLineBetween(`hwy-${i}`, sorted[i]!, sorted[i + 1]!))
  }

  return lines
}

function generateRailways(hubs: GeoPoint[], rng: SeededRandom): GeoLine[] {
  if (hubs.length < 2) return []

  const cosLat = Math.cos((hubs[0]!.lat * Math.PI) / 180) || 0.001
  const lines: GeoLine[] = []
  const sorted = [...hubs].sort((a, b) => a.lat - b.lat)

  for (let i = 0; i < sorted.length - 1; i += 1) {
    const from = sorted[i]!
    const to = sorted[i + 1]!
    // Slightly offset railway from highway
    const offset = (rng() - 0.5) * 0.3
    const mid: GeoPoint = {
      lon: (from.lon + to.lon) / 2 + offset / cosLat,
      lat: (from.lat + to.lat) / 2 + offset,
    }
    const dFrom = Math.sqrt(
      Math.pow((mid.lon - from.lon) * cosLat, 2) + Math.pow(mid.lat - from.lat, 2),
    )
    const dTo = Math.sqrt(
      Math.pow((mid.lon - to.lon) * cosLat, 2) + Math.pow(mid.lat - to.lat, 2),
    )
    const steps = Math.max(3, Math.ceil((dFrom + dTo) / 1.5) + 1)
    const pts = [...interpolateGeoArc(from, mid, Math.ceil(steps / 2)), ...interpolateGeoArc(mid, to, Math.ceil(steps / 2)).slice(1)]
    lines.push({ id: `rail-${i}`, points: pts })
  }

  return lines
}

// ── Airports ──────────────────────────────────────────────────────────────────

function generateAirports(hubs: GeoPoint[], area: number, rng: SeededRandom): CountryAirport[] {
  const count = Math.min(hubs.length, 1 + Math.floor(Math.log10(Math.max(area, 1000)) - 2))
  const airports: CountryAirport[] = []
  const cosLat = Math.cos((hubs[0]!.lat * Math.PI) / 180) || 0.001

  for (let i = 0; i < count; i += 1) {
    const hub = hubs[i]!
    const jitter = 0.2
    airports.push({
      id: `airport-${i}`,
      position: {
        lon: hub.lon + (rng() - 0.5) * jitter / cosLat,
        lat: hub.lat + (rng() - 0.5) * jitter,
      },
      isInternational: i === 0,
    })
  }

  return airports
}

// ── Seaports ──────────────────────────────────────────────────────────────────

function generateSeaports(
  center: GeoPoint,
  radiusDeg: number,
  count: number,
  rng: SeededRandom,
): CountrySeaport[] {
  const cosLat = Math.cos((center.lat * Math.PI) / 180) || 0.001
  const seaports: CountrySeaport[] = []

  for (let i = 0; i < count; i += 1) {
    // Place seaports on the outer ring of the country (0.7–1.0 × radiusDeg)
    const angle = rng() * Math.PI * 2
    const dist = (0.7 + rng() * 0.3) * radiusDeg
    seaports.push({
      id: `seaport-${i}`,
      position: {
        lon: center.lon + (dist * Math.cos(angle)) / cosLat,
        lat: center.lat + dist * Math.sin(angle),
      },
    })
  }

  return seaports
}

// ── Rivers ────────────────────────────────────────────────────────────────────

function generateRivers(
  center: GeoPoint,
  radiusDeg: number,
  count: number,
  rng: SeededRandom,
): CountryRiver[] {
  const cosLat = Math.cos((center.lat * Math.PI) / 180) || 0.001
  const rivers: CountryRiver[] = []

  for (let i = 0; i < count; i += 1) {
    // River starts near the edge and flows generally toward the center
    const startAngle = rng() * Math.PI * 2
    const startDist = (0.6 + rng() * 0.4) * radiusDeg
    const start: GeoPoint = {
      lon: center.lon + (startDist * Math.cos(startAngle)) / cosLat,
      lat: center.lat + startDist * Math.sin(startAngle),
    }
    // End point: center ± small offset
    const endOffset = 0.15 * radiusDeg
    const end: GeoPoint = {
      lon: center.lon + ((rng() - 0.5) * endOffset) / cosLat,
      lat: center.lat + (rng() - 0.5) * endOffset,
    }

    // Build a meandering path with 3 control points
    const steps = 16
    const pts: GeoPoint[] = []
    for (let s = 0; s <= steps; s += 1) {
      const t = s / steps
      const base = {
        lon: start.lon + (end.lon - start.lon) * t,
        lat: start.lat + (end.lat - start.lat) * t,
      }
      // Sinusoidal meander perpendicular to flow
      const meander = Math.sin(t * Math.PI * 2.5 + rng() * Math.PI) * radiusDeg * 0.06
      const perpAngle = startAngle + Math.PI / 2
      pts.push({
        lon: base.lon + (meander * Math.cos(perpAngle)) / cosLat,
        lat: base.lat + meander * Math.sin(perpAngle),
      })
    }

    rivers.push({
      id: `river-${i}`,
      points: pts,
      width: 0.04 + rng() * 0.06,
    })
  }

  return rivers
}

// ── Parks ─────────────────────────────────────────────────────────────────────

function generateParks(
  center: GeoPoint,
  radiusDeg: number,
  count: number,
  rng: SeededRandom,
): CountryPark[] {
  const cosLat = Math.cos((center.lat * Math.PI) / 180) || 0.001
  const parks: CountryPark[] = []

  for (let i = 0; i < count; i += 1) {
    const angle = rng() * Math.PI * 2
    const dist = (0.1 + rng() * 0.7) * radiusDeg
    parks.push({
      id: `park-${i}`,
      center: {
        lon: center.lon + (dist * Math.cos(angle)) / cosLat,
        lat: center.lat + dist * Math.sin(angle),
      },
      radiusDeg: (0.04 + rng() * 0.08) * radiusDeg,
    })
  }

  return parks
}

// ── Land use ──────────────────────────────────────────────────────────────────

const LANDUSE_TYPES: LanduseType[] = ['forest', 'agricultural', 'urban', 'desert', 'wetland']

function generateLanduse(
  center: GeoPoint,
  radiusDeg: number,
  count: number,
  rng: SeededRandom,
): CountryLanduse[] {
  const cosLat = Math.cos((center.lat * Math.PI) / 180) || 0.001
  const zones: CountryLanduse[] = []

  for (let i = 0; i < count; i += 1) {
    const angle = rng() * Math.PI * 2
    const dist = rng() * radiusDeg * 0.9
    const type = LANDUSE_TYPES[Math.floor(rng() * LANDUSE_TYPES.length)] ?? 'agricultural'
    zones.push({
      id: `landuse-${i}`,
      center: {
        lon: center.lon + (dist * Math.cos(angle)) / cosLat,
        lat: center.lat + dist * Math.sin(angle),
      },
      radiusDeg: (0.06 + rng() * 0.12) * radiusDeg,
      type,
    })
  }

  return zones
}

// ── Public API ────────────────────────────────────────────────────────────────

export function generateCountryInfrastructure(country: Country): CountryInfrastructure {
  const seed = country.numericCode ^ hashString(country.isoCode)
  const rng = createSeededRandom(seed)

  const [centerLon, centerLat] = country.center
  const center: GeoPoint = { lon: centerLon, lat: centerLat }

  // Approximate country extent in degrees; at least 1° for tiny nations
  const radiusDeg = Math.max(1.0, Math.min(28, Math.sqrt(country.area / Math.PI) / 111))

  // Number of "city hub" nodes scales with country size
  const hubCount = Math.min(12, Math.max(3, 2 + Math.floor(Math.log10(country.area + 1))))

  const hubs = generateHubs(center, radiusDeg, hubCount, rng)

  const roads = generateRoads(hubs, 2)
  const highways = generateHighways(hubs)
  const railways = generateRailways(hubs, rng)
  const airports = generateAirports(hubs, country.area, rng)

  // Seaports: 0–3, weighted toward smaller/island nations
  const seaportCount = rng() < 0.2 ? 0 : Math.min(3, 1 + Math.floor(rng() * 2.5))
  const seaports = generateSeaports(center, radiusDeg, seaportCount, rng)

  const riverCount = 1 + Math.floor(rng() * 3)
  const rivers = generateRivers(center, radiusDeg, riverCount, rng)

  const parkCount = 1 + Math.floor(rng() * 5)
  const parks = generateParks(center, radiusDeg, parkCount, rng)

  const landuseCount = 4 + Math.floor(rng() * 8)
  const landuse = generateLanduse(center, radiusDeg, landuseCount, rng)

  return {
    isoCode: country.isoCode,
    highways,
    roads,
    railways,
    airports,
    seaports,
    rivers,
    parks,
    landuse,
  }
}

export { geoCirclePoints }
