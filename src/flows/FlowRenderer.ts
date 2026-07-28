import {
  AdditiveBlending,
  BufferGeometry,
  Color,
  Float32BufferAttribute,
  Group,
  Line,
  Matrix4,
  PerspectiveCamera,
  QuadraticBezierCurve3,
  Scene,
  ShaderMaterial,
  Vector3,
  WebGLRenderer,
} from 'three'
import type { GlobeFrameSnapshot } from '../stores/globeViewStore'
import type { FlowModel } from './types'
import { FLOW_TYPE_CONFIG } from '../stores/flowStore'
import { COUNTRIES } from '../data/countries'
import { projectLngLatToCartesian, EARTH_RADIUS } from '../utils/globe'

// ── Constants ─────────────────────────────────────────────────────────────────

/** Min / max tube-equivalent radius (world units) for value normalisation */
const MIN_LINE_OPACITY = 0.35
const MAX_LINE_OPACITY = 0.85

/** Number of segments along each arc */
const ARC_SEGMENTS = 60

/** How far above EARTH_RADIUS the arc peaks (relative, proportional to chord) */
const ARC_LIFT_FACTOR = 0.55

/** Value range for opacity normalisation (USD billions) */
const VALUE_MIN = 1
const VALUE_MAX = 600

// ── Shader code ───────────────────────────────────────────────────────────────

const FLOW_VERT = /* glsl */ `
  varying float vProgress;
  void main() {
    vProgress = uv.x;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`

const FLOW_FRAG = /* glsl */ `
  uniform float uTime;
  uniform vec3  uColor;
  uniform float uAlpha;

  varying float vProgress;

  void main() {
    // Moving pulse: one bright head (~15 % of arc length) that repeats
    float t    = fract(vProgress - uTime * 0.28);
    float head = smoothstep(0.0, 0.12, t) * (1.0 - smoothstep(0.6, 1.0, t));
    float base = 0.18;                 // dim "trail" always present
    float brightness = base + (1.0 - base) * head;
    gl_FragColor = vec4(uColor, uAlpha * brightness);
    if (gl_FragColor.a < 0.01) discard;
  }
`

// ── Helper: country centre lookup ─────────────────────────────────────────────

const countryCenter = new Map<string, [number, number]>()
for (const c of COUNTRIES) {
  countryCenter.set(c.isoCode, c.center as [number, number])
}

function getCenter(isoCode: string): [number, number] | null {
  return countryCenter.get(isoCode) ?? null
}

// ── Helper: arc geometry ──────────────────────────────────────────────────────

/**
 * Build a BufferGeometry for a single arc between two lat/lon points.
 * The arc is lifted above the sphere surface proportional to the chord length.
 */
function buildArcGeometry(
  srcLon: number,
  srcLat: number,
  dstLon: number,
  dstLat: number,
): BufferGeometry {
  const r = EARTH_RADIUS * 1.01           // slightly above surface
  const [ax, ay, az] = projectLngLatToCartesian(srcLon, srcLat, r)
  const [bx, by, bz] = projectLngLatToCartesian(dstLon, dstLat, r)

  const start = new Vector3(ax, ay, az)
  const end   = new Vector3(bx, by, bz)

  // Mid-point of great-circle arc, lifted by ARC_LIFT_FACTOR × chord length
  const mid = start.clone().add(end).multiplyScalar(0.5)
  const chordLen = start.distanceTo(end)
  const lift = chordLen * ARC_LIFT_FACTOR
  mid.normalize().multiplyScalar(EARTH_RADIUS + lift)

  const curve = new QuadraticBezierCurve3(start, mid, end)
  const points = curve.getPoints(ARC_SEGMENTS)

  const positions = new Float32Array(points.length * 3)
  const uvs       = new Float32Array(points.length * 2)

  for (let i = 0; i < points.length; i++) {
    positions[i * 3]     = points[i].x
    positions[i * 3 + 1] = points[i].y
    positions[i * 3 + 2] = points[i].z
    uvs[i * 2]           = i / (points.length - 1)  // progress 0→1 along arc
    uvs[i * 2 + 1]       = 0
  }

  const geo = new BufferGeometry()
  geo.setAttribute('position', new Float32BufferAttribute(positions, 3))
  geo.setAttribute('uv',       new Float32BufferAttribute(uvs, 2))
  return geo
}

// ── Helper: value → opacity normalisation ─────────────────────────────────────

function normaliseValue(value: number): number {
  const t = Math.min(Math.max((value - VALUE_MIN) / (VALUE_MAX - VALUE_MIN), 0), 1)
  return MIN_LINE_OPACITY + t * (MAX_LINE_OPACITY - MIN_LINE_OPACITY)
}

// ── FlowRenderer ──────────────────────────────────────────────────────────────

