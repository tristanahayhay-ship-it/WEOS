/** Geographic continents */
export type Continent =
  | 'Africa'
  | 'Asia'
  | 'Europe'
  | 'North America'
  | 'South America'
  | 'Oceania'
  | 'Antarctica'

/**
 * Core country model.
 * `numericCode` matches the ISO 3166-1 numeric ID used as feature IDs
 * in the world-atlas/countries-110m.json topology.
 */
export interface Country {
  /** ISO 3166-1 numeric code — matches world-atlas topojson feature IDs */
  numericCode: number
  /** ISO 3166-1 alpha-2 (e.g. "US") */
  isoCode: string
  /** ISO 3166-1 alpha-3 (e.g. "USA") */
  iso3Code: string
  /** Display name */
  name: string
  /** English official name */
  englishName: string
  /** Capital city */
  capital: string
  /** Continent */
  continent: Continent
  /** Approximate geographic center [longitude, latitude] */
  center: [number, number]
  /** Area in km² */
  area: number
}

/**
 * Economic data attachment.
 * Designed to be fetched and attached at runtime in future phases
 * without requiring changes to the Country model itself.
 *
 * All numeric fields are in standard units:
 *   gdpUsd          — current USD billions
 *   gdpPerCapitaUsd — current USD
 *   inflationPercent    — annual CPI inflation rate (%)
 *   interestRatePercent — central-bank policy/benchmark rate (%)
 */
export interface CountryEconomicData {
  isoCode: string
  population: number | null
  gdpUsd: number | null
  gdpPerCapitaUsd: number | null
  inflationPercent: number | null
  interestRatePercent: number | null
  /** Primary currency name (e.g. "US Dollar") */
  currency: string | null
  /** ISO 4217 currency code (e.g. "USD") */
  currencyCode: string | null
  /** Representative IANA time-zone identifier(s) */
  timeZones: string[]
}
