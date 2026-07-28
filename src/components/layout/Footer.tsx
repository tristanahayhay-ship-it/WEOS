import { useStore } from '../../store/useStore'
import { ZoomLevel } from '../../types'

/** All 11 WEOS zoom levels — L0 (global) through L10 (real-time). */
const modeLinks: Array<{ label: string; level: ZoomLevel; icon: string }> = [
  { label: 'L0 GLOBAL',    level: ZoomLevel.TongTheHeThong, icon: '🌐' },
  { label: 'L1 CLUSTER',   level: ZoomLevel.VungDiaKinhTe,  icon: '◉' },
  { label: 'L2 CONTINENT', level: ZoomLevel.LucDia,         icon: '◎' },
  { label: 'L3 COUNTRY',   level: ZoomLevel.QuocGia,        icon: '◍' },
  { label: 'L4 CORRIDOR',  level: ZoomLevel.VungLienKet,    icon: '◌' },
  { label: 'L5 PROVINCE',  level: ZoomLevel.TinhThanh,      icon: '▤' },
  { label: 'L6 CITY',      level: ZoomLevel.DoThi,          icon: '⌂' },
  { label: 'L7 ENTITY',    level: ZoomLevel.DinhChe,        icon: '▦' },
  { label: 'L8 CORP',      level: ZoomLevel.DoanhNghiep,    icon: '◧' },
  { label: 'L9 FACILITY',  level: ZoomLevel.CoSo,           icon: '◫' },
  { label: 'L10 REALTIME', level: ZoomLevel.ThoiGianThuc,   icon: '⏱' },
]

export function Footer() {
  const zoomLevel = useStore((state) => state.zoomLevel)
  const setZoomLevel = useStore((state) => state.setZoomLevel)

  return (
    <footer className="footer-bar">
      <div className="footer-modes">
        {modeLinks.map((item) => (
          <button
            key={item.label}
            type="button"
            className={`footer-mode ${zoomLevel === item.level ? 'active' : ''}`}
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
