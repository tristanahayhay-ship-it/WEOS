import type { ReactNode } from 'react'
import Topbar from './Topbar'
import Footer from './Footer'

interface ShellProps {
  children?: ReactNode
}

export default function Shell({ children }: ShellProps) {
  return (
    <div className="flex flex-col h-full w-full overflow-hidden" style={{ background: 'var(--weos-bg)' }}>
      <Topbar />

      <main className="relative flex-1 overflow-hidden">
        {/* Map / visualization canvas will be mounted here by future phases */}
        {children ?? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center space-y-3">
              <h1
                className="text-4xl font-bold tracking-tight"
                style={{ color: 'var(--weos-accent)' }}
              >
                WEOS
              </h1>
              <p style={{ color: 'var(--weos-text-muted)' }}>
                World Economic Operating System
              </p>
            </div>
          </div>
        )}
      </main>

      <Footer />
    </div>
  )
}
