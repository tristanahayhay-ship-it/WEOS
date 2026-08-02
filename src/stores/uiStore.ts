import { create } from 'zustand'
import type { TopbarTab, CountryTab, ViewMode } from '../types/ui'

interface UIState {
  activeTab: TopbarTab
  activeCountryTab: CountryTab
  viewMode: ViewMode
  setActiveTab: (tab: TopbarTab) => void
  setActiveCountryTab: (tab: CountryTab) => void
  setViewMode: (mode: ViewMode) => void
}

export const useUIStore = create<UIState>((set) => ({
  activeTab: 'global-view',
  activeCountryTab: 'overview',
  viewMode: '3d',
  setActiveTab: (tab) => set({ activeTab: tab }),
  setActiveCountryTab: (tab) => set({ activeCountryTab: tab }),
  setViewMode: (mode) => set({ viewMode: mode }),
}))
