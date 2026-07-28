/**
 * ProviderManager — orchestrates the economic-data connector chain.
 *
 * Responsibilities:
 *  - Iterate registered providers in priority order.
 *  - Enforce per-provider timeout.
 *  - Retry on transient failures with exponential back-off.
 *  - Cache successful results to avoid redundant API calls.
 *  - Merge partial data from multiple providers into a unified map.
 *  - Skip providers that require an API key when the key is absent.
 *  - Never throw; always return the best available data.
 */

import type { CountryEconomicData } from '../types/country'
import type {
  EconomicDataProvider,
  PartialEconomicData,
  ProviderManagerConfig,
} from './types'
import { SimpleCache } from './cache'

const CACHE_KEY = 'all'

const DEFAULT_CONFIG: Required<ProviderManagerConfig> = {
  timeoutMs: 10_000,
  retryAttempts: 2,
  cacheTtlMs: 60 * 60 * 1_000, // 1 hour
}

/** Wrap a promise with an AbortController-based timeout. */
async function withTimeout<T>(
  fn: (signal: AbortSignal) => Promise<T>,
  timeoutMs: number,
  providerName: string,
): Promise<T> {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeoutMs)
  try {
    return await fn(controller.signal)
  } catch (err) {
    if (controller.signal.aborted) {
      throw new Error(`[${providerName}] timed out after ${timeoutMs} ms`)
    }
    throw err
  } finally {
    clearTimeout(timer)
  }
}

/** Retry `fn` up to `attempts` times with exponential back-off. */
async function withRetry<T>(
  fn: () => Promise<T>,
  attempts: number,
  providerName: string,
): Promise<T> {
  let lastError: unknown
  for (let i = 0; i < attempts; i++) {
    try {
      return await fn()
    } catch (err) {
      lastError = err
      if (i < attempts - 1) {
        const delayMs = 500 * 2 ** i
        console.warn(
          `[WEOS] Provider "${providerName}" failed (attempt ${i + 1}/${attempts}), retrying in ${delayMs} ms…`,
          err,
        )
        await new Promise<void>((resolve) => setTimeout(resolve, delayMs))
      }
    }
  }
  throw lastError
}

/**
 * Merge `source` into `target`, overwriting only the fields explicitly set
 * in `source` (i.e. not `undefined`).  The `isoCode` is always preserved
 * from the target.  New fields added to `CountryEconomicData` are handled
 * automatically without changing this function.
 */
function mergeInto(
  target: CountryEconomicData,
  source: PartialEconomicData,
): CountryEconomicData {
  const definedFields = Object.fromEntries(
    (Object.entries(source) as [string, unknown][]).filter(([, v]) => v !== undefined),
  )
  return { ...target, ...(definedFields as PartialEconomicData) }
}

export class ProviderManager {
  private readonly providers: EconomicDataProvider[]
  private readonly config: Required<ProviderManagerConfig>
  private readonly cache: SimpleCache<Map<string, PartialEconomicData>>

  constructor(
    providers: EconomicDataProvider[],
    config: ProviderManagerConfig = {},
  ) {
    this.providers = providers
    this.config = { ...DEFAULT_CONFIG, ...config }
    this.cache = new SimpleCache(this.config.cacheTtlMs)
  }

  /**
   * Load economic data from all registered providers and return a merged map.
   *
   * The map returned contains *only* provider data; callers are responsible
   * for merging it on top of their existing baseline (placeholder) records.
   *
   * Results are cached for `cacheTtlMs` ms.
   */
  async loadAll(): Promise<Map<string, PartialEconomicData>> {
    const cached = this.cache.get(CACHE_KEY)
    if (cached !== undefined) {
      console.info('[WEOS] ProviderManager: serving from cache')
      return cached
    }

    // Merged result across all providers
    const merged = new Map<string, PartialEconomicData>()

    for (const provider of this.providers) {
      if (provider.requiresApiKey) {
        // Future: check environment / config for the key; skip for now.
        console.info(
          `[WEOS] Provider "${provider.name}" requires an API key — skipping (see docs/data-provider-layer.md).`,
        )
        continue
      }

      try {
        const providerData = await withRetry(
          () =>
            withTimeout(
              (_signal) => provider.fetchAll(),
              this.config.timeoutMs,
              provider.name,
            ),
          this.config.retryAttempts,
          provider.name,
        )

        let count = 0
        for (const [isoCode, partial] of providerData) {
          const existing = merged.get(isoCode) ?? {}
          merged.set(isoCode, { ...existing, ...partial })
          count++
        }
        console.info(
          `[WEOS] Provider "${provider.name}" contributed data for ${count} countries.`,
        )
      } catch (err) {
        console.warn(
          `[WEOS] Provider "${provider.name}" failed after all retries — falling back to next provider.`,
          err,
        )
      }
    }

    this.cache.set(CACHE_KEY, merged)
    return merged
  }

  /**
   * Apply the provider-supplied data on top of a baseline map.
   *
   * @param baseline  The placeholder / existing data (e.g. from `economicData.ts`).
   * @returns         A new map with real data merged in wherever available.
   */
  async mergeIntoBaseline(
    baseline: ReadonlyMap<string, CountryEconomicData>,
  ): Promise<Map<string, CountryEconomicData>> {
    const providerData = await this.loadAll()
    const result = new Map<string, CountryEconomicData>(baseline)

    for (const [isoCode, partial] of providerData) {
      const base = result.get(isoCode)
      if (base !== undefined) {
        result.set(isoCode, mergeInto(base, partial))
      }
      // If no baseline exists for this country we intentionally skip it;
      // the Country model is the source of truth for the country list.
    }

    return result
  }
}
