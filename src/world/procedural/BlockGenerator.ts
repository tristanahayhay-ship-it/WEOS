import { clamp } from './random'
import type { Block, RoadGraph, RoadType, Vec2, ZoningType } from './types'

// ── Geometry helpers ──────────────────────────────────────────────────────

/** Signed area of a polygon (positive = CCW winding). */
function signedArea(pts: Vec2[]): number {
  let area = 0
  const n = pts.length
  for (let i = 0; i < n; i++) {
    const a = pts[i]!
    const b = pts[(i + 1) % n]!
    area += a.x * b.y - b.x * a.y
  }
  return area * 0.5
}

function polygonCentroid(pts: Vec2[]): Vec2 {
  let x = 0
  let y = 0
  for (const p of pts) {
    x += p.x
    y += p.y
  }
  return { x: x / pts.length, y: y / pts.length }
}

// ── Zoning rules ──────────────────────────────────────────────────────────

function zoningFromPosition(center: Vec2, cbdCenter: Vec2, density: number): ZoningType {
  const dist = Math.hypot(center.x - cbdCenter.x, center.y - cbdCenter.y)
  if (dist < 0.055) return 'cbd'
  if (dist < 0.1 && density > 0.52) return 'commercial'
  // Place industrial further from CBD on one quadrant
  if (
    center.x - cbdCenter.x > 0.09 &&
    center.y - cbdCenter.y < -0.06
  )
    return 'industrial'
  if (density < 0.32) return 'residential'
  return 'mixed_use'
}

function densityFromRoadTypes(types: RoadType[]): number {
  const score: Record<RoadType, number> = {
    highway: 1.0,
    primary: 0.8,
    secondary: 0.55,
    local: 0.35,
  }
  if (types.length === 0) return 0.2
  const total = types.reduce((s, t) => s + score[t], 0)
  return clamp(total / types.length, 0.12, 1.0)
}

// ── Planar face detection ─────────────────────────────────────────────────

const MAX_FACE_AREA = 0.028   // discard faces larger than this (outer / huge blocks)
const MIN_FACE_AREA = 0.00006 // discard degenerate slivers

/**
 * Find all bounded interior faces of the planar road graph using the
 * standard "next CCW half-edge at each node" traversal.
 *
 * For each directed half-edge (u → v), the face continues along the
 * outgoing edge from v whose angle is the smallest positive CCW rotation
 * from the incoming direction (v → u).
 */
function findFaces(
  nodePos: Map<string, Vec2>,
  adjSorted: Map<string, Array<{ toId: string; angle: number }>>,
): Vec2[][] {
  const used = new Set<string>()
  const faces: Vec2[][] = []

  for (const [fromId, nbrs] of adjSorted) {
    for (const { toId } of nbrs) {
      const startKey = `${fromId}→${toId}`
      if (used.has(startKey)) continue

      const face: Vec2[] = []
      let curFrom = fromId
      let curTo = toId

      for (let step = 0; step < 400; step++) {
        const key = `${curFrom}→${curTo}`
        if (used.has(key)) break
        used.add(key)

        face.push(nodePos.get(curTo)!)

        // At curTo: find the next CCW outgoing edge after the reverse (curTo → curFrom)
        const inAngle = Math.atan2(
          nodePos.get(curFrom)!.y - nodePos.get(curTo)!.y,
          nodePos.get(curFrom)!.x - nodePos.get(curTo)!.x,
        )

        const toNbrs = adjSorted.get(curTo) ?? []
        if (toNbrs.length === 0) break

        let bestNext: string | null = null
        let bestDelta = Infinity
        for (const nb of toNbrs) {
          let delta = nb.angle - inAngle
          while (delta <= 0) delta += 2 * Math.PI
          if (delta < bestDelta) {
            bestDelta = delta
            bestNext = nb.toId
          }
        }
        if (!bestNext) break

        const nextFrom = curTo
        const nextTo = bestNext
        curFrom = nextFrom
        curTo = nextTo

        if (curFrom === fromId && curTo === toId) break
      }

      if (face.length < 3) continue
      const area = signedArea(face)
      if (area > MIN_FACE_AREA && area < MAX_FACE_AREA) {
        faces.push(face)
      }
    }
  }

  return faces
}

