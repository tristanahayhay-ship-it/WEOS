import { useStore } from '../../store/useStore'
import { ZoomLevel } from '../../types'

const modeLinks: Array<{ label: string; level: ZoomLevel; icon: string }> = [
  { label: 'GLOBAL VIEW', level: ZoomLevel.TongTheHeThong, icon: '🌐' },
  { label: 'REGION VIEW', level: ZoomLevel.VungDiaKinhTe, icon: '◉' },
  { label: 'COUNTRY VIEW', level: ZoomLevel.QuocGia, icon: '◎' },
  { label: 'CITY VIEW', level: ZoomLevel.DoThi, icon: '⌂' },
  { label: 'ASSET VIEW', level: ZoomLevel.DinhChe, icon: '◌' },
  { label: 'ECONOMIC MAP', level: ZoomLevel.DoanhNghiep, icon: '▦' },
]

export function Footer() {
  const zoomLevel = useStore((state) => state.zoomLevel)
  const setZoomLevel = useStore((state) => state.setZoomLevel)

  return (
    <footer className="footer-bar">
      <div className="footer-modes">
        {modeLinks.map((item, index) => (
          <button
            key={item.label}
            type="button"
            className={`footer-mode ${zoomLevel === item.level || (index === 0 && zoomLevel <= ZoomLevel.VungDiaKinhTe) ? 'active' : ''}`}
            onClick={() => setZoomLevel(item.level)}
          >
            <span>{item.icon}</span>
            {item.label}
          </button>
        ))}
      </div>
      <div className="footer-tools">
        <span>◈</span>
        <span>⌁</span>
        <span>◍</span>
        <span>⟲</span>
      </div>
    </footer>
  )
}
