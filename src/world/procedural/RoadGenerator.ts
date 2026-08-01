import { createSeededRandom } from './random'
import type {
  CityMorphology,
  Intersection,
  River,
  RoadEdge,
  RoadGraph,
  RoadNode,
  RoadSegment,
  RoadType,
  Roundabout,
  Vec2,
} from './types'

// ── Constants ──────────────────────────────────────────────────────────────

const CITY_EXTENT = 0.24
const SNAP_GRID = 0.0012

const ROAD_WIDTH: Record<RoadType, number> = {
  highway: 0.012,
  primary: 0.008,
  secondary: 0.005,
  local: 0.003,
}

// ── Low-level geometry helpers ─────────────────────────────────────────────

function vecDist(a: Vec2, b: Vec2): number {
  return Math.hypot(b.x - a.x, b.y - a.y)
}

function vecLerp(a: Vec2, b: Vec2, t: number): Vec2 {
  return { x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t }
}

/**
 * Liang-Barsky clip against the symmetric box [-E, E] × [-E, E].
 * Returns the clipped segment or null if entirely outside.
 */
function clipToExtent(p0: Vec2, p1: Vec2): [Vec2, Vec2] | null {
  const E = CITY_EXTENT
  const dx = p1.x - p0.x
  const dy = p1.y - p0.y
  const checks: Array<[number, number]> = [
    [-dx, p0.x + E],  // left:   x >= -E  →  -dx·t ≤ p0.x+E
    [dx, E - p0.x],   // right:  x <=  E
    [-dy, p0.y + E],  // bottom: y >= -E
    [dy, E - p0.y],   // top:    y <=  E
  ]
  let t0 = 0
  let t1 = 1
  for (const [p, q] of checks) {
    if (Math.abs(p) < 1e-12) {
      if (q < 0) return null
    } else {
      const t = q / p
      if (p < 0) {
        if (t > t0) t0 = t
      } else {
        if (t < t1) t1 = t
      }
    }
  }
  if (t0 > t1 + 1e-10) return null
  return [vecLerp(p0, p1, t0), vecLerp(p0, p1, t1)]
}

/**
 * Strict interior crossing of two line segments.
 * Returns [t, u] where 0 < t,u < 1.
 */
function segCross(a: Vec2, b: Vec2, c: Vec2, d: Vec2): [number, number] | null {
  const dx1 = b.x - a.x
  const dy1 = b.y - a.y
  const dx2 = d.x - c.x
  const dy2 = d.y - c.y
  const denom = dx1 * dy2 - dy1 * dx2
  if (Math.abs(denom) < 1e-12) return null
  const dx3 = c.x - a.x
  const dy3 = c.y - a.y
  const t = (dx3 * dy2 - dy3 * dx2) / denom
  const u = (dx3 * dy1 - dy3 * dx1) / denom
  if (t > 1e-6 && t < 1 - 1e-6 && u > 1e-6 && u < 1 - 1e-6) return [t, u]
  return null
}

// ── Raw-line primitives (2-point segments only) ───────────────────────────

interface RawLine {
  type: RoadType
  p0: Vec2
  p1: Vec2
}

function addLine(out: RawLine[], type: RoadType, p0: Vec2, p1: Vec2): void {
  const clipped = clipToExtent(p0, p1)
  if (clipped && vecDist(clipped[0], clipped[1]) > 0.003) {
    out.push({ type, p0: clipped[0], p1: clipped[1] })
  }
}

// ── Morphology: Grid (US-style) ───────────────────────────────────────────

