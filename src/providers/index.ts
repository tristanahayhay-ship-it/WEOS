/**
 * Default provider chain for WEOS Phase 4A.
 *
 * Providers are tried in the order they are listed.
 * If a provider fails or returns no data, the next one is tried.
 * Partial data from each successful provider is merged into the baseline.
 *
 * To add a new source:
 *  1. Create a connector in `src/providers/connectors/`.
 *  2. Import and add it to the `defaultProviders` array below.
 *  3. See `docs/data-provider-layer.md` for the full guide.
 */

import { ProviderManager } from './providerManager'
import { WorldBankConnector } from './connectors/worldBankConnector'
import { ImfConnector } from './connectors/imfConnector'
import { FredConnector } from './connectors/fredConnector'

/** Ordered list of active data providers. */
const defaultProviders = [
  new WorldBankConnector(), // Primary: real Population + GDP data
  new ImfConnector(),       // Secondary: inflation / interest rates (stub, activate as needed)
  new FredConnector(),      // Tertiary: FRED — requires VITE_FRED_API_KEY (stub)
]

/**
 * Singleton ProviderManager used by `economicStore`.
 * Import this wherever you need to trigger a data refresh.
 */
export const providerManager = new ProviderManager(defaultProviders, {
  timeoutMs: 10_000,
  retryAttempts: 2,
  cacheTtlMs: 60 * 60 * 1_000, // 1 hour
})

export { ProviderManager } from './providerManager'
export type { EconomicDataProvider, PartialEconomicData, ProviderManagerConfig } from './types'
