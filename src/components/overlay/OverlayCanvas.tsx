import { useEffect, useRef } from 'react'
import { useOverlayStore }    from '../../stores/overlayStore'
import { useEconomicStore }   from '../../stores/economicStore'
import { OVERLAYS }           from '../../overlays'
import { overlayEngine }      from '../../overlays/overlayEngine'
import { COUNTRIES }          from '../../data/countries'
import type { OverlayMetric } from '../../overlays/types'
import type { CountryEconomicData } from '../../types/country'

/**
 * Dot radius in canvas pixels for each country marker.
 */
const DOT_RADIUS = 3.5

/**
 * Fraction of Math.min(width, height) used as the projected globe radius.
 * Must approximate GlobeEngine's sphere rendering area (the globe sphere fills
 * roughly 84 % of the shorter canvas dimension).
 */
const GLOBE_RADIUS_FACTOR = 0.42

/**
 * Convert geographic coordinates to an approximate screen position.
 *
 * The globe is a unit sphere rendered with a Z-rotation of 23.4° (axial tilt)
 * and an OrbitControls camera initially positioned on the +Z axis.
 * This function projects lon/lat onto the visible hemisphere using an
 * orthographic approximation, which is accurate for the default orientation
 * and degrades gracefully as the user rotates the globe.
 *
 * Returns `null` for points on the hidden (back) hemisphere.
 */
function project(
  lon: number,
  lat: number,
  cx: number,
  cy: number,
  radius: number,
): { x: number; y: number } | null {
  const TILT = (23.4 * Math.PI) / 180

  const lonRad = (lon * Math.PI) / 180
  const latRad = (lat * Math.PI) / 180

  // 3-D Cartesian on unit sphere (globe-local axes: x=right, y=up, z=toward camera)
  const x0 = Math.cos(latRad) * Math.sin(lonRad)
  const y0 = Math.sin(latRad)
  const z0 = Math.cos(latRad) * Math.cos(lonRad)

  // Apply axial tilt (Z-rotation of 23.4°)
  const x1 = x0 * Math.cos(TILT) - y0 * Math.sin(TILT)
  const y1 = x0 * Math.sin(TILT) + y0 * Math.cos(TILT)
  const z1 = z0

  // Back hemisphere — skip
  if (z1 < 0) return null

  return {
    x: cx + x1 * radius,
    y: cy - y1 * radius,
  }
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

  const overlay     = OVERLAYS[activeMetric]
  const globeRadius = Math.min(w, h) * GLOBE_RADIUS_FACTOR
  const cx          = w / 2
  const cy          = h / 2

  for (const country of COUNTRIES) {
    const [lon, lat] = country.center
    const pos = project(lon, lat, cx, cy, globeRadius)
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

  // Re-draw whenever overlay state or economic data changes
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Sync canvas logical size with CSS size
    const { offsetWidth: w, offsetHeight: h } = canvas
    if (canvas.width !== w || canvas.height !== h) {
      canvas.width  = w
      canvas.height = h
    }

    if (!isVisible) {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      return
    }

    drawDots(ctx, activeMetric, econData)
  }, [isVisible, activeMetric, econData])

  // Re-draw on container resize
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ro = new ResizeObserver(() => {
      const ctx = canvas.getContext('2d')
      if (!ctx) return

      canvas.width  = canvas.offsetWidth
      canvas.height = canvas.offsetHeight

      const { isVisible: visible, activeMetric: metric } = useOverlayStore.getState()
      if (!visible) {
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        return
      }

      const { data } = useEconomicStore.getState()
      drawDots(ctx, metric, data)
    })

    ro.observe(canvas)
    return () => ro.disconnect()
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="pointer-events-none absolute inset-0 w-full h-full"
      style={{ zIndex: 5 }}
      aria-hidden="true"
    />
  )
}

