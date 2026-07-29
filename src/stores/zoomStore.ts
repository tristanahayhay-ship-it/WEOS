import { create } from 'zustand'
import type { ZoomLevelId, ZoomTransitionState } from '../zoom/types'
import { ZOOM_LEVELS, ZOOM_LEVEL_LIST, levelFromCameraDistance } from '../zoom/levels'
import { useOverlayStore } from './overlayStore'
import { useFlowStore } from './flowStore'

interface ZoomState {
  /** Currently active zoom level */
  activeLevel: ZoomLevelId

  /** Transition state — null when idle */
  transition: ZoomTransitionState | null

  /**
   * Target camera distance requested by goToLevel().
   * GlobeEngine consumes this each render frame and lerps the camera toward it.
   * Set to null once the camera arrives within a small tolerance.
   */
  pendingCameraDistance: number | null

  // ── Navigation ────────────────────────────────────────────────────────────

  /**
   * Instantly switch the active level (no camera animation).
   * Side-effects: synchronises overlay / flow / panel stores to match new level.
   */
  setLevel: (id: ZoomLevelId) => void

  /**
   * Animate the camera to the target level's canonical camera distance.
   * Sets pendingCameraDistance so GlobeEngine can drive the animation.
   */
  goToLevel: (id: ZoomLevelId) => void

  /** Move one level deeper (toward Corporation). Clamps at innermost. */
  zoomIn: () => void

  /** Move one level shallower (toward Global). Clamps at outermost. */
  zoomOut: () => void

  /**
   * Called by GlobeEngine each frame with the current camera distance.
   * Updates the active level when the user manually orbits/zooms past a boundary.
   */
  syncFromCameraDistance: (distance: number) => void

  /**
   * Called by GlobeEngine once the camera has arrived at pendingCameraDistance.
   * Clears the pending target and marks transition complete.
   */
  clearPendingCamera: () => void
}

/** Apply level-specific settings to dependent stores (overlay / flow). */
function applyLevelSideEffects(id: ZoomLevelId) {
  const level = ZOOM_LEVELS[id]

  // Overlay
  const overlayStore = useOverlayStore.getState()
  overlayStore.setVisible(level.overlay.visible)
  if (level.overlay.metric) {
    overlayStore.setActiveMetric(level.overlay.metric)
  }

  // Flow
  const flowStore = useFlowStore.getState()
  flowStore.setVisible(level.flow.visible)
}

export const useZoomStore = create<ZoomState>()((set, get) => ({
    activeLevel: 0,
    transition: null,
    pendingCameraDistance: null,

    setLevel: (id) => {
      const current = get().activeLevel
      if (current === id) return

      set({
        activeLevel: id,
        transition: null,
      })

      applyLevelSideEffects(id)
    },

    goToLevel: (id) => {
      const current = get().activeLevel
      const level = ZOOM_LEVELS[id]

      set({
        activeLevel: id,
        pendingCameraDistance: level.cameraDistance,
        transition: {
          isTransitioning: true,
          fromLevel: current,
          toLevel: id,
          startedAt: Date.now(),
        },
      })

      applyLevelSideEffects(id)
    },

    zoomIn: () => {
      const { activeLevel } = get()
      const nextId = Math.min(activeLevel + 1, ZOOM_LEVEL_LIST.length - 1) as ZoomLevelId
      get().goToLevel(nextId)
    },

    zoomOut: () => {
      const { activeLevel } = get()
      const prevId = Math.max(activeLevel - 1, 0) as ZoomLevelId
      get().goToLevel(prevId)
    },

    syncFromCameraDistance: (distance) => {
      // Don't override level while a programmatic transition is pending
      if (get().pendingCameraDistance !== null) return

      const detectedLevel = levelFromCameraDistance(distance)
      const { activeLevel } = get()

      if (detectedLevel !== activeLevel) {
        set({ activeLevel: detectedLevel })
        applyLevelSideEffects(detectedLevel)
      }
    },

    clearPendingCamera: () => {
      set({
        pendingCameraDistance: null,
        transition: null,
      })
    },
  }))
