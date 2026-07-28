export const ECONOMIC_SOURCE_IDS = ['worldBank', 'fred', 'imf', 'oecd'] as const

export type EconomicSourceId = (typeof ECONOMIC_SOURCE_IDS)[number]

export type EconomicFrequency = 'realtime' | 'daily' | 'monthly' | 'quarterly' | 'annual'

export type EconomicIndicatorCode =
  | 'gdp'
  | 'inflation'
  | 'interestRate'
  | 'population'
  | 'unemployment'
  | 'industrialProduction'

export type EconomicMetadataValue = string | number | boolean | null

export interface EconomicDataPoint {
  key: string
  countryCode: string
  indicator: EconomicIndicatorCode
  value: number | null
  unit: string
  observedAt: string
  source: EconomicSourceId
  frequency: EconomicFrequency
  isMock: boolean
  metadata: Record<string, EconomicMetadataValue>
}

export interface EconomicRawSnapshot<TRawRecord> {
  source: EconomicSourceId
  fetchedAt: string
  records: TRawRecord[]
  isMock: boolean
}

export interface EconomicDataConnector<TRawRecord = unknown> {
  readonly source: EconomicSourceId
  fetchLatest: () => Promise<EconomicRawSnapshot<TRawRecord>>
  normalize: (snapshot: EconomicRawSnapshot<TRawRecord>) => EconomicDataPoint[]
}

export type SourceFetchStatus = 'idle' | 'fetching' | 'ready' | 'error'

export interface EconomicSourceState {
  status: SourceFetchStatus
  lastFetchedAt: string | null
  lastUpdatedAt: string | null
  isCached: boolean
  error: string | null
  recordCount: number
}

export interface EconomicCacheEntry {
  source: EconomicSourceId
  fetchedAt: string
  expiresAt: number
  records: EconomicDataPoint[]
}

export interface DataPipelineRunResult {
  source: EconomicSourceId
  records: EconomicDataPoint[]
  fromCache: boolean
}

export const createEmptyEconomicSourceState = (): EconomicSourceState => ({
  status: 'idle',
  lastFetchedAt: null,
  lastUpdatedAt: null,
  isCached: false,
  error: null,
  recordCount: 0,
})
