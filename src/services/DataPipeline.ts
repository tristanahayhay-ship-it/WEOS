import { fredConnector } from '../dataSources/fred'
import { imfConnector } from '../dataSources/imf'
import { oecdConnector } from '../dataSources/oecd'
import { worldBankConnector } from '../dataSources/worldBank'
import { useRealtimeStore } from '../stores/realtimeStore'
import type {
  DataPipelineRunResult,
  EconomicCacheEntry,
  EconomicDataConnector,
  EconomicDataPoint,
  EconomicSourceId,
} from '../types/economic'
import { ECONOMIC_SOURCE_NAMES } from '../types/economic'

const DEFAULT_CACHE_TTL_MS = 5 * 60 * 1000

type RegisteredConnector = EconomicDataConnector<any>

const DEFAULT_CONNECTORS: Record<EconomicSourceId, RegisteredConnector> = {
  worldBank: worldBankConnector,
  fred: fredConnector,
  imf: imfConnector,
  oecd: oecdConnector,
}

export class DataPipeline {
  private readonly connectors: Record<EconomicSourceId, RegisteredConnector>

  private readonly cacheTtlMs: number

  private readonly cache = new Map<EconomicSourceId, EconomicCacheEntry>()

  constructor(connectors: Record<EconomicSourceId, RegisteredConnector> = DEFAULT_CONNECTORS, cacheTtlMs = DEFAULT_CACHE_TTL_MS) {
    this.connectors = connectors
    this.cacheTtlMs = cacheTtlMs
  }

  async refreshSource(source: EconomicSourceId): Promise<DataPipelineRunResult> {
    const store = useRealtimeStore.getState()
    const cachedEntry = this.cache.get(source)
    const now = Date.now()

    store.setSourceState(source, {
      status: 'fetching',
      loading: true,
      error: null,
      isCached: false,
      sourceName: ECONOMIC_SOURCE_NAMES[source],
    })

    if (cachedEntry && cachedEntry.expiresAt > now) {
      return this.applyRecords(source, cachedEntry.records, cachedEntry.fetchedAt, true, cachedEntry.expiresAt)
    }

    const expiresAt = now + this.cacheTtlMs
    const snapshot = await this.connectors[source].fetchLatest()
    const normalizedRecords = this.connectors[source].normalize(snapshot)

    this.cache.set(source, {
      source,
      fetchedAt: snapshot.fetchedAt,
      expiresAt,
      records: normalizedRecords,
    })

    return this.applyRecords(source, normalizedRecords, snapshot.fetchedAt, false, expiresAt)
  }

  async refreshAll(sources: EconomicSourceId[] = Object.keys(this.connectors) as EconomicSourceId[]): Promise<DataPipelineRunResult[]> {
    const results: DataPipelineRunResult[] = []

    for (const source of sources) {
      try {
        results.push(await this.refreshSource(source))
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown realtime data pipeline error'
        useRealtimeStore.getState().setSourceState(source, {
          status: 'error',
          loading: false,
          error: message,
          isCached: false,
          sourceName: ECONOMIC_SOURCE_NAMES[source],
        })
      }
    }

    return results
  }

  clearCache(source?: EconomicSourceId): void {
    if (source) {
      this.cache.delete(source)
      return
    }

    this.cache.clear()
  }

  getCachedRecords(source: EconomicSourceId): EconomicDataPoint[] | null {
    const cachedEntry = this.cache.get(source)
    if (!cachedEntry || cachedEntry.expiresAt <= Date.now()) {
      return null
    }

    return cachedEntry.records
  }

  /**
   * Returns the Unix epoch (ms) at which the cache entry for `source` expires,
   * or `null` if there is no valid cache entry.
   */
  getCacheExpiry(source: EconomicSourceId): number | null {
    const cachedEntry = this.cache.get(source)
    if (!cachedEntry || cachedEntry.expiresAt <= Date.now()) {
      return null
    }

    return cachedEntry.expiresAt
  }

  private applyRecords(
    source: EconomicSourceId,
    records: EconomicDataPoint[],
    fetchedAt: string,
    fromCache: boolean,
    expiresAt: number,
  ): DataPipelineRunResult {
    const store = useRealtimeStore.getState()
    const updatedAt = new Date().toISOString()

    store.replaceSourceRecords(source, records)
    store.setSourceState(source, {
      status: 'ready',
      loading: false,
      lastFetchedAt: fetchedAt,
      lastUpdatedAt: updatedAt,
      isCached: fromCache,
      error: null,
      recordCount: records.length,
      cacheExpires: new Date(expiresAt).toISOString(),
      sourceName: ECONOMIC_SOURCE_NAMES[source],
    })
    store.setLastPipelineRunAt(updatedAt)

    return {
      source,
      records,
      fromCache,
    }
  }
}

export const realtimeDataPipeline = new DataPipeline()
