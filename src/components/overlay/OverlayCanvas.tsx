import { useEffect, useRef } from 'react'
import { useOverlayStore }    from '../../stores/overlayStore'
import { useEconomicStore }   from '../../stores/economicStore'
import { OVERLAYS }           from '../../overlays'
import { overlayEngine }      from '../../overlays/overlayEngine'
import { COUNTRIES }          from '../../data/countries'
import { EARTH_RADIUS, projectLngLatToCartesian } from '../../utils/globe'
import { useGlobeViewStore } from '../../stores/globeViewStore'
import type { OverlayMetric } from '../../overlays/types'
import type { CountryEconomicData } from '../../types/country'
import { Matrix4, Vector3 } from 'three'

/**
 * Dot radius in canvas pixels for each country marker.
 */
const DOT_RADIUS = 3.5

const worldMatrix = new Matrix4()
const worldInverse = new Matrix4()
const viewMatrix = new Matrix4()
const viewProjectionMatrix = new Matrix4()
const cameraWorldPos = new Vector3()
const localPoint = new Vector3()
const worldPoint = new Vector3()
const cameraLocalPos = new Vector3()
const toCamera = new Vector3()

interface ProjectionContext {
  worldMatrix: Matrix4
  worldInverse: Matrix4
  viewProjectionMatrix: Matrix4
  cameraWorldPos: Vector3
}

/**
 * Convert geographic coordinates to a screen point using the current
 * GlobeEngine world/camera matrices.
 */
function project(
  lon: number,
  lat: number,
  width: number,
  height: number,
  projection: ProjectionContext,
): { x: number; y: number } | null {
  const [x, y, z] = projectLngLatToCartesian(lon, lat, EARTH_RADIUS)
  localPoint.set(x, y, z)

  // Back side of the sphere from the active camera view — skip
  cameraLocalPos.copy(projection.cameraWorldPos).applyMatrix4(projection.worldInverse)
  toCamera.copy(cameraLocalPos).sub(localPoint)
  if (localPoint.dot(toCamera) <= 0) return null

  worldPoint
    .copy(localPoint)
    .applyMatrix4(projection.worldMatrix)
    .applyMatrix4(projection.viewProjectionMatrix)
  if (worldPoint.z < -1 || worldPoint.z > 1) return null

  return { x: ((worldPoint.x + 1) * width) / 2, y: ((1 - worldPoint.y) * height) / 2 }
}

/**
 * Draw all country overlay dots onto `ctx` using the given metric and data.
 * Extracted to avoid duplicating the drawing logic in two effect callbacks.
 */
function drawDots(
  ctx: CanvasRenderingContext2D,
  activeMetric: OverlayMetric,
  econData: ReadonlyMap<string, CountryEconomicData>,
): void {
  const w = ctx.canvas.width
  const h = ctx.canvas.height

  ctx.clearRect(0, 0, w, h)

  const frame = useGlobeViewStore.getState().frame
  if (!frame) return

  worldMatrix.fromArray(frame.worldMatrix)
  worldInverse.copy(worldMatrix).invert()
  viewProjectionMatrix.fromArray(frame.projectionMatrix).multiply(viewMatrix.fromArray(frame.viewMatrix))
  cameraWorldPos.fromArray(frame.cameraWorldPosition)

  const projection: ProjectionContext = {
    worldMatrix,
    worldInverse,
    viewProjectionMatrix,
    cameraWorldPos,
  }

  const overlay     = OVERLAYS[activeMetric]

  for (const country of COUNTRIES) {
    const [lon, lat] = country.center
    const pos = project(lon, lat, w, h, projection)
    if (!pos) continue

    const econ   = econData.get(country.isoCode) ?? null
    const result = overlayEngine.getColor(overlay, econ)

    ctx.beginPath()
    ctx.arc(pos.x, pos.y, DOT_RADIUS, 0, Math.PI * 2)
    ctx.fillStyle   = result.color
    ctx.globalAlpha = result.hasData ? 0.82 : 0.35
    ctx.fill()

    // Thin ring to distinguish overlapping dots
    ctx.strokeStyle = 'rgba(0,0,0,0.4)'
    ctx.lineWidth   = 0.5
    ctx.stroke()
  }

  ctx.globalAlpha = 1
}

/**
 * OverlayCanvas — a transparent HTML5 canvas that sits on top of the Three.js
 * globe canvas and draws one colored dot per country at its geographic centre.
 *
 * The component reads from `overlayStore` and `economicStore` only — it never
 * calls the Globe Engine or modifies any globe internals.
 */
export default function OverlayCanvas() {
  const canvasRef    = useRef<HTMLCanvasElement>(null)
  const isVisible    = useOverlayStore((s) => s.isVisible)
  const activeMetric = useOverlayStore((s) => s.activeMetric)
  const econData     = useEconomicStore((s) => s.data)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let rafId = 0

    const syncSize = () => {
      const { offsetWidth, offsetHeight } = canvas
      if (canvas.width !== offsetWidth || canvas.height !== offsetHeight) {
        canvas.width = offsetWidth
        canvas.height = offsetHeight
      }
    }

    const drawFrame = () => {
      syncSize()

      const { isVisible: visible, activeMetric: metric } = useOverlayStore.getState()
      if (!visible) {
        ctx.clearRect(0, 0, canvas.width, canvas.height)
      } else {
        const { data } = useEconomicStore.getState()
        drawDots(ctx, metric, data)
      }

      rafId = window.requestAnimationFrame(drawFrame)
    }

    drawFrame()

    const ro = new ResizeObserver(syncSize)
    ro.observe(canvas)

    return () => {
      window.cancelAnimationFrame(rafId)
      ro.disconnect()
    }
  }, [])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas?.getContext('2d')
    if (!ctx) return

    if (!isVisible) {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      return
    }

    drawDots(ctx, activeMetric, econData)
  }, [isVisible, activeMetric, econData])

  return (
    <canvas
      ref={canvasRef}
      className="pointer-events-none absolute inset-0 w-full h-full"
      style={{ zIndex: 5 }}
      aria-hidden="true"
    />
  )
}
