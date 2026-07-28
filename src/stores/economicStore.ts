import { create } from 'zustand'
import type { CountryEconomicData } from '../types/country'
import { ECONOMIC_DATA_BY_ISO } from '../data/economicData'

/**
 * State shape for the economic data layer.
 *
 * Phase 3B: backed by static placeholder data.
 * Phase 4+: override `data` with live API responses without touching the UI.
 */
interface EconomicState {
  /** All known economic records, keyed by ISO alpha-2 code. */
  data: ReadonlyMap<string, CountryEconomicData>

  /**
   * Look up economic data for a given ISO alpha-2 country code.
   * Returns `null` if no record is available.
   */
  getEconomicData: (isoCode: string) => CountryEconomicData | null

  /**
   * Phase 4 hook: replace a single country's record with live data.
   * Calling this with a partial record will be supported after API integration.
   */
  setEconomicData: (record: CountryEconomicData) => void
}

export const useEconomicStore = create<EconomicState>((set, get) => ({
  data: ECONOMIC_DATA_BY_ISO,

  getEconomicData: (isoCode) => get().data.get(isoCode) ?? null,

  setEconomicData: (record) =>
    set((state) => {
      const next = new Map(state.data)
      next.set(record.isoCode, record)
      return { data: next }
    }),
}))
