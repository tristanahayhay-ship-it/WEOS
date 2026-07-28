import { create } from 'zustand'

export interface ScreenPoint {
  x: number
  y: number
}

export interface GlobeFrameSnapshot {
  worldMatrix: number[]
  viewMatrix: number[]
  projectionMatrix: number[]
  cameraWorldPosition: [number, number, number]
  /** CSS-pixel width of the Three.js renderer viewport. */
  viewportWidth: number
  /** CSS-pixel height of the Three.js renderer viewport. */
  viewportHeight: number
  /**
   * Screen positions (CSS px) of DEBUG_COUNTRIES computed via
   * `vector.project(camera)` inside GlobeEngine — the Three.js ground truth.
   * null = back-facing or outside clip volume.
   */
  spritePoints: Array<ScreenPoint | null>
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

