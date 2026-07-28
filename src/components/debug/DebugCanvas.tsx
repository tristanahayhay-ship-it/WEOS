import { useEffect, useRef, useState } from 'react'
import { Matrix4, Vector3 } from 'three'
import { useDebugStore } from '../../stores/debugStore'
import { useGlobeViewStore } from '../../stores/globeViewStore'
import { EARTH_RADIUS, projectLngLatToCartesian } from '../../utils/globe'
import { DEBUG_COUNTRIES } from '../../utils/debugCountries'

// ── Scratch objects (allocated once) ─────────────────────────────────────────
const _wm   = new Matrix4()
const _wi   = new Matrix4()
const _vm   = new Matrix4()
const _pm   = new Matrix4()
const _cam  = new Vector3()
const _lp   = new Vector3()
const _wp   = new Vector3()
const _cl   = new Vector3()
const _tc   = new Vector3()

interface PointPair {
  name:   string
  color:  string
  sprite: { x: number; y: number } | null  // Three.js ground truth
  canvas: { x: number; y: number } | null  // OverlayCanvas pipeline
  delta:  number | null
}

/**
 * Recomputes a screen point using the exact same pipeline as OverlayCanvas.
 * Uses the matrix snapshots stored in the globeViewStore frame.
 */
function computeCanvasPoint(
  lon: number,
  lat: number,
  w: number,
  h: number,
): { x: number; y: number } | null {
  const [x, y, z] = projectLngLatToCartesian(lon, lat, EARTH_RADIUS)
  _lp.set(x, y, z)

  _cl.copy(_cam).applyMatrix4(_wi)
  _tc.copy(_cl).sub(_lp)
  if (_lp.dot(_tc) <= 0) return null

  _wp.copy(_lp).applyMatrix4(_wm)
  _wp.applyMatrix4(_vm)
  _wp.applyMatrix4(_pm)
  if (_wp.z < -1 || _wp.z > 1) return null

  return { x: ((_wp.x + 1) * w) / 2, y: ((1 - _wp.y) * h) / 2 }
}

/** Draw a crosshair at (cx, cy) with the given colour. */
function drawCrosshair(
  ctx: CanvasRenderingContext2D,
  cx: number,
  cy: number,
  color: string,
  size: number,
) {
  ctx.strokeStyle = color
  ctx.lineWidth   = 2
  ctx.beginPath()
  ctx.moveTo(cx - size, cy)
  ctx.lineTo(cx + size, cy)
  ctx.moveTo(cx, cy - size)
  ctx.lineTo(cx, cy + size)
  ctx.stroke()
}

/** Draw a hollow circle at (cx, cy). */
function drawCircle(
  ctx: CanvasRenderingContext2D,
  cx: number,
  cy: number,
  color: string,
  r: number,
) {
  ctx.strokeStyle = color
  ctx.lineWidth   = 2
  ctx.beginPath()
  ctx.arc(cx, cy, r, 0, Math.PI * 2)
  ctx.stroke()
}

// ─────────────────────────────────────────────────────────────────────────────

interface DebugRow extends PointPair {}

/**
 * DebugCanvas — overlay that:
 * 1. Draws crosshairs at the Three.js ground-truth sprite positions (solid colour).
 * 2. Draws circles at the OverlayCanvas-pipeline computed positions (white).
 * 3. Renders an HTML table with live pixel deltas.
 *
 * Activated by pressing Shift+D.
 */
