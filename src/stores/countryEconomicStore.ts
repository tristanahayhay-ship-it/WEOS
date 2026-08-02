import { create } from 'zustand'
import type { Country } from '../types/country'
import type { CountryEconomicLayer } from '../world/country/types'
import { generateEconomicLayer } from '../world/country/CountryEconomicGenerator'

interface CountryEconomicState {
  /** ISO code of the country whose layer is currently loaded */
  activeIsoCode: string | null
  /** ISO code currently being generated, if any */
  loadingIsoCode: string | null
  /** The currently loaded economic layer (null when no country is selected) */
  layer: CountryEconomicLayer | null

  /**
   * Load (or retrieve from cache) the economic layer for the given country.
   * Calling with the same country as the current one is a no-op.
   */
  loadForCountry: (country: Country) => void

  /** Clear the active layer (e.g. when country is deselected) */
  clear: () => void
  /** Clear active layer and cached layers to release memory when exiting Country View */
  release: () => void
}

/** Per-session in-memory cache so re-selecting the same country is instant */
const cache = new Map<string, CountryEconomicLayer>()
let pendingLoadCancel: (() => void) | null = null
let loadRequestToken = 0

function scheduleCountryLoad(work: () => void) {
  if (typeof window !== 'undefined' && 'requestIdleCallback' in window) {
    const handle = window.requestIdleCallback(work, { timeout: 160 })
    return () => window.cancelIdleCallback(handle)
  }

  const handle = globalThis.setTimeout(work, 0)
  return () => globalThis.clearTimeout(handle)
}

export const useCountryEconomicStore = create<CountryEconomicState>((set, get) => ({
  activeIsoCode: null,
  loadingIsoCode: null,
  layer: null,

  loadForCountry: (country) => {
    const currentState = get()
    if (
      currentState.activeIsoCode === country.isoCode
      && (currentState.layer?.isoCode === country.isoCode || currentState.loadingIsoCode === country.isoCode)
    ) {
      return
    }

    let layer = cache.get(country.isoCode)
    if (!layer) {
      const requestToken = ++loadRequestToken
      pendingLoadCancel?.()

      set({
        activeIsoCode: country.isoCode,
        loadingIsoCode: country.isoCode,
        layer: null,
      })

      pendingLoadCancel = scheduleCountryLoad(() => {
        pendingLoadCancel = null
        const cachedLayer = cache.get(country.isoCode) ?? generateEconomicLayer(country)
        cache.set(country.isoCode, cachedLayer)

        if (requestToken !== loadRequestToken || get().activeIsoCode !== country.isoCode) return
        set({
          loadingIsoCode: null,
          layer: cachedLayer,
        })
      })
      return
    }

    pendingLoadCancel?.()
    pendingLoadCancel = null
    set({ activeIsoCode: country.isoCode, loadingIsoCode: null, layer })
  },

  clear: () => {
    pendingLoadCancel?.()
    pendingLoadCancel = null
    set({ activeIsoCode: null, loadingIsoCode: null, layer: null })
  },
  release: () => {
    pendingLoadCancel?.()
    pendingLoadCancel = null
    cache.clear()
    set({ activeIsoCode: null, loadingIsoCode: null, layer: null })
  },
}))
