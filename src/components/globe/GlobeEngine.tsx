import { useEffect, useMemo, useRef } from 'react'
import { useCountryStore } from '../../stores/countryStore'
import { useCountryInteraction } from '../../hooks/useCountryInteraction'
import {
  AdditiveBlending,
  BackSide,
  BoxGeometry,
  BufferGeometry,
  CylinderGeometry,
  Color,
  DirectionalLight,
  Float32BufferAttribute,
  Group,
  HemisphereLight,
  Line,
  LineBasicMaterial,
  MathUtils,
  Material,
  Matrix4,
  Mesh,
  MeshBasicMaterial,
  MeshPhongMaterial,
  Object3D,
  PlaneGeometry,
  PerspectiveCamera,
  Scene,
  SRGBColorSpace,
  SphereGeometry,
  Vector3,
  WebGLRenderer,
} from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { useUIStore } from '../../stores/uiStore'
import { useElementSize } from '../../hooks/useElementSize'
import { useGlobeViewStore } from '../../stores/globeViewStore'
import { useDebugStore } from '../../stores/debugStore'
import { useZoomStore } from '../../stores/zoomStore'
import type { ZoomLevelId } from '../../zoom/types'
import {
  COASTLINE_PATHS,
  COUNTRY_BOUNDARY_PATHS,
  EARTH_RADIUS,
  projectLngLatToCartesian,
} from '../../utils/globe'
import { DEBUG_COUNTRIES } from '../../utils/debugCountries'

/** Lerp speed for programmatic camera-distance animation (units/second). */
const CAMERA_LERP_SPEED = 3.5
/** Distance tolerance to consider camera "arrived" at a pending target. */
const CAMERA_ARRIVE_TOLERANCE = 0.005

const VIEW_MODE_LABELS = {
  '2d': '2D MAP',
  '3d': '3D GLOBE',
  'flow': 'FLOW',
  'chart': 'CHART',
} as const

const MOBILE_BREAKPOINT = 640
const MOBILE_CAMERA_DISTANCE = 3.2
const DESKTOP_CAMERA_DISTANCE = 2.8

function getCameraDistance(width: number) {
  return width < MOBILE_BREAKPOINT ? MOBILE_CAMERA_DISTANCE : DESKTOP_CAMERA_DISTANCE
}

// ── Pre-allocated scratch objects for per-frame sprite-point computation ──────
const _sv          = new Vector3()
const _svCamLocal  = new Vector3()
const _svToCamera  = new Vector3()
const _svWorldInv  = new Matrix4()

/**
 * Build a Group of 5 small Mesh markers, one per DEBUG_COUNTRY.
 * Placed at EARTH_RADIUS * 1.025 to sit visibly above the surface.
 * Start invisible; visibility is controlled by debug mode.
 */
function createDebugMarkers(): Group {
  const group = new Group()
  const geo   = new SphereGeometry(0.028, 8, 8)

  for (const c of DEBUG_COUNTRIES) {
    const [x, y, z] = projectLngLatToCartesian(c.lon, c.lat, EARTH_RADIUS * 1.025)
    const mat  = new MeshBasicMaterial({ color: c.color })
    const mesh = new Mesh(geo, mat)
    mesh.position.set(x, y, z)
    group.add(mesh)
  }

  group.visible = false
  return group
}

function createLineGroup(
  paths: Float32Array[],
  color: string,
  opacity: number,
) {
  const group = new Group()
  const material = new LineBasicMaterial({
    color,
    opacity,
    transparent: opacity < 1,
  })

  for (const positions of paths) {
    const geometry = new BufferGeometry()
    geometry.setAttribute('position', new Float32BufferAttribute(positions, 3))

    group.add(new Line(geometry, material))
  }

  return group
}

function disposeWorld(object: Group | Scene) {
  object.traverse((child: Object3D) => {
    if (child instanceof Mesh) {
      child.geometry.dispose()

      if (Array.isArray(child.material)) {
        child.material.forEach((material: Material) => material.dispose())
      } else {
        child.material.dispose()
      }
    }

    if (child instanceof Line) {
      child.geometry.dispose()

      if (Array.isArray(child.material)) {
        child.material.forEach((material: Material) => material.dispose())
      } else {
        child.material.dispose()
      }
    }
  })
}

