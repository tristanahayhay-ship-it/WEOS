import { create } from 'zustand'
import type { OverlayMetric } from '../overlays/types'

interface OverlayState {
  /** Whether the overlay layer is currently visible */
  isVisible: boolean
  /** The currently active overlay metric */
  activeMetric: OverlayMetric
  /** Show or hide the entire overlay layer */
  setVisible: (visible: boolean) => void
  /** Switch to a different overlay metric */
  setActiveMetric: (metric: OverlayMetric) => void
  /** Toggle overlay visibility on/off */
  toggleVisibility: () => void
}

export const useOverlayStore = create<OverlayState>((set) => ({
  isVisible: false,
  activeMetric: 'gdp',

  setVisible: (visible) => set({ isVisible: visible }),
  setActiveMetric: (metric) => set({ activeMetric: metric }),
  toggleVisibility: () => set((state) => ({ isVisible: !state.isVisible })),
}))
