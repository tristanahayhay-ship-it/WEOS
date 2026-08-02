import { useEffect, useMemo, useRef } from 'react'
import { useCountryStore } from '../../stores/countryStore'
import { useCountryInteraction } from '../../hooks/useCountryInteraction'
import {
  AdditiveBlending,
  BackSide,
  BufferGeometry,
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
  PerspectiveCamera,
  Scene,
  SRGBColorSpace,
  SphereGeometry,
  Texture,
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
import type { Country } from '../../types/country'
import { getCountryBoundaryGeometry, getCountryBoundaryRings } from '../../utils/countryGeometry'
import { addCountryInfrastructure } from '../../world/country/CountryInfrastructureScene'
import { generateEconomicLayer } from '../../world/country/CountryEconomicGenerator'
import { addResolvedCountryFlowNodes } from '../../world/country/CountryEconomicScene'
import { getAdminData } from '../../view/adminDivisionMockData'
import { flattenGeoBoundaryRings, resolveCountryFlowModel } from '../../world/country/countryFlowModel'

/** Lerp speed for programmatic camera-distance animation (units/second). */
const CAMERA_DAMPING = 9
/** Distance tolerance to consider camera "arrived" at a pending target. */
const CAMERA_ARRIVE_TOLERANCE = 0.003

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

function disposeWorld(object: Object3D) {
  object.traverse((child: Object3D) => {
    if (child instanceof Mesh) {
      child.geometry.dispose()

      if (Array.isArray(child.material)) {
        child.material.forEach((material: Material) => disposeMaterialWithTextures(material))
      } else {
        disposeMaterialWithTextures(child.material)
      }
    }

    if (child instanceof Line) {
      child.geometry.dispose()

      if (Array.isArray(child.material)) {
        child.material.forEach((material: Material) => disposeMaterialWithTextures(material))
      } else {
        disposeMaterialWithTextures(child.material)
      }
    }
  })
}

const LAYER_FADE_SPEED = 4.5
const DEPTH_WRITE_ALPHA_THRESHOLD = 0.35
const ALPHA_UPDATE_THRESHOLD = 0.002
const COUNTRY_BORDER_ALTITUDE = 0.018
const COUNTRY_DETAIL_LEVELS = [2, 3] as const
const COUNTRY_DETAIL_CLEAR_ALPHA_THRESHOLD = 0.06
const BASE_OPACITY_BY_MATERIAL = new WeakMap<Material, number>()
const MATERIAL_TEXTURE_KEYS = [
  'map',
  'alphaMap',
  'aoMap',
  'bumpMap',
  'displacementMap',
  'emissiveMap',
  'envMap',
  'lightMap',
  'metalnessMap',
  'normalMap',
  'roughnessMap',
  'specularMap',
  'gradientMap',
] as const

function disposeMaterialWithTextures(material: Material) {
  const textureAwareMaterial = material as Material & Partial<Record<(typeof MATERIAL_TEXTURE_KEYS)[number], unknown>>
  for (const key of MATERIAL_TEXTURE_KEYS) {
    const texture = textureAwareMaterial[key]
    if (texture instanceof Texture) texture.dispose()
  }
  material.dispose()
}

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
  layers: Record<ZoomLevelId, WorldLayerState>
  coastlineAlpha: number
  boundaryAlpha: number
}

function setGroupOpacity(group: Object3D, alpha: number) {
  group.traverse((child) => {
    if (!(child instanceof Mesh || child instanceof Line)) return
    const materials = Array.isArray(child.material) ? child.material : [child.material]
    for (const material of materials) {
      if (!BASE_OPACITY_BY_MATERIAL.has(material)) {
        BASE_OPACITY_BY_MATERIAL.set(material, material.opacity)
      }
      const baseOpacity = BASE_OPACITY_BY_MATERIAL.get(material) ?? material.opacity
      material.transparent = true
      material.opacity = baseOpacity * alpha
      material.depthWrite = alpha > DEPTH_WRITE_ALPHA_THRESHOLD
    }
  })
  group.visible = alpha > 0.01
}