const DEFAULT_COUNTRY_CENTER: [number, number] = [10, 48]
const LAYER_FADE_SPEED = 4.5
const WORLD_DETAIL_SURFACE = EARTH_RADIUS * 1.03

interface WorldLayerState {
  group: Group
  alpha: number
}

interface WorldBundle {
  world: Group
  earth: Mesh
  atmosphere: Mesh
  coastlines: Group
  countryBoundaries: Group
  detailAnchor: Group
  layers: Record<ZoomLevelId, WorldLayerState>
}

function createSeededRandom(seed: number) {
  let state = (seed >>> 0) || 1
  return () => {
    state = (state * 1664525 + 1013904223) >>> 0
    return state / 0xffffffff
  }
}

function setGroupOpacity(group: Object3D, alpha: number) {
  group.traverse((child) => {
    if (!(child instanceof Mesh || child instanceof Line)) return
    const materials = Array.isArray(child.material) ? child.material : [child.material]
    for (const material of materials) {
      const userData = material.userData as { baseOpacity?: number }
      const baseOpacity = userData.baseOpacity ?? material.opacity
      if (userData.baseOpacity == null) userData.baseOpacity = baseOpacity
      material.transparent = true
      material.opacity = baseOpacity * alpha
      material.depthWrite = alpha > 0.35
    }
  })
  group.visible = alpha > 0.01
}

function addRoadMesh(group: Group, x: number, y: number, length: number, width: number, angle: number, color: string) {
  const road = new Mesh(
    new BoxGeometry(length, width, 0.0018),
    new MeshPhongMaterial({ color, transparent: true, opacity: 0.95 }),
  )
  road.position.set(x, y, 0.0012)
  road.rotation.z = angle
  group.add(road)
}

function createCityLayer(seed: number): Group {
  const rand = createSeededRandom(seed)
  const layer = new Group()

  const ground = new Mesh(
    new PlaneGeometry(0.52, 0.52),
    new MeshPhongMaterial({ color: '#111827', transparent: true, opacity: 0.86 }),
  )
  ground.position.set(0, 0, -0.001)
  layer.add(ground)

  for (let i = 0; i < 20; i += 1) {
    const length = 0.34 + rand() * 0.24
    const x = (rand() - 0.5) * 0.34
    const y = (rand() - 0.5) * 0.34
    const angle = rand() * Math.PI
    addRoadMesh(layer, x, y, length, 0.010, angle, '#4b5563')
  }

  for (let i = 0; i < 50; i += 1) {
    const length = 0.18 + rand() * 0.16
    const x = (rand() - 0.5) * 0.4
    const y = (rand() - 0.5) * 0.4
    const angle = rand() * Math.PI
    addRoadMesh(layer, x, y, length, 0.0048, angle, '#6b7280')
  }

  for (let i = 0; i < 5; i += 1) {
    const park = new Mesh(
      new PlaneGeometry(0.06 + rand() * 0.04, 0.045 + rand() * 0.035),
      new MeshPhongMaterial({ color: '#1f8a4c', transparent: true, opacity: 0.9 }),
    )
    park.position.set((rand() - 0.5) * 0.38, (rand() - 0.5) * 0.38, 0.001)
    layer.add(park)
  }

  for (let i = 0; i < 5; i += 1) {
    const river = new Mesh(
      new BoxGeometry(0.13, 0.022, 0.0016),
      new MeshPhongMaterial({ color: '#2780e3', transparent: true, opacity: 0.86 }),
    )
    river.position.set(-0.21 + i * 0.1, 0.08 * Math.sin(i * 0.8) - 0.04, 0.0013)
    river.rotation.z = -0.2 + i * 0.08
    layer.add(river)
  }

  const cbdCenter = new Vector3(0.02, 0.01, 0.0015)
  for (let i = 0; i < 3; i += 1) {
    const tower = new Mesh(
      new CylinderGeometry(0.014, 0.016, 0.15 + rand() * 0.1, 10),
      new MeshPhongMaterial({ color: '#74a8ff', emissive: '#1d4ed8', emissiveIntensity: 0.2, transparent: true, opacity: 0.95 }),
    )
    tower.position.set(cbdCenter.x + (i - 1) * 0.028, cbdCenter.y + (i % 2) * 0.016, 0.07)
    layer.add(tower)
  }

  const industrialPad = new Mesh(
    new PlaneGeometry(0.16, 0.11),
    new MeshPhongMaterial({ color: '#3f3f46', transparent: true, opacity: 0.8 }),
  )
  industrialPad.position.set(0.15, -0.16, 0.0009)
  layer.add(industrialPad)

  for (let i = 0; i < 12; i += 1) {
    const bW = 0.014 + rand() * 0.018
    const bD = 0.014 + rand() * 0.018
    const bH = 0.016 + rand() * 0.03
    const block = new Mesh(
      new BoxGeometry(bW, bD, bH),
      new MeshPhongMaterial({ color: '#9ca3af', transparent: true, opacity: 0.95 }),
    )
    block.position.set(0.09 + rand() * 0.12, -0.2 + rand() * 0.08, bH * 0.5 + 0.0012)
    layer.add(block)
  }

  for (let i = 0; i < 100; i += 1) {
    const bW = 0.008 + rand() * 0.018
    const bD = 0.008 + rand() * 0.018
    const bH = 0.01 + rand() * 0.07
    const block = new Mesh(
      new BoxGeometry(bW, bD, bH),
      new MeshPhongMaterial({
        color: i % 9 === 0 ? '#cbd5e1' : '#94a3b8',
        transparent: true,
        opacity: 0.96,
      }),
    )
    block.position.set((rand() - 0.5) * 0.42, (rand() - 0.5) * 0.42, bH * 0.5 + 0.0012)
    layer.add(block)
  }

  return layer
}

