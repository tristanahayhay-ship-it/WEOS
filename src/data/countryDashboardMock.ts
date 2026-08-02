import type { Country, CountryEconomicData } from '../types/country'

export interface CountryDashboardChartPoint {
  label: string
  value: number
}

export interface CountryDashboardCompany {
  name: string
  marketCapUsdB: number
  industry: string
  headquarters: string
}

export interface CountryDashboardSector {
  name: 'Finance' | 'Technology' | 'Manufacturing' | 'Energy' | 'Healthcare' | 'Consumer' | 'Agriculture'
  sharePercent: number
}

export interface CountryDashboardNewsItem {
  category: 'economic' | 'policy' | 'market'
  title: string
  source: string
  time: string
}

export interface CountryDashboardSummary {
  economicHealth: 'Strong' | 'Stable' | 'Watching'
  growthTrend: 'Upward' | 'Flat' | 'Cooling'
  riskLevel: 'Low' | 'Medium' | 'High'
  capitalFlowStatus: 'Inflow' | 'Balanced' | 'Outflow'
}

// ── Indicator group types ─────────────────────────────────────────────────────

export type IndicatorGroupId =
  | 'growth_output'
  | 'inflation_prices'
  | 'labour_market'
  | 'money_banking'
  | 'business_production'
  | 'consumer_market'
  | 'trade_external'
  | 'government_finance'
  | 'housing'
  | 'taxes'
  | 'energy_commodities'
  | 'risk_stability'
  | 'digital_innovation'
  | 'infrastructure_logistics'
  | 'corporate_health'
  | 'competitiveness'
  | 'human_capital'
  | 'health_welfare'
  | 'green_transition'
  | 'geopolitics'

export interface IndicatorMetric {
  label: string
  value: string
  /** Optional CSS colour — green for positive, red for risk */
  color?: string
}

export interface IndicatorGroup {
  id: IndicatorGroupId
  title: string
  /** Metrics that have data available — empty array means the group is hidden */
  metrics: IndicatorMetric[]
}

export interface CountryDashboardData {
  gdpGrowthPercent: number
  inflationPercent: number | null
  interestRatePercent: number | null
  unemploymentPercent: number | null
  pmi: number
  publicDebtPercentGdp: number
  exportsUsdB: number
  importsUsdB: number
  fxReservesUsdB: number
  creditRating: string
  gdpChart: CountryDashboardChartPoint[]
  inflationChart: CountryDashboardChartPoint[]
  interestRateChart: CountryDashboardChartPoint[]
  tradeBalanceChart: CountryDashboardChartPoint[]
  topCompanies: CountryDashboardCompany[]
  sectors: CountryDashboardSector[]
  news: CountryDashboardNewsItem[]
  summary: CountryDashboardSummary
  /**
   * Clustered indicator groups — only groups with at least one available metric
   * are included.  Render only what is present; hide unavailable groups entirely.
   */
  indicatorGroups: IndicatorGroup[]
}

// ── Helpers ───────────────────────────────────────────────────────────────────

const INDUSTRIES = ['Finance', 'Technology', 'Manufacturing', 'Energy', 'Healthcare', 'Consumer', 'Agriculture'] as const
const CREDIT_RATINGS = ['AAA', 'AA+', 'AA', 'AA-', 'A+', 'A', 'A-', 'BBB+', 'BBB'] as const

function hashIso(isoCode: string) {
  return Array.from(isoCode).reduce((acc, char) => acc + char.charCodeAt(0), 0)
}

function seeded(isoCode: string, offset: number, min: number, max: number, decimals = 2) {
  const hash = hashIso(isoCode) + offset * 37
  const value = min + ((Math.sin(hash) + 1) / 2) * (max - min)
  return Number(value.toFixed(decimals))
}

function makeTrend(isoCode: string, start: number, volatility: number, labels: string[]) {
  return labels.map((label, index) => ({
    label,
    value: Number((start + seeded(isoCode, index + label.length, -volatility, volatility)).toFixed(2)),
  }))
}

function fmtB(value: number | null): string {
  if (value == null) return '—'
  if (value >= 1000) return `$${(value / 1000).toFixed(2)}T`
  return `$${value.toFixed(1)}B`
}

function fmtRate(value: number | null): string {
  if (value == null) return '—'
  return `${value.toFixed(2)}%`
}