function gridLines(rand: () => number): { lines: RawLine[]; cbdCenter: Vec2 } {
  const lines: RawLine[] = []
  const E = CITY_EXTENT

  // CBD near origin with small offset
  const cbdCenter: Vec2 = { x: (rand() - 0.5) * 0.06, y: (rand() - 0.5) * 0.06 }

  // ── Arterial verticals (north–south) ──
  const av = [cbdCenter.x + (rand() - 0.5) * 0.02]
  av.push(-0.15 + (rand() - 0.5) * 0.035)
  av.push(0.15 + (rand() - 0.5) * 0.035)
  for (const x of av) {
    addLine(lines, 'highway', { x, y: -E }, { x, y: E })
  }

  // ── Arterial horizontals ──
  const ah = [cbdCenter.y + (rand() - 0.5) * 0.02]
  ah.push(-0.13 + (rand() - 0.5) * 0.03)
  ah.push(0.14 + (rand() - 0.5) * 0.03)
  for (const y of ah) {
    addLine(lines, 'highway', { x: -E, y }, { x: E, y })
  }

  // ── Primary verticals ──
  const pv = [-0.09, -0.05, 0.04, 0.08, -0.19, 0.19]
  for (const base of pv) {
    const x = base + (rand() - 0.5) * 0.02
    addLine(lines, 'primary', { x, y: -E }, { x, y: E })
  }

  // ── Primary horizontals ──
  const ph = [-0.07, 0.08, -0.185, 0.185]
  for (const base of ph) {
    const y = base + (rand() - 0.5) * 0.02
    addLine(lines, 'primary', { x: -E, y }, { x: E, y })
  }

  // ── Secondary verticals (dense inner grid) ──
  const secSpacingX = 0.038 + rand() * 0.012
  for (let x = -E + secSpacingX; x < E; x += secSpacingX) {
    const jx = (rand() - 0.5) * 0.01
    addLine(lines, 'secondary', { x: x + jx, y: -E }, { x: x + jx, y: E })
  }

  // ── Secondary horizontals ──
  const secSpacingY = 0.038 + rand() * 0.012
  for (let y = -E + secSpacingY; y < E; y += secSpacingY) {
    const jy = (rand() - 0.5) * 0.01
    addLine(lines, 'secondary', { x: -E, y: y + jy }, { x: E, y: y + jy })
  }

  // ── Diagonal local roads (break the uniform grid feel) ──
  for (let d = 0; d < 5; d++) {
    const angle = (d % 2 === 0 ? Math.PI / 4 : -Math.PI / 4) + (rand() - 0.5) * 0.35
    const ox = cbdCenter.x + (rand() - 0.5) * 0.14
    const oy = cbdCenter.y + (rand() - 0.5) * 0.14
    const len = 0.07 + rand() * 0.12
    addLine(lines, 'local', { x: ox, y: oy }, { x: ox + Math.cos(angle) * len, y: oy + Math.sin(angle) * len })
  }

  return { lines, cbdCenter }
}

// ── Morphology: Radial (Paris / Moscow) ───────────────────────────────────

function radialLines(rand: () => number): { lines: RawLine[]; cbdCenter: Vec2 } {
  const lines: RawLine[] = []
  const cbdCenter: Vec2 = { x: (rand() - 0.5) * 0.05, y: (rand() - 0.5) * 0.05 }

  // Ring roads – 4 concentric "circles" represented as dense polygons
  const rings: Array<{ r: number; type: RoadType; segs: number }> = [
    { r: 0.052 + rand() * 0.008, type: 'highway', segs: 18 },
    { r: 0.105 + rand() * 0.01, type: 'primary', segs: 22 },
    { r: 0.16 + rand() * 0.012, type: 'primary', segs: 26 },
    { r: 0.21 + rand() * 0.01, type: 'secondary', segs: 30 },
  ]

  for (const ring of rings) {
    const pts: Vec2[] = []
    for (let s = 0; s <= ring.segs; s++) {
      const angle = (s / ring.segs) * Math.PI * 2
      const jitter = 1 + (rand() - 0.5) * 0.07
      pts.push({
        x: cbdCenter.x + Math.cos(angle) * ring.r * jitter,
        y: cbdCenter.y + Math.sin(angle) * ring.r * jitter,
      })
    }
    for (let s = 0; s < pts.length - 1; s++) {
      addLine(lines, ring.type, pts[s]!, pts[s + 1]!)
    }
  }

  // Main spoke roads from CBD outward (8 spokes)
  for (let s = 0; s < 8; s++) {
    const angle = (s / 8) * Math.PI * 2 + (rand() - 0.5) * 0.12
    const type: RoadType = s % 2 === 0 ? 'highway' : 'primary'
    addLine(
      lines,
      type,
      cbdCenter,
      { x: cbdCenter.x + Math.cos(angle) * CITY_EXTENT * 1.1, y: cbdCenter.y + Math.sin(angle) * CITY_EXTENT * 1.1 },
    )
  }

  // Inter-ring secondary spokes (between primary spokes)
  const innerR = rings[0]!.r * 1.05
  const outerR = CITY_EXTENT * 0.9
  for (let s = 0; s < 8; s++) {
    const angle = ((s + 0.5) / 8) * Math.PI * 2 + (rand() - 0.5) * 0.1
    addLine(
      lines,
      'secondary',
      { x: cbdCenter.x + Math.cos(angle) * innerR, y: cbdCenter.y + Math.sin(angle) * innerR },
      { x: cbdCenter.x + Math.cos(angle) * outerR, y: cbdCenter.y + Math.sin(angle) * outerR },
    )
  }

  return { lines, cbdCenter }
}

