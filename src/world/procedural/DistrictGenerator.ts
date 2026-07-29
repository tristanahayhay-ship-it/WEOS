import type { Block, District, DistrictType } from './types'

function districtTypeFromBlock(block: Block): DistrictType {
  switch (block.zoning) {
    case 'cbd':
      return 'financial'
    case 'commercial':
      return 'commercial'
    case 'industrial':
      return 'industrial'
    case 'mixed_use':
      return 'technology'
    case 'residential':
    default:
      return 'residential'
  }
}

function districtName(type: DistrictType): string {
  switch (type) {
    case 'financial':
      return 'Financial Core'
    case 'commercial':
      return 'Commercial Belt'
    case 'industrial':
      return 'Industrial Zone'
    case 'technology':
      return 'Technology Quarter'
    case 'government':
      return 'Government District'
    case 'university':
      return 'University District'
    case 'airport':
      return 'Airport District'
    case 'port':
      return 'Port District'
    case 'residential':
    default:
      return 'Residential District'
  }
}

function centerOfBlock(block: Block) {
  const [sw, se, ne, nw] = block.polygon
  if (!sw || !se || !ne || !nw) return { x: 0, y: 0 }
  return {
    x: (sw.x + se.x + ne.x + nw.x) / 4,
    y: (sw.y + se.y + ne.y + nw.y) / 4,
  }
}

function polygonFromExtents(minX: number, maxX: number, minY: number, maxY: number) {
  return [
    { x: minX, y: minY },
    { x: maxX, y: minY },
    { x: maxX, y: maxY },
    { x: minX, y: maxY },
  ]
}

export function generateDistricts(blocks: Block[]): District[] {
  const grouped = new Map<DistrictType, Block[]>()

  for (const block of blocks) {
    const type = districtTypeFromBlock(block)
    const current = grouped.get(type)
    if (current) {
      current.push(block)
    } else {
      grouped.set(type, [block])
    }
  }

  const districts: District[] = []
  let index = 0
  for (const [type, districtBlocks] of grouped.entries()) {
    if (districtBlocks.length === 0) continue

    let minX = Number.POSITIVE_INFINITY
    let minY = Number.POSITIVE_INFINITY
    let maxX = Number.NEGATIVE_INFINITY
    let maxY = Number.NEGATIVE_INFINITY
    let densityTotal = 0

    for (const block of districtBlocks) {
      const c = centerOfBlock(block)
      minX = Math.min(minX, c.x - 0.02)
      minY = Math.min(minY, c.y - 0.02)
      maxX = Math.max(maxX, c.x + 0.02)
      maxY = Math.max(maxY, c.y + 0.02)
      densityTotal += block.density
    }

    const density = densityTotal / districtBlocks.length
    districts.push({
      id: `district-${index}`,
      name: districtName(type),
      type,
      polygon: polygonFromExtents(minX, maxX, minY, maxY),
      blockIds: districtBlocks.map((block) => block.id),
      population: Math.round(18000 + districtBlocks.length * 1200 * density),
      gdpUsdBillions: Number((8 + districtBlocks.length * 0.65 * density).toFixed(2)),
      density,
    })
    index += 1
  }

  return districts
}
