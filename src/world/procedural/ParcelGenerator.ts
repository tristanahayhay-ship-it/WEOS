import { createSeededRandom } from './random'
import type { Block, Parcel } from './types'

const MIN_REMAINING_RATIO = 1.4
const MIN_PARCEL_SIZE = 0.004
const MIN_PARCEL_WIDTH = 0.012
const WIDTH_DIVISION_FACTOR = 4

function splitDimension(size: number, target: number, rand: () => number): number[] {
  const result: number[] = []
  let remaining = size
  const minSize = target * 0.65
  const maxSize = target * 1.35

  while (remaining > minSize * MIN_REMAINING_RATIO) {
    const next = Math.min(remaining - minSize, minSize + rand() * (maxSize - minSize))
    result.push(next)
    remaining -= next
  }

  if (remaining > MIN_PARCEL_SIZE) result.push(remaining)
  return result
}

export function generateParcels(blocks: Block[], seed: number): Parcel[] {
  const rand = createSeededRandom(seed + 31)
  const parcels: Parcel[] = []
  let index = 0

  for (const block of blocks) {
    const [sw, se, ne, nw] = block.polygon
    if (!sw || !se || !ne || !nw) continue

    const minX = sw.x
    const maxX = se.x
    const minY = sw.y
    const maxY = nw.y
    const width = maxX - minX
    const depth = maxY - minY

    const parcelBands = splitDimension(width, Math.max(MIN_PARCEL_WIDTH, width / WIDTH_DIVISION_FACTOR), rand)
    const rowCount = depth > 0.035 ? 2 : 1
    const rowDepth = depth / rowCount

    let xCursor = minX
    for (const bandWidth of parcelBands) {
      for (let row = 0; row < rowCount; row += 1) {
        const rowMinY = minY + row * rowDepth
        const rowMaxY = rowMinY + rowDepth
        const polygon = [
          { x: xCursor, y: rowMinY },
          { x: xCursor + bandWidth, y: rowMinY },
          { x: xCursor + bandWidth, y: rowMaxY },
          { x: xCursor, y: rowMaxY },
        ]

        parcels.push({
          id: `parcel-${index}`,
          blockId: block.id,
          polygon,
          width: bandWidth,
          depth: rowDepth,
          frontage: bandWidth,
          zoning: block.zoning,
        })
        index += 1
      }
      xCursor += bandWidth
    }
  }

  return parcels
}
