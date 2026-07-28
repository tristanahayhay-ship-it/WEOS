import { Footer } from './Footer'
import { SidebarLeft } from './SidebarLeft'
import { SidebarRight } from './SidebarRight'
import { Topbar } from './Topbar'
import { MapContainer } from '../map/MapContainer'
import { FlowAnimation } from '../map/FlowAnimation'
import { zoomLevelLabels } from '../../data/mockData'
import { FLOW_SPEED_MAX, FLOW_SPEED_MIN, FLOW_SPEED_STEP, useStore } from '../../store/useStore'

const FLOW_SPEED_SLIDER_MULTIPLIER = 1 / FLOW_SPEED_STEP
const FLOW_SPEED_SLIDER_MIN = FLOW_SPEED_MIN * FLOW_SPEED_SLIDER_MULTIPLIER
const FLOW_SPEED_SLIDER_MAX = FLOW_SPEED_MAX * FLOW_SPEED_SLIDER_MULTIPLIER

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
              min={FLOW_SPEED_SLIDER_MIN}
              max={FLOW_SPEED_SLIDER_MAX}
              step={1}
              value={Math.round(flowSpeed * FLOW_SPEED_SLIDER_MULTIPLIER)}
              aria-label="Flow animation speed"
              onChange={(event) => setFlowSpeed(Number(event.target.value) / FLOW_SPEED_SLIDER_MULTIPLIER)}
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
