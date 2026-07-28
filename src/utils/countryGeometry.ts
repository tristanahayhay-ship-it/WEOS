import { BufferGeometry, Float32BufferAttribute, Mesh, MeshBasicMaterial, DoubleSide } from 'three'
import { ShapeUtils } from 'three'
import { feature } from 'topojson-client'
import countriesTopology from 'world-atlas/countries-110m.json'
import { projectLngLatToCartesian, EARTH_RADIUS } from './globe'
import type { Country } from '../types/country'
import { COUNTRY_BY_NUMERIC } from '../data/countries'

/** Altitude above the Earth sphere for highlight meshes */
const HIGHLIGHT_ALTITUDE = 0.012

// ─── Types ────────────────────────────────────────────────────────────────────

type TopoTopology = Parameters<typeof feature>[0]
type TopoObject = Exclude<Parameters<typeof feature>[1], undefined>

interface GeoPolygon {
  type: 'Polygon'
  coordinates: number[][][]
}

interface GeoMultiPolygon {
  type: 'MultiPolygon'
  coordinates: number[][][][]
}

type GeoGeometry = GeoPolygon | GeoMultiPolygon

interface GeoFeature {
  type: 'Feature'
  id: number | string
  geometry: GeoGeometry
  properties: Record<string, unknown>
}

interface GeoFeatureCollection {
  type: 'FeatureCollection'
  features: GeoFeature[]
}

// ─── Precomputed polygon index ────────────────────────────────────────────────

interface PolygonEntry {
  numericCode: number
  /** Each element is a Polygon's outer ring as [lng, lat][] */
  rings: number[][][]
  /** Bounding box [minLng, minLat, maxLng, maxLat] for quick rejection */
  bbox: [number, number, number, number]
}

function computeBbox(rings: number[][][]): [number, number, number, number] {
  let minLng = Infinity
  let minLat = Infinity
  let maxLng = -Infinity
  let maxLat = -Infinity

  for (const ring of rings) {
    for (const [lng, lat] of ring) {
      if (lng < minLng) minLng = lng
      if (lat < minLat) minLat = lat
      if (lng > maxLng) maxLng = lng
      if (lat > maxLat) maxLat = lat
    }
  }

  return [minLng, minLat, maxLng, maxLat]
}

function extractRings(geometry: GeoGeometry): number[][][] {
  if (geometry.type === 'Polygon') {
    return [geometry.coordinates[0]]
  }
  return geometry.coordinates.map((poly) => poly[0])
}

function buildPolygonIndex(): PolygonEntry[] {
  const col = feature(
    countriesTopology as unknown as TopoTopology,
    countriesTopology.objects.countries as TopoObject,
  ) as unknown as GeoFeatureCollection

  return col.features.map((f) => {
    const numericCode = typeof f.id === 'string' ? parseInt(f.id, 10) : f.id
    const rings = extractRings(f.geometry)
    return {
      numericCode,
      rings,
      bbox: computeBbox(rings),
    }
  })
}

const POLYGON_INDEX: PolygonEntry[] = buildPolygonIndex()

// ─── Point-in-polygon ────────────────────────────────────────────────────────

function pointInRing(lng: number, lat: number, ring: number[][]): boolean {
  let inside = false
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [xi, yi] = ring[i]
    const [xj, yj] = ring[j]
    const intersect = yi > lat !== yj > lat && lng < ((xj - xi) * (lat - yi)) / (yj - yi) + xi
    if (intersect) inside = !inside
  }
  return inside
}

/**
 * Find the country at a given [longitude, latitude] by testing polygon membership.
 * Returns the matched Country from the dataset, or null if not found.
 */
export function findCountryAtPoint(lng: number, lat: number): Country | null {
  for (const entry of POLYGON_INDEX) {
    const [minLng, minLat, maxLng, maxLat] = entry.bbox

    // Quick bounding-box rejection
    if (lng < minLng || lng > maxLng || lat < minLat || lat > maxLat) {
      continue
    }

    // Full point-in-polygon test across all rings of this country
    for (const ring of entry.rings) {
      if (pointInRing(lng, lat, ring)) {
        return COUNTRY_BY_NUMERIC.get(entry.numericCode) ?? null
      }
    }
  }

  return null
}

