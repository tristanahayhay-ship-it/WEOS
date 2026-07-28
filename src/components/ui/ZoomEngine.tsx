import { zoomLevelDescriptions, zoomLevelLabels } from '../../data/mockData'
import { useStore } from '../../store/useStore'
import { ZoomLevel } from '../../types'
import { EntityPanel } from '../panels/EntityPanel'
import { RealTimePanel } from '../panels/RealTimePanel'

export function ZoomEngine() {
  const zoomLevel = useStore((state) => state.zoomLevel)
  const selectedEntity = useStore((state) => state.selectedEntity)

  if (zoomLevel === ZoomLevel.ThoiGianThuc) {
    return <RealTimePanel />
  }

  return (
    <div className="zoom-context list-stack">
      <div className="entity-header">
        <div>
          <h3>{zoomLevelLabels[zoomLevel]}</h3>
          <p className="muted">{zoomLevelDescriptions[zoomLevel]}</p>
        </div>
        <span className="badge-chip">Context AI</span>
      </div>
      {selectedEntity ? (
        <EntityPanel entity={selectedEntity} zoomLevel={zoomLevel} />
      ) : (
        <div className="panel-card">
          <p>Chọn một thực thể trên bản đồ để hiển thị hồ sơ, dòng vốn và chỉ số kinh tế phù hợp cấp zoom hiện tại.</p>
        </div>
      )}
    </div>
  )
}
