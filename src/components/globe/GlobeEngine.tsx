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
  Vector3,
  WebGLRenderer,
} from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { useUIStore } from '../../stores/uiStore'
import { useElementSize } from '../../hooks/useElementSize'
import { useGlobeViewStore } from '../../stores/globeViewStore'
import { useDebugStore } from '../../stores/debugStore'
import {
  COASTLINE_PATHS,
  COUNTRY_BOUNDARY_PATHS,
  EARTH_RADIUS,
  projectLngLatToCartesian,
} from '../../utils/globe'
import { DEBUG_COUNTRIES } from '../../utils/debugCountries'

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

function createWorld() {
  const world = new Group()

  const earth = new Mesh(
    new SphereGeometry(EARTH_RADIUS, 96, 96),
    new MeshPhongMaterial({
      color: '#102a43',
      emissive: '#07131f',
      shininess: 20,
      specular: new Color('#1f4d70'),
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

  world.rotation.z = MathUtils.degToRad(23.4)
  world.add(earth, atmosphere, coastlines, countryBoundaries)

  return world
}

export default function GlobeEngine() {
  const currentViewMode = useUIStore((state) => state.viewMode)
  const { ref: containerRef, size } = useElementSize<HTMLDivElement>()
  const rendererRef = useRef<WebGLRenderer | null>(null)
  const cameraRef = useRef<PerspectiveCamera | null>(null)
  const controlsRef = useRef<OrbitControls | null>(null)
  const sceneRef = useRef<Scene | null>(null)
  const worldRef = useRef<Group | null>(null)
  const debugMarkersRef = useRef<Group | null>(null)
  const focusTarget = useMemo(() => new Vector3(0, 0, 0), [])

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

    const world = createWorld()
    const debugMarkers = createDebugMarkers()
    world.add(debugMarkers)

    scene.add(fillLight, keyLight, world)
    camera.position.set(0, 0, DESKTOP_CAMERA_DISTANCE)

    rendererRef.current = renderer
    cameraRef.current = camera
    controlsRef.current = controls
    sceneRef.current = scene
    worldRef.current = world
    debugMarkersRef.current = debugMarkers

    const renderFrame = () => {
      controls.update()
      scene.updateMatrixWorld()
      camera.updateMatrixWorld()

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
      debugMarkersRef.current = null
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