// ─── Three.js mesh builder ────────────────────────────────────────────────────

/**
 * Build a BufferGeometry from a single polygon outer ring projected onto the globe sphere.
 * Uses an equirectangular 2D projection for triangulation, then maps back to 3D.
 */
function buildRingGeometry(ring: number[][], radius: number): BufferGeometry | null {
  if (ring.length < 3) return null

  const contour = ring.map(([lng, lat]) => ({ x: lng, y: lat }))

  let triangles: number[][]
  try {
    triangles = ShapeUtils.triangulateShape(contour, [])
  } catch (err) {
    console.warn('[countryGeometry] triangulateShape failed for ring of length', ring.length, err)
    return null
  }

  if (triangles.length === 0) return null

  const positions: number[] = []
  for (const [lng, lat] of ring) {
    const [x, y, z] = projectLngLatToCartesian(lng, lat, radius)
    positions.push(x, y, z)
  }

  const indices: number[] = []
  for (const [a, b, c] of triangles) {
    indices.push(a, b, c)
  }

  const geometry = new BufferGeometry()
  geometry.setAttribute('position', new Float32BufferAttribute(positions, 3))
  geometry.setIndex(indices)
  geometry.computeVertexNormals()
  return geometry
}

/** Geometry cache — keyed by numeric country code */
const geometryCache = new Map<number, BufferGeometry | null>()

/** Build (or return cached) a merged highlight geometry for a country. */
function getCountryHighlightGeometry(numericCode: number): BufferGeometry | null {
  if (geometryCache.has(numericCode)) {
    return geometryCache.get(numericCode) ?? null
  }

  const entry = POLYGON_INDEX.find((e) => e.numericCode === numericCode)
  if (!entry) {
    geometryCache.set(numericCode, null)
    return null
  }

  const radius = EARTH_RADIUS + HIGHLIGHT_ALTITUDE
  const geometries: BufferGeometry[] = []

  for (const ring of entry.rings) {
    const geom = buildRingGeometry(ring, radius)
    if (geom) geometries.push(geom)
  }

  if (geometries.length === 0) {
    geometryCache.set(numericCode, null)
    return null
  }

  // Merge all ring geometries into one
  const allPositions: number[] = []
  const allIndices: number[] = []
  let offset = 0

  for (const geom of geometries) {
    const pos = geom.getAttribute('position')
    for (let i = 0; i < pos.count; i++) {
      allPositions.push(pos.getX(i), pos.getY(i), pos.getZ(i))
    }
    const idx = geom.getIndex()
    if (idx) {
      for (let i = 0; i < idx.count; i++) {
        allIndices.push(idx.getX(i) + offset)
      }
    }
    offset += pos.count
    geom.dispose()
  }

  const merged = new BufferGeometry()
  merged.setAttribute('position', new Float32BufferAttribute(allPositions, 3))
  merged.setIndex(allIndices)
  merged.computeVertexNormals()

  geometryCache.set(numericCode, merged)
  return merged
}

// ─── Highlight mesh factories ─────────────────────────────────────────────────

/** Create a hover-highlight mesh for a country (caller owns disposal of material). */
export function createHoverMesh(country: Country, material: MeshBasicMaterial): Mesh | null {
  const geom = getCountryHighlightGeometry(country.numericCode)
  if (!geom) return null
  return new Mesh(geom, material)
}

/** Create a selected-highlight mesh for a country (caller owns disposal of material). */
export function createSelectedMesh(country: Country, material: MeshBasicMaterial): Mesh | null {
  const geom = getCountryHighlightGeometry(country.numericCode)
  if (!geom) return null
  return new Mesh(geom, material)
}

/** Shared hover material — created once, never disposed during the session. */
export const hoverMaterial = new MeshBasicMaterial({
  color: '#4fc3f7',
  transparent: true,
  opacity: 0.38,
  side: DoubleSide,
  depthWrite: false,
})

/** Shared selected material — created once, never disposed during the session. */
export const selectedMaterial = new MeshBasicMaterial({
  color: '#ffc107',
  transparent: true,
  opacity: 0.48,
  side: DoubleSide,
  depthWrite: false,
})