function createDistrictLayer(seed: number): Group {
  const rand = createSeededRandom(seed + 29)
  const layer = new Group()

  for (let i = 0; i < 60; i += 1) {
    const length = 0.08 + rand() * 0.1
    const angle = rand() * Math.PI
    addRoadMesh(layer, (rand() - 0.5) * 0.3, (rand() - 0.5) * 0.3, length, 0.003, angle, '#9ca3af')
  }

  for (let i = 0; i < 4; i += 1) {
    const boundary = createLineGroup(
      [new Float32Array([
        -0.2 + i * 0.1, -0.2, 0.002,
        -0.2 + i * 0.1, 0.2, 0.002,
      ])],
      '#f59e0b',
      0.7,
    )
    layer.add(boundary)
  }

  for (let i = 0; i < 200; i += 1) {
    const bW = 0.006 + rand() * 0.012
    const bD = 0.006 + rand() * 0.012
    const bH = 0.012 + rand() * 0.08
    const block = new Mesh(
      new BoxGeometry(bW, bD, bH),
      new MeshPhongMaterial({ color: '#bfc9d9', transparent: true, opacity: 0.96 }),
    )
    block.position.set((rand() - 0.5) * 0.32, (rand() - 0.5) * 0.32, bH * 0.5 + 0.0013)
    layer.add(block)
  }

  return layer
}

function createInstitutionLayer(seed: number): Group {
  const rand = createSeededRandom(seed + 73)
  const layer = new Group()
  const labels = ['bank', 'exchange', 'port', 'airport', 'factory', 'warehouse']

  for (let i = 0; i < 24; i += 1) {
    const radius = 0.03 + rand() * 0.16
    const angle = rand() * Math.PI * 2
    const x = Math.cos(angle) * radius
    const y = Math.sin(angle) * radius
    const h = 0.018 + rand() * 0.03
    const node = new Mesh(
      new CylinderGeometry(0.008, 0.01, h, 8),
      new MeshPhongMaterial({ color: '#fbbf24', emissive: '#92400e', emissiveIntensity: 0.25, transparent: true, opacity: 0.95 }),
    )
    node.position.set(x, y, h * 0.5 + 0.0018)
    node.userData['kind'] = labels[i % labels.length]
    layer.add(node)
  }

  return layer
}

