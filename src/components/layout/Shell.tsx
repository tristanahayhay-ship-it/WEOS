import { Footer } from './Footer'
import { SidebarLeft } from './SidebarLeft'
import { SidebarRight } from './SidebarRight'
import { Topbar } from './Topbar'
import { MapContainer } from '../map/MapContainer'
import { FlowAnimation } from '../map/FlowAnimation'
import { ZoomEngine } from '../ui/ZoomEngine'
import { useStore } from '../../store/useStore'
import { zoomLevelLabels } from '../../data/mockData'

export function Shell() {
  const zoomLevel = useStore((state) => state.zoomLevel)
  const mapMode = useStore((state) => state.mapMode)

  return (
    <div className="weos-shell">
      <Topbar />
      <main className="app-grid">
        <SidebarLeft />
        <section className="map-stage" aria-label="Bản đồ song sinh số kinh tế toàn cầu">
          <div className="map-header">
            <div>
              <p className="map-title">Digital Twin of the Global Economy</p>
              <p className="muted">{zoomLevelLabels[zoomLevel]} · Chế độ {mapMode}</p>
            </div>
            <span className="map-badge">Dòng vốn trực tiếp</span>
          </div>
          <MapContainer />
          <FlowAnimation />
          <div className="map-overlay overlay-top-left">
            <ZoomEngine />
          </div>
        </section>
        <SidebarRight />
      </main>
      <Footer />
    </div>
  )
}
