import { useUIStore } from '../../stores/uiStore'
import type { TopbarTab } from '../../types/ui'

const TABS: { id: TopbarTab; label: string }[] = [
  { id: 'global-view', label: 'GLOBAL VIEW' },
  { id: 'flows', label: 'FLOWS' },
  { id: 'sectors', label: 'SECTORS' },
  { id: 'nations', label: 'NATIONS' },
  { id: 'analytics', label: 'ANALYTICS' },
  { id: 'settings', label: 'SETTINGS' },
]

export default function Topbar() {
  const { activeTab, setActiveTab } = useUIStore()

  return (
    <header
      className="flex items-center h-11 px-4 shrink-0 border-b"
      style={{
        background: 'var(--weos-surface)',
        borderColor: 'var(--weos-border)',
      }}
    >
      <span
        className="text-sm font-bold tracking-widest mr-6 shrink-0"
        style={{ color: 'var(--weos-accent)' }}
      >
        WEOS
      </span>

      <nav className="flex gap-1 overflow-x-auto">
        {TABS.map((tab) => {
          const isActive = activeTab === tab.id
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className="px-3 py-1.5 text-xs font-semibold tracking-wider rounded transition-colors whitespace-nowrap"
              style={{
                background: isActive ? 'var(--weos-accent)' : 'transparent',
                color: isActive ? '#fff' : 'var(--weos-text-muted)',
              }}
            >
              {tab.label}
            </button>
          )
        })}
      </nav>
    </header>
  )
}