function createCorporationLayer(seed: number): Group {
  const rand = createSeededRandom(seed + 199)
  const layer = new Group()
  const nodePositions: Vector3[] = []

  for (let i = 0; i < 30; i += 1) {
    const radius = 0.03 + rand() * 0.2
    const angle = rand() * Math.PI * 2
    const x = Math.cos(angle) * radius
    const y = Math.sin(angle) * radius
    const h = 0.012 + rand() * 0.02
    const node = new Mesh(
      new BoxGeometry(0.01, 0.01, h),
      new MeshPhongMaterial({ color: '#38bdf8', emissive: '#1d4ed8', emissiveIntensity: 0.22, transparent: true, opacity: 0.95 }),
    )
    node.position.set(x, y, h * 0.5 + 0.0018)
    layer.add(node)
    nodePositions.push(new Vector3(x, y, 0.002))
  }

  for (let i = 0; i < 100; i += 1) {
    const a = nodePositions[Math.floor(rand() * nodePositions.length)]
    const b = nodePositions[Math.floor(rand() * nodePositions.length)]
    if (!a || !b || a.equals(b)) continue

    const route = createLineGroup(
      [new Float32Array([a.x, a.y, a.z + 0.0008, b.x, b.y, b.z + 0.0008])],
      '#7dd3fc',
      0.75,
    )
    layer.add(route)
  }

  return layer
}

function createCountryLayer(seed: number): Group {
  const rand = createSeededRandom(seed + 11)
  const layer = new Group()
  const colors = ['#f97316', '#0ea5e9', '#34d399', '#f43f5e']

  for (let i = 0; i < 16; i += 1) {
    const radius = 0.03 + rand() * 0.18
    const angle = rand() * Math.PI * 2
    const x = Math.cos(angle) * radius
    const y = Math.sin(angle) * radius
    const h = 0.01 + rand() * 0.02
    const marker = new Mesh(
      new CylinderGeometry(0.007, 0.01, h, 10),
      new MeshPhongMaterial({ color: colors[i % colors.length], transparent: true, opacity: 0.9 }),
    )
    marker.position.set(x, y, h * 0.5 + 0.0015)
    layer.add(marker)
  }

  return layer
}

function createContinentLayer(): Group {
  const layer = new Group()
  const centers: Array<[number, number]> = [
    [-100, 45],
    [-60, -15],
    [20, 50],
    [20, 8],
    [95, 35],
    [135, -24],
  ]
  for (const [lon, lat] of centers) {
    const [x, y, z] = projectLngLatToCartesian(lon, lat, EARTH_RADIUS * 1.01)
    const region = new Mesh(
      new SphereGeometry(0.06, 10, 10),
      new MeshPhongMaterial({ color: '#2563eb', emissive: '#1d4ed8', emissiveIntensity: 0.2, transparent: true, opacity: 0.35 }),
    )
    region.position.set(x, y, z)
    layer.add(region)
  }

  const routes: Array<[[number, number], [number, number], string]> = [
    [[-74, 40], [2, 49], '#60a5fa'],
    [[2, 49], [103, 1], '#60a5fa'],
    [[139, 35], [-118, 34], '#93c5fd'],
    [[32, 30], [55, 25], '#93c5fd'],
  ]

  for (const [from, to, color] of routes) {
    const [sx, sy, sz] = projectLngLatToCartesian(from[0], from[1], EARTH_RADIUS * 1.016)
    const [ex, ey, ez] = projectLngLatToCartesian(to[0], to[1], EARTH_RADIUS * 1.016)
    const path = createLineGroup([new Float32Array([sx, sy, sz, ex, ey, ez])], color, 0.6)
    layer.add(path)
  }

  return layer
}

function updateAnchorTransform(anchor: Group, lon: number, lat: number) {
  const lonRad = MathUtils.degToRad(lon)
  const [x, y, z] = projectLngLatToCartesian(lon, lat, WORLD_DETAIL_SURFACE)
  const up = new Vector3(x, y, z).normalize()
  const east = new Vector3(-Math.sin(lonRad), 0, -Math.cos(lonRad)).normalize()
  const north = new Vector3().crossVectors(up, east).normalize()

  anchor.position.set(x, y, z)
  const basis = new Matrix4().makeBasis(east, north, up)
  anchor.setRotationFromMatrix(basis)
}

