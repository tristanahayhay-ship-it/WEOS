import type { EconomicDataConnector, EconomicDataPoint, EconomicRawSnapshot } from '../types/economic'

interface WorldBankMockRecord {
  countryCode: string
  seriesCode: 'gdp' | 'population'
  latestValue: number
  date: string
  unit: string
  label: string
}

const WORLD_BANK_MOCK_RECORDS: WorldBankMockRecord[] = [
  {
    countryCode: 'US',
    seriesCode: 'gdp',
    latestValue: 27.36,
    date: '2024-12-31T00:00:00Z',
    unit: 'USD trillions',
    label: 'GDP (current US$)',
  },
  {
    countryCode: 'CN',
    seriesCode: 'gdp',
    latestValue: 17.79,
    date: '2024-12-31T00:00:00Z',
    unit: 'USD trillions',
    label: 'GDP (current US$)',
  },
  {
    countryCode: 'IN',
    seriesCode: 'population',
    latestValue: 1438069596,
    date: '2024-12-31T00:00:00Z',
    unit: 'people',
    label: 'Population, total',
  },
]

const normalizeWorldBankRecord = (
  record: WorldBankMockRecord,
  snapshot: EconomicRawSnapshot<WorldBankMockRecord>,
): EconomicDataPoint => ({
  key: `${snapshot.source}:${record.countryCode}:${record.seriesCode}`,
  countryCode: record.countryCode,
  indicator: record.seriesCode,
  value: record.latestValue,
  unit: record.unit,
  observedAt: record.date,
  source: snapshot.source,
  frequency: 'annual',
  isMock: snapshot.isMock,
  metadata: {
    label: record.label,
    provider: 'World Bank mock connector',
  },
})

export const worldBankConnector: EconomicDataConnector<WorldBankMockRecord> = {
  source: 'worldBank',
  fetchLatest: async () => ({
    source: 'worldBank',
    fetchedAt: '2026-01-15T00:00:00Z',
    records: WORLD_BANK_MOCK_RECORDS,
    isMock: true,
  }),
  normalize: (snapshot) => snapshot.records.map((record) => normalizeWorldBankRecord(record, snapshot)),
}
