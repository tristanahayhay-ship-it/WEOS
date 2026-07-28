/**
 * SyncEngine – Phase 6.3: Economic Data Synchronization Engine
 *
 * Wraps the DataPipeline and adds:
 *   - Refresh Scheduler      – polls for stale connectors and triggers background refresh
 *   - TTL Cache              – delegates to DataPipeline; skips refresh when cache is valid
 *   - Retry Policy           – exponential-backoff retry on transient failures
 *   - Request Timeout        – per-request timeout via Promise.race
 *   - Connector Status       – updates realtimeStore with connectorStatus / lastError
 *   - Error Recovery         – retries before marking a connector as permanently errored
 *   - Background Refresh     – non-blocking; never blocks UI or the DataPipeline API
 *   - Request Queue          – ensures at most one in-flight request per connector
 *   - Rate Limiting          – enforces minimum refresh interval; backs off on HTTP 429
 *
 * Public interface is intentionally minimal so the UI and DataPipeline remain unchanged.
 */

import { realtimeDataPipeline } from './DataPipeline'
import { useRealtimeStore } from '../stores/realtimeStore'
import { ECONOMIC_SOURCE_IDS, type ConnectorSyncStatus, type EconomicSourceId, type SyncEngineConfig } from '../types/economic'

/** Per-connector runtime state tracked exclusively inside the SyncEngine. */
interface ConnectorRuntimeState {
  /** True while a network request is in-flight for this connector. */
  inFlight: boolean
  /** Unix epoch (ms) of the most recent successful refresh. 0 = never. */
  lastRefreshAt: number
  /** Unix epoch (ms) until which the connector is rate-limited. 0 = not limited. */
  rateLimitUntil: number
  /** True if the rate-limit warning has already been logged for this cooldown period. */
  rateLimitLogged: boolean
  /** Pending retry or rate-limit timer handle. */
  scheduledTimer: ReturnType<typeof setTimeout> | null
}

const DEFAULT_CONFIG: Required<SyncEngineConfig> = {
  autoRefreshIntervalMs: 60_000,
  minRefreshIntervalMs: 30_000,
  timeoutMs: 15_000,
  maxRetries: 3,
  retryBaseDelayMs: 1_000,
  rateLimitBackoffMs: 60_000,
}

export class SyncEngine {
  private readonly config: Required<SyncEngineConfig>

  private readonly runtime: Record<EconomicSourceId, ConnectorRuntimeState>

  private schedulerHandle: ReturnType<typeof setInterval> | null = null

  private started = false

  constructor(config: SyncEngineConfig = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config }

