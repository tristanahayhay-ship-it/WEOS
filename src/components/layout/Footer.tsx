import { useUIStore } from '../../stores/uiStore'
import type { ViewMode } from '../../types/ui'

const MODES: { id: ViewMode; label: string; icon: string }[] = [
  { id: '2d', label: '2D MAP', icon: '🗺' },
  { id: '3d', label: '3D GLOBE', icon: '🌐' },
  { id: 'flow', label: 'FLOW', icon: '⟳' },
  { id: 'chart', label: 'CHART', icon: '📊' },
]

export default function Footer() {
  const { viewMode, setViewMode } = useUIStore()

  return (
    <footer
      className="flex items-center justify-center h-11 gap-2 px-4 shrink-0 border-t"
      style={{
        background: 'var(--weos-surface)',
        borderColor: 'var(--weos-border)',
      }}
    >
      {MODES.map((mode) => {
        const isActive = viewMode === mode.id
        return (
          <button
            key={mode.id}
            onClick={() => setViewMode(mode.id)}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold tracking-wider rounded transition-colors"
            style={{
              background: isActive ? 'var(--weos-accent-dim)' : 'transparent',
              color: isActive ? '#fff' : 'var(--weos-text-muted)',
              border: isActive ? '1px solid var(--weos-accent)' : '1px solid transparent',
            }}
          >
            <span>{mode.icon}</span>
            <span>{mode.label}</span>
          </button>
        )
      })}
    </footer>
  )
}
