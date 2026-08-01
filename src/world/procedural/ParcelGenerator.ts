import { createSeededRandom } from './random'
import type { Block, Parcel, Vec2 } from './types'

// ── Sutherland-Hodgman polygon clipping ───────────────────────────────────

/**
 * Clip `polygon` against the half-plane defined by the line through
 * (0, value) or (value, 0) depending on `axis`, keeping the side where
 * `axis-coord * side >= value * side`.
 */
function clipByAxisLine(polygon: Vec2[], axis: 'x' | 'y', value: number, side: 1 | -1): Vec2[] {
  if (polygon.length === 0) return []

  const coord = (p: Vec2) => (axis === 'x' ? p.x : p.y)
  const inside = (p: Vec2) => side * (coord(p) - value) >= -1e-10

  const lerp = (p: Vec2, q: Vec2, t: number): Vec2 => ({
    x: p.x + (q.x - p.x) * t,
    y: p.y + (q.y - p.y) * t,
  })

  const intersect = (p: Vec2, q: Vec2): Vec2 => {
    const cp = coord(p)
    const cq = coord(q)
    const t = (value - cp) / (cq - cp)
    return lerp(p, q, t)
  }

  const result: Vec2[] = []
  for (let i = 0; i < polygon.length; i++) {
    const curr = polygon[i]!
    const next = polygon[(i + 1) % polygon.length]!
    if (inside(curr)) {
      result.push(curr)
      if (!inside(next)) result.push(intersect(curr, next))
    } else if (inside(next)) {
      result.push(intersect(curr, next))
    }
  }
  return result
}

function clipPolygonToStrip(polygon: Vec2[], axis: 'x' | 'y', lo: number, hi: number): Vec2[] {
  let pts = clipByAxisLine(polygon, axis, lo, 1)   // keep coord >= lo
  pts = clipByAxisLine(pts, axis, hi, -1)           // keep coord <= hi
  return pts
}

// ── Geometry helpers ───────────────────────────────────────────────────────

function polygonArea(pts: Vec2[]): number {
  let a = 0
  for (let i = 0; i < pts.length; i++) {
    const p = pts[i]!
    const q = pts[(i + 1) % pts.length]!
    a += p.x * q.y - q.x * p.y
  }
  return Math.abs(a * 0.5)
}

function blockBounds(polygon: Vec2[]): { minX: number; maxX: number; minY: number; maxY: number } {
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity
  for (const p of polygon) {
    if (p.x < minX) minX = p.x
    if (p.x > maxX) maxX = p.x
    if (p.y < minY) minY = p.y
    if (p.y > maxY) maxY = p.y
  }
  return { minX, maxX, minY, maxY }
}

// ── Parcel splitting ───────────────────────────────────────────────────────

const MIN_PARCEL_AREA = 0.000018
const MIN_STRIP_WIDTH = 0.006

/**
 * Split `size` into N unequal sub-ranges whose widths vary by ±35%.
 */
function splitDimension(size: number, targetWidth: number, rand: () => number): number[] {
  const result: number[] = []
  let remaining = size
  const lo = targetWidth * 0.65
  const hi = targetWidth * 1.35
  while (remaining > lo * 1.35) {
    const next = Math.min(remaining - lo, lo + rand() * (hi - lo))
    result.push(next)
    remaining -= next
  }
  if (remaining > MIN_STRIP_WIDTH) result.push(remaining)
  return result
}

// ── Public API ─────────────────────────────────────────────────────────────

export function generateParcels(blocks: Block[], seed: number): Parcel[] {
  const rand = createSeededRandom(seed + 31)
  const parcels: Parcel[] = []
  let index = 0

  for (const block of blocks) {
    const { minX, maxX, minY, maxY } = blockBounds(block.polygon)
    const blockW = maxX - minX
    const blockH = maxY - minY
    if (blockW < MIN_STRIP_WIDTH || blockH < MIN_STRIP_WIDTH) continue

    // Choose split axis: split perpendicular to the longer dimension
    const splitAlongX = blockW >= blockH

    const primarySize = splitAlongX ? blockW : blockH
    const targetStrip = Math.max(MIN_STRIP_WIDTH, primarySize / 4)
    const strips = splitDimension(primarySize, targetStrip, rand)

    // Row subdivision (double-deep parcels for large blocks)
    const secondarySize = splitAlongX ? blockH : blockW
    const rowCount = secondarySize > 0.032 ? 2 : 1
    const rowSize = secondarySize / rowCount

    let cursor = splitAlongX ? minX : minY

    for (const stripWidth of strips) {
      const stripLo = cursor
      const stripHi = cursor + stripWidth

      for (let row = 0; row < rowCount; row++) {
        const rowLo = (splitAlongX ? minY : minX) + row * rowSize
        const rowHi = rowLo + rowSize

        // Clip the block polygon to the strip × row rectangle
        const clipped = splitAlongX
          ? clipPolygonToStrip(
              clipPolygonToStrip(block.polygon, 'x', stripLo, stripHi),
              'y',
              rowLo,
              rowHi,
            )
          : clipPolygonToStrip(
              clipPolygonToStrip(block.polygon, 'y', stripLo, stripHi),
              'x',
              rowLo,
              rowHi,
            )

        const area = polygonArea(clipped)
        if (clipped.length < 3 || area < MIN_PARCEL_AREA) continue

        parcels.push({
          id: `parcel-${index++}`,
          blockId: block.id,
          polygon: clipped,
          width: splitAlongX ? stripWidth : rowSize,
          depth: splitAlongX ? rowSize : stripWidth,
          frontage: stripWidth,
          zoning: block.zoning,
        })
      }

      cursor += stripWidth
    }
  }

  return parcels
}

