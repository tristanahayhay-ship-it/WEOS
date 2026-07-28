import { useOverlayStore } from '../../stores/overlayStore'
import { OVERLAYS, OVERLAY_LIST } from '../../overlays'
import type { OverlayMetric } from '../../overlays/types'

/**
 * OverlayPanel — floating control panel that lets the user:
 *  - Toggle the overlay layer on / off
 *  - Switch between GDP, Population, Inflation, and Interest Rate overlays
 *
 * Reads from and writes to `overlayStore` only.  No Globe Engine internals
 * are accessed or modified.
 */
export default function OverlayPanel() {
  const isVisible    = useOverlayStore((s) => s.isVisible)
  const activeMetric = useOverlayStore((s) => s.activeMetric)
  const toggle       = useOverlayStore((s) => s.toggleVisibility)
  const setMetric    = useOverlayStore((s) => s.setActiveMetric)

  const activeOverlay = OVERLAYS[activeMetric]

  return (
    <div
      className="absolute flex flex-col gap-2"
      style={{
        bottom: 64,
        left: 12,
        zIndex: 15,
        minWidth: 180,
      }}
      aria-label="Economic overlay controls"
    >
      {/* Toggle button */}
      <button
        type="button"
        onClick={toggle}
        className="flex items-center gap-2 px-3 py-2 rounded text-xs font-medium tracking-wide transition-all"
        style={{
          background: isVisible
            ? 'rgba(59,130,246,0.9)'
            : 'rgba(8,13,24,0.85)',
          color: isVisible ? '#fff' : 'rgba(121,196,255,0.8)',
          border: `1px solid ${isVisible ? 'rgba(59,130,246,0.6)' : 'rgba(121,196,255,0.25)'}`,
          backdropFilter: 'blur(8px)',
        }}
        aria-pressed={isVisible}
      >
        <span
          style={{
            display: 'inline-block',
            width: 8,
            height: 8,
            borderRadius: '50%',
            background: isVisible ? '#fff' : 'rgba(121,196,255,0.5)',
          }}
        />
        OVERLAY {isVisible ? 'ON' : 'OFF'}
      </button>

      {/* Metric selector — shown only when overlay is active */}
      {isVisible && (
        <div
          className="flex flex-col gap-1 rounded p-2"
          style={{
            background: 'rgba(8,13,24,0.88)',
            border: '1px solid rgba(121,196,255,0.18)',
            backdropFilter: 'blur(8px)',
          }}
        >
          <span
            className="text-[9px] tracking-[0.22em] uppercase mb-1"
            style={{ color: 'rgba(121,196,255,0.5)' }}
          >
            Active Overlay
          </span>
          {OVERLAY_LIST.map((ov) => {
            const isActive = ov.id === activeMetric
            return (
              <button
                key={ov.id}
                type="button"
                onClick={() => setMetric(ov.id as OverlayMetric)}
                className="flex items-center gap-2 px-2 py-1.5 rounded text-xs text-left transition-all"
                style={{
                  background: isActive
                    ? 'rgba(59,130,246,0.22)'
                    : 'transparent',
                  color: isActive
                    ? activeOverlay.colorScale[activeOverlay.colorScale.length - 1].color
                    : 'rgba(217,239,255,0.65)',
                  border: `1px solid ${isActive ? 'rgba(59,130,246,0.4)' : 'transparent'}`,
                }}
                aria-pressed={isActive}
              >
                <span
                  style={{
                    display: 'inline-block',
                    width: 8,
                    height: 8,
                    borderRadius: 2,
                    background: ov.colorScale[ov.colorScale.length - 1].color,
                    flexShrink: 0,
                  }}
                />
                {ov.name}
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}
