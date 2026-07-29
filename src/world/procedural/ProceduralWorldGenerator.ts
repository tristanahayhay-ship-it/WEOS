import { generateBlocks } from './BlockGenerator'
import { generateBuildings } from './BuildingGenerator'
import { generateCorporations } from './CorporationGenerator'
import { generateDistricts } from './DistrictGenerator'
import { generateInstitutions } from './InstitutionGenerator'
import { generateParcels } from './ParcelGenerator'
import { generateParks } from './ParkGenerator'
import { generateRivers } from './RiverGenerator'
import { generateRoadGraph } from './RoadGenerator'
import type { ProceduralWorldModel } from './types'

export function generateProceduralWorld(seed: number): ProceduralWorldModel {
  const rivers = generateRivers(seed)
  const roads = generateRoadGraph(seed, rivers)
  const blocks = generateBlocks(roads.corridors)
  const parcels = generateParcels(blocks, seed)
  const buildings = generateBuildings(parcels, seed)
  const districts = generateDistricts(blocks)
  const parks = generateParks(blocks, parcels, seed)
  const institutions = generateInstitutions(buildings)
  const corporations = generateCorporations(buildings)

  return {
    rivers,
    roads,
    blocks,
    parcels,
    buildings,
    districts,
    parks,
    institutions,
    corporations,
  }
}
