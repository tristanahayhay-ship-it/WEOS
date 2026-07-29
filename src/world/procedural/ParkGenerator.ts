import { createSeededRandom } from './random'
import type { Block, Park, Parcel } from './types'

function centerOfPolygon(polygon: Array<{ x: number, y: number }>) {
  let x = 0
  let y = 0
  for (const point of polygon) {
    x += point.x
    y += point.y
  }
  return {
    x: x / polygon.length,
    y: y / polygon.length,
  }
}

function treeGridForPolygon(
  polygon: Array<{ x: number, y: number }>,
  count: number,
  rand: () => number,
) {
  const [sw, se, ne, nw] = polygon
  if (!sw || !se || !ne || !nw) return []
  const minX = sw.x
  const maxX = se.x
  const minY = sw.y
  const maxY = nw.y

  const trees: Array<{ x: number, y: number }> = []
  for (let i = 0; i < count; i += 1) {
    trees.push({
      x: minX + (maxX - minX) * rand(),
      y: minY + (maxY - minY) * rand(),
    })
  }
  return trees
}

export function generateParks(blocks: Block[], parcels: Parcel[], seed: number): Park[] {
  const rand = createSeededRandom(seed + 71)
  const parks: Park[] = []

  const eligibleBlocks = blocks
    .filter((block) => block.zoning === 'residential' || block.zoning === 'mixed_use')
    .slice(0, Math.max(3, Math.floor(blocks.length * 0.1)))

  let index = 0
  for (const block of eligibleBlocks) {
    const blockParcels = parcels.filter((parcel) => parcel.blockId === block.id)
    if (blockParcels.length === 0) continue

    const chosenParcel = blockParcels[Math.floor(rand() * blockParcels.length)]
    if (!chosenParcel) continue

    const center = centerOfPolygon(chosenParcel.polygon)
    const sizeX = Math.max(0.008, chosenParcel.width * 0.7)
    const sizeY = Math.max(0.008, chosenParcel.depth * 0.7)
    const polygon = [
      { x: center.x - sizeX * 0.5, y: center.y - sizeY * 0.5 },
      { x: center.x + sizeX * 0.5, y: center.y - sizeY * 0.5 },
      { x: center.x + sizeX * 0.5, y: center.y + sizeY * 0.5 },
      { x: center.x - sizeX * 0.5, y: center.y + sizeY * 0.5 },
    ]

    parks.push({
      id: `park-${index}`,
      polygon,
      treePositions: treeGridForPolygon(polygon, 6 + Math.floor(rand() * 10), rand),
    })
    index += 1
  }

  return parks
}