function fmtPop(value: number | null): string {
  if (value == null) return '—'
  if (value >= 1e9) return `${(value / 1e9).toFixed(2)}B`
  if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`
  if (value >= 1e3) return `${(value / 1e3).toFixed(0)}K`
  return String(value)
}

/** Build only the indicator groups that have real data — hide everything else. */
function buildIndicatorGroups(
  country: Country,
  economic: CountryEconomicData | null,
  derived: {
    gdpGrowthPercent: number
    inflationPercent: number
    interestRatePercent: number
    unemploymentPercent: number
    pmi: number
    publicDebtPercentGdp: number
    exportsUsdB: number
    importsUsdB: number
    fxReservesUsdB: number
    creditRating: string
  },
): IndicatorGroup[] {
  const groups: IndicatorGroup[] = []

  // ── 1. Growth & Output ────────────────────────────────────────────────────
  const growthMetrics: IndicatorMetric[] = []
  if (economic?.gdpUsd != null) {
    growthMetrics.push({ label: 'GDP', value: fmtB(economic.gdpUsd) })
  }
  growthMetrics.push({
    label: 'GDP Growth',
    value: fmtRate(derived.gdpGrowthPercent),
    color: derived.gdpGrowthPercent >= 0 ? '#34d399' : '#f87171',
  })
  if (economic?.gdpPerCapitaUsd != null) {
    growthMetrics.push({
      label: 'GDP per Capita',
      value: `$${Math.round(economic.gdpPerCapitaUsd).toLocaleString('en-US')}`,
    })
  }
  if (growthMetrics.length > 0) {
    groups.push({ id: 'growth_output', title: 'Growth & Output', metrics: growthMetrics })
  }

  // ── 2. Inflation & Prices ─────────────────────────────────────────────────
  if (derived.inflationPercent != null) {
    const inflColor = derived.inflationPercent <= 4 ? '#34d399' : derived.inflationPercent <= 8 ? '#f59e0b' : '#f87171'
    groups.push({
      id: 'inflation_prices',
      title: 'Inflation & Prices',
      metrics: [{ label: 'Inflation Rate (CPI)', value: fmtRate(derived.inflationPercent), color: inflColor }],
    })
  }

  // ── 3. Labour Market ──────────────────────────────────────────────────────
  if (derived.unemploymentPercent != null) {
    const uColor = derived.unemploymentPercent <= 5 ? '#34d399' : derived.unemploymentPercent <= 10 ? '#f59e0b' : '#f87171'
    const labourMetrics: IndicatorMetric[] = [
      { label: 'Unemployment Rate', value: fmtRate(derived.unemploymentPercent), color: uColor },
    ]
    if (economic?.population != null) {
      labourMetrics.push({ label: 'Population', value: fmtPop(economic.population) })
    }
    groups.push({ id: 'labour_market', title: 'Labour Market', metrics: labourMetrics })
  }

  // ── 4. Money & Banking ────────────────────────────────────────────────────
  const moneyMetrics: IndicatorMetric[] = []
  if (economic?.interestRatePercent != null) {
    moneyMetrics.push({ label: 'Interest Rate', value: fmtRate(economic.interestRatePercent) })
  } else if (derived.interestRatePercent != null) {
    moneyMetrics.push({ label: 'Interest Rate (est.)', value: fmtRate(derived.interestRatePercent) })
  }
  if (derived.fxReservesUsdB > 0) {
    moneyMetrics.push({ label: 'FX Reserves', value: fmtB(derived.fxReservesUsdB) })
  }
  if (economic?.currencyCode != null && economic.currency != null) {
    moneyMetrics.push({ label: 'Currency', value: `${economic.currency} (${economic.currencyCode})` })
  }
  if (moneyMetrics.length > 0) {
    groups.push({ id: 'money_banking', title: 'Money & Banking', metrics: moneyMetrics })
  }

  // ── 5. Business & Production ──────────────────────────────────────────────
  groups.push({
    id: 'business_production',
    title: 'Business & Production',
    metrics: [
      { label: 'PMI (est.)', value: derived.pmi.toFixed(1), color: derived.pmi >= 50 ? '#34d399' : '#f87171' },
    ],
  })

  // ── 7. Trade & External ───────────────────────────────────────────────────
  const tradeBalance = derived.exportsUsdB - derived.importsUsdB
  groups.push({
    id: 'trade_external',
    title: 'Trade & External',
    metrics: [
      { label: 'Exports', value: fmtB(derived.exportsUsdB) },
      { label: 'Imports', value: fmtB(derived.importsUsdB) },
      {
        label: 'Trade Balance',
        value: `${tradeBalance >= 0 ? '+' : ''}${fmtB(tradeBalance)}`,
        color: tradeBalance >= 0 ? '#34d399' : '#f87171',
      },
    ],
  })

  // ── 8. Government Finance ─────────────────────────────────────────────────
  groups.push({
    id: 'government_finance',
    title: 'Government Finance',
    metrics: [
      {
        label: 'Public Debt / GDP',
        value: fmtRate(derived.publicDebtPercentGdp),
        color: derived.publicDebtPercentGdp < 60 ? '#34d399' : derived.publicDebtPercentGdp < 100 ? '#f59e0b' : '#f87171',
      },
      { label: 'Credit Rating', value: derived.creditRating },
    ],
  })

  // ── 20. Geopolitics / Risk & Stability ────────────────────────────────────
  // Derived from inflation + debt as a simple composite proxy
  const riskProxy = (derived.inflationPercent / 20 + derived.publicDebtPercentGdp / 200) / 2
  const riskLabel = riskProxy < 0.3 ? 'Low' : riskProxy < 0.6 ? 'Moderate' : 'Elevated'
  const riskColor = riskProxy < 0.3 ? '#34d399' : riskProxy < 0.6 ? '#f59e0b' : '#f87171'
  groups.push({
    id: 'risk_stability',
    title: 'Risk & Stability',
    metrics: [
      { label: 'Risk Indicator', value: riskLabel, color: riskColor },
      { label: 'Country', value: `${country.englishName} (${country.isoCode})` },
    ],
  })

  return groups
}

export function buildCountryDashboardMock(country: Country, economic: CountryEconomicData | null): CountryDashboardData {
  const gdp = economic?.gdpUsd ?? seeded(country.isoCode, 1, 25, 2200)
  const inflation = economic?.inflationPercent ?? seeded(country.isoCode, 2, 1.5, 10)
  const interest = economic?.interestRatePercent ?? seeded(country.isoCode, 3, 0.5, 9)

  const exportsUsdB = Number((Math.max(gdp * seeded(country.isoCode, 4, 0.18, 0.55), 8)).toFixed(2))
  const importsUsdB = Number((Math.max(gdp * seeded(country.isoCode, 5, 0.16, 0.58), 8)).toFixed(2))
  const tradeBalance = exportsUsdB - importsUsdB

  const years = ['2019', '2020', '2021', '2022', '2023', '2024']
  const months = ['Jan', 'Mar', 'May', 'Jul', 'Sep', 'Nov']

  const topCompanies: CountryDashboardCompany[] = Array.from({ length: 5 }, (_, index) => {
    const industry = INDUSTRIES[(hashIso(country.isoCode) + index) % INDUSTRIES.length]
    const shortName = country.englishName.split(' ')[0] ?? country.englishName
    return {
      name: `${shortName} ${industry} Group ${index + 1}`,
      marketCapUsdB: Number((seeded(country.isoCode, 40 + index, 15, 650)).toFixed(2)),
      industry,
      headquarters: country.capital,
    }
  })

  const sectorWeights = [22, 19, 17, 14, 11, 10, 7]
  const sectorShift = hashIso(country.isoCode) % sectorWeights.length
  const sectors: CountryDashboardSector[] = INDUSTRIES.map((name, index) => {
    const weight = sectorWeights[(index + sectorShift) % sectorWeights.length] ?? 10
    return {
      name,
      sharePercent: weight,
    }
  })

  const summary: CountryDashboardSummary = {
    economicHealth: inflation < 4.5 ? 'Strong' : inflation < 8 ? 'Stable' : 'Watching',
    growthTrend: seeded(country.isoCode, 90, -0.5, 0.8) > 0.2 ? 'Upward' : seeded(country.isoCode, 91, -0.8, 0.5) < -0.2 ? 'Cooling' : 'Flat',
    riskLevel: seeded(country.isoCode, 92, 0, 1) > 0.7 ? 'High' : seeded(country.isoCode, 93, 0, 1) > 0.35 ? 'Medium' : 'Low',
    capitalFlowStatus: tradeBalance > 30 ? 'Inflow' : tradeBalance < -30 ? 'Outflow' : 'Balanced',
  }

  const gdpGrowthPercent = seeded(country.isoCode, 6, -1.2, 7.4)
  const unemploymentPercent = seeded(country.isoCode, 7, 2.4, 14.5)
  const pmi = seeded(country.isoCode, 8, 45, 58, 1)
  const publicDebtPercentGdp = seeded(country.isoCode, 9, 28, 132)
  const fxReservesUsdB = Number((Math.max(gdp * seeded(country.isoCode, 10, 0.08, 0.42), 5)).toFixed(2))
  const creditRating = CREDIT_RATINGS[hashIso(country.isoCode) % CREDIT_RATINGS.length] ?? 'BBB'

  const indicatorGroups = buildIndicatorGroups(country, economic, {
    gdpGrowthPercent,
    inflationPercent: inflation,
    interestRatePercent: interest,
    unemploymentPercent,
    pmi,
    publicDebtPercentGdp,
    exportsUsdB,
    importsUsdB,
    fxReservesUsdB,
    creditRating,
  })

  return {
    gdpGrowthPercent,
    inflationPercent: inflation,
    interestRatePercent: interest,
    unemploymentPercent,
    pmi,
    publicDebtPercentGdp,
    exportsUsdB,
    importsUsdB,
    fxReservesUsdB,
    creditRating,
    gdpChart: makeTrend(country.isoCode, gdp * 0.72, gdp * 0.12, years),
    inflationChart: makeTrend(country.isoCode, inflation, 1.4, years),
    interestRateChart: makeTrend(country.isoCode, interest, 1.1, years),
    tradeBalanceChart: makeTrend(country.isoCode, tradeBalance, Math.max(Math.abs(tradeBalance) * 0.45, 6), months),
    topCompanies,
    sectors,
    news: [
      {
        category: 'economic',
        title: `${country.englishName} updates quarterly economic outlook`,
        source: 'WEOS Macro Desk',
        time: '2h ago',
      },
      {
        category: 'policy',
        title: `${country.capital} announces new fiscal policy package`,
        source: 'Policy Monitor',
        time: '5h ago',
      },
      {
        category: 'market',
        title: `Market indices in ${country.englishName} close mixed on trade data`,
        source: 'Market Wire',
        time: '9h ago',
      },
    ],
    summary,
    indicatorGroups,
  }
}
