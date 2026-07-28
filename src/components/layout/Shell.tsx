import type { ReactNode } from 'react'
import Topbar from './Topbar'
import Footer from './Footer'
import GlobeEngine from '../globe/GlobeEngine'
import CountryPanel from '../panels/CountryPanel'

interface ShellProps {
  children?: ReactNode
}

export default function Shell({ children }: ShellProps) {
  return (
    <div className="flex flex-col h-full w-full overflow-hidden" style={{ background: 'var(--weos-bg)' }}>
      <Topbar />

      <main className="relative flex-1 overflow-hidden">
        {children ?? <GlobeEngine />}
        <CountryPanel />
      </main>

      <Footer />
    </div>
  )
}
