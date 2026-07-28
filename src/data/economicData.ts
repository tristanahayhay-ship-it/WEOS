import { COUNTRIES } from './countries'
import type { CountryEconomicData } from '../types/economic'

const CURRENCY_BY_CONTINENT = {
  Africa: 'XAF',
  Antarctica: 'USD',
  Asia: 'USD',
  Europe: 'EUR',
  'North America': 'USD',
  Oceania: 'AUD',
  'South America': 'USD',
} as const

function estimateTimeZone(offsetHours: number): string {
  const rounded = Math.round(offsetHours)
  if (rounded === 0) return 'UTC+00:00'
  const sign = rounded > 0 ? '+' : '-'
  return `UTC${sign}${String(Math.abs(rounded)).padStart(2, '0')}:00`
}

function buildPlaceholderEconomicData(isoCode: string, longitude: number, area: number, continent: keyof typeof CURRENCY_BY_CONTINENT): CountryEconomicData {
  const estimatedPopulation = Math.max(50_000, Math.round(area * 120))
  const gdpPerCapitaUsd = 12_000 + Math.round(Math.abs(longitude) * 180)
  const gdpUsd = estimatedPopulation * gdpPerCapitaUsd

  return {
    isoCode,
    gdpUsd,
    population: estimatedPopulation,
    gdpPerCapitaUsd,
    inflationPct: Number((2 + (Math.abs(longitude) % 8) * 0.35).toFixed(1)),
    interestRatePct: Number((1 + (area % 25) * 0.2).toFixed(1)),
    currency: CURRENCY_BY_CONTINENT[continent],
    timeZone: estimateTimeZone(longitude / 15),
  }
}

export const COUNTRY_ECONOMIC_DATA: ReadonlyMap<string, CountryEconomicData> = new Map(
  COUNTRIES.map((country) => [
    country.isoCode,
    buildPlaceholderEconomicData(
      country.isoCode,
      country.center[0],
      country.area,
      country.continent,
    ),
  ]),
)
