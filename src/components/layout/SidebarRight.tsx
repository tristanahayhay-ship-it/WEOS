import { useMemo } from 'react'

import { aiInsights, capitalFlows, countries, newsFeed } from '../../data/mockData'
import { useStore } from '../../store/useStore'
import { AlertBadge } from '../ui/AlertBadge'

export function SidebarRight() {
  const alerts = useStore((state) => state.alerts)
  const acknowledgeAlert = useStore((state) => state.acknowledgeAlert)

  const rankings = useMemo(() => {
    const netMap = new Map<string, number>()

    capitalFlows.forEach((flow) => {
      netMap.set(flow.to, (netMap.get(flow.to) ?? 0) + flow.value)
      netMap.set(flow.from, (netMap.get(flow.from) ?? 0) - flow.value)
    })

    const rows = countries.map((country) => ({
      name: country.name,
      code: country.code,
      net: netMap.get(country.id) ?? 0,
    }))

    return {
      inflow: [...rows].sort((a, b) => b.net - a.net).slice(0, 5),
      outflow: [...rows].sort((a, b) => a.net - b.net).slice(0, 5),
    }
  }, [])

  return (
    <aside className="sidebar sidebar-right sidebar-scroll">
      <section className="sidebar-panel">
        <div className="section-title-row">
          <h3>AI GLOBAL ANALYSIS</h3>
          <span className="small-tag">LIVE</span>
        </div>
        <div className="list-stack">
          {aiInsights.map((insight) => (
            <div key={insight.id} className="panel-card">
              <div className="entity-header">
                <strong>{insight.title}</strong>
                <span className={`badge-chip trend-${insight.signal}`}>{insight.confidence}%</span>
              </div>
              <p>{insight.summary}</p>
              <p className="metric-meta">{insight.scope} · {insight.timestamp}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="sidebar-panel">
        <div className="section-title-row">
          <h3>CAPITAL FLOW RANKING (24H)</h3>
          <span className="small-tag">LIVE</span>
        </div>
        <div className="rank-grid">
          <div className="rank-card">
            <h3>TOP INFLOW</h3>
            <div className="list-stack">
              {rankings.inflow.map((row, index) => (
                <div key={row.code} className="rank-row">
                  <span className="rank-number">#{index + 1}</span>
                  <div style={{ flex: 1 }}>
                    <strong>{row.name}</strong>
                    <p className="rank-value">{row.code}</p>
                  </div>
                  <span className="trend-up">+{row.net.toFixed(0)}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="rank-card">
            <h3>TOP OUTFLOW</h3>
            <div className="list-stack">
              {rankings.outflow.map((row, index) => (
                <div key={row.code} className="rank-row">
                  <span className="rank-number">#{index + 1}</span>
                  <div style={{ flex: 1 }}>
                    <strong>{row.name}</strong>
                    <p className="rank-value">{row.code}</p>
                  </div>
                  <span className="trend-down">{row.net.toFixed(0)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="sidebar-panel">
        <div className="section-title-row">
          <h3>CRITICAL ALERTS</h3>
          <span className="small-tag">{alerts.filter((item) => !item.acknowledged).length} chưa xử lý</span>
        </div>
        <div className="alert-stack">
          {alerts.map((alert) => (
            <AlertBadge key={alert.id} alert={alert} onAcknowledge={() => acknowledgeAlert(alert.id)} />
          ))}
        </div>
      </section>

      <section className="sidebar-panel">
        <div className="section-title-row">
          <h3>NEWS FEED</h3>
          <span className="small-tag">LIVE</span>
        </div>
        <div className="news-stack">
          {newsFeed.map((news) => (
            <article key={news.id} className="news-item">
              <div className="entity-header" style={{ width: '100%' }}>
                <strong>{news.title}</strong>
                <span className={`badge-chip ${news.impact}`}>{news.impact}</span>
              </div>
              <p>{news.summary}</p>
              <p className="news-time">{news.region} · {news.source} · {news.timestamp}</p>
            </article>
          ))}
        </div>
      </section>
    </aside>
  )
}