function updateGroupAlpha(
  group: Group,
  currentAlpha: number,
  targetAlpha: number,
  fadeLerp: number,
) {
  const nextAlpha = MathUtils.lerp(currentAlpha, targetAlpha, fadeLerp)
  const changed = Math.abs(nextAlpha - currentAlpha) > ALPHA_UPDATE_THRESHOLD
  if (changed) setGroupOpacity(group, nextAlpha)
  return nextAlpha
}

function buildCountryLinePaths(rings: number[][][], radius: number) {
  const paths: Float32Array[] = []

  for (const ring of rings) {
    if (ring.length < 2) continue

    let currentPoints: number[] = []

    for (let index = 0; index < ring.length; index += 1) {
      const [longitude, latitude] = ring[index] ?? []
      if (longitude == null || latitude == null) continue

      if (
        index > 0 &&
        Math.abs(longitude - ring[index - 1]![0]) > 180 &&
        currentPoints.length >= 6
      ) {
        paths.push(new Float32Array(currentPoints))
        currentPoints = []
      }

      const [x, y, z] = projectLngLatToCartesian(longitude, latitude, radius)
      currentPoints.push(x, y, z)
    }

    if (currentPoints.length >= 6) {
      paths.push(new Float32Array(currentPoints))
    }
  }

  return paths
}

function clearGroup(group: Group) {
  while (group.children.length > 0) {
    const child = group.children[0]!
    group.remove(child)
    disposeWorld(child)
  }
}

function animateCapitalPulse(group: Group, nowMs: number) {
  const phase = nowMs * 0.0045
  group.traverse((object) => {
    const role = object.userData?.capitalPulseRole
    if (!role || !(object instanceof Mesh)) return

    if (role === 'core') {
      const scale = 1 + 0.18 * (0.5 + 0.5 * Math.sin(phase))
      object.scale.setScalar(scale)
      return
    }

    if (role === 'glow' && object.material instanceof MeshBasicMaterial) {
      const baseOpacity = typeof object.userData.baseOpacity === 'number' ? object.userData.baseOpacity : 0.25
      const pulse = 0.55 + 0.45 * (0.5 + 0.5 * Math.sin(phase + Math.PI / 2))
      object.material.opacity = baseOpacity * pulse
    }
  })
}

