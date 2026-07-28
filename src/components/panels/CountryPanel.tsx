import type { GeoEntity } from '../../types'
import { ZoomLevel } from '../../types'
import { MetricCard } from '../ui/MetricCard'

interface CountryPanelProps {
  country: GeoEntity
  zoomLevel: ZoomLevel
}

const zoomVisibilityMap: Record<number, number> = {
  0: 4,
  1: 6,
  2: 8,
  3: 10,
  4: 12,
  5: 14,
  6: 16,
  7: 18,
  8: 19,
  9: 20,
  10: 20,
}

export function CountryPanel({ country, zoomLevel }: CountryPanelProps) {
  const visibleGroups = Object.values(country.metricGroups).slice(0, zoomVisibilityMap[zoomLevel] ?? 8)

  return (
    <div className="country-panel list-stack">
      <div className="entity-header">
        <div>
          <h3>{country.name}</h3>
          <p className="muted">{country.code} · {country.continent} · Zoom L{zoomLevel}</p>
        </div>
        <span className="badge-chip">Health {country.economicHealth}</span>
      </div>
      <p>{country.description}</p>
      <div className="entity-tags">
        {country.tags.map((tag) => (
          <span key={tag} className="entity-tag">{tag}</span>
        ))}
      </div>
      <div className="metrics-grid">
        <MetricCard title="GDP" value={`${country.coreMetrics.gdp.toLocaleString('vi-VN')} tỷ USD`} trend={country.coreMetrics.gdpGrowth >= 0 ? 'up' : 'down'} />
        <MetricCard title="Tăng trưởng" value={`${country.coreMetrics.gdpGrowth.toFixed(1)}%`} trend={country.coreMetrics.gdpGrowth >= 3 ? 'up' : 'stable'} />
        <MetricCard title="Lạm phát" value={`${country.coreMetrics.inflation.toFixed(1)}%`} trend={country.coreMetrics.inflation <= 3 ? 'up' : 'down'} />
        <MetricCard title="Thất nghiệp" value={`${country.coreMetrics.unemployment.toFixed(1)}%`} trend={country.coreMetrics.unemployment <= 5 ? 'up' : 'down'} />
        <MetricCard title="Lãi suất" value={`${country.coreMetrics.interestRate.toFixed(2)}%`} trend={country.coreMetrics.interestRate < 5 ? 'up' : 'stable'} />
        <MetricCard title="Dự trữ FX" value={`${country.coreMetrics.fxReserves.toLocaleString('vi-VN')} tỷ`} trend="up" />
      </div>
      <div className="country-groups">
        {visibleGroups.map((group) => (
          <div key={group.key} className="metric-card">
            <div className="metric-header">
              <h4 className="metric-title">{group.title}</h4>
              <span className={`badge-chip trend-${group.trend}`}>{group.score}/100</span>
            </div>
            <p className="metric-meta">{group.summary}</p>
            <div className="list-stack" style={{ marginTop: 10 }}>
              {group.metrics.map((metric) => (
                <div key={metric.label} className="list-row">
                  <span>{metric.label}</span>
                  <span className={`trend-${metric.trend}`}>
                    {metric.value}
                    {metric.unit ? ` ${metric.unit}` : ''}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
      {zoomLevel < ZoomLevel.ThoiGianThuc ? (
        <p className="muted">Tăng zoom để mở thêm lớp định chế, doanh nghiệp và mô phỏng dòng lệnh.</p>
      ) : null}
    </div>
  )
}
