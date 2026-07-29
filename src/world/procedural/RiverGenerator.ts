import { createSeededRandom } from './random'
import type { River, Vec2 } from './types'

const CITY_EXTENT = 0.24

function createRiverPath(seed: number): Vec2[] {
  const rand = createSeededRandom(seed)
  const points: Vec2[] = []
  const amplitude = 0.035 + rand() * 0.02
  const phase = rand() * Math.PI * 2
  const yOffset = -0.02 + rand() * 0.04

  const steps = 24
  for (let i = 0; i <= steps; i += 1) {
    const t = i / steps
    const x = -CITY_EXTENT + t * CITY_EXTENT * 2
    const y = yOffset + Math.sin(t * Math.PI * 2 + phase) * amplitude
    points.push({ x, y })
  }

  return points
}

export function generateRivers(seed: number): River[] {
  return [
    {
      id: 'river-main',
      centerline: createRiverPath(seed + 3),
      width: 0.02,
    },
  ]
}
