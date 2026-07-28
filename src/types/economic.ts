export const ECONOMIC_SOURCE_IDS = ['worldBank', 'fred', 'imf', 'oecd'] as const

export type EconomicSourceId = (typeof ECONOMIC_SOURCE_IDS)[number]

/** Human-readable display names for each data source. */
export const ECONOMIC_SOURCE_NAMES: Record<EconomicSourceId, string> = {
  worldBank: 'World Bank',
  fred: 'FRED (Federal Reserve)',
  imf: 'IMF',
  oecd: 'OECD',
}

export type EconomicFrequency = 'realtime' | 'daily' | 'monthly' | 'quarterly' | 'annual'

export type EconomicIndicatorCode =
  | 'gdp'
  | 'gdpPerCapita'
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

/** Extended status reported by the SyncEngine layer (superset of SourceFetchStatus). */
export type ConnectorSyncStatus = SourceFetchStatus | 'rate-limited' | 'retrying'

export interface EconomicSourceState {
  // ── existing fields ──────────────────────────────────────────────────────
  status: SourceFetchStatus
  lastFetchedAt: string | null
  lastUpdatedAt: string | null
  isCached: boolean
  error: string | null
  recordCount: number
  // ── Phase 6.3: sync metadata ─────────────────────────────────────────────
  /** True while a network request for this source is in-flight. */
  loading: boolean
  /** ISO timestamp at which the current cache entry expires (null = no cache). */
  cacheExpires: string | null
  /** Fine-grained sync status including rate-limit and retry states. */
  connectorStatus: ConnectorSyncStatus
  /** Last error message; persisted across successful refreshes for diagnostics. */
  lastError: string | null
  /** Human-readable name of the data source. */
  sourceName: string
}

/** Configuration for the SyncEngine. */
export interface SyncEngineConfig {
  /** How often (ms) the scheduler polls for stale connectors. Default: 60 000. */
  autoRefreshIntervalMs?: number
  /** Minimum gap (ms) between refreshes of the same connector. Default: 30 000. */
  minRefreshIntervalMs?: number
  /** Per-request timeout (ms). Default: 15 000. */
  timeoutMs?: number
  /** Maximum retry attempts before marking a connector as error. Default: 3. */
  maxRetries?: number
  /** Base delay (ms) for exponential-backoff retries. Default: 1 000. */
  retryBaseDelayMs?: number
  /** Extra cooldown (ms) applied when a connector returns HTTP 429. Default: 60 000. */
  rateLimitBackoffMs?: number
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

export const createEmptyEconomicSourceState = (sourceName = ''): EconomicSourceState => ({
  status: 'idle',
  lastFetchedAt: null,
  lastUpdatedAt: null,
  isCached: false,
  error: null,
  recordCount: 0,
  // Phase 6.3
  loading: false,
  cacheExpires: null,
  connectorStatus: 'idle',
  lastError: null,
  sourceName,
})
