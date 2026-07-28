import { useEffect, useMemo, useState } from 'react'

import { countries } from '../../data/mockData'
import { useStore } from '../../store/useStore'

export function Topbar() {
  const [utcClock, setUtcClock] = useState(() => new Date().toISOString().slice(11, 19))
  const mapMode = useStore((state) => state.mapMode)
  const toggleMapMode = useStore((state) => state.toggleMapMode)
  const selectedEntity = useStore((state) => state.selectedEntity)

  useEffect(() => {
    const timer = window.setInterval(() => {
      setUtcClock(new Date().toISOString().slice(11, 19))
    }, 1000)

    return () => window.clearInterval(timer)
  }, [])

  const globalRisk = useMemo(() => {
    const risk = countries.reduce((sum, country) => sum + country.coreMetrics.riskIndex, 0) / countries.length
    return risk.toFixed(1)
  }, [])

  return (
    <header className="topbar">
      <div className="branding">
        <div className="brand-mark">WΞ</div>
        <div className="brand-copy">
          <h1>WEOS</h1>
          <p>Hệ điều hành kinh tế thế giới · Bảng điều khiển song sinh số thời gian thực</p>
        </div>
      </div>

      <div className="topbar-center">
        <div className="topbar-pill">UTC <strong>{utcClock}</strong></div>
        <div className="topbar-pill live">
          <span className="live-dot" />
          LIVE
        </div>
        <div className="topbar-pill">Rủi ro toàn cầu <strong>{globalRisk}</strong></div>
      </div>

      <div className="topbar-right">
        <div className="topbar-pill">Tiêu điểm <strong>{selectedEntity?.name ?? 'Toàn cầu'}</strong></div>
        <button type="button" className={`mode-toggle ${mapMode === '3D' ? 'active' : ''}`} onClick={toggleMapMode}>
          Bản đồ {mapMode === '2D' ? '2D → 3D' : '3D → 2D'}
        </button>
      </div>
    </header>
  )
}