// ── Edge-type look-up for a face ──────────────────────────────────────────

function roadTypesForFace(
  polygon: Vec2[],
  adjTypes: Map<string, RoadType[]>,
  nodePos: Map<string, Vec2>,
): RoadType[] {
  // Approximate: find the two nodes nearest to the face polygon centroid
  const c = polygonCentroid(polygon)
  const sorted = [...nodePos.entries()].sort(
    ([, a], [, b]) => Math.hypot(a.x - c.x, a.y - c.y) - Math.hypot(b.x - c.x, b.y - c.y),
  )
  const types: RoadType[] = []
  for (const [id] of sorted.slice(0, 4)) {
    for (const t of adjTypes.get(id) ?? []) {
      types.push(t)
    }
  }
  return types.length > 0 ? types : ['local']
}

// ── Public API ────────────────────────────────────────────────────────────

export function generateBlocks(roadGraph: RoadGraph): Block[] {
  const { nodes, edges, cbdCenter } = roadGraph

  if (nodes.length === 0 || edges.length === 0) return []

  // Build position map
  const nodePos = new Map<string, Vec2>()
  for (const n of nodes) nodePos.set(n.id, n.position)

  // Build type map per node (what road types touch each node)
  const nodeEdgeTypes = new Map<string, RoadType[]>()
  for (const n of nodes) nodeEdgeTypes.set(n.id, [])
  for (const e of edges) {
    nodeEdgeTypes.get(e.fromNodeId)!.push(e.type)
    nodeEdgeTypes.get(e.toNodeId)!.push(e.type)
  }

  // Build adjacency list, sorted CCW by angle (both directions for each edge)
  const adj = new Map<string, Array<{ toId: string; angle: number }>>()
  for (const n of nodes) adj.set(n.id, [])

  for (const e of edges) {
    const fp = nodePos.get(e.fromNodeId)!
    const tp = nodePos.get(e.toNodeId)!
    adj.get(e.fromNodeId)!.push({
      toId: e.toNodeId,
      angle: Math.atan2(tp.y - fp.y, tp.x - fp.x),
    })
    adj.get(e.toNodeId)!.push({
      toId: e.fromNodeId,
      angle: Math.atan2(fp.y - tp.y, fp.x - tp.x),
    })
  }
  for (const [, nbrs] of adj) nbrs.sort((a, b) => a.angle - b.angle)

  const faces = findFaces(nodePos, adj)

  const blocks: Block[] = []
  let idx = 0

  for (const polygon of faces) {
    const area = Math.abs(signedArea(polygon))
    const center = polygonCentroid(polygon)

    // Ensure centroid is inside city extent
    const E = 0.24
    if (Math.abs(center.x) > E * 1.05 || Math.abs(center.y) > E * 1.05) continue

    const adjacentTypes = roadTypesForFace(polygon, nodeEdgeTypes, nodePos)
    const density = densityFromRoadTypes(adjacentTypes)
    const zoning = zoningFromPosition(center, cbdCenter, density)

    // orientation: angle of dominant edge
    let maxEdgeLen = 0
    let orientation = 0
    for (let i = 0; i < polygon.length; i++) {
      const a = polygon[i]!
      const b = polygon[(i + 1) % polygon.length]!
      const len = Math.hypot(b.x - a.x, b.y - a.y)
      if (len > maxEdgeLen) {
        maxEdgeLen = len
        orientation = Math.atan2(b.y - a.y, b.x - a.x)
      }
    }

    blocks.push({
      id: `block-${idx++}`,
      polygon,
      area,
      orientation,
      adjacentRoadTypes: adjacentTypes,
      density,
      zoning,
    })
  }

  return blocks
}
