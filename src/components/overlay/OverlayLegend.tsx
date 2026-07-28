import { useOverlayStore } from '../../stores/overlayStore'
import { OVERLAYS }        from '../../overlays'

/**
 * OverlayLegend — explains the active color scale to the user.
 *
 * Rendered only when the overlay is visible.
 * Reads `overlayStore` only — no Globe Engine internals are accessed.
 */
export default function OverlayLegend() {
  const isVisible    = useOverlayStore((s) => s.isVisible)
  const activeMetric = useOverlayStore((s) => s.activeMetric)

  if (!isVisible) return null

  const overlay = OVERLAYS[activeMetric]
  const stops   = overlay.colorScale

  // Build the CSS gradient string from the overlay color stops
  const gradientStops = stops
    .map((s) => `${s.color} ${(s.position * 100).toFixed(0)}%`)
    .join(', ')
  const gradient = `linear-gradient(to right, ${gradientStops})`

  return (
    <div
      className="absolute flex flex-col gap-1.5 rounded p-3"
      style={{
        bottom: 64,
        right: 12,
        zIndex: 15,
        minWidth: 200,
        maxWidth: 240,
        background: 'rgba(8,13,24,0.88)',
        border: '1px solid rgba(121,196,255,0.18)',
        backdropFilter: 'blur(8px)',
      }}
      aria-label="Overlay legend"
    >
      {/* Header */}
      <div className="flex flex-col gap-0.5">
        <span
          className="text-[9px] tracking-[0.22em] uppercase"
          style={{ color: 'rgba(121,196,255,0.5)' }}
        >
          Legend
        </span>
        <span className="text-xs font-semibold" style={{ color: '#d9efff' }}>
          {overlay.name}
        </span>
        <span className="text-[10px]" style={{ color: 'rgba(217,239,255,0.5)' }}>
          {overlay.description}
        </span>
      </div>

      {/* Gradient bar */}
      <div
        style={{
          height: 10,
          borderRadius: 5,
          background: gradient,
        }}
        aria-hidden="true"
      />

      {/* Stop labels */}
      <div className="flex justify-between">
        {stops
          .filter((_, i) => i === 0 || i === Math.floor(stops.length / 2) || i === stops.length - 1)
          .map((s) => (
            <span
              key={s.position}
              className="text-[9px]"
              style={{ color: 'rgba(217,239,255,0.55)' }}
            >
              {s.label}
            </span>
          ))}
      </div>

      {/* No data indicator */}
      <div className="flex items-center gap-2 mt-0.5">
        <span
          style={{
            display: 'inline-block',
            width: 10,
            height: 10,
            borderRadius: 2,
            background: overlay.noDataColor,
            border: '1px solid rgba(121,196,255,0.2)',
          }}
        />
        <span className="text-[9px]" style={{ color: 'rgba(217,239,255,0.45)' }}>
          No Data
        </span>
      </div>
    </div>
  )
}
