import countriesTopology from 'world-atlas/countries-110m.json'
import landTopology from 'world-atlas/land-110m.json'
import { mesh } from 'topojson-client'

export const EARTH_RADIUS = 1
export const COASTLINE_ALTITUDE = 0.006
export const COUNTRY_ALTITUDE = 0.01

type WorldAtlasTopology = {
  objects: Record<string, object>
}

type MultiLineGeometry = {
  type: 'MultiLineString'
  coordinates: number[][][]
}

type MeshTopology = Parameters<typeof mesh>[0]
type MeshObject = Exclude<Parameters<typeof mesh>[1], undefined>
type MeshFilter = Exclude<Parameters<typeof mesh>[2], undefined>

function projectLngLatToCartesian(
  longitude: number,
  latitude: number,
  radius: number,
): [number, number, number] {
  const phi = ((90 - latitude) * Math.PI) / 180
  const theta = ((longitude + 180) * Math.PI) / 180

  return [
    -(radius * Math.sin(phi) * Math.cos(theta)),
    radius * Math.cos(phi),
    radius * Math.sin(phi) * Math.sin(theta),
  ]
}

function buildLinePositions(
  coordinates: number[][][],
  radius: number,
): Float32Array[] {
  const paths: Float32Array[] = []

  for (const path of coordinates) {
    if (path.length < 2) {
      continue
    }

    let currentPoints: number[] = []

    for (let index = 0; index < path.length; index += 1) {
      const [longitude, latitude] = path[index]

      if (
        index > 0 &&
        Math.abs(longitude - path[index - 1][0]) > 180 &&
        currentPoints.length >= 6
      ) {
        paths.push(new Float32Array(currentPoints))
        currentPoints = []
      }

      const [x, y, z] = projectLngLatToCartesian(longitude, latitude, radius)
      currentPoints.push(x, y, z)
    }

    if (currentPoints.length >= 6) {
      paths.push(new Float32Array(currentPoints))
    }
  }

  return paths
}

function toMultiLineGeometry(
  topology: WorldAtlasTopology,
  objectKey: string,
  filter?: MeshFilter,
) {
  return mesh(
    topology as MeshTopology,
    topology.objects[objectKey] as MeshObject,
    filter,
  ) as unknown as MultiLineGeometry
}

const coastlineGeometry = toMultiLineGeometry(
  landTopology as WorldAtlasTopology,
  'land',
)

const countryBoundaryGeometry = toMultiLineGeometry(
  countriesTopology as WorldAtlasTopology,
  'countries',
  (left, right) => left !== right,
)

export const COASTLINE_PATHS = buildLinePositions(
  coastlineGeometry.coordinates,
  EARTH_RADIUS + COASTLINE_ALTITUDE,
)

export const COUNTRY_BOUNDARY_PATHS = buildLinePositions(
  countryBoundaryGeometry.coordinates,
  EARTH_RADIUS + COUNTRY_ALTITUDE,
)
