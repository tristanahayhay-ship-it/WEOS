import { ECONOMIC_DATA_BY_ISO } from '../data/economicData'
import type { CountryEconomicData } from '../types/country'
import type { EconomicDataPoint, EconomicIndicatorCode } from '../types/economic'

const INDICATOR_TO_FIELD: Partial<Record<EconomicIndicatorCode, keyof CountryEconomicData>> = {
  gdp: 'gdpUsd',
  gdpPerCapita: 'gdpPerCapitaUsd',
  population: 'population',
  inflation: 'inflationPercent',
  interestRate: 'interestRatePercent',
}

const toTimestamp = (value: string): number => {
  const parsed = Date.parse(value)
  return Number.isNaN(parsed) ? -1 : parsed
}

const createFallbackCountryEconomicData = (isoCode: string): CountryEconomicData => ({
  isoCode,
  population: null,
  gdpUsd: null,
  gdpPerCapitaUsd: null,
  inflationPercent: null,
  interestRatePercent: null,
  currency: null,
  currencyCode: null,
  timeZones: [],
})

export function getLatestRealtimeRecordsByIndicator(
  records: Record<string, EconomicDataPoint>,
  countryCode: string,
): Partial<Record<EconomicIndicatorCode, EconomicDataPoint>> {
  const latest: Partial<Record<EconomicIndicatorCode, EconomicDataPoint>> = {}

  for (const record of Object.values(records)) {
    if (record.countryCode !== countryCode) continue

    const previous = latest[record.indicator]
    const currentObservedAt = toTimestamp(record.observedAt)
    const previousObservedAt = previous ? toTimestamp(previous.observedAt) : -1
    if (!previous || currentObservedAt >= previousObservedAt) {
      latest[record.indicator] = record
    }
  }

  return latest
}

export function buildRealtimeEconomicMap(
  records: Record<string, EconomicDataPoint>,
  fallbackMap: ReadonlyMap<string, CountryEconomicData> = ECONOMIC_DATA_BY_ISO,
): ReadonlyMap<string, CountryEconomicData> {
  const next = new Map<string, CountryEconomicData>()

  for (const [isoCode, fallback] of fallbackMap.entries()) {
    next.set(isoCode, { ...fallback })
  }

  const latestObservedAtByIndicator = new Map<string, number>()

  for (const record of Object.values(records)) {
    const field = INDICATOR_TO_FIELD[record.indicator]
    if (!field || record.value == null) continue

    const indicatorKey = `${record.countryCode}:${record.indicator}`
    const currentObservedAt = toTimestamp(record.observedAt)
    const previousObservedAt = latestObservedAtByIndicator.get(indicatorKey) ?? -1
    if (currentObservedAt < previousObservedAt) continue

    latestObservedAtByIndicator.set(indicatorKey, currentObservedAt)

    const existing = next.get(record.countryCode) ?? createFallbackCountryEconomicData(record.countryCode)
    next.set(record.countryCode, {
      ...existing,
      [field]: record.value,
    })
  }

  return next
}
