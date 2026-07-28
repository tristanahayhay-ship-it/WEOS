import type { GeoEntity } from '../../types'
import { ZoomLevel } from '../../types'
import { MetricCard } from '../ui/MetricCard'
import { CountryPanel } from './CountryPanel'

interface EntityPanelProps {
  entity: GeoEntity
  zoomLevel: ZoomLevel
}

export function EntityPanel({ entity, zoomLevel }: EntityPanelProps) {
  if (entity.type === 'country') {
    return <CountryPanel country={entity} zoomLevel={zoomLevel} />
  }

  return (
    <div className="entity-panel list-stack">
      <div className="entity-header">
        <div>
          <h3>{entity.name}</h3>
          <p className="muted">{entity.type.toUpperCase()} · {entity.continent}</p>
        </div>
        <span className="badge-chip">L{zoomLevel}</span>
      </div>
      <p>{entity.description}</p>
      <div className="metrics-grid">
        <MetricCard title="Sức khỏe" value={`${entity.economicHealth}/100`} trend={entity.economicHealth > 75 ? 'up' : 'down'} />
        <MetricCard title="Dân số" value={`${entity.population}M`} trend="stable" />
        <MetricCard title="Rủi ro" value={entity.coreMetrics.riskIndex.toFixed(1)} trend={entity.coreMetrics.riskIndex < 50 ? 'up' : 'down'} />
      </div>
    </div>
  )
}
