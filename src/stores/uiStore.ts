import { create } from 'zustand'
import type { TopbarTab, ViewMode } from '../types/ui'

interface UIState {
  activeTab: TopbarTab
  viewMode: ViewMode
  setActiveTab: (tab: TopbarTab) => void
  setViewMode: (mode: ViewMode) => void
}

export const useUIStore = create<UIState>((set) => ({
  activeTab: 'global-view',
  viewMode: '2d',
  setActiveTab: (tab) => set({ activeTab: tab }),
  setViewMode: (mode) => set({ viewMode: mode }),
}))