function createWorld(): WorldBundle {
  const world = new Group()

  const earth = new Mesh(
    new SphereGeometry(EARTH_RADIUS, 96, 96),
    new MeshPhongMaterial({
      color: '#102a43',
      emissive: '#07131f',
      shininess: 20,
      specular: new Color('#1f4d70'),
      transparent: true,
      opacity: 1,
    }),
  )

  const atmosphere = new Mesh(
    new SphereGeometry(EARTH_RADIUS * 1.035, 64, 64),
    new MeshBasicMaterial({
      color: '#4da3ff',
      transparent: true,
      opacity: 0.12,
      side: BackSide,
      blending: AdditiveBlending,
      depthWrite: false,
    }),
  )

  const coastlines = createLineGroup(COASTLINE_PATHS, '#79c4ff', 0.9)
  const countryBoundaries = createLineGroup(COUNTRY_BOUNDARY_PATHS, '#d9efff', 0.45)
  const detailAnchor = new Group()

  const layer0 = new Group()
  const layer1 = createContinentLayer()
  const layer2 = createCountryLayer(7)
  const layer3 = createCityLayer(11)
  const layer4 = createDistrictLayer(17)
  const layer5 = createInstitutionLayer(23)
  const layer6 = createCorporationLayer(31)
  detailAnchor.add(layer2, layer3, layer4, layer5, layer6)

  updateAnchorTransform(detailAnchor, DEFAULT_COUNTRY_CENTER[0], DEFAULT_COUNTRY_CENTER[1])

  world.rotation.z = MathUtils.degToRad(23.4)
  world.add(earth, atmosphere, coastlines, countryBoundaries, layer0, layer1, detailAnchor)

  const layers: Record<ZoomLevelId, WorldLayerState> = {
    0: { group: layer0, alpha: 1 },
    1: { group: layer1, alpha: 0 },
    2: { group: layer2, alpha: 0 },
    3: { group: layer3, alpha: 0 },
    4: { group: layer4, alpha: 0 },
    5: { group: layer5, alpha: 0 },
    6: { group: layer6, alpha: 0 },
  }

  for (const key of Object.keys(layers)) {
    const level = Number(key) as ZoomLevelId
    setGroupOpacity(layers[level].group, layers[level].alpha)
  }

  return { world, earth, atmosphere, coastlines, countryBoundaries, detailAnchor, layers }
}

