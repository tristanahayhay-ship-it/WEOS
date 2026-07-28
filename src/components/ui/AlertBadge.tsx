import type { AlertItem } from '../../types'

interface AlertBadgeProps {
  alert: AlertItem
  onAcknowledge: () => void
}

export function AlertBadge({ alert, onAcknowledge }: AlertBadgeProps) {
  return (
    <div className={`alert-badge ${alert.severity}`}>
      <div className="alert-top">
        <strong>{alert.title}</strong>
        <span className="badge-chip">{alert.severity.toUpperCase()}</span>
      </div>
      <p>{alert.description}</p>
      <div className="entity-header" style={{ marginTop: 10 }}>
        <span className="metric-meta">{alert.entityCode ?? 'GLOBAL'} · {alert.timestamp}</span>
        <button type="button" className="alert-action" onClick={onAcknowledge} disabled={alert.acknowledged}>
          {alert.acknowledged ? 'Đã xử lý' : 'Xác nhận'}
        </button>
      </div>
    </div>
  )
}
