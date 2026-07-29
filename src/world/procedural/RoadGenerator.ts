import { createSeededRandom } from './random'
import type {
  Intersection,
  River,
  RoadBridge,
  RoadCorridor,
  RoadGraph,
  RoadSegment,
  RoadType,
  Roundabout,
  Vec2,
} from './types'

const CITY_EXTENT = 0.24

const ROAD_WIDTH: Record<RoadType, number> = {
  highway: 0.012,
  primary: 0.008,
  secondary: 0.005,
  local: 0.003,
}

function createRoadSegment(id: string, type: RoadType, start: Vec2, end: Vec2): RoadSegment {
  return {
    id,
    type,
    width: ROAD_WIDTH[type],
    points: [start, end],
    bridges: [],
  }
}

function sampleRiverYAtX(river: River, x: number): number | null {
  for (let i = 0; i < river.centerline.length - 1; i += 1) {
    const a = river.centerline[i]
    const b = river.centerline[i + 1]
    if (!a || !b) continue
    const minX = Math.min(a.x, b.x)
    const maxX = Math.max(a.x, b.x)
    if (x < minX || x > maxX) continue
    const span = b.x - a.x
    if (Math.abs(span) < 1e-6) return a.y
    const t = (x - a.x) / span
    return a.y + (b.y - a.y) * t
  }
  return null
}

function annotateBridges(roads: RoadSegment[], rivers: River[]) {
  if (rivers.length === 0) return
  const river = rivers[0]
  if (!river) return

  for (const road of roads) {
    const [start, end] = road.points
    if (!start || !end) continue

    if (Math.abs(start.x - end.x) < 1e-6) {
      const yAtRoad = sampleRiverYAtX(river, start.x)
      if (yAtRoad === null) continue
      const minY = Math.min(start.y, end.y)
      const maxY = Math.max(start.y, end.y)
      if (yAtRoad >= minY && yAtRoad <= maxY) {
        const bridge: RoadBridge = {
          id: `${road.id}-bridge-0`,
          position: { x: start.x, y: yAtRoad },
          roadType: road.type,
          span: river.width * 2.4,
        }
        road.bridges.push(bridge)
      }
      continue
    }

    const minX = Math.min(start.x, end.x)
    const maxX = Math.max(start.x, end.x)
    const samples = 10
    for (let i = 0; i <= samples; i += 1) {
      const t = i / samples
      const x = minX + (maxX - minX) * t
      const y = start.y + (end.y - start.y) * t
      const yRiver = sampleRiverYAtX(river, x)
      if (yRiver === null) continue
      if (Math.abs(y - yRiver) <= river.width * 0.6) {
        road.bridges.push({
          id: `${road.id}-bridge-${road.bridges.length}`,
          position: { x, y: yRiver },
          roadType: road.type,
          span: river.width * 2,
        })
        break
      }
    }
  }
}

function buildCorridors(rand: () => number): RoadCorridor[] {
  const baseX: Array<[number, RoadType]> = [
    [0, 'highway'],
    [-0.14, 'primary'],
    [0.14, 'primary'],
    [-0.09, 'secondary'],
    [0.09, 'secondary'],
    [-0.045, 'local'],
    [0.045, 'local'],
    [-0.19, 'secondary'],
    [0.19, 'secondary'],
  ]

  const baseY: Array<[number, RoadType]> = [
    [0.02, 'highway'],
    [-0.12, 'primary'],
    [0.13, 'primary'],
    [-0.075, 'secondary'],
    [0.08, 'secondary'],
    [-0.035, 'local'],
    [0.045, 'local'],
    [-0.185, 'secondary'],
    [0.185, 'secondary'],
  ]

  const corridors: RoadCorridor[] = []
  for (const [coord, type] of baseX) {
    const jitter = type === 'highway' ? (rand() - 0.5) * 0.01 : (rand() - 0.5) * 0.006
    corridors.push({ axis: 'x', coord: coord + jitter, type, width: ROAD_WIDTH[type] })
  }
  for (const [coord, type] of baseY) {
    const jitter = type === 'highway' ? (rand() - 0.5) * 0.01 : (rand() - 0.5) * 0.006
    corridors.push({ axis: 'y', coord: coord + jitter, type, width: ROAD_WIDTH[type] })
  }

  return corridors
}

function buildRoadsFromCorridors(corridors: RoadCorridor[]): RoadSegment[] {
  const roads: RoadSegment[] = []
  let index = 0

  for (const corridor of corridors) {
    const id = `road-${index}`
    index += 1
    if (corridor.axis === 'x') {
      roads.push(
        createRoadSegment(
          id,
          corridor.type,
          { x: corridor.coord, y: -CITY_EXTENT },
          { x: corridor.coord, y: CITY_EXTENT },
        ),
      )
    } else {
      roads.push(
        createRoadSegment(
          id,
          corridor.type,
          { x: -CITY_EXTENT, y: corridor.coord },
          { x: CITY_EXTENT, y: corridor.coord },
        ),
      )
    }
  }

  return roads
}

function hasTwoPoints(road: RoadSegment): boolean {
  return road.points.length >= 2
}

function buildIntersections(roads: RoadSegment[]): Intersection[] {
  const vertical = roads.filter((road) => {
    if (!hasTwoPoints(road)) return false
    const [start, end] = road.points
    if (!start || !end) return false
    return Math.abs(start.x - end.x) < 1e-6
  })
  const horizontal = roads.filter((road) => {
    if (!hasTwoPoints(road)) return false
    const [start, end] = road.points
    if (!start || !end) return false
    return Math.abs(start.y - end.y) < 1e-6
  })

  const intersections: Intersection[] = []
  let index = 0
  for (const vRoad of vertical) {
    for (const hRoad of horizontal) {
      const x = vRoad.points[0]!.x
      const y = hRoad.points[0]!.y
      intersections.push({
        id: `intersection-${index}`,
        position: { x, y },
        roadIds: [vRoad.id, hRoad.id],
        kind: vRoad.type === 'primary' && hRoad.type === 'primary' ? 'roundabout' : 'cross',
      })
      index += 1
    }
  }

  return intersections
}

function buildRoundabouts(intersections: Intersection[]): Roundabout[] {
  const roundabouts: Roundabout[] = []
  let index = 0
  for (const intersection of intersections) {
    if (intersection.kind !== 'roundabout') continue
    roundabouts.push({
      id: `roundabout-${index}`,
      center: intersection.position,
      radius: 0.006,
      connectedRoadIds: intersection.roadIds,
    })
    index += 1
  }
  return roundabouts
}

export function generateRoadGraph(seed: number, rivers: River[]): RoadGraph {
  const rand = createSeededRandom(seed + 17)
  const corridors = buildCorridors(rand)
  const roads = buildRoadsFromCorridors(corridors)
  annotateBridges(roads, rivers)
  const intersections = buildIntersections(roads)
  const roundabouts = buildRoundabouts(intersections)

  return {
    roads,
    intersections,
    roundabouts,
    corridors,
  }
}
