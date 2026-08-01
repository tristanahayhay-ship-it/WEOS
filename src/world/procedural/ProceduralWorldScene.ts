import {
  BufferGeometry,
  CatmullRomCurve3,
  Color,
  ConeGeometry,
  CylinderGeometry,
  ExtrudeGeometry,
  Float32BufferAttribute,
  Group,
  Line,
  LineBasicMaterial,
  Mesh,
  MeshPhongMaterial,
  PlaneGeometry,
  Shape,
  TubeGeometry,
  Vector3,
} from 'three'
import { generateProceduralWorld } from './ProceduralWorldGenerator'
import type {
  Block,
  Building,
  District,
  Park,
  ProceduralWorldModel,
  RoadBridge,
  RoadSegment,
  RoadType,
  Vec2,
  ZoningType,
} from './types'

interface ProceduralLayerBundle {
  city: Group
  district: Group
  institution: Group
  corporation: Group
  model: ProceduralWorldModel
}

const ROAD_COLORS: Record<RoadType, string> = {
  highway: '#6b7280',
  primary: '#4b5563',
  secondary: '#8b95a5',
  local: '#a7b0c0',
}

const ZONING_COLORS: Record<ZoningType, string> = {
  cbd: '#90caf9',
  commercial: '#b0bec5',
  industrial: '#9e9e9e',
  mixed_use: '#a7bfa3',
  residential: '#d1d5db',
}

function createPolygonShape(points: Vec2[]): Shape {
  const shape = new Shape()
  if (points.length === 0) return shape

  shape.moveTo(points[0]!.x, points[0]!.y)
  for (let i = 1; i < points.length; i += 1) {
    const point = points[i]
    if (!point) continue
    shape.lineTo(point.x, point.y)
  }
  return shape
}

/**
 * Render roads – handles multi-point polylines by creating a quad for
 * each consecutive pair of points along the road.
 */
function addRoads(target: Group, roads: RoadSegment[], visibleTypes: Set<RoadType>) {
  for (const road of roads) {
    if (!visibleTypes.has(road.type)) continue
    const pts = road.points
    if (pts.length < 2) continue

    const color = ROAD_COLORS[road.type]
    const mat = new MeshPhongMaterial({ color, transparent: true, opacity: 0.95 })

    for (let i = 0; i < pts.length - 1; i += 1) {
      const start = pts[i]
      const end = pts[i + 1]
      if (!start || !end) continue

      const length = Math.hypot(end.x - start.x, end.y - start.y)
      if (length < 1e-6) continue
      const angle = Math.atan2(end.y - start.y, end.x - start.x)
      const cx = (start.x + end.x) * 0.5
      const cy = (start.y + end.y) * 0.5

      const mesh = new Mesh(new PlaneGeometry(length, road.width), mat)
      mesh.position.set(cx, cy, 0.001)
      mesh.rotation.z = angle
      target.add(mesh)
    }

    for (const bridge of road.bridges) {
      const angle =
        pts.length >= 2
          ? Math.atan2(pts[1]!.y - pts[0]!.y, pts[1]!.x - pts[0]!.x)
          : 0
      addBridge(target, bridge, angle)
    }
  }
}

function addBridge(target: Group, bridge: RoadBridge, angle: number) {
  const bridgeWidth = bridge.roadType === 'highway' ? 0.014 : 0.01
  const bridgeDeck = new Mesh(
    new PlaneGeometry(bridge.span, bridgeWidth),
    new MeshPhongMaterial({ color: '#cbd5e1', transparent: true, opacity: 0.95 }),
  )
  bridgeDeck.position.set(bridge.position.x, bridge.position.y, 0.0022)
  bridgeDeck.rotation.z = angle
  target.add(bridgeDeck)

  const arch = new Mesh(
    new CylinderGeometry(bridgeWidth * 0.18, bridgeWidth * 0.18, bridge.span, 10),
    new MeshPhongMaterial({ color: '#94a3b8', transparent: true, opacity: 0.85 }),
  )
  arch.rotation.z = angle + Math.PI * 0.5
  arch.position.set(bridge.position.x, bridge.position.y, 0.0014)
  target.add(arch)
}

function addBlockOutlines(target: Group, blocks: Block[], opacity: number) {
  for (const block of blocks) {
    const points: number[] = []
    for (const point of block.polygon) {
      points.push(point.x, point.y, 0.0015)
    }
    const first = block.polygon[0]
    if (first) points.push(first.x, first.y, 0.0015)

    const geometry = new BufferGeometry()
    geometry.setAttribute('position', new Float32BufferAttribute(points, 3))
    const line = new Line(
      geometry,
      new LineBasicMaterial({ color: '#64748b', transparent: true, opacity }),
    )
    target.add(line)
  }
}

