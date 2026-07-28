import { useEffect, useRef } from 'react'
import { useOverlayStore }    from '../../stores/overlayStore'
import { useEconomicStore }   from '../../stores/economicStore'
import { OVERLAYS }           from '../../overlays'
import { overlayEngine }      from '../../overlays/overlayEngine'
import { COUNTRIES }          from '../../data/countries'

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
 * OverlayCanvas — a transparent HTML5 canvas that sits on top of the Three.js
 * globe canvas and draws one colored dot per country at its geographic centre.
 *
 * The component reads from `overlayStore` and `economicStore` only — it never
 * calls the Globe Engine or modifies any globe internals.
 */
export default function OverlayCanvas() {
  const canvasRef   = useRef<HTMLCanvasElement>(null)
  const isVisible   = useOverlayStore((s) => s.isVisible)
  const activeMetric = useOverlayStore((s) => s.activeMetric)
  const econData    = useEconomicStore((s) => s.data)

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

    ctx.clearRect(0, 0, w, h)

    if (!isVisible) return

    const overlay = OVERLAYS[activeMetric]

    // The globe sphere occupies the largest circle that fits in the canvas,
    // scaled to match GlobeEngine's approximate rendering area.
    const globeRadius = Math.min(w, h) * 0.42
    const cx = w / 2
    const cy = h / 2

    for (const country of COUNTRIES) {
      const [lon, lat] = country.center
      const pos = project(lon, lat, cx, cy, globeRadius)
      if (!pos) continue

      const econ   = econData.get(country.isoCode) ?? null
      const result = overlayEngine.getColor(overlay, econ)

      const dotRadius = 3.5

      ctx.beginPath()
      ctx.arc(pos.x, pos.y, dotRadius, 0, Math.PI * 2)
      ctx.fillStyle = result.color
      ctx.globalAlpha = result.hasData ? 0.82 : 0.35
      ctx.fill()

      // Thin ring to distinguish overlapping dots
      ctx.strokeStyle = 'rgba(0,0,0,0.4)'
      ctx.lineWidth   = 0.5
      ctx.stroke()
    }

    ctx.globalAlpha = 1
  }, [isVisible, activeMetric, econData])

  // Re-render on resize
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ro = new ResizeObserver(() => {
      // Force a repaint by updating a dependency; simplest: trigger the draw
      // effect by toggling a state change is not possible without state.
      // Instead we clear and re-draw directly here.
      const ctx = canvas.getContext('2d')
      if (!ctx) return
      canvas.width  = canvas.offsetWidth
      canvas.height = canvas.offsetHeight
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      if (!useOverlayStore.getState().isVisible) return

      const { activeMetric } = useOverlayStore.getState()
      const overlay = OVERLAYS[activeMetric]
      const { data: econData } = useEconomicStore.getState()

      const w = canvas.width
      const h = canvas.height
      const globeRadius = Math.min(w, h) * 0.42
      const cx = w / 2
      const cy = h / 2

      for (const country of COUNTRIES) {
        const [lon, lat] = country.center
        const pos = project(lon, lat, cx, cy, globeRadius)
        if (!pos) continue

        const econ   = econData.get(country.isoCode) ?? null
        const result = overlayEngine.getColor(overlay, econ)

        ctx.beginPath()
        ctx.arc(pos.x, pos.y, 3.5, 0, Math.PI * 2)
        ctx.fillStyle   = result.color
        ctx.globalAlpha = result.hasData ? 0.82 : 0.35
        ctx.fill()
        ctx.strokeStyle = 'rgba(0,0,0,0.4)'
        ctx.lineWidth   = 0.5
        ctx.stroke()
      }

      ctx.globalAlpha = 1
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