function populateCountryDetailLayer(group: Group, country: Country | null) {
  clearGroup(group)

  if (!country) return

  const rings = getCountryBoundaryRings(country.numericCode)
  const boundary = getCountryBoundaryGeometry(country.numericCode)
  const adminData = getAdminData(country.isoCode)

  const economicLayer = generateEconomicLayer(country)
  const flowModel = resolveCountryFlowModel({
    country,
    economicLayer,
    nationalBoundary: boundary,
    nationalBoundaryRings: rings,
    adminData,
  })

  const nationalRings = flattenGeoBoundaryRings(flowModel?.country.boundary ?? null)
  const fallbackNationalRings = nationalRings.length > 0 ? nationalRings : rings
  const divisionRings = flowModel?.country.divisions
    ?.flatMap((division) => flattenGeoBoundaryRings(division.boundary))
    ?? []

  const renderableModel = flowModel?.capital ? flowModel : null

  const boundaryRings = renderableModel ? fallbackNationalRings : rings
  if (boundaryRings.length > 0) {
    group.add(createLineGroup(buildCountryLinePaths(boundaryRings, EARTH_RADIUS + COUNTRY_BORDER_ALTITUDE), '#f8fafc', 0.95))
  }

  if (divisionRings.length > 0) {
    group.add(createLineGroup(
      buildCountryLinePaths(divisionRings, EARTH_RADIUS + COUNTRY_BORDER_ALTITUDE + 0.0007),
      '#67e8f9',
      0.56,
    ))
  }

  // V2: infrastructure layer (highways, roads, railways, airports, seaports,
  //     landuse zones, rivers, parks) — rendered beneath economic nodes.
  addCountryInfrastructure(group, country)

  if (renderableModel) {
    addResolvedCountryFlowNodes(group, renderableModel)
  }
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

  const layer0 = new Group()
  const layer1 = createContinentLayer()
  const layer2 = new Group()
  const layer3 = new Group()
  const layer4 = new Group()
  const layer5 = new Group()
  const layer6 = new Group()

  world.rotation.z = MathUtils.degToRad(23.4)
  world.add(earth, atmosphere, coastlines, countryBoundaries, layer0, layer1, layer2, layer3, layer4, layer5, layer6)

  const layers: Record<ZoomLevelId, WorldLayerState> = {
    0: { group: layer0, alpha: 1 },
    1: { group: layer1, alpha: 0 },
    2: { group: layer2, alpha: 0 },
    3: { group: layer3, alpha: 0 },
    4: { group: layer4, alpha: 0 },
    5: { group: layer5, alpha: 0 },
    6: { group: layer6, alpha: 0 },
  }

  for (const level of [0, 1, 2, 3, 4, 5, 6] as const) {
    setGroupOpacity(layers[level].group, layers[level].alpha)
  }

  return {
    world,
    earth,
    atmosphere,
    coastlines,
    countryBoundaries,
    layers,
    coastlineAlpha: 1,
    boundaryAlpha: 1,
  }
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
  const countryDetailKeyRef = useRef<string>('')
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
    controls.dampingFactor = 0.08
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
    camera.position.set(0, 0, getCameraDistance(container.clientWidth))

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
          const nextDist = MathUtils.damp(currentDist, pendingDist, CAMERA_DAMPING, deltaSeconds)
          camera.position.normalize().multiplyScalar(nextDist)
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
      const selectedCountry = countryState.selectedCountry
      const countryDetailKey = selectedCountry?.isoCode ?? ''
      const shouldClearCountryDetail = (
        countryDetailKey === ''
        && countryDetailKeyRef.current !== ''
        && activeLevel < 2
        && worldBundle.layers[2].alpha <= COUNTRY_DETAIL_CLEAR_ALPHA_THRESHOLD
      )

      if ((selectedCountry && countryDetailKey !== countryDetailKeyRef.current) || shouldClearCountryDetail) {
        for (const level of COUNTRY_DETAIL_LEVELS) {
          populateCountryDetailLayer(worldBundle.layers[level].group, selectedCountry ?? null)
        }
        countryDetailKeyRef.current = countryDetailKey
      }

      const preserveCountryView = selectedCountry !== null && activeLevel >= 2

      // Clamp to 1 to keep interpolation stable on dropped/long frames.
      const fadeLerp = Math.min(1, LAYER_FADE_SPEED * deltaSeconds)
      for (const level of [0, 1, 2, 3, 4, 5, 6] as const) {
        const state = worldBundle.layers[level]
        const targetAlpha = level === activeLevel ? 1 : 0
        state.alpha = updateGroupAlpha(state.group, state.alpha, targetAlpha, fadeLerp)
      }
      for (const level of COUNTRY_DETAIL_LEVELS) {
        animateCapitalPulse(worldBundle.layers[level].group, now)
      }

      const globeAlphaTarget = activeLevel <= 3 || preserveCountryView ? 1 : 0.22
      const earthMaterial = worldBundle.earth.material as MeshPhongMaterial
      earthMaterial.opacity = MathUtils.lerp(earthMaterial.opacity, globeAlphaTarget, fadeLerp)
      const atmosphereMaterial = worldBundle.atmosphere.material as MeshBasicMaterial
      const atmosphereTarget = activeLevel <= 3 || preserveCountryView ? 0.12 : 0.02
      atmosphereMaterial.opacity = MathUtils.lerp(atmosphereMaterial.opacity, atmosphereTarget, fadeLerp)
      const boundaryAlphaTarget = activeLevel <= 3 || preserveCountryView ? 1 : 0.15
      const coastAlphaTarget = activeLevel <= 3 || preserveCountryView ? 1 : 0.2
      worldBundle.boundaryAlpha = updateGroupAlpha(
        worldBundle.countryBoundaries,
        worldBundle.boundaryAlpha,
        boundaryAlphaTarget,
        fadeLerp,
      )
      worldBundle.coastlineAlpha = updateGroupAlpha(
        worldBundle.coastlines,
        worldBundle.coastlineAlpha,
        coastAlphaTarget,
        fadeLerp,
      )

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
      countryDetailKeyRef.current = ''
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
