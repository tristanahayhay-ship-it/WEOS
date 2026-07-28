import { zoomLevelDescriptions, zoomLevelLabels } from '../../data/mockData'
import { useStore } from '../../store/useStore'
import { ZoomLevel } from '../../types'

const levels = Array.from({ length: 11 }, (_, index) => index as ZoomLevel)

export function Footer() {
  const zoomLevel = useStore((state) => state.zoomLevel)
  const setZoomLevel = useStore((state) => state.setZoomLevel)
  const zoomIn = useStore((state) => state.zoomIn)
  const zoomOut = useStore((state) => state.zoomOut)

  return (
    <footer className="footer-bar">
      <div>
        <p className="panel-title">Điều hướng độ sâu</p>
        <p className="footer-meta">{zoomLevelDescriptions[zoomLevel]}</p>
      </div>
      <div className="zoom-controls">
        <button type="button" className="zoom-button" onClick={zoomOut}>
          -
        </button>
        {levels.map((level) => (
          <button
            key={level}
            type="button"
            className={`zoom-button ${zoomLevel === level ? 'active' : ''}`}
            onClick={() => setZoomLevel(level)}
          >
            {zoomLevelLabels[level]}
          </button>
        ))}
        <button type="button" className="zoom-button" onClick={zoomIn}>
          +
        </button>
      </div>
    </footer>
  )
}
