import { useEffect, useMemo, useRef } from 'react'
import { useOverlayStore }    from '../../stores/overlayStore'
import { useRealtimeStore } from '../../stores/realtimeStore'
import { OVERLAYS }           from '../../overlays'
import { overlayEngine }      from '../../overlays/overlayEngine'
import { COUNTRIES }          from '../../data/countries'
import { ECONOMIC_DATA_BY_ISO } from '../../data/economicData'
import { EARTH_RADIUS, projectLngLatToCartesian } from '../../utils/globe'
import { useGlobeViewStore } from '../../stores/globeViewStore'
import type { OverlayMetric } from '../../overlays/types'
import type { CountryEconomicData } from '../../types/country'
import { Matrix4, Vector3 } from 'three'
import { buildRealtimeEconomicMap } from '../../utils/realtimeEconomic'

/**
 * Dot radius in canvas pixels for each country marker.
 */
const DOT_RADIUS = 3.5
const OVERLAY_FADE_MS = 220

// Re-usable singletons — allocated once, mutated in-place each frame.
const worldMatrix   = new Matrix4()
const worldInverse  = new Matrix4()
// View matrix (camera.matrixWorldInverse snapshot) and projection matrix stored
// separately so that the projection step mirrors what Vector3.project(camera)
// does internally: applyMatrix4(matrixWorldInverse) → applyMatrix4(projectionMatrix).
const viewMatrix    = new Matrix4()
const projMatrix    = new Matrix4()
const cameraWorldPos  = new Vector3()
const localPoint      = new Vector3()
const worldPoint      = new Vector3()
const cameraLocalPos  = new Vector3()
const toCamera        = new Vector3()

interface ProjectionContext {
  worldMatrix:  Matrix4
  worldInverse: Matrix4
  /** Camera view matrix (camera.matrixWorldInverse). */
  viewMatrix:   Matrix4
  /** Camera projection matrix. */
  projMatrix:   Matrix4
  cameraWorldPos: Vector3
}

/**
 * Convert geographic coordinates to a screen point using the current
 * GlobeEngine world/camera matrices.
 *
 * The projection pipeline mirrors Vector3.project(camera) exactly:
 *   local → world (worldMatrix)
 *   world → view  (viewMatrix  = camera.matrixWorldInverse)
 *   view  → NDC   (projMatrix  = camera.projectionMatrix, includes w-divide)
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

  // Back side of the sphere from the active camera view — skip.
  cameraLocalPos.copy(projection.cameraWorldPos).applyMatrix4(projection.worldInverse)
  toCamera.copy(cameraLocalPos).sub(localPoint)
  if (localPoint.dot(toCamera) <= 0) return null

  // local → world → view (applyMatrix4 handles the homogeneous w-divide).
  worldPoint.copy(localPoint).applyMatrix4(projection.worldMatrix)
  worldPoint.applyMatrix4(projection.viewMatrix)
  worldPoint.applyMatrix4(projection.projMatrix)
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
  viewMatrix.fromArray(frame.viewMatrix)
  projMatrix.fromArray(frame.projectionMatrix)
  cameraWorldPos.fromArray(frame.cameraWorldPosition)

  const projection: ProjectionContext = {
    worldMatrix,
    worldInverse,
    viewMatrix,
    projMatrix,
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
 * The component reads from `overlayStore` and `realtimeStore` only — it never
 * calls the Globe Engine or modifies any globe internals.
 */
export default function OverlayCanvas() {
  const canvasRef    = useRef<HTMLCanvasElement>(null)
  const isVisible    = useOverlayStore((s) => s.isVisible)
  const activeMetric = useOverlayStore((s) => s.activeMetric)
  const records      = useRealtimeStore((s) => s.records)
  const econData = useMemo(
    () => buildRealtimeEconomicMap(records, ECONOMIC_DATA_BY_ISO),
    [records],
  )
  const econDataRef = useRef<ReadonlyMap<string, CountryEconomicData>>(econData)
  const econDataVersionRef = useRef(0)
  const hideAfterRef = useRef(0)
  const lastDrawRef = useRef({
    frameVersion: -1,
    dataVersion: -1,
    metric: activeMetric,
    width: 0,
    height: 0,
    cleared: false,
  })

  useEffect(() => {
    econDataRef.current = econData
    econDataVersionRef.current += 1
  }, [econData])

  useEffect(() => {
    hideAfterRef.current = isVisible ? 0 : performance.now() + OVERLAY_FADE_MS
    if (isVisible) {
      lastDrawRef.current.frameVersion = -1
      lastDrawRef.current.cleared = false
    }
  }, [isVisible])

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

      const width = canvas.width
      const height = canvas.height
      const {
        isVisible: visible,
        activeMetric: metric,
      } = useOverlayStore.getState()
      const {
        frame,
        frameVersion,
      } = useGlobeViewStore.getState()
      const keepLastFrame = visible || performance.now() < hideAfterRef.current
      const sizeChanged = width !== lastDrawRef.current.width || height !== lastDrawRef.current.height

      if (!keepLastFrame || !frame || width === 0 || height === 0) {
        if (!lastDrawRef.current.cleared) {
          ctx.clearRect(0, 0, width, height)
          lastDrawRef.current.cleared = true
        }
      } else {
        const shouldRedraw = (
          sizeChanged
          || frameVersion !== lastDrawRef.current.frameVersion
          || metric !== lastDrawRef.current.metric
          || econDataVersionRef.current !== lastDrawRef.current.dataVersion
        )

        if (shouldRedraw) {
          lastDrawRef.current = {
            frameVersion,
            dataVersion: econDataVersionRef.current,
            metric,
            width,
            height,
            cleared: false,
          }
        }

        if (shouldRedraw && visible) {
          drawDots(ctx, metric, econDataRef.current)
        }
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

    if (!isVisible) return

    drawDots(ctx, activeMetric, econData)
  }, [isVisible, activeMetric, econData])

  return (
    <canvas
      ref={canvasRef}
      className="pointer-events-none absolute inset-0 w-full h-full"
      style={{
        zIndex: 5,
        opacity: isVisible ? 1 : 0,
        transition: `opacity ${OVERLAY_FADE_MS}ms ease`,
      }}
      aria-hidden="true"
    />
  )
}
