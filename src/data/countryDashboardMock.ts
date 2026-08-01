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
}

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

  return {
    gdpGrowthPercent: seeded(country.isoCode, 6, -1.2, 7.4),
    inflationPercent: inflation,
    interestRatePercent: interest,
    unemploymentPercent: seeded(country.isoCode, 7, 2.4, 14.5),
    pmi: seeded(country.isoCode, 8, 45, 58, 1),
    publicDebtPercentGdp: seeded(country.isoCode, 9, 28, 132),
    exportsUsdB,
    importsUsdB,
    fxReservesUsdB: Number((Math.max(gdp * seeded(country.isoCode, 10, 0.08, 0.42), 5)).toFixed(2)),
    creditRating: CREDIT_RATINGS[hashIso(country.isoCode) % CREDIT_RATINGS.length] ?? 'BBB',
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
  }
}