// ── Morphology: Organic (Tokyo / London) ──────────────────────────────────

function organicLines(rand: () => number): { lines: RawLine[]; cbdCenter: Vec2 } {
  const lines: RawLine[] = []
  const cbdCenter: Vec2 = { x: (rand() - 0.5) * 0.07, y: (rand() - 0.5) * 0.07 }

  // Primary arterials: winding paths growing from CBD
  const numPrimary = 7
  for (let i = 0; i < numPrimary; i++) {
    let angle = (i / numPrimary) * Math.PI * 2 + (rand() - 0.5) * 0.5
    let pos: Vec2 = { ...cbdCenter }
    const stepLen = 0.024 + rand() * 0.014
    const numSteps = 8 + Math.floor(rand() * 5)
    for (let s = 0; s < numSteps; s++) {
      angle += (rand() - 0.5) * 0.28
      const next: Vec2 = { x: pos.x + Math.cos(angle) * stepLen, y: pos.y + Math.sin(angle) * stepLen }
      const clipped = clipToExtent(pos, next)
      if (!clipped) break
      const type: RoadType = s < 3 ? 'highway' : s < 6 ? 'primary' : 'secondary'
      lines.push({ type, p0: clipped[0], p1: clipped[1] })
      pos = clipped[1]
      if (Math.abs(pos.x) >= CITY_EXTENT * 0.97 || Math.abs(pos.y) >= CITY_EXTENT * 0.97) break
    }
  }

  // Secondary roads: shorter winding branches
  for (let i = 0; i < 22; i++) {
    const angle0 = rand() * Math.PI * 2
    const startR = 0.02 + rand() * 0.15
    let pos: Vec2 = {
      x: cbdCenter.x + Math.cos(angle0) * startR,
      y: cbdCenter.y + Math.sin(angle0) * startR,
    }
    let dir = angle0 + Math.PI * 0.5 + (rand() - 0.5) * 0.8
    const numSteps = 2 + Math.floor(rand() * 3)
    for (let s = 0; s < numSteps; s++) {
      dir += (rand() - 0.5) * 0.32
      const len = 0.038 + rand() * 0.04
      const next: Vec2 = { x: pos.x + Math.cos(dir) * len, y: pos.y + Math.sin(dir) * len }
      const clipped = clipToExtent(pos, next)
      if (!clipped) break
      lines.push({ type: 'secondary', p0: clipped[0], p1: clipped[1] })
      pos = clipped[1]
      if (Math.abs(pos.x) >= CITY_EXTENT * 0.97 || Math.abs(pos.y) >= CITY_EXTENT * 0.97) break
    }
  }

  // Local connectors
  for (let i = 0; i < 18; i++) {
    const angle = rand() * Math.PI * 2
    const r = 0.04 + rand() * 0.18
    const p0: Vec2 = { x: cbdCenter.x + Math.cos(angle) * r, y: cbdCenter.y + Math.sin(angle) * r }
    const dir = angle + Math.PI * 0.5 + (rand() - 0.5) * 0.5
    const len = 0.04 + rand() * 0.07
    addLine(lines, 'local', p0, { x: p0.x + Math.cos(dir) * len, y: p0.y + Math.sin(dir) * len })
  }

  return { lines, cbdCenter }
}

