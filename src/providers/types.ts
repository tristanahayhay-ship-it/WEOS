import type { CountryEconomicData } from '../types/country'

/**
 * Partial economic data that a provider can contribute.
 * Providers only fill the fields they support; the manager merges
 * contributions from multiple providers into a single record.
 */
export type PartialEconomicData = Partial<Omit<CountryEconomicData, 'isoCode'>>

/**
 * Contract every economic-data connector must satisfy.
 *
 * Adding a new source:
 *  1. Create a class that implements this interface.
 *  2. Register it in `src/providers/index.ts`.
 *
 * See `docs/data-provider-layer.md` for the full guide.
 */
export interface EconomicDataProvider {
  /** Human-readable name used in logs and diagnostics. */
  readonly name: string

  /**
   * Whether this connector needs an API key.
   * When `true` the manager skips the connector if the key is absent,
   * so the app never hangs waiting for an unauthenticated request.
   */
  readonly requiresApiKey: boolean

  /**
   * Batch-fetch economic data for all supported countries.
   *
   * @returns A map from ISO alpha-2 code → partial data.
   *          Return an empty `Map` if no data is available rather than
   *          throwing — the manager treats an empty map as a graceful
   *          no-op and tries the next provider in the chain.
   */
  fetchAll(): Promise<Map<string, PartialEconomicData>>
}

/** Runtime configuration passed to `ProviderManager`. */
export interface ProviderManagerConfig {
  /** Maximum ms to wait for a single `fetchAll()` call (default: 10 000). */
  timeoutMs?: number
  /** Retry attempts per provider on transient failure (default: 2). */
  retryAttempts?: number
  /** Cache TTL in ms; cached data is served without a network round-trip (default: 3 600 000 = 1 h). */
  cacheTtlMs?: number
}
