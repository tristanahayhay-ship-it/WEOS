import { clamp } from './random'
import type { Block, RoadCorridor, RoadType, Vec2, ZoningType } from './types'

const MIN_BLOCK_WIDTH = 0.008
const MIN_BLOCK_DEPTH = 0.008

function zoningFromBlockCenter(x: number, y: number, density: number): ZoningType {
  const radial = Math.hypot(x, y)
  if (radial < 0.055) return 'cbd'
  if (radial < 0.1 && density > 0.52) return 'commercial'
  if (x > 0.08 && y < -0.06) return 'industrial'
  if (density < 0.32) return 'residential'
  return 'mixed_use'
}

function densityFromAdjacentRoads(roadTypes: RoadType[]): number {
  const scoreMap: Record<RoadType, number> = {
    highway: 1,
    primary: 0.8,
    secondary: 0.55,
    local: 0.35,
  }

  const score = roadTypes.reduce((total, type) => total + scoreMap[type], 0)
  return clamp(score / (roadTypes.length * 1), 0.12, 1)
}

function sortByCoord(corridors: RoadCorridor[], axis: 'x' | 'y'): RoadCorridor[] {
  return corridors
    .filter((corridor) => corridor.axis === axis)
    .sort((a, b) => a.coord - b.coord)
}

function polygonArea(points: Vec2[]): number {
  let area = 0
  for (let i = 0; i < points.length; i += 1) {
    const current = points[i]
    const next = points[(i + 1) % points.length]
    if (!current || !next) continue
    area += current.x * next.y - next.x * current.y
  }
  return Math.abs(area * 0.5)
}

export function generateBlocks(corridors: RoadCorridor[]): Block[] {
  const vertical = sortByCoord(corridors, 'x')
  const horizontal = sortByCoord(corridors, 'y')
  const blocks: Block[] = []
  let index = 0

  for (let xi = 0; xi < vertical.length - 1; xi += 1) {
    const west = vertical[xi]
    const east = vertical[xi + 1]
    if (!west || !east) continue

    const minX = west.coord + west.width * 0.5
    const maxX = east.coord - east.width * 0.5
    const width = maxX - minX
    if (width <= MIN_BLOCK_WIDTH) continue

    for (let yi = 0; yi < horizontal.length - 1; yi += 1) {
      const south = horizontal[yi]
      const north = horizontal[yi + 1]
      if (!south || !north) continue

      const minY = south.coord + south.width * 0.5
      const maxY = north.coord - north.width * 0.5
      const depth = maxY - minY
      if (depth <= MIN_BLOCK_DEPTH) continue

      const polygon = [
        { x: minX, y: minY },
        { x: maxX, y: minY },
        { x: maxX, y: maxY },
        { x: minX, y: maxY },
      ]

      const area = polygonArea(polygon)
      const orientation = width >= depth ? 0 : Math.PI * 0.5
      const adjacentRoadTypes: RoadType[] = [west.type, east.type, south.type, north.type]
      const density = densityFromAdjacentRoads(adjacentRoadTypes)
      const centerX = (minX + maxX) * 0.5
      const centerY = (minY + maxY) * 0.5
      const zoning = zoningFromBlockCenter(centerX, centerY, density)

      blocks.push({
        id: `block-${index}`,
        polygon,
        area,
        orientation,
        adjacentRoadTypes,
        density,
        zoning,
      })
      index += 1
    }
  }

  return blocks
}
