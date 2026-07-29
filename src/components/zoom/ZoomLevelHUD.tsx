import { useZoomStore } from '../../stores/zoomStore'
import { ZOOM_LEVEL_LIST } from '../../zoom/levels'
import type { ZoomLevelId } from '../../zoom/types'

/**
 * ZoomLevelHUD — compact overlay widget that shows the current zoom level and
 * lets the user jump directly to any level via the level ladder.
 *
 * Reads from / writes to `zoomStore` only.  No direct access to GlobeEngine
 * internals or other stores.
 */
export default function ZoomLevelHUD() {
  const activeLevel = useZoomStore((s) => s.activeLevel)
  const goToLevel   = useZoomStore((s) => s.goToLevel)
  const zoomIn      = useZoomStore((s) => s.zoomIn)
  const zoomOut     = useZoomStore((s) => s.zoomOut)
  const transition  = useZoomStore((s) => s.transition)

  const currentMeta = ZOOM_LEVEL_LIST[activeLevel]

  return (
    <div
      className="pointer-events-auto absolute flex flex-col gap-1"
      style={{
        right: 12,
        top: '50%',
        transform: 'translateY(-50%)',
        zIndex: 20,
      }}
      aria-label="Zoom level navigator"
    >
      {/* Zoom-out button — moves toward Global (level 0) */}
      <button
        type="button"
        onClick={zoomOut}
        disabled={activeLevel === 0}
        title="Zoom out one level"
        style={buttonStyle(activeLevel === 0)}
      >
        ▲
      </button>

      {/* Level ladder — click a node to jump directly */}
      <div
        className="flex flex-col gap-[3px] items-end"
        style={{
          background: 'rgba(8,13,24,0.78)',
          border: '1px solid rgba(121,196,255,0.18)',
          borderRadius: 6,
          padding: '6px 8px',
          backdropFilter: 'blur(8px)',
        }}
      >
        {ZOOM_LEVEL_LIST.map((level) => {
          const isActive = level.id === activeLevel
          return (
            <button
              key={level.id}
              type="button"
              onClick={() => goToLevel(level.id as ZoomLevelId)}
              title={level.label}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: '2px 4px',
                borderRadius: 3,
              }}
            >
              {/* Indicator dot */}
              <span
                style={{
                  display: 'inline-block',
                  width: isActive ? 8 : 5,
                  height: isActive ? 8 : 5,
                  borderRadius: '50%',
                  background: isActive ? '#79c4ff' : 'rgba(121,196,255,0.3)',
                  flexShrink: 0,
                  transition: 'all 0.2s ease',
                  boxShadow: isActive ? '0 0 6px #79c4ff' : 'none',
                }}
              />
              <span
                style={{
                  fontSize: 9,
                  letterSpacing: '0.15em',
                  textTransform: 'uppercase',
                  color: isActive ? '#d9efff' : 'rgba(121,196,255,0.4)',
                  fontWeight: isActive ? 700 : 400,
                  transition: 'color 0.2s ease',
                }}
              >
                {level.name}
              </span>
            </button>
          )
        })}
      </div>

      {/* Zoom-in button — moves toward Corporation (level 6) */}
      <button
        type="button"
        onClick={zoomIn}
        disabled={activeLevel === ZOOM_LEVEL_LIST.length - 1}
        title="Zoom in one level"
        style={buttonStyle(activeLevel === ZOOM_LEVEL_LIST.length - 1)}
      >
        ▼
      </button>

      {/* Current-level label */}
      <div
        style={{
          marginTop: 4,
          padding: '3px 6px',
          background: 'rgba(8,13,24,0.78)',
          border: '1px solid rgba(121,196,255,0.18)',
          borderRadius: 4,
          backdropFilter: 'blur(8px)',
          textAlign: 'right',
        }}
      >
        <span
          style={{
            fontSize: 9,
            letterSpacing: '0.2em',
            textTransform: 'uppercase',
            color: transition?.isTransitioning ? '#f59e0b' : '#79c4ff',
          }}
        >
          {transition?.isTransitioning ? 'MOVING…' : currentMeta.name}
        </span>
      </div>
    </div>
  )
}

function buttonStyle(disabled: boolean): React.CSSProperties {
  return {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: 28,
    height: 28,
    background: disabled ? 'rgba(8,13,24,0.4)' : 'rgba(8,13,24,0.78)',
    border: `1px solid ${disabled ? 'rgba(121,196,255,0.08)' : 'rgba(121,196,255,0.25)'}`,
    borderRadius: 4,
    color: disabled ? 'rgba(121,196,255,0.2)' : '#79c4ff',
    fontSize: 11,
    cursor: disabled ? 'not-allowed' : 'pointer',
    backdropFilter: 'blur(8px)',
    alignSelf: 'flex-end',
  }
}
