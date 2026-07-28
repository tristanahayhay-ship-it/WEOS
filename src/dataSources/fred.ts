import type { EconomicDataConnector, EconomicDataPoint, EconomicRawSnapshot } from '../types/economic'

interface FredMockRecord {
  seriesId: keyof typeof SERIES_TO_INDICATOR
  countryCode: string
  observationDate: string
  value: number
  units: string
}

const SERIES_TO_INDICATOR = {
  'US-CPI': 'inflation',
  'US-FEDFUNDS': 'interestRate',
  'DE-IR3TIB': 'interestRate',
} as const

const FRED_MOCK_RECORDS: FredMockRecord[] = [
  {
    seriesId: 'US-CPI',
    countryCode: 'US',
    observationDate: '2026-01-01T00:00:00Z',
    value: 2.7,
    units: 'percent',
  },
  {
    seriesId: 'US-FEDFUNDS',
    countryCode: 'US',
    observationDate: '2026-01-01T00:00:00Z',
    value: 4.5,
    units: 'percent',
  },
  {
    seriesId: 'DE-IR3TIB',
    countryCode: 'DE',
    observationDate: '2026-01-01T00:00:00Z',
    value: 3.1,
    units: 'percent',
  },
]

const normalizeFredRecord = (
  record: FredMockRecord,
  snapshot: EconomicRawSnapshot<FredMockRecord>,
): EconomicDataPoint => ({
  key: `${snapshot.source}:${record.countryCode}:${record.seriesId}`,
  countryCode: record.countryCode,
  indicator: SERIES_TO_INDICATOR[record.seriesId],
  value: record.value,
  unit: record.units,
  observedAt: record.observationDate,
  source: snapshot.source,
  frequency: 'monthly',
  isMock: snapshot.isMock,
  metadata: {
    seriesId: record.seriesId,
    provider: 'FRED mock connector',
  },
})

export const fredConnector: EconomicDataConnector<FredMockRecord> = {
  source: 'fred',
  fetchLatest: async () => ({
    source: 'fred',
    fetchedAt: '2026-01-15T00:05:00Z',
    records: FRED_MOCK_RECORDS,
    isMock: true,
  }),
  normalize: (snapshot) => snapshot.records.map((record) => normalizeFredRecord(record, snapshot)),
}
