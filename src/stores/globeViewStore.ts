import { create } from 'zustand'

interface GlobeFrameSnapshot {
  worldMatrix: number[]
  viewMatrix: number[]
  projectionMatrix: number[]
  cameraWorldPosition: [number, number, number]
}

interface GlobeViewState {
  frame: GlobeFrameSnapshot | null
  setFrame: (frame: GlobeFrameSnapshot) => void
  clearFrame: () => void
}

export const useGlobeViewStore = create<GlobeViewState>((set) => ({
  frame: null,
  setFrame: (frame) => set({ frame }),
  clearFrame: () => set({ frame: null }),
}))

