import { Component, type ErrorInfo, type ReactNode, useEffect } from 'react'
import Topbar from './Topbar'
import Footer from './Footer'
import GlobeEngine from '../globe/GlobeEngine'
import CountryPanel from '../panels/CountryPanel'
import { OverlayCanvas, OverlayPanel, OverlayLegend } from '../overlay'
import { FlowCanvas, FlowPanel } from '../flow'
import { DebugCanvas } from '../debug'
import { useDebugStore } from '../../stores/debugStore'
import ZoomLevelHUD from '../zoom/ZoomLevelHUD'

// ─── Error boundary — catches any render-time crash and shows a recoverable UI ─

interface ErrorBoundaryState {
  error: Error | null
}

class AppErrorBoundary extends Component<{ children: ReactNode }, ErrorBoundaryState> {
  constructor(props: { children: ReactNode }) {
    super(props)
    this.state = { error: null }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('[WEOS] Uncaught render error:', error, info.componentStack)
  }

  render() {
    if (this.state.error) {
      return (
        <div
          className="flex flex-col items-center justify-center h-full w-full gap-4"
          style={{ background: 'var(--weos-bg)', color: 'var(--weos-text)' }}
        >
          <p className="text-lg font-semibold" style={{ color: 'var(--weos-accent)' }}>
            WEOS encountered an error
          </p>
          <p className="text-sm" style={{ color: 'var(--weos-text-muted)' }}>
            {this.state.error.message}
          </p>
          <button
            type="button"
            className="px-4 py-2 text-sm rounded"
            style={{ background: 'var(--weos-accent)', color: '#fff' }}
            onClick={() => window.location.reload()}
          >
            Retry
          </button>
        </div>
      )
    }
    return this.props.children
  }
}

// ─────────────────────────────────────────────────────────────────────────────

interface ShellProps {
  children?: ReactNode
}

export default function Shell({ children }: ShellProps) {
  const toggleDebug = useDebugStore((s) => s.toggle)

  // Shift+D toggles the Sprite ↔ OverlayCanvas comparison overlay.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.shiftKey && e.key === 'D') toggleDebug()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [toggleDebug])

  return (
    <div className="flex flex-col h-full w-full overflow-hidden" style={{ background: 'var(--weos-bg)' }}>
      <Topbar />

      <main className="relative flex-1 overflow-hidden">
        <AppErrorBoundary>
          {children ?? <GlobeEngine />}
          <OverlayCanvas />
          <OverlayPanel />
          <OverlayLegend />
          <FlowCanvas />
          <FlowPanel />
          <CountryPanel />
          <DebugCanvas />
          <ZoomLevelHUD />
        </AppErrorBoundary>
      </main>

      <Footer />
    </div>
  )
}
