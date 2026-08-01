import { create } from 'zustand'
import type { Country } from '../types/country'
import type { CountryEconomicLayer } from '../world/country/types'
import { generateEconomicLayer } from '../world/country/CountryEconomicGenerator'

interface CountryEconomicState {
  /** ISO code of the country whose layer is currently loaded */
  activeIsoCode: string | null
  /** The currently loaded economic layer (null when no country is selected) */
  layer: CountryEconomicLayer | null

  /**
   * Load (or retrieve from cache) the economic layer for the given country.
   * Calling with the same country as the current one is a no-op.
   */
  loadForCountry: (country: Country) => void

  /** Clear the active layer (e.g. when country is deselected) */
  clear: () => void
}

/** Per-session in-memory cache so re-selecting the same country is instant */
const cache = new Map<string, CountryEconomicLayer>()

export const useCountryEconomicStore = create<CountryEconomicState>((set, get) => ({
  activeIsoCode: null,
  layer: null,

  loadForCountry: (country) => {
    if (get().activeIsoCode === country.isoCode) return

    let layer = cache.get(country.isoCode)
    if (!layer) {
      layer = generateEconomicLayer(country)
      cache.set(country.isoCode, layer)
    }

    set({ activeIsoCode: country.isoCode, layer })
  },

  clear: () => set({ activeIsoCode: null, layer: null }),
}))
