export type RoadType = 'highway' | 'primary' | 'secondary' | 'local'

export type ZoningType =
  | 'residential'
  | 'commercial'
  | 'cbd'
  | 'industrial'
  | 'mixed_use'

export type DistrictType =
  | 'residential'
  | 'commercial'
  | 'financial'
  | 'industrial'
  | 'government'
  | 'technology'
  | 'university'
  | 'airport'
  | 'port'

export interface Vec2 {
  x: number
  y: number
}

export interface River {
  id: string
  centerline: Vec2[]
  width: number
}

export interface RoadBridge {
  id: string
  position: Vec2
  roadType: RoadType
  span: number
}

export interface RoadSegment {
  id: string
  type: RoadType
  points: Vec2[]
  width: number
  bridges: RoadBridge[]
}

export interface Intersection {
  id: string
  position: Vec2
  roadIds: string[]
  kind: 'cross' | 'roundabout'
}

export interface Roundabout {
  id: string
  center: Vec2
  radius: number
  connectedRoadIds: string[]
}

export interface RoadCorridor {
  axis: 'x' | 'y'
  coord: number
  type: RoadType
  width: number
}

export interface RoadGraph {
  roads: RoadSegment[]
  intersections: Intersection[]
  roundabouts: Roundabout[]
  corridors: RoadCorridor[]
}

export interface Block {
  id: string
  polygon: Vec2[]
  area: number
  orientation: number
  adjacentRoadTypes: RoadType[]
  density: number
  zoning: ZoningType
}

export interface Parcel {
  id: string
  blockId: string
  polygon: Vec2[]
  width: number
  depth: number
  frontage: number
  zoning: ZoningType
}

export interface Building {
  id: string
  parcelId: string
  footprint: Vec2[]
  height: number
  zoning: ZoningType
  levels: number
}

export interface District {
  id: string
  name: string
  type: DistrictType
  polygon: Vec2[]
  blockIds: string[]
  population: number
  gdpUsdBillions: number
  density: number
}

export interface Park {
  id: string
  polygon: Vec2[]
  treePositions: Vec2[]
}

export interface Institution {
  id: string
  type:
    | 'parliament'
    | 'ministry'
    | 'central_bank'
    | 'exchange'
    | 'university'
    | 'hospital'
    | 'port'
    | 'airport'
  buildingIds: string[]
}

export interface Corporation {
  id: string
  name: string
  facilityType: 'hq' | 'office_complex' | 'logistics_center' | 'factory' | 'warehouse'
  buildingIds: string[]
}

export interface ProceduralWorldModel {
  rivers: River[]
  roads: RoadGraph
  blocks: Block[]
  parcels: Parcel[]
  buildings: Building[]
  districts: District[]
  parks: Park[]
  institutions: Institution[]
  corporations: Corporation[]
}