// ── Morphology: Coastal (Hong Kong / Rio) ─────────────────────────────────

function coastalLines(rand: () => number): { lines: RawLine[]; cbdCenter: Vec2 } {
  const lines: RawLine[] = []
  const E = CITY_EXTENT

  const coastY = -E * 0.82
  const cbdCenter: Vec2 = { x: (rand() - 0.5) * 0.05, y: coastY + 0.115 }

  // Roads parallel to the coastline
  const offsets: Array<{ o: number; type: RoadType }> = [
    { o: 0.025, type: 'highway' },
    { o: 0.068, type: 'primary' },
    { o: 0.12, type: 'primary' },
    { o: 0.175, type: 'secondary' },
    { o: 0.24, type: 'secondary' },
    { o: 0.33, type: 'local' },
    { o: 0.43, type: 'local' },
  ]
  for (const { o, type } of offsets) {
    const y = coastY + o
    if (y > E) continue
    const j = (rand() - 0.5) * 0.009
    // Slight curve: 3-point approximation
    const midX = (rand() - 0.5) * 0.06
    const midY = y + j + (rand() - 0.5) * 0.012
    addLine(lines, type, { x: -E, y: y + j }, { x: midX, y: midY })
    addLine(lines, type, { x: midX, y: midY }, { x: E, y: y + j })
  }

  // Roads perpendicular to coast (down to the water)
  const numPerp = 10 + Math.floor(rand() * 4)
  for (let i = 0; i < numPerp; i++) {
    const baseX = -E + (i + 0.5) * (E * 2 / numPerp)
    const x = baseX + (rand() - 0.5) * 0.014
    const type: RoadType = i % 3 === 0 ? 'primary' : i % 2 === 0 ? 'secondary' : 'local'
    addLine(lines, type, { x, y: coastY }, { x, y: E })
  }

  return { lines, cbdCenter }
}

// ── Morphology: River-based (London / Cairo / Budapest) ───────────────────

function riverLines(rand: () => number, rivers: River[]): { lines: RawLine[]; cbdCenter: Vec2 } {
  const lines: RawLine[] = []
  const E = CITY_EXTENT

  // Locate river
  let riverY = 0.0
  const river = rivers[0]
  if (river) {
    const mid = Math.floor(river.centerline.length / 2)
    riverY = river.centerline[mid]?.y ?? 0.0
  }

  const cbdCenter: Vec2 = { x: (rand() - 0.5) * 0.05, y: riverY + 0.1 }

  // Parallel roads on both sides of the river
  const parallelOff = [-0.19, -0.13, -0.07, -0.033, 0.033, 0.07, 0.13, 0.19, 0.26]
  for (const off of parallelOff) {
    const y = riverY + off
    if (y < -E || y > E) continue
    const j = (rand() - 0.5) * 0.009
    const type: RoadType =
      Math.abs(off) < 0.045 ? 'highway' : Math.abs(off) < 0.11 ? 'primary' : 'secondary'
    addLine(lines, type, { x: -E, y: y + j }, { x: E, y: y + j })
  }

  // Perpendicular roads (become bridges over the river)
  const numPerp = 9 + Math.floor(rand() * 3)
  for (let i = 0; i < numPerp; i++) {
    const baseX = -E + (i + 0.5) * (E * 2 / numPerp)
    const x = baseX + (rand() - 0.5) * 0.015
    const type: RoadType = i % 3 === 0 ? 'highway' : i % 2 === 0 ? 'primary' : 'secondary'
    addLine(lines, type, { x, y: -E }, { x, y: E })
  }

  return { lines, cbdCenter }
}

// ── Planar-graph construction ─────────────────────────────────────────────

interface SplitPt {
  t: number
  point: Vec2
}

/**
 * From a flat list of 2-point road lines, build a proper planar graph:
 * 1. Find all crossing intersections.
 * 2. Handle T-intersections (endpoint on segment interior).
 * 3. Split each line at all intersection points.
 * 4. Snap nearby points to a grid, creating shared nodes.
 * 5. Return nodes + directed (undirected stored as two entries) edges.
 */
