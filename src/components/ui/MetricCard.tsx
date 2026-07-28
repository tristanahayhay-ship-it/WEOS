import type { TrendDirection } from '../../types'

interface MetricCardProps {
  title: string
  value: string
  trend: TrendDirection
  subtitle?: string
}

export function MetricCard({ title, value, trend, subtitle }: MetricCardProps) {
  return (
    <div className="metric-card">
      <div className="metric-header">
        <p className="metric-title">{title}</p>
        <span className={`badge-chip trend-${trend}`}>{trend.toUpperCase()}</span>
      </div>
      <div className={`metric-value trend-${trend}`}>{value}</div>
      {subtitle ? <p className="metric-meta">{subtitle}</p> : null}
    </div>
  )
}
