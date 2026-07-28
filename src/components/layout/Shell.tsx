import { Footer } from './Footer'
import { SidebarLeft } from './SidebarLeft'
import { SidebarRight } from './SidebarRight'
import { Topbar } from './Topbar'
import { MapContainer } from '../map/MapContainer'
import { FlowAnimation } from '../map/FlowAnimation'
import { zoomLevelLabels } from '../../data/mockData'
import { FLOW_SPEED_MAX, FLOW_SPEED_MIN, useStore } from '../../store/useStore'

export function Shell() {
  const mapMode = useStore((state) => state.mapMode)
  const flowSpeed = useStore((state) => state.flowSpeed)
  const setFlowSpeed = useStore((state) => state.setFlowSpeed)
  const zoomLevel = useStore((state) => state.zoomLevel)
  const selectedEntity = useStore((state) => state.selectedEntity)

  return (
    <div className="weos-shell">
      <Topbar />
      <main className="app-grid">
        <SidebarLeft />
        <section className="map-stage" aria-label="Bản đồ song sinh số kinh tế toàn cầu">
          <div className="map-header">
            <p className="map-title">GLOBAL CAPITAL FLOW NETWORK</p>
            <span className="map-badge">LIVE</span>
            <span className="map-badge">{zoomLevelLabels[zoomLevel]}</span>
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
            <input
              type="range"
              min={FLOW_SPEED_MIN * 10}
              max={FLOW_SPEED_MAX * 10}
              step={1}
              value={Math.round(flowSpeed * 10)}
              aria-label="Flow animation speed"
              onChange={(event) => setFlowSpeed(Number(event.target.value) / 10)}
            />
            <span>
              FLOW SPEED {flowSpeed.toFixed(1)}x · {mapMode} · {selectedEntity?.code ?? 'GLOBAL'}
            </span>
          </div>
        </section>
        <SidebarRight />
      </main>
      <Footer />
    </div>
  )
}
