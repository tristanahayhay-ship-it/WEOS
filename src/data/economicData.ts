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
const POPULATION_DENSITY_MULTIPLIER = 120
const LONGITUDE_GDP_MULTIPLIER = 180
const INFLATION_BASE_PCT = 2
const INFLATION_LONGITUDE_MODULO = 8
const INFLATION_LONGITUDE_MULTIPLIER = 0.35
const INTEREST_RATE_BASE_PCT = 1
const INTEREST_RATE_AREA_MODULO = 25
const INTEREST_RATE_AREA_MULTIPLIER = 0.2

function estimateTimeZone(offsetHours: number): string {
  const rounded = Math.round(offsetHours)
  if (rounded === 0) return 'UTC+00:00'
  const sign = rounded > 0 ? '+' : '-'
  return `UTC${sign}${String(Math.abs(rounded)).padStart(2, '0')}:00`
}

function buildPlaceholderEconomicData(isoCode: string, longitude: number, area: number, continent: keyof typeof CURRENCY_BY_CONTINENT): CountryEconomicData {
  const estimatedPopulation = Math.max(50_000, Math.round(area * POPULATION_DENSITY_MULTIPLIER))
  const gdpPerCapitaUsd = 12_000 + Math.round(Math.abs(longitude) * LONGITUDE_GDP_MULTIPLIER)
  const gdpUsd = estimatedPopulation * gdpPerCapitaUsd

  return {
    isoCode,
    gdpUsd,
    population: estimatedPopulation,
    gdpPerCapitaUsd,
    inflationPct: Number(
      (
        INFLATION_BASE_PCT
        + (Math.abs(longitude) % INFLATION_LONGITUDE_MODULO) * INFLATION_LONGITUDE_MULTIPLIER
      ).toFixed(1),
    ),
    interestRatePct: Number(
      (
        INTEREST_RATE_BASE_PCT
        + (area % INTEREST_RATE_AREA_MODULO) * INTEREST_RATE_AREA_MULTIPLIER
      ).toFixed(1),
    ),
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