    this.runtime = Object.fromEntries(
      ECONOMIC_SOURCE_IDS.map((id) => [
        id,
        {
          inFlight: false,
          lastRefreshAt: 0,
          rateLimitUntil: 0,
          rateLimitLogged: false,
          scheduledTimer: null,
        } satisfies ConnectorRuntimeState,
      ]),
    ) as Record<EconomicSourceId, ConnectorRuntimeState>
  }

  // ── Lifecycle ─────────────────────────────────────────────────────────────

  /**
   * Start the background refresh scheduler.
   * Safe to call multiple times – subsequent calls are no-ops.
   */
  start(): void {
    if (this.started) return
    this.started = true
    this.schedulerHandle = setInterval(
      () => void this.tickScheduler(),
      this.config.autoRefreshIntervalMs,
    )
    // Trigger an immediate pass so data is fetched on startup without waiting
    // for the first interval tick.
    void this.tickScheduler()
  }

  /**
   * Stop the background scheduler and cancel all pending timers.
   * Safe to call multiple times.
   */
  stop(): void {
    if (!this.started) return
    this.started = false

    if (this.schedulerHandle !== null) {
      clearInterval(this.schedulerHandle)
      this.schedulerHandle = null
    }

    for (const state of Object.values(this.runtime)) {
      if (state.scheduledTimer !== null) {
        clearTimeout(state.scheduledTimer)
        state.scheduledTimer = null
      }
    }
  }

  // ── Manual refresh API ────────────────────────────────────────────────────

  /**
   * Manually trigger a refresh for a single connector.
   * Rate-limit and in-flight guards still apply.
   */
  async refresh(source: EconomicSourceId): Promise<void> {
    await this.doRefresh(source, 0, true)
  }

  /**
   * Manually trigger a refresh for all connectors (non-blocking per connector).
   */
  async refreshAll(): Promise<void> {
    await Promise.allSettled(ECONOMIC_SOURCE_IDS.map((id) => this.doRefresh(id, 0, true)))
  }

  // ── Internal scheduler tick ───────────────────────────────────────────────

  private async tickScheduler(): Promise<void> {
    const now = Date.now()

    for (const source of ECONOMIC_SOURCE_IDS) {
      const state = this.runtime[source]

      // Skip connectors with an active request or pending retry timer
      if (state.inFlight || state.scheduledTimer !== null) continue

      // Skip if still inside rate-limit cooldown
      if (state.rateLimitUntil > now) continue

      // Skip if the TTL cache is still valid
      if (realtimeDataPipeline.getCacheExpiry(source) !== null) continue

      // Skip if last refresh was too recent (minimum interval guard)
      if (state.lastRefreshAt > 0 && now - state.lastRefreshAt < this.config.minRefreshIntervalMs) continue

      void this.doRefresh(source, 0, false)
    }
  }

  // ── Core refresh logic ────────────────────────────────────────────────────

  /**
   * Execute a refresh for `source` with retry and rate-limit handling.
   *
   * @param source       Connector to refresh.
   * @param retryCount   Current retry depth (0 = first attempt).
   * @param forceRefresh When true, skips the minimum-interval guard
   *                     (used for manual refresh calls).
   */
  private async doRefresh(
    source: EconomicSourceId,
    retryCount: number,
    forceRefresh: boolean,
  ): Promise<void> {
    const state = this.runtime[source]
    const now = Date.now()

    // ── Rate limit guard ──────────────────────────────────────────────────
    if (state.rateLimitUntil > now) {
      if (!state.rateLimitLogged) {
        state.rateLimitLogged = true
        console.info(`[SyncEngine] ${source}: rate-limited, skipping (${Math.ceil((state.rateLimitUntil - now) / 1000)}s remaining)`)
      }
      return
    }

    // ── Duplicate request guard ───────────────────────────────────────────
    if (state.inFlight) return

    // ── Minimum interval guard (first attempt only) ───────────────────────
    if (retryCount === 0 && !forceRefresh && state.lastRefreshAt > 0 && now - state.lastRefreshAt < this.config.minRefreshIntervalMs) {
      return
    }

    // ── Mark in-flight ────────────────────────────────────────────────────
    state.inFlight = true
    this.setConnectorStatus(source, retryCount > 0 ? 'retrying' : 'fetching', null)

    try {
      // ── Apply per-request timeout ─────────────────────────────────────
      const timeoutMs = this.config.timeoutMs
      let timeoutHandle: ReturnType<typeof setTimeout> | null = null
      const timeoutPromise = new Promise<never>((_, reject) => {
        timeoutHandle = setTimeout(
          () => reject(new Error(`[SyncEngine] ${source}: request timed out after ${timeoutMs}ms`)),
          timeoutMs,
        )
      })

      await Promise.race([realtimeDataPipeline.refreshSource(source), timeoutPromise])

      // Clear the timeout timer so it doesn't fire after the race is won
      if (timeoutHandle !== null) {
        clearTimeout(timeoutHandle)
      }

      // ── Success ───────────────────────────────────────────────────────
      state.inFlight = false
      state.lastRefreshAt = Date.now()
      state.rateLimitUntil = 0
      state.rateLimitLogged = false
      this.setConnectorStatus(source, 'ready', null)
    } catch (error) {
      state.inFlight = false
      const message = error instanceof Error ? error.message : String(error)

      const isRateLimited =
        message.includes('429') || message.toLowerCase().includes('rate limit')

      if (isRateLimited) {
        // ── Rate-limit: back off, then retry ─────────────────────────────
        state.rateLimitUntil = Date.now() + this.config.rateLimitBackoffMs
        this.setConnectorStatus(source, 'rate-limited', message)
        console.warn(
          `[SyncEngine] ${source}: HTTP 429 – backing off for ${this.config.rateLimitBackoffMs}ms`,
        )

        state.scheduledTimer = setTimeout(() => {
          state.scheduledTimer = null
          state.rateLimitLogged = false
          void this.doRefresh(source, 0, false)
        }, this.config.rateLimitBackoffMs)
      } else if (retryCount < this.config.maxRetries) {
        // ── Transient error: exponential-backoff retry ────────────────────
        const delay = this.config.retryBaseDelayMs * Math.pow(2, retryCount)
        this.setConnectorStatus(source, 'retrying', message)
        console.warn(
          `[SyncEngine] ${source}: error (attempt ${retryCount + 1}/${this.config.maxRetries}), retrying in ${delay}ms – ${message}`,
        )

        state.scheduledTimer = setTimeout(() => {
          state.scheduledTimer = null
          void this.doRefresh(source, retryCount + 1, false)
        }, delay)
      } else {
        // ── Max retries exhausted ─────────────────────────────────────────
        this.setConnectorStatus(source, 'error', message)
        console.error(
          `[SyncEngine] ${source}: max retries (${this.config.maxRetries}) exhausted – ${message}`,
        )
      }
    }
  }

  // ── Store helpers ─────────────────────────────────────────────────────────

  private setConnectorStatus(
    source: EconomicSourceId,
    status: ConnectorSyncStatus,
    error: string | null,
  ): void {
    const update: Parameters<ReturnType<typeof useRealtimeStore.getState>['setSourceState']>[1] = {
      connectorStatus: status,
    }

    if (error !== null) {
      update.lastError = error
    }

    useRealtimeStore.getState().setSourceState(source, update)
  }
}

/**
 * Singleton SyncEngine instance.
 * Call `syncEngine.start()` to activate background refresh.
 */
export const syncEngine = new SyncEngine()
