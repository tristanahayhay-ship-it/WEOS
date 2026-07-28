import { create } from 'zustand'
import { COUNTRY_ECONOMIC_DATA } from '../data/economicData'
import type { CountryEconomicData } from '../types/economic'

interface EconomicState {
  byIsoCode: ReadonlyMap<string, CountryEconomicData>
  getByIsoCode: (isoCode: string) => CountryEconomicData | null
  setAll: (entries: ReadonlyMap<string, CountryEconomicData>) => void
}

export const useEconomicStore = create<EconomicState>((set, get) => ({
  byIsoCode: COUNTRY_ECONOMIC_DATA,
  getByIsoCode: (isoCode) => get().byIsoCode.get(isoCode) ?? null,
  setAll: (entries) => set({ byIsoCode: entries }),
}))
