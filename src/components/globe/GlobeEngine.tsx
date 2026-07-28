import { useEffect, useMemo, useRef } from 'react'
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
import {
  COASTLINE_PATHS,
  COUNTRY_BOUNDARY_PATHS,
  EARTH_RADIUS,
} from '../../utils/globe'

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
  const focusTarget = useMemo(() => new Vector3(0, 0, 0), [])

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

    scene.add(fillLight, keyLight, world)
    camera.position.set(0, 0, DESKTOP_CAMERA_DISTANCE)

    rendererRef.current = renderer
    cameraRef.current = camera
    controlsRef.current = controls
    sceneRef.current = scene
    worldRef.current = world

    const renderFrame = () => {
      controls.update()
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
    }
  }, [containerRef, focusTarget])

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
    </section>
  )
}
