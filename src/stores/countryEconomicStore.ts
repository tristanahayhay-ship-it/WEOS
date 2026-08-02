import { create } from 'zustand'
import type { Country } from '../types/country'
import type { CountryEconomicLayer } from '../world/country/types'
import { generateEconomicLayer } from '../world/country/CountryEconomicGenerator'
import type { CountryDashboardData } from '../data/countryDashboardMock'
import { buildCountryDashboardMock } from '../data/countryDashboardMock'
import { ECONOMIC_DATA_BY_ISO } from '../data/economicData'

interface CountryEconomicState {
  /** ISO code of the country whose layer is currently loaded */
  activeIsoCode: string | null
  /** ISO code currently being generated, if any */
  loadingIsoCode: string | null
  /** The currently loaded economic layer (null when no country is selected) */
  layer: CountryEconomicLayer | null
  /** Full dashboard data (charts, sectors, companies, news, summary) for the active country */
  dashboard: CountryDashboardData | null

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
const dashboardCache = new Map<string, CountryDashboardData>()
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
  dashboard: null,

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
        dashboard: null,
      })

      pendingLoadCancel = scheduleCountryLoad(() => {
        pendingLoadCancel = null
        const economicData = ECONOMIC_DATA_BY_ISO.get(country.isoCode) ?? null
        const cachedLayer = cache.get(country.isoCode) ?? generateEconomicLayer(country, economicData)
        cache.set(country.isoCode, cachedLayer)

        const cachedDashboard = dashboardCache.get(country.isoCode) ?? buildCountryDashboardMock(country, economicData)
        dashboardCache.set(country.isoCode, cachedDashboard)

        if (requestToken !== loadRequestToken || get().activeIsoCode !== country.isoCode) return
        set({
          loadingIsoCode: null,
          layer: cachedLayer,
          dashboard: cachedDashboard,
        })
      })
      return
    }

    const economicData = ECONOMIC_DATA_BY_ISO.get(country.isoCode) ?? null
    const cachedDashboard = dashboardCache.get(country.isoCode) ?? buildCountryDashboardMock(country, economicData)
    dashboardCache.set(country.isoCode, cachedDashboard)

    pendingLoadCancel?.()
    pendingLoadCancel = null
    set({ activeIsoCode: country.isoCode, loadingIsoCode: null, layer, dashboard: cachedDashboard })
  },

  clear: () => {
    pendingLoadCancel?.()
    pendingLoadCancel = null
    set({ activeIsoCode: null, loadingIsoCode: null, layer: null, dashboard: null })
  },
  release: () => {
    pendingLoadCancel?.()
    pendingLoadCancel = null
    cache.clear()
    dashboardCache.clear()
    set({ activeIsoCode: null, loadingIsoCode: null, layer: null, dashboard: null })
  },
}))
