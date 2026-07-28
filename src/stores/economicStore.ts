import { create } from 'zustand'
import type { CountryEconomicData } from '../types/country'
import { ECONOMIC_DATA_BY_ISO } from '../data/economicData'
import { providerManager } from '../providers'

/** Status of the background provider load. */
export type ProviderStatus = 'idle' | 'loading' | 'loaded' | 'error'

/**
 * State shape for the economic data layer.
 *
 * Phase 3B: backed by static placeholder data.
 * Phase 4A: `initializeFromProviders()` merges real data on top of placeholders.
 *           The placeholder data remains active until providers respond, so the UI
 *           is always functional regardless of network availability.
 */
interface EconomicState {
  /** All known economic records, keyed by ISO alpha-2 code. */
  data: ReadonlyMap<string, CountryEconomicData>

  /** Lifecycle status of the provider-layer initialisation. */
  providerStatus: ProviderStatus

  /**
   * Look up economic data for a given ISO alpha-2 country code.
   * Returns `null` if no record is available.
   */
  getEconomicData: (isoCode: string) => CountryEconomicData | null

  /**
   * Replace a single country's record (used by tests and direct overrides).
   */
  setEconomicData: (record: CountryEconomicData) => void

  /**
   * Trigger an async load from all registered providers.
   * Safe to call multiple times; subsequent calls while loading are no-ops.
   * Real data is merged on top of placeholders; placeholder values are kept
   * for any field the providers do not supply.
   */
  initializeFromProviders: () => Promise<void>
}

export const useEconomicStore = create<EconomicState>((set, get) => ({
  data: ECONOMIC_DATA_BY_ISO,
  providerStatus: 'idle',

  getEconomicData: (isoCode) => get().data.get(isoCode) ?? null,

  setEconomicData: (record) =>
    set((state) => {
      const next = new Map(state.data)
      next.set(record.isoCode, record)
      return { data: next }
    }),

  initializeFromProviders: async () => {
    if (get().providerStatus !== 'idle') return
    set({ providerStatus: 'loading' })
    try {
      const merged = await providerManager.mergeIntoBaseline(get().data)
      set({ data: merged, providerStatus: 'loaded' })
      console.info('[WEOS] economicStore: provider data merged successfully.')
    } catch (err) {
      set({ providerStatus: 'error' })
      console.warn('[WEOS] economicStore: provider initialisation failed — placeholder data retained.', err)
    }
  },
}))

// Auto-initialise in the background after the first render frame.
// The placeholder data remains in place until providers respond, so the UI
// is never blocked or broken by this background task.
setTimeout(() => {
  void useEconomicStore.getState().initializeFromProviders()
}, 0)
