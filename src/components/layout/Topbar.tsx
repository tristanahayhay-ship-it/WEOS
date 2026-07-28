import { useEffect, useState } from 'react'

import { useStore } from '../../store/useStore'

const navTabs = ['GLOBAL VIEW', 'ECONOMY', 'MARKETS', 'CAPITAL FLOW', 'INDUSTRY', 'AI ANALYTICS', 'NEWS', 'SETTINGS']

export function Topbar() {
  const [utcClock, setUtcClock] = useState(() => new Date().toISOString().slice(11, 19))
  const mapMode = useStore((state) => state.mapMode)
  const toggleMapMode = useStore((state) => state.toggleMapMode)

  useEffect(() => {
    const timer = window.setInterval(() => {
      setUtcClock(new Date().toISOString().slice(11, 19))
    }, 1000)

    return () => window.clearInterval(timer)
  }, [])

  return (
    <header className="topbar">
      <div className="branding">
        <div className="brand-copy">
          <h1>WEOS</h1>
          <p>WORLD ECONOMIC OPERATING SYSTEM · Level 0 · Global View</p>
        </div>
      </div>

      <nav className="top-nav" aria-label="Main dashboard views">
        {navTabs.map((tab, index) => (
          <button key={tab} type="button" className={`top-nav-item ${index === 0 ? 'active' : ''}`}>
            {tab}
          </button>
        ))}
      </nav>

      <div className="topbar-right">
        <div className="topbar-pill clock-pill">{utcClock} UTC</div>
        <div className="topbar-pill live">
          <span className="live-dot" />
          LIVE
        </div>
        <button type="button" className={`mode-toggle ${mapMode === '3D' ? 'active' : ''}`} onClick={toggleMapMode}>
          {mapMode === '2D' ? '3D EARTH' : '2D MAP'}
        </button>
      </div>
    </header>
  )
}