export default function GlobeEngine() {
  const currentViewMode = useUIStore((state) => state.viewMode)
  const { ref: containerRef, size } = useElementSize<HTMLDivElement>()
  const rendererRef = useRef<WebGLRenderer | null>(null)
  const cameraRef = useRef<PerspectiveCamera | null>(null)
  const controlsRef = useRef<OrbitControls | null>(null)
  const sceneRef = useRef<Scene | null>(null)
  const worldRef = useRef<Group | null>(null)
  const worldBundleRef = useRef<WorldBundle | null>(null)
  const debugMarkersRef = useRef<Group | null>(null)
  const detailAnchorKeyRef = useRef<string>('')
  const focusTarget = useMemo(() => new Vector3(0, 0, 0), [])
  /** Monotonic clock used for camera-distance lerp delta-time calculation. */
  const lastFrameTimeRef = useRef<number>(performance.now())

  // Country interaction layer (hover + click + highlight)
  useCountryInteraction(containerRef, cameraRef, worldRef)

  const hoveredCountry = useCountryStore((s) => s.hoveredCountry)
  const tooltipPos = useCountryStore((s) => s.tooltipScreenPos)

  useEffect(() => {
    const container = containerRef.current

    if (!container || rendererRef.current) {
      return
    }

    const scene = new Scene()
    const camera = new PerspectiveCamera(45, 1, 0.1, 100)
    const renderer = new WebGLRenderer({
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance',
    })

    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.outputColorSpace = SRGBColorSpace
    renderer.domElement.style.width = '100%'
    renderer.domElement.style.height = '100%'
    renderer.domElement.style.display = 'block'
    container.appendChild(renderer.domElement)

    const controls = new OrbitControls(camera, renderer.domElement)
    controls.enableDamping = true
    controls.enablePan = true
    controls.enableZoom = true
    controls.screenSpacePanning = false
    controls.rotateSpeed = 0.65
    controls.zoomSpeed = 0.85
    controls.panSpeed = 0.7
    controls.minDistance = 1.75
    controls.maxDistance = 5.5
    controls.target.copy(focusTarget)

    const keyLight = new DirectionalLight('#ffffff', 2.4)
    keyLight.position.set(4, 2.5, 4.5)

    const fillLight = new HemisphereLight('#b7ddff', '#02070d', 1.2)

    const worldBundle = createWorld()
    const world = worldBundle.world
    const debugMarkers = createDebugMarkers()
    world.add(debugMarkers)

    scene.add(fillLight, keyLight, world)
    camera.position.set(0, 0, DESKTOP_CAMERA_DISTANCE)

    rendererRef.current = renderer
    cameraRef.current = camera
    controlsRef.current = controls
    sceneRef.current = scene
    worldRef.current = world
    worldBundleRef.current = worldBundle
    debugMarkersRef.current = debugMarkers

    const renderFrame = () => {
      // ── Delta time for camera animation ─────────────────────────────────────
      const now = performance.now()
      const deltaSeconds = Math.min((now - lastFrameTimeRef.current) / 1000, 0.1)
      lastFrameTimeRef.current = now

      // ── Zoom orchestration: animate camera toward pending target distance ───
      const zoomState = useZoomStore.getState()
      const pendingDist = zoomState.pendingCameraDistance
      if (pendingDist !== null) {
        const currentDist = camera.position.length()
        const diff = pendingDist - currentDist
        if (Math.abs(diff) < CAMERA_ARRIVE_TOLERANCE) {
          // Snap to exact target and clear pending
          camera.position.normalize().multiplyScalar(pendingDist)
          zoomState.clearPendingCamera()
        } else {
          // Lerp toward target distance, preserving direction
          const step = Math.sign(diff) * Math.min(Math.abs(diff), CAMERA_LERP_SPEED * deltaSeconds)
          camera.position.normalize().multiplyScalar(currentDist + step)
        }
      }

      // Single controls update per frame covers both animation and user input
      controls.update()
      scene.updateMatrixWorld()
      camera.updateMatrixWorld()

      // ── Report camera distance to zoom store for level detection ─────────
      zoomState.syncFromCameraDistance(camera.position.length())

      const activeLevel = zoomState.activeLevel
      const countryState = useCountryStore.getState()
      const focusedCountry = countryState.selectedCountry ?? countryState.hoveredCountry
      const [focusLon, focusLat] = focusedCountry?.center ?? DEFAULT_COUNTRY_CENTER
      const focusKey = focusedCountry?.isoCode ?? 'default'
      if (focusKey !== detailAnchorKeyRef.current) {
        updateAnchorTransform(worldBundle.detailAnchor, focusLon, focusLat)
        detailAnchorKeyRef.current = focusKey
      }

      for (const key of Object.keys(worldBundle.layers)) {
        const level = Number(key) as ZoomLevelId
        const state = worldBundle.layers[level]
        const targetAlpha = level === activeLevel ? 1 : 0
        state.alpha = MathUtils.lerp(state.alpha, targetAlpha, Math.min(1, LAYER_FADE_SPEED * deltaSeconds))
        setGroupOpacity(state.group, state.alpha)
      }

      const globeAlphaTarget = activeLevel <= 2 ? 1 : 0.22
      const earthMaterial = worldBundle.earth.material as MeshPhongMaterial
      earthMaterial.opacity = MathUtils.lerp(earthMaterial.opacity, globeAlphaTarget, Math.min(1, LAYER_FADE_SPEED * deltaSeconds))
      const atmosphereMaterial = worldBundle.atmosphere.material as MeshBasicMaterial
      const atmosphereTarget = activeLevel <= 2 ? 0.12 : 0.02
      atmosphereMaterial.opacity = MathUtils.lerp(atmosphereMaterial.opacity, atmosphereTarget, Math.min(1, LAYER_FADE_SPEED * deltaSeconds))
      const boundaryAlphaTarget = activeLevel <= 2 ? 1 : 0.15
      const coastAlphaTarget = activeLevel <= 2 ? 1 : 0.2
      setGroupOpacity(worldBundle.countryBoundaries, boundaryAlphaTarget)
      setGroupOpacity(worldBundle.coastlines, coastAlphaTarget)

      // ── Compute sprite screen positions via Three.js ground truth ───────────
      // This is the reference: vector.project(camera) applied to each test point.
      const vw = renderer.domElement.clientWidth
      const vh = renderer.domElement.clientHeight
      _svWorldInv.copy(world.matrixWorld).invert()

      const spritePoints = DEBUG_COUNTRIES.map(({ lon, lat }) => {
        const [x, y, z] = projectLngLatToCartesian(lon, lat, EARTH_RADIUS)
        _sv.set(x, y, z)

        // Same back-face culling used by OverlayCanvas.
        _svCamLocal.set(camera.position.x, camera.position.y, camera.position.z)
          .applyMatrix4(_svWorldInv)
        if (_sv.dot(_svToCamera.copy(_svCamLocal).sub(_sv)) <= 0) return null

        _sv.applyMatrix4(world.matrixWorld).project(camera)
        if (_sv.z < -1 || _sv.z > 1) return null

        return { x: ((_sv.x + 1) * vw) / 2, y: ((1 - _sv.y) * vh) / 2 }
      })

      useGlobeViewStore.getState().setFrame({
        worldMatrix: [...world.matrixWorld.elements],
        viewMatrix: [...camera.matrixWorldInverse.elements],
        projectionMatrix: [...camera.projectionMatrix.elements],
        cameraWorldPosition: [camera.position.x, camera.position.y, camera.position.z],
        viewportWidth: vw,
        viewportHeight: vh,
        spritePoints,
      })

      renderer.render(scene, camera)
    }

    renderer.setAnimationLoop(renderFrame)

    return () => {
      renderer.setAnimationLoop(null)
      controls.dispose()
      disposeWorld(scene)
      renderer.dispose()
      renderer.domElement.remove()
      rendererRef.current = null
      cameraRef.current = null
      controlsRef.current = null
      sceneRef.current = null
      worldRef.current = null
      worldBundleRef.current = null
      debugMarkersRef.current = null
      detailAnchorKeyRef.current = ''
      useGlobeViewStore.getState().clearFrame()
    }
  }, [containerRef, focusTarget])

  // ── Keep debug markers visible only when debug mode is active ──────────────
  useEffect(() => {
    return useDebugStore.subscribe((state) => {
      const m = debugMarkersRef.current
      if (m) m.visible = state.enabled
    })
  }, [])

  useEffect(() => {
    const renderer = rendererRef.current
    const camera = cameraRef.current

    if (!renderer || !camera || !size) {
      return
    }

    renderer.setSize(size.width, size.height, false)
    camera.aspect = size.width / size.height
    camera.position.set(0, 0, getCameraDistance(size.width))
    camera.updateProjectionMatrix()
  }, [size])

  return (
    <section
      className="relative h-full w-full"
      style={{
        background:
          'radial-gradient(circle at 50% 45%, rgba(18, 47, 82, 0.3), rgba(4, 8, 15, 0.96) 70%)',
      }}
    >
      <div ref={containerRef} className="h-full w-full cursor-grab active:cursor-grabbing" />

      <div
        className="pointer-events-none absolute left-4 top-4 rounded-md border px-3 py-2 text-[11px] tracking-[0.25em] uppercase"
        style={{
          background: 'rgba(10, 14, 26, 0.7)',
          borderColor: 'rgba(121, 196, 255, 0.3)',
          color: '#d9efff',
          backdropFilter: 'blur(8px)',
        }}
      >
        {VIEW_MODE_LABELS[currentViewMode]}
      </div>

      <div
        className="pointer-events-none absolute bottom-4 left-4 rounded-md border px-3 py-2 text-xs"
        style={{
          background: 'rgba(10, 14, 26, 0.7)',
          borderColor: 'rgba(121, 196, 255, 0.25)',
          color: 'var(--weos-text-muted)',
          backdropFilter: 'blur(8px)',
        }}
      >
        Rotate • Zoom • Pan
      </div>

      {hoveredCountry && tooltipPos && (
        <div
          className="pointer-events-none absolute z-10 rounded border px-2 py-1 text-xs"
          style={{
            left: tooltipPos.x + 14,
            top: tooltipPos.y - 32,
            background: 'rgba(8, 13, 24, 0.9)',
            borderColor: 'rgba(121, 196, 255, 0.4)',
            color: '#d9efff',
            backdropFilter: 'blur(6px)',
            whiteSpace: 'nowrap',
          }}
        >
          {hoveredCountry.name}
        </div>
      )}
    </section>
  )
}
