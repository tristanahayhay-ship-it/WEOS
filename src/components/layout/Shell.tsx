import { Footer } from './Footer'
import { SidebarLeft } from './SidebarLeft'
import { SidebarRight } from './SidebarRight'
import { Topbar } from './Topbar'
import { MapContainer } from '../map/MapContainer'
import { FlowAnimation } from '../map/FlowAnimation'
import { useStore } from '../../store/useStore'

export function Shell() {
  const mapMode = useStore((state) => state.mapMode)

  return (
    <div className="weos-shell">
      <Topbar />
      <main className="app-grid">
        <SidebarLeft />
        <section className="map-stage" aria-label="Bản đồ song sinh số kinh tế toàn cầu">
          <div className="map-header">
            <p className="map-title">GLOBAL CAPITAL FLOW NETWORK</p>
            <span className="map-badge">LIVE</span>
          </div>

          <div className="map-legend">
            <p><span className="legend-dot inflow" /> INFLOW</p>
            <p><span className="legend-dot outflow" /> OUTFLOW</p>
            <p><span className="legend-dot neutral" /> NEUTRAL</p>
          </div>

          <MapContainer />
          <FlowAnimation />

          {/* Atmosphere glow ring — purely decorative, sits above map but below controls */}
          <div className="atmosphere-overlay" aria-hidden="true" />
          <div className="flow-control-bar">
            <span>REAL-TIME FLOW ANIMATION</span>
            <input type="range" min={0} max={100} defaultValue={52} aria-label="Flow animation timeline" />
            <span>FLOW SPEED 1.0x · {mapMode}</span>
          </div>
        </section>
        <SidebarRight />
      </main>
      <Footer />
    </div>
  )
}
