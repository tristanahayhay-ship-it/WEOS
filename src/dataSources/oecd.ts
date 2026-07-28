import type { EconomicDataConnector, EconomicDataPoint, EconomicRawSnapshot } from '../types/economic'

interface OecdMockRecord {
  location: string
  subject: 'industrialProduction' | 'unemployment'
  timePeriod: string
  obsValue: number
  measureUnit: string
  frequency: 'monthly' | 'quarterly'
}

const OECD_MOCK_RECORDS: OecdMockRecord[] = [
  {
    location: 'FR',
    subject: 'industrialProduction',
    timePeriod: '2026-01-01T00:00:00Z',
    obsValue: 101.8,
    measureUnit: 'index',
    frequency: 'monthly',
  },
  {
    location: 'GB',
    subject: 'unemployment',
    timePeriod: '2026-01-01T00:00:00Z',
    obsValue: 4.2,
    measureUnit: 'percent',
    frequency: 'monthly',
  },
  {
    location: 'CA',
    subject: 'industrialProduction',
    timePeriod: '2025-10-01T00:00:00Z',
    obsValue: 99.4,
    measureUnit: 'index',
    frequency: 'quarterly',
  },
]

const normalizeOecdRecord = (
  record: OecdMockRecord,
  snapshot: EconomicRawSnapshot<OecdMockRecord>,
): EconomicDataPoint => ({
  key: `${snapshot.source}:${record.location}:${record.subject}:${record.timePeriod}`,
  countryCode: record.location,
  indicator: record.subject,
  value: record.obsValue,
  unit: record.measureUnit,
  observedAt: record.timePeriod,
  source: snapshot.source,
  frequency: record.frequency,
  isMock: snapshot.isMock,
  metadata: {
    provider: 'OECD mock connector',
  },
})

export const oecdConnector: EconomicDataConnector<OecdMockRecord> = {
  source: 'oecd',
  fetchLatest: async () => ({
    source: 'oecd',
    fetchedAt: '2026-01-15T00:15:00Z',
    records: OECD_MOCK_RECORDS,
    isMock: true,
  }),
  normalize: (snapshot) => snapshot.records.map((record) => normalizeOecdRecord(record, snapshot)),
}
