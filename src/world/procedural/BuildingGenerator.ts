import { createSeededRandom } from './random'
import type { Building, Parcel, ZoningType } from './types'

const HEIGHT_PER_LEVEL = 0.0045

function heightRange(zoning: ZoningType): [number, number] {
  switch (zoning) {
    case 'cbd':
      return [0.065, 0.18]
    case 'commercial':
      return [0.035, 0.09]
    case 'industrial':
      return [0.015, 0.04]
    case 'mixed_use':
      return [0.025, 0.07]
    case 'residential':
    default:
      return [0.015, 0.05]
  }
}

function createFootprint(parcel: Parcel, rand: () => number) {
  const [sw, se, ne, nw] = parcel.polygon
  if (!sw || !se || !ne || !nw) return parcel.polygon

  const leftInset = 0.0009 + rand() * 0.0018
  const rightInset = 0.0009 + rand() * 0.0018
  const bottomInset = 0.0009 + rand() * 0.0018
  const topInset = 0.0009 + rand() * 0.0018

  const minX = sw.x + leftInset
  const maxX = se.x - rightInset
  const minY = sw.y + bottomInset
  const maxY = nw.y - topInset

  if (maxX - minX < 0.003 || maxY - minY < 0.003) {
    return parcel.polygon
  }

  return [
    { x: minX, y: minY },
    { x: maxX, y: minY },
    { x: maxX, y: maxY },
    { x: minX, y: maxY },
  ]
}

export function generateBuildings(parcels: Parcel[], seed: number): Building[] {
  const rand = createSeededRandom(seed + 53)
  const buildings: Building[] = []

  for (let i = 0; i < parcels.length; i += 1) {
    const parcel = parcels[i]
    if (!parcel) continue

    const [minHeight, maxHeight] = heightRange(parcel.zoning)
    const height = minHeight + rand() * (maxHeight - minHeight)
    const levels = Math.max(1, Math.round(height / HEIGHT_PER_LEVEL))
    const footprint = createFootprint(parcel, rand)

    buildings.push({
      id: `building-${i}`,
      parcelId: parcel.id,
      footprint,
      height,
      zoning: parcel.zoning,
      levels,
    })
  }

  return buildings
}