function buildPlanarGraph(lines: RawLine[]): { nodes: RoadNode[]; edges: RoadEdge[] } {
  // Per-line split lists
  const splits: SplitPt[][] = lines.map(() => [])

  // 1. Crossing intersections
  for (let i = 0; i < lines.length; i++) {
    const la = lines[i]!
    for (let j = i + 1; j < lines.length; j++) {
      const lb = lines[j]!
      const r = segCross(la.p0, la.p1, lb.p0, lb.p1)
      if (r) {
        const [t, u] = r
        splits[i]!.push({ t, point: vecLerp(la.p0, la.p1, t) })
        splits[j]!.push({ t: u, point: vecLerp(lb.p0, lb.p1, u) })
      }
    }
  }

  // 2. T-intersections: each endpoint checked against every other segment
  for (let i = 0; i < lines.length; i++) {
    for (const ep of [lines[i]!.p0, lines[i]!.p1]) {
      for (let j = 0; j < lines.length; j++) {
        if (i === j) continue
        const lb = lines[j]!
        const dx = lb.p1.x - lb.p0.x
        const dy = lb.p1.y - lb.p0.y
        const len2 = dx * dx + dy * dy
        if (len2 < 1e-12) continue
        const t = ((ep.x - lb.p0.x) * dx + (ep.y - lb.p0.y) * dy) / len2
        if (t <= 0.01 || t >= 0.99) continue
        const proj: Vec2 = { x: lb.p0.x + t * dx, y: lb.p0.y + t * dy }
        if (vecDist(proj, ep) < SNAP_GRID * 2) {
          splits[j]!.push({ t, point: proj })
        }
      }
    }
  }

  // 3. Node creation with grid-snapping
  const nodeMap = new Map<string, RoadNode>()
  let nodeIdx = 0

  function getNode(pt: Vec2): RoadNode {
    const key = `${Math.round(pt.x / SNAP_GRID)},${Math.round(pt.y / SNAP_GRID)}`
    let n = nodeMap.get(key)
    if (!n) {
      n = { id: `n${nodeIdx++}`, position: { x: pt.x, y: pt.y } }
      nodeMap.set(key, n)
    }
    return n
  }

  // 4. Build edges
  const edges: RoadEdge[] = []
  let edgeIdx = 0

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]!
    const raw: SplitPt[] = [
      { t: 0, point: line.p0 },
      ...splits[i]!.sort((a, b) => a.t - b.t),
      { t: 1, point: line.p1 },
    ]

    // Deduplicate nearby t-values
    const deduped: SplitPt[] = [raw[0]!]
    for (let k = 1; k < raw.length; k++) {
      if (raw[k]!.t - deduped[deduped.length - 1]!.t > 4e-3) {
        deduped.push(raw[k]!)
      }
    }

    for (let k = 0; k < deduped.length - 1; k++) {
      const from = getNode(deduped[k]!.point)
      const to = getNode(deduped[k + 1]!.point)
      if (from.id === to.id) continue
      edges.push({
        id: `e${edgeIdx++}`,
        fromNodeId: from.id,
        toNodeId: to.id,
        type: line.type,
        width: ROAD_WIDTH[line.type],
        points: [from.position, to.position],
        bridges: [],
      })
    }
  }

  return { nodes: [...nodeMap.values()], edges }
}

// ── River bridge annotation ───────────────────────────────────────────────

function sampleRiverY(river: River, x: number): number | null {
  for (let i = 0; i < river.centerline.length - 1; i++) {
    const a = river.centerline[i]!
    const b = river.centerline[i + 1]!
    const minX = Math.min(a.x, b.x)
    const maxX = Math.max(a.x, b.x)
    if (x < minX || x > maxX) continue
    const span = b.x - a.x
    if (Math.abs(span) < 1e-8) return a.y
    return a.y + (b.y - a.y) * ((x - a.x) / span)
  }
  return null
}