interface FlowEntry {
  line: Line
  material: ShaderMaterial
}

/**
 * Standalone Three.js renderer for 3D capital-flow arcs.
 *
 * Usage:
 *  1. `new FlowRenderer(canvas)` — attach to a transparent overlay canvas.
 *  2. Call `updateFlows(flows)` whenever flow data or visibility changes.
 *  3. Call `syncCamera(frame)` each animation frame with the latest GlobeEngine snapshot.
 *  4. Call `setTime(t)` each animation frame with the monotonic clock.
 *  5. Call `render()` to draw the frame.
 *  6. Call `dispose()` on cleanup.
 */
export class FlowRenderer {
  private readonly scene: Scene
  private readonly camera: PerspectiveCamera
  private readonly renderer: WebGLRenderer
  /** Group that mirrors the Globe world group matrix (incl. axial tilt). */
  private readonly flowGroup: Group
  /** Active line objects, keyed by flow id. */
  private readonly entries = new Map<string, FlowEntry>()

  constructor(canvas: HTMLCanvasElement) {
    this.scene    = new Scene()
    this.camera   = new PerspectiveCamera(45, 1, 0.1, 100)
    this.flowGroup = new Group()
    this.flowGroup.matrixAutoUpdate = false

    this.renderer = new WebGLRenderer({
      canvas,
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance',
    })
    this.renderer.setClearColor(0x000000, 0)
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))

    this.scene.add(this.flowGroup)
  }

  // ── Public API ──────────────────────────────────────────────────────────────

  /**
   * Rebuild arc geometry for all visible flows.
   * Call when the flow list or visible types change.
   */
  updateFlows(flows: FlowModel[]): void {
    // Remove arcs that are no longer in the list
    const nextIds = new Set(flows.map((f) => f.id))
    for (const [id, entry] of this.entries) {
      if (!nextIds.has(id)) {
        this.flowGroup.remove(entry.line)
        entry.line.geometry.dispose()
        entry.material.dispose()
        this.entries.delete(id)
      }
    }

    // Add arcs for new flows
    for (const flow of flows) {
      if (this.entries.has(flow.id)) continue

      const src = getCenter(flow.sourceCountry)
      const dst = getCenter(flow.targetCountry)
      if (!src || !dst) continue

      const geo      = buildArcGeometry(src[0], src[1], dst[0], dst[1])
      const cfg      = FLOW_TYPE_CONFIG[flow.flowType]
      const col      = new Color(cfg.colorHex)
      const alpha    = normaliseValue(flow.value)

      const mat = new ShaderMaterial({
        vertexShader:   FLOW_VERT,
        fragmentShader: FLOW_FRAG,
        uniforms: {
          uTime:  { value: 0 },
          uColor: { value: col },
          uAlpha: { value: alpha },
        },
        transparent:    true,
        depthWrite:     false,
        blending:       AdditiveBlending,
      })

      const line = new Line(geo, mat)
      this.flowGroup.add(line)
      this.entries.set(flow.id, { line, material: mat })
    }
  }

  /**
   * Synchronise the camera and world matrices with the latest GlobeEngine frame.
   * Must be called every animation frame before `render()`.
   */
  syncCamera(frame: GlobeFrameSnapshot): void {
    // Mirror globe world matrix (includes 23.4° axial tilt + OrbitControls rotation)
    this.flowGroup.matrix.fromArray(frame.worldMatrix)
    this.flowGroup.matrixWorldNeedsUpdate = true

    // Reconstruct camera from view matrix (matrixWorldInverse) and projection
    this.camera.matrixWorldInverse.fromArray(frame.viewMatrix)
    this.camera.matrixWorld.copy(this.camera.matrixWorldInverse).invert()
    this.camera.projectionMatrix.fromArray(frame.projectionMatrix)
    this.camera.projectionMatrixInverse.copy(this.camera.projectionMatrix).invert()
  }

  /** Update the animation clock on all flow shader materials. */
  setTime(t: number): void {
    for (const { material } of this.entries.values()) {
      material.uniforms.uTime.value = t
    }
  }

  /** Draw the current frame. */
  render(): void {
    this.renderer.render(this.scene, this.camera)
  }

  /** Resize the renderer and update camera aspect ratio. */
  resize(width: number, height: number): void {
    this.renderer.setSize(width, height, false)
    this.camera.aspect = width / height
    this.camera.updateProjectionMatrix()
  }

  /** Free all GPU resources. */
  dispose(): void {
    for (const { line, material } of this.entries.values()) {
      line.geometry.dispose()
      material.dispose()
    }
    this.entries.clear()
    this.renderer.dispose()
  }
}

// Re-export the Matrix4 helper used in FlowCanvas for convenience
export { Matrix4 }
