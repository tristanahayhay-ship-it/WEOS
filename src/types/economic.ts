export interface CountryEconomicData {
  isoCode: string
  gdpUsd: number | null
  population: number | null
  gdpPerCapitaUsd: number | null
  inflationPct: number | null
  interestRatePct: number | null
  currency: string | null
  timeZone: string | null
}
