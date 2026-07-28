import { useFlowStore, FLOW_TYPE_CONFIG } from '../../stores/flowStore'
import type { FlowType } from '../../flows/types'

const FLOW_TYPES: FlowType[] = ['trade', 'investment', 'debt', 'aid']

/**
 * FlowPanel — floating control panel for the Capital Flow layer.
 *
 * Lets the user:
 *  - Toggle the entire flow layer on / off
 *  - Enable or disable individual flow types (trade / investment / debt / aid)
 *
 * Reads from and writes to `flowStore` only.
 * No Globe Engine internals are accessed or modified.
 */
export default function FlowPanel() {
  const isVisible    = useFlowStore((s) => s.isVisible)
  const visibleTypes = useFlowStore((s) => s.visibleTypes)
  const toggle       = useFlowStore((s) => s.toggleVisibility)
  const toggleType   = useFlowStore((s) => s.toggleFlowType)

  return (
    <div
      className="absolute flex flex-col gap-2"
      style={{
        bottom: 64,
        right: 12,
        zIndex: 15,
        minWidth: 180,
      }}
      aria-label="Capital flow controls"
    >
      {/* Master toggle */}
      <button
        type="button"
        onClick={toggle}
        className="flex items-center gap-2 px-3 py-2 rounded text-xs font-medium tracking-wide transition-all"
        style={{
          background:    isVisible ? 'rgba(99,102,241,0.9)' : 'rgba(8,13,24,0.85)',
          color:         isVisible ? '#fff' : 'rgba(121,196,255,0.8)',
          border:       `1px solid ${isVisible ? 'rgba(99,102,241,0.6)' : 'rgba(121,196,255,0.25)'}`,
          backdropFilter: 'blur(8px)',
        }}
        aria-pressed={isVisible}
      >
        <span
          style={{
            display:      'inline-block',
            width:        8,
            height:       8,
            borderRadius: '50%',
            background:   isVisible ? '#fff' : 'rgba(121,196,255,0.5)',
          }}
        />
        FLOWS {isVisible ? 'ON' : 'OFF'}
      </button>

      {/* Per-type toggles — shown only when layer is active */}
      {isVisible && (
        <div
          className="flex flex-col gap-1 rounded p-2"
          style={{
            background:     'rgba(8,13,24,0.88)',
            border:         '1px solid rgba(121,196,255,0.18)',
            backdropFilter: 'blur(8px)',
          }}
        >
          <span
            className="text-[9px] tracking-[0.22em] uppercase mb-1"
            style={{ color: 'rgba(121,196,255,0.5)' }}
          >
            Flow Types
          </span>

          {FLOW_TYPES.map((type) => {
            const cfg      = FLOW_TYPE_CONFIG[type]
            const active   = visibleTypes.includes(type)
            return (
              <button
                key={type}
                type="button"
                onClick={() => toggleType(type)}
                className="flex items-center gap-2 px-2 py-1.5 rounded text-xs text-left transition-all"
                style={{
                  background: active
                    ? `${cfg.color}22`
                    : 'transparent',
                  color: active
                    ? cfg.color
                    : 'rgba(121,196,255,0.45)',
                  border: `1px solid ${active ? cfg.color + '55' : 'transparent'}`,
                }}
                aria-pressed={active}
              >
                <span
                  style={{
                    display:      'inline-block',
                    width:        8,
                    height:       8,
                    borderRadius: '50%',
                    background:   active ? cfg.color : 'rgba(121,196,255,0.3)',
                    flexShrink:   0,
                  }}
                />
                {cfg.label}
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}