function annotateBridges(edges: RoadEdge[], rivers: River[]) {
  const river = rivers[0]
  if (!river) return

  for (const edge of edges) {
    const [s, e] = edge.points
    if (!s || !e) continue

    if (Math.abs(s.x - e.x) < 1e-6) {
      const yR = sampleRiverY(river, s.x)
      if (yR === null) continue
      const lo = Math.min(s.y, e.y)
      const hi = Math.max(s.y, e.y)
      if (yR >= lo && yR <= hi) {
        edge.bridges.push({
          id: `${edge.id}-br`,
          position: { x: s.x, y: yR },
          roadType: edge.type,
          span: river.width * 2.4,
        })
      }
    } else {
      const samples = 8
      for (let k = 0; k <= samples; k++) {
        const t = k / samples
        const x = s.x + (e.x - s.x) * t
        const y = s.y + (e.y - s.y) * t
        const yR = sampleRiverY(river, x)
        if (yR === null) continue
        if (Math.abs(y - yR) <= river.width * 0.65) {
          edge.bridges.push({
            id: `${edge.id}-br${edge.bridges.length}`,
            position: { x, y: yR },
            roadType: edge.type,
            span: river.width * 2,
          })
          break
        }
      }
    }
  }
}

// ── Legacy helpers (kept for scene-renderer compatibility) ────────────────

function buildLegacyRoads(edges: RoadEdge[]): RoadSegment[] {
  return edges.map((e) => ({
    id: e.id,
    type: e.type,
    width: e.width,
    points: e.points,
    bridges: e.bridges,
  }))
}

function buildLegacyIntersections(nodes: RoadNode[], edges: RoadEdge[]): Intersection[] {
  // Build adjacency count per node
  const degree = new Map<string, number>()
  for (const n of nodes) degree.set(n.id, 0)
  const edgeTypesAt = new Map<string, RoadType[]>()
  for (const n of nodes) edgeTypesAt.set(n.id, [])
  for (const e of edges) {
    degree.set(e.fromNodeId, (degree.get(e.fromNodeId) ?? 0) + 1)
    degree.set(e.toNodeId, (degree.get(e.toNodeId) ?? 0) + 1)
    edgeTypesAt.get(e.fromNodeId)!.push(e.type)
    edgeTypesAt.get(e.toNodeId)!.push(e.type)
  }

  const result: Intersection[] = []
  let idx = 0
  for (const n of nodes) {
    if ((degree.get(n.id) ?? 0) < 3) continue
    const types = edgeTypesAt.get(n.id) ?? []
    const hasHigher = types.some((t) => t === 'highway' || t === 'primary')
    result.push({
      id: `int-${idx++}`,
      position: n.position,
      roadIds: [],
      kind: hasHigher ? 'roundabout' : 'cross',
    })
  }
  return result
}

function buildLegacyRoundabouts(intersections: Intersection[]): Roundabout[] {
  return intersections
    .filter((i) => i.kind === 'roundabout')
    .map((i, idx) => ({
      id: `rab-${idx}`,
      center: i.position,
      radius: 0.005,
      connectedRoadIds: i.roadIds,
    }))
}

// ── Public API ────────────────────────────────────────────────────────────

export function selectMorphology(seed: number): CityMorphology {
  const list: CityMorphology[] = ['grid', 'radial', 'organic', 'coastal', 'river']
  return list[seed % list.length]!
}

export function generateRoadGraph(seed: number, rivers: River[]): RoadGraph {
  const rand = createSeededRandom(seed + 17)
  const morphology = selectMorphology(seed)

  let lines: RawLine[]
  let cbdCenter: Vec2

  switch (morphology) {
    case 'grid':
      ;({ lines, cbdCenter } = gridLines(rand))
      break
    case 'radial':
      ;({ lines, cbdCenter } = radialLines(rand))
      break
    case 'organic':
      ;({ lines, cbdCenter } = organicLines(rand))
      break
    case 'coastal':
      ;({ lines, cbdCenter } = coastalLines(rand))
      break
    case 'river':
      ;({ lines, cbdCenter } = riverLines(rand, rivers))
      break
  }

  const { nodes, edges } = buildPlanarGraph(lines)
  annotateBridges(edges, rivers)

  const roads = buildLegacyRoads(edges)
  const intersections = buildLegacyIntersections(nodes, edges)
  const roundabouts = buildLegacyRoundabouts(intersections)

  return {
    nodes,
    edges,
    morphology,
    cbdCenter,
    roads,
    intersections,
    roundabouts,
    corridors: [],
  }
}