export default function DebugCanvas() {
  const enabled      = useDebugStore((s) => s.enabled)
  const canvasRef    = useRef<HTMLCanvasElement>(null)
  const [rows, setRows] = useState<DebugRow[]>([])

  useEffect(() => {
    if (!enabled) return

    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let rafId = 0
    let maxDeltaEver = 0

    const syncSize = () => {
      const { offsetWidth: ow, offsetHeight: oh } = canvas
      if (canvas.width !== ow || canvas.height !== oh) {
        canvas.width  = ow
        canvas.height = oh
      }
    }

    const drawFrame = () => {
      syncSize()
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      const frame = useGlobeViewStore.getState().frame
      if (!frame) {
        rafId = requestAnimationFrame(drawFrame)
        return
      }

      const w = canvas.width
      const h = canvas.height

      // Populate scratch matrices from frame snapshot.
      _wm.fromArray(frame.worldMatrix)
      _wi.copy(_wm).invert()
      _vm.fromArray(frame.viewMatrix)
      _pm.fromArray(frame.projectionMatrix)
      _cam.fromArray(frame.cameraWorldPosition)

      const pairs: DebugRow[] = DEBUG_COUNTRIES.map((c, i) => {
        const sprite = frame.spritePoints[i]
        const canvas_ = computeCanvasPoint(c.lon, c.lat, w, h)

        let delta: number | null = null
        if (sprite && canvas_) {
          const dx = sprite.x - canvas_.x
          const dy = sprite.y - canvas_.y
          delta = Math.sqrt(dx * dx + dy * dy)
          if (delta > maxDeltaEver) maxDeltaEver = delta
        }

        return { name: c.name, color: c.color, sprite, canvas: canvas_, delta }
      })

      // ── Draw Three.js ground-truth markers (crosshair) ───────────────────
      for (const { sprite, color } of pairs) {
        if (sprite) drawCrosshair(ctx, sprite.x, sprite.y, color, 12)
      }

      // ── Draw OverlayCanvas-pipeline markers (circle) ─────────────────────
      for (const { canvas: cp, color } of pairs) {
        if (cp) drawCircle(ctx, cp.x, cp.y, '#ffffff', 8)
        if (cp) drawCircle(ctx, cp.x, cp.y, color, 6)
      }

      setRows(pairs)
      rafId = requestAnimationFrame(drawFrame)
    }

    drawFrame()
    return () => cancelAnimationFrame(rafId)
  }, [enabled])

  if (!enabled) return null

  return (
    <>
      {/* Transparent canvas for drawing markers */}
      <canvas
        ref={canvasRef}
        className="pointer-events-none absolute inset-0 w-full h-full"
        style={{ zIndex: 20 }}
        aria-hidden="true"
      />

      {/* Data table */}
      <div
        className="pointer-events-none absolute right-4 top-16 rounded-md border text-xs"
        style={{
          background: 'rgba(5, 8, 18, 0.92)',
          borderColor: 'rgba(121, 196, 255, 0.4)',
          backdropFilter: 'blur(8px)',
          color: '#d9efff',
          zIndex: 21,
          minWidth: 340,
        }}
      >
        {/* Header */}
        <div
          className="px-3 py-2 font-bold tracking-widest uppercase text-[10px] border-b"
          style={{ borderColor: 'rgba(121, 196, 255, 0.25)', color: '#79c4ff' }}
        >
          Sprite ↔ OverlayCanvas Comparison
          <span className="ml-2 normal-case font-normal text-[9px]" style={{ color: '#8899aa' }}>
            ╋ = Three.js · ○ = Canvas  (Shift+D to hide)
          </span>
        </div>

        {/* Rows */}
        <table className="w-full border-collapse">
          <thead>
            <tr
              className="text-[9px] uppercase tracking-wider"
              style={{ color: '#4d7a99', borderBottom: '1px solid rgba(121,196,255,0.15)' }}
            >
              <th className="px-3 py-1 text-left">Country</th>
              <th className="px-2 py-1 text-right">Sprite (px)</th>
              <th className="px-2 py-1 text-right">Canvas (px)</th>
              <th className="px-2 py-1 text-right">Δ</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => {
              const ok     = r.delta !== null && r.delta < 1
              const deltaStr = r.delta !== null
                ? r.delta < 0.001 ? '<0.001' : r.delta.toFixed(3)
                : '—'
              return (
                <tr
                  key={r.name}
                  className="border-t"
                  style={{ borderColor: 'rgba(121,196,255,0.08)' }}
                >
                  <td className="px-3 py-1 flex items-center gap-1.5">
                    <span
                      className="inline-block rounded-full"
                      style={{ width: 8, height: 8, background: r.color, flexShrink: 0 }}
                    />
                    {r.name}
                  </td>
                  <td className="px-2 py-1 text-right font-mono" style={{ color: '#8899aa' }}>
                    {r.sprite ? `${r.sprite.x.toFixed(1)},${r.sprite.y.toFixed(1)}` : 'hidden'}
                  </td>
                  <td className="px-2 py-1 text-right font-mono" style={{ color: '#8899aa' }}>
                    {r.canvas ? `${r.canvas.x.toFixed(1)},${r.canvas.y.toFixed(1)}` : 'hidden'}
                  </td>
                  <td
                    className="px-2 py-1 text-right font-mono font-bold"
                    style={{ color: r.delta === null ? '#4d7a99' : ok ? '#44ff88' : '#ff4444' }}
                  >
                    {deltaStr}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>

        {/* Verdict */}
        {rows.length > 0 && (
          <div
            className="px-3 py-2 border-t text-[10px] font-mono"
            style={{ borderColor: 'rgba(121,196,255,0.15)' }}
          >
            {(() => {
              const visibleDeltas = rows.filter((r) => r.delta !== null)
              if (visibleDeltas.length === 0) return (
                <span style={{ color: '#4d7a99' }}>No visible markers in current view.</span>
              )
              const maxD = Math.max(...visibleDeltas.map((r) => r.delta!))
              const allOk = maxD < 1
              return (
                <span style={{ color: allOk ? '#44ff88' : '#ff4444' }}>
                  {allOk ? '✅' : '❌'} max Δ this frame: {maxD < 0.001 ? '<0.001' : maxD.toFixed(3)} px
                  {allOk ? ' — projection confirmed correct' : ' — DRIFT DETECTED'}
                </span>
              )
            })()}
          </div>
        )}
      </div>
    </>
  )
}
