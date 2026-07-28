import { useMemo } from 'react'
import ReactECharts from 'echarts-for-react'

import { capitalFlows, countries, economicCalendar, marketIndices } from '../../data/mockData'

const compactCurrency = new Intl.NumberFormat('vi-VN', {
  maximumFractionDigits: 0,
  notation: 'compact',
})

export function SidebarLeft() {
  const flowSummary = useMemo(() => {
    const total = capitalFlows.reduce((sum, flow) => sum + flow.value, 0)
    const average = total / capitalFlows.length
    const fastest = capitalFlows.reduce((candidate, flow) => (flow.speed > candidate.speed ? flow : candidate), capitalFlows[0])
    const averageRisk = countries.reduce((sum, country) => sum + country.coreMetrics.riskIndex, 0) / countries.length

    return {
      total,
      average,
      fastest,
      averageRisk,
    }
  }, [])

  const gaugeOption = useMemo(
    () => ({
      backgroundColor: 'transparent',
      series: [
        {
          type: 'gauge',
          min: 0,
          max: 100,
          progress: { show: true, width: 14, itemStyle: { color: '#00d4ff' } },
          axisLine: { lineStyle: { width: 14, color: [[1, 'rgba(255,255,255,0.08)']] } },
          pointer: { itemStyle: { color: '#00ff88' } },
          axisTick: { show: false },
          splitLine: { show: false },
          axisLabel: { show: false },
          detail: { valueAnimation: true, color: '#e5f7ff', formatter: '{value}' },
          data: [{ value: Number(flowSummary.averageRisk.toFixed(1)) }],
        },
      ],
    }),
    [flowSummary.averageRisk],
  )

  return (
    <aside className="sidebar sidebar-left sidebar-scroll">
      <section className="sidebar-panel">
        <div className="section-title-row">
          <h3>Toàn cảnh thị trường</h3>
          <span className="small-tag">6 chỉ số</span>
        </div>
        <div className="list-stack">
          {marketIndices.map((index) => (
            <div key={index.id} className="market-item">
              <div>
                <strong>{index.name}</strong>
                <p className="muted">{index.region}</p>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div className="kpi-value">{index.value.toLocaleString('vi-VN')}</div>
                <div className={index.change >= 0 ? 'trend-up' : 'trend-down'}>
                  {index.change >= 0 ? '+' : ''}
                  {index.change.toFixed(2)}%
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="sidebar-panel">
        <div className="section-title-row">
          <h3>Tóm tắt dòng vốn 24h</h3>
          <span className="small-tag">{capitalFlows.length} hành lang</span>
        </div>
        <div className="stat-pair">
          <div className="metric-card">
            <p className="metric-title">Tổng notional</p>
            <div className="kpi-value">{compactCurrency.format(flowSummary.total)} tỷ USD</div>
            <p className="metric-meta">Xuyên khu vực & sovereign</p>
          </div>
          <div className="metric-card">
            <p className="metric-title">Bình quân/hành lang</p>
            <div className="kpi-value">{flowSummary.average.toFixed(1)}</div>
            <p className="metric-meta">tỷ USD / 24h</p>
          </div>
        </div>
        <div className="panel-card">
          <div className="entity-header">
            <strong>Hành lang nhanh nhất</strong>
            <span className="badge-chip">{flowSummary.fastest.speed.toFixed(1)}x</span>
          </div>
          <p>
            {flowSummary.fastest.category}: <strong>{flowSummary.fastest.from.toUpperCase()}</strong> →{' '}
            <strong>{flowSummary.fastest.to.toUpperCase()}</strong>
          </p>
        </div>
      </section>

      <section className="sidebar-panel">
        <div className="section-title-row">
          <h3>Lịch kinh tế</h3>
          <span className="small-tag">Sắp tới</span>
        </div>
        <div className="calendar-stack">
          {economicCalendar.map((event) => (
            <div key={event.id} className="calendar-item">
              <div className="entity-header">
                <strong>{event.title}</strong>
                <span className={`badge-chip ${event.importance}`}>{event.importance.toUpperCase()}</span>
              </div>
              <p className="muted">{event.entity}</p>
              <p className="calendar-time">{event.timestamp}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="sidebar-panel">
        <div className="section-title-row">
          <h3>Gauge rủi ro toàn cầu</h3>
          <span className="small-tag">AI tổng hợp</span>
        </div>
        <div className="gauge-box">
          <ReactECharts option={gaugeOption} style={{ height: '100%', width: '100%' }} />
        </div>
      </section>
    </aside>
  )
}