function addDistrictBoundaries(target: Group, districts: District[]) {
  for (const district of districts) {
    const points: number[] = []
    for (const point of district.polygon) {
      points.push(point.x, point.y, 0.002)
    }
    const first = district.polygon[0]
    if (first) points.push(first.x, first.y, 0.002)

    const geometry = new BufferGeometry()
    geometry.setAttribute('position', new Float32BufferAttribute(points, 3))
    const line = new Line(
      geometry,
      new LineBasicMaterial({ color: '#f59e0b', transparent: true, opacity: 0.78 }),
    )
    target.add(line)
  }
}

function addBuildings(target: Group, buildings: Building[]) {
  for (const building of buildings) {
    if (building.footprint.length < 3) continue
    const shape = createPolygonShape(building.footprint)
    const extrude = new ExtrudeGeometry(shape, {
      depth: building.height,
      bevelEnabled: false,
    })
    const color = ZONING_COLORS[building.zoning]
    const emissive = new Color(color).multiplyScalar(0.1)
    const mesh = new Mesh(
      extrude,
      new MeshPhongMaterial({
        color,
        emissive,
        emissiveIntensity: building.zoning === 'cbd' ? 0.25 : 0.1,
        transparent: true,
        opacity: 0.96,
      }),
    )
    mesh.position.z = 0.0013
    target.add(mesh)
  }
}

function addParks(target: Group, parks: Park[]) {
  for (const park of parks) {
    const shape = createPolygonShape(park.polygon)
    const parkMesh = new Mesh(
      new ExtrudeGeometry(shape, { depth: 0.00045, bevelEnabled: false }),
      new MeshPhongMaterial({ color: '#1f8a4c', transparent: true, opacity: 0.9 }),
    )
    parkMesh.position.z = 0.0011
    target.add(parkMesh)

    for (const tree of park.treePositions) {
      const trunk = new Mesh(
        new CylinderGeometry(0.00025, 0.00025, 0.0011, 6),
        new MeshPhongMaterial({ color: '#6b4f2b', transparent: true, opacity: 0.95 }),
      )
      trunk.position.set(tree.x, tree.y, 0.00165)
      target.add(trunk)

      const canopy = new Mesh(
        new ConeGeometry(0.001, 0.0023, 7),
        new MeshPhongMaterial({ color: '#2b9f52', transparent: true, opacity: 0.95 }),
      )
      canopy.position.set(tree.x, tree.y, 0.0032)
      target.add(canopy)
    }
  }
}

function addRivers(target: Group, model: ProceduralWorldModel) {
  for (const river of model.rivers) {
    const points = river.centerline.map((point) => new Vector3(point.x, point.y, 0.0008))
    if (points.length < 2) continue
    const curve = new CatmullRomCurve3(points)
    const mesh = new Mesh(
      new TubeGeometry(curve, 80, river.width * 0.46, 10, false),
      new MeshPhongMaterial({ color: '#2f8be8', transparent: true, opacity: 0.88 }),
    )
    target.add(mesh)
  }
}

function addParcels(target: Group, model: ProceduralWorldModel) {
  for (const parcel of model.parcels) {
    const points: number[] = []
    for (const point of parcel.polygon) {
      points.push(point.x, point.y, 0.0014)
    }
    const first = parcel.polygon[0]
    if (first) points.push(first.x, first.y, 0.0014)

    const geometry = new BufferGeometry()
    geometry.setAttribute('position', new Float32BufferAttribute(points, 3))
    target.add(
      new Line(
        geometry,
        new LineBasicMaterial({ color: '#6b7280', transparent: true, opacity: 0.2 }),
      ),
    )
  }
}

export function createProceduralLayers(seed: number): ProceduralLayerBundle {
  const model = generateProceduralWorld(seed)

  const city = new Group()
  addRivers(city, model)
  addRoads(city, model.roads.roads, new Set<RoadType>(['highway', 'primary']))
  addBlockOutlines(city, model.blocks, 0.22)
  addBuildings(city, model.buildings)
  addParks(city, model.parks)

  const district = new Group()
  addRivers(district, model)
  addRoads(district, model.roads.roads, new Set<RoadType>(['highway', 'primary', 'secondary', 'local']))
  addBlockOutlines(district, model.blocks, 0.35)
  addParcels(district, model)
  addBuildings(district, model.buildings)
  addParks(district, model.parks)
  addDistrictBoundaries(district, model.districts)

  const institution = new Group()
  const corporation = new Group()

  return {
    city,
    district,
    institution,
    corporation,
    model,
  }
}

