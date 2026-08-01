import { createSeededRandom } from './random'
import type { Building, Parcel, Vec2, ZoningType } from './types'

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

/** Shrink a convex/concave polygon inward by `inset` on all sides. */
function insetPolygon(pts: Vec2[], inset: number): Vec2[] {
  const n = pts.length
  if (n < 3) return pts

  const result: Vec2[] = []

  for (let i = 0; i < n; i++) {
    const prev = pts[(i - 1 + n) % n]!
    const curr = pts[i]!
    const next = pts[(i + 1) % n]!

    // Edge normals (pointing inward for CCW polygon)
    const e1x = curr.x - prev.x
    const e1y = curr.y - prev.y
    const len1 = Math.hypot(e1x, e1y) || 1
    const n1x = e1y / len1    // inward normal of edge prev→curr
    const n1y = -e1x / len1

    const e2x = next.x - curr.x
    const e2y = next.y - curr.y
    const len2 = Math.hypot(e2x, e2y) || 1
    const n2x = e2y / len2    // inward normal of edge curr→next
    const n2y = -e2x / len2

    // Bisector direction
    const bx = n1x + n2x
    const by = n1y + n2y
    const blen = Math.hypot(bx, by) || 1

    // Miter length so inset is perpendicular to each edge
    const sinHalf = (n1x * n2y - n1y * n2x) * 0.5
    const miter = Math.abs(sinHalf) > 0.08 ? inset / (blen / 2) : inset

    result.push({
      x: curr.x + (bx / blen) * miter,
      y: curr.y + (by / blen) * miter,
    })
  }

  return result
}

function polygonArea(pts: Vec2[]): number {
  let a = 0
  for (let i = 0; i < pts.length; i++) {
    const p = pts[i]!
    const q = pts[(i + 1) % pts.length]!
    a += p.x * q.y - q.x * p.y
  }
  return Math.abs(a * 0.5)
}

export function generateBuildings(parcels: Parcel[], seed: number): Building[] {
  const rand = createSeededRandom(seed + 53)
  const buildings: Building[] = []

  for (let i = 0; i < parcels.length; i++) {
    const parcel = parcels[i]
    if (!parcel) continue

    const [minH, maxH] = heightRange(parcel.zoning)
    const height = minH + rand() * (maxH - minH)
    const levels = Math.max(1, Math.round(height / HEIGHT_PER_LEVEL))

    // Setback: CBD buildings are slimmer (tower feel), others use gentle setback
    const setbackFraction =
      parcel.zoning === 'cbd'
        ? 0.12 + rand() * 0.08
        : 0.06 + rand() * 0.06

    const minDim = Math.min(parcel.width, parcel.depth)
    const inset = Math.max(0.0008, minDim * setbackFraction)

    let footprint = insetPolygon(parcel.polygon, inset)

    // Discard degenerate footprints
    if (footprint.length < 3 || polygonArea(footprint) < 0.000004) {
      footprint = parcel.polygon
    }

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

