import type {
  ViewState,
  WorldData,
  ActiveScope,
  DashboardModel,
  DashboardSection,
  DashboardRankEntry,
} from './types'

// ── Helpers ───────────────────────────────────────────────────────────────────

function fmt(value: number | null, suffix: string, decimals = 1): string {
  if (value == null) return '—'
  return `${value.toFixed(decimals)}${suffix}`
}

function fmtT(value: number | null): string {
  if (value == null) return '—'
  return `$${value.toFixed(1)}T`
}

function fmtB(value: number | null): string {
  if (value == null) return '—'
  if (value >= 1000) return `$${(value / 1000).toFixed(2)}T`
  return `$${value.toFixed(1)}B`
}

function fmtPop(value: number | null): string {
  if (value == null) return '—'
  if (value >= 1e9) return `${(value / 1e9).toFixed(2)}B`
  if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`
  if (value >= 1e3) return `${(value / 1e3).toFixed(0)}K`
  return String(value)
}

function trendLabel(trend?: 'up' | 'flat' | 'down'): string {
  if (trend === 'up') return '↑'
  if (trend === 'down') return '↓'
  return '→'
}

function riskColor(score: number | null): string {
  if (score == null) return '#94a3b8'
  if (score < 30) return '#34d399'
  if (score < 60) return '#f59e0b'
  return '#f87171'
}

// ── Level 0 — Global Dashboard ────────────────────────────────────────────────

function buildGlobalDashboard(worldData: WorldData): DashboardModel {
  const sections: DashboardSection[] = []

  // World macro indicators
  if (worldData.macroMetrics.length > 0) {
    sections.push({
      id: 'global-macro',
      type: 'macro_indicators',
      title: 'World Macro Overview',
      metrics: worldData.macroMetrics.map((m) => ({
        label: m.label,
        value: `${m.value} ${m.unit} ${trendLabel(m.trend)}`,
      })),
    })
  }

  // Top global hubs ranked by importance
  const topHubs = [...worldData.globalHubs]
    .sort((a, b) => b.importance - a.importance)
    .slice(0, 8)

  if (topHubs.length > 0) {
    const rankings: DashboardRankEntry[] = topHubs.map((hub, i) => ({
      rank: i + 1,
      name: hub.name,
      value: hub.volumeUsdB != null ? fmtB(hub.volumeUsdB) : `${(hub.importance * 100).toFixed(0)} idx`,
    }))
    sections.push({
      id: 'global-hubs',
      type: 'rankings',
      title: 'Top Global Hubs',
      rankings,
    })
  }

  // Top global flows
  const topFlows = [...worldData.globalFlows]
    .sort((a, b) => b.value - a.value)
    .slice(0, 6)

  if (topFlows.length > 0) {
    const hubIndex = new Map(worldData.globalHubs.map((h) => [h.id, h.name]))
    sections.push({
      id: 'global-flows',
      type: 'capital_flow',
      title: 'Top Capital Flows',
      metrics: topFlows.map((f) => ({
        label: `${hubIndex.get(f.fromId) ?? f.fromId} → ${hubIndex.get(f.toId) ?? f.toId}`,
        value: fmtB(f.value),
        color: '#60a5fa',
      })),
    })
  }

  // Continent summary
  const continentEntries = Object.values(worldData.continents).filter(Boolean)
  if (continentEntries.length > 0) {
    const rankings: DashboardRankEntry[] = continentEntries
      .filter((c) => c.gdpUsdT != null)
      .sort((a, b) => (b.gdpUsdT ?? 0) - (a.gdpUsdT ?? 0))
      .map((c, i) => ({
        rank: i + 1,
        name: c.name,
        value: fmtT(c.gdpUsdT),
        trend: (c.growthPercent ?? 0) > 2.5 ? 'up' : (c.growthPercent ?? 0) < 0.5 ? 'down' : 'flat',
      }))
    sections.push({
      id: 'global-continents',
      type: 'rankings',
      title: 'GDP by Continent',
      rankings,
    })
  }

  return {
    level: 0,
    scopeId: 'global',
    title: 'Global Economic View',
    subtitle: 'World-scale intelligence',
    sections,
  }
}

// ── Level 1 — Continent Dashboard ────────────────────────────────────────────

function buildContinentDashboard(
  worldData: WorldData,
  continentName: string,
): DashboardModel {
  const cd = worldData.continents[continentName as keyof typeof worldData.continents]
  const sections: DashboardSection[] = []

  if (cd) {
    // Aggregate metrics
    sections.push({
      id: 'continent-agg',
      type: 'macro_indicators',
      title: 'Continental Overview',
      metrics: [
        { label: 'GDP',        value: fmtT(cd.gdpUsdT) },
        { label: 'Population', value: fmtPop(cd.population) },
        { label: 'GDP Growth', value: fmt(cd.growthPercent, '%') },
        { label: 'Risk Score', value: cd.riskScore != null ? `${cd.riskScore}/100` : '—', color: riskColor(cd.riskScore) },
      ].filter((m) => m.value !== '—'),
    })

    // Country GDP rankings
    if (cd.countryRankings.length > 0) {
      sections.push({
        id: 'continent-rankings',
        type: 'rankings',
        title: `Top Economies — ${cd.name}`,
        rankings: cd.countryRankings.map((entry) => ({
          rank: entry.rank,
          name: entry.name,
          value: fmtT(entry.gdpUsdT),
        })),
      })
    }

    // Regional flows
    const topFlows = [...cd.flows]
      .sort((a, b) => b.value - a.value)
      .slice(0, 5)

    if (topFlows.length > 0) {
      const hubIndex = new Map(cd.hubs.map((h) => [h.id, h.name]))
      sections.push({
        id: 'continent-flows',
        type: 'capital_flow',
        title: 'Regional Capital Flows',
        metrics: topFlows.map((f) => ({
          label: `${hubIndex.get(f.fromId) ?? f.fromId} → ${hubIndex.get(f.toId) ?? f.toId}`,
          value: fmtB(f.value),
          color: '#60a5fa',
        })),
      })
    }
  } else {
    // Graceful fallback: surface the available data
    sections.push({
      id: 'continent-fallback',
      type: 'macro_indicators',
      title: 'Continental Overview',
      metrics: [
        { label: 'Region', value: continentName },
        { label: 'Data', value: 'Detailed data not yet available.' },
      ],
    })
  }

  return {
    level: 1,
    scopeId: continentName,
    title: `${continentName}`,
    subtitle: 'Continental economic intelligence',
    sections,
  }
}

// ── Level 2 — Country Dashboard (stub — real data from countryDashboardMock) ─

/**
 * Returns a minimal country-level dashboard header.
 * The full dashboard content is rendered by CountryPanel which reads directly
 * from countryEconomicStore and economicStore.
 */
function buildCountryDashboard(isoCode: string): DashboardModel {
  return {
    level: 2,
    scopeId: isoCode,
    title: 'National Dashboard',
    subtitle: 'Country economic intelligence',
    sections: [],
  }
}

// ── Level 3 — Administrative Division Dashboard ───────────────────────────────

/**
 * Returns a minimal division-level dashboard header.
 * Full content is rendered by AdminDivisionPanel which reads from
 * adminDivisionMockData and countryEconomicStore.
 */
function buildAdminDivisionDashboard(countryIsoCode: string): DashboardModel {
  return {
    level: 3,
    scopeId: countryIsoCode,
    title: 'Regional Dashboard',
    subtitle: 'Administrative division intelligence',
    sections: [],
  }
}

// ── Public entry point ────────────────────────────────────────────────────────

/**
 * Compose the DashboardModel for the current zoom level and scope.
 * Each level has its own composition logic; sections are omitted when
 * the underlying data is unavailable (graceful degradation).
 */
export function buildDashboard(
  viewState: ViewState,
  worldData: WorldData,
  scope: ActiveScope,
): DashboardModel {
  switch (viewState.level) {
    case 0:
      return buildGlobalDashboard(worldData)

    case 1:
      return buildContinentDashboard(
        worldData,
        scope.type === 'continent' ? scope.continent : 'Global',
      )

    case 2:
      return buildCountryDashboard(
        scope.type === 'country' ? scope.isoCode : '',
      )

    case 3:
      return buildAdminDivisionDashboard(
        scope.type === 'division' ? scope.countryIsoCode
          : scope.type === 'country' ? scope.isoCode
          : '',
      )

    default:
      return buildGlobalDashboard(worldData)
  }
}
