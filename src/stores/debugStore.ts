import { create } from 'zustand'

interface DebugState {
  /** Whether the Sprite ↔ OverlayCanvas comparison overlay is active (Shift+D). */
  enabled: boolean
  toggle: () => void
}

export const useDebugStore = create<DebugState>((set) => ({
  enabled: false,
  toggle: () => set((s) => ({ enabled: !s.enabled })),
}))
