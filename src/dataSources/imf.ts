import type { EconomicDataConnector, EconomicDataPoint, EconomicRawSnapshot } from '../types/economic'

interface ImfMockRecord {
  member: string
  indicator: 'inflation' | 'unemployment'
  period: string
  value: number
  unitName: string
  dataset: string
}

const IMF_MOCK_RECORDS: ImfMockRecord[] = [
  {
    member: 'JP',
    indicator: 'inflation',
    period: '2026-01-01T00:00:00Z',
    value: 2.1,
    unitName: 'percent',
    dataset: 'IFS',
  },
  {
    member: 'BR',
    indicator: 'inflation',
    period: '2026-01-01T00:00:00Z',
    value: 4.4,
    unitName: 'percent',
    dataset: 'IFS',
  },
  {
    member: 'ZA',
    indicator: 'unemployment',
    period: '2026-01-01T00:00:00Z',
    value: 32.2,
    unitName: 'percent',
    dataset: 'WEO',
  },
]

const normalizeImfRecord = (
  record: ImfMockRecord,
  snapshot: EconomicRawSnapshot<ImfMockRecord>,
): EconomicDataPoint => ({
  key: `${snapshot.source}:${record.member}:${record.indicator}`,
  countryCode: record.member,
  indicator: record.indicator,
  value: record.value,
  unit: record.unitName,
  observedAt: record.period,
  source: snapshot.source,
  frequency: 'monthly',
  isMock: snapshot.isMock,
  metadata: {
    dataset: record.dataset,
    provider: 'IMF mock connector',
  },
})

export const imfConnector: EconomicDataConnector<ImfMockRecord> = {
  source: 'imf',
  fetchLatest: async () => ({
    source: 'imf',
    fetchedAt: '2026-01-15T00:10:00Z',
    records: IMF_MOCK_RECORDS,
    isMock: true,
  }),
  normalize: (snapshot) => snapshot.records.map((record) => normalizeImfRecord(record, snapshot)),
}
