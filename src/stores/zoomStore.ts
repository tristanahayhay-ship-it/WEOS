import { create } from 'zustand'
import type { ZoomLevelId, ZoomTransitionState } from '../zoom/types'
import { ZOOM_LEVELS, levelFromCameraDistance } from '../zoom/levels'
import { useOverlayStore } from './overlayStore'
import { useFlowStore } from './flowStore'
import { useCountryStore } from './countryStore'
import { useCountryEconomicStore } from './countryEconomicStore'

/** Maximum zoom level exposed in the 4-level economic-intelligence framework (0–3). */
const COUNTRY_VIEW_MAX_LEVEL: ZoomLevelId = 3
/** Minimum zoom level at which a country must be selected (Country / Division). */
const COUNTRY_SCOPE_MIN_LEVEL: ZoomLevelId = 2
const LEVEL_SYNC_HYSTERESIS = 0.06

function clampLevelToCountryScope(id: ZoomLevelId): ZoomLevelId {
  return (Math.min(id, COUNTRY_VIEW_MAX_LEVEL) as ZoomLevelId)
}

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
  const clampedLevel = clampLevelToCountryScope(id)
  const level = ZOOM_LEVELS[clampedLevel]

  // Overlay
  const overlayStore = useOverlayStore.getState()
  overlayStore.setVisible(level.overlay.visible)
  if (level.overlay.metric) {
    overlayStore.setActiveMetric(level.overlay.metric)
  }

  // Flow — master visibility + LOD level
  const flowStore = useFlowStore.getState()
  flowStore.setVisible(level.flow.visible)
  // Notify the LOD engine regardless of master visibility so fade transitions
  // begin immediately; the canvas CSS opacity gate handles the full hide.
  flowStore.setLodLevel(clampedLevel)

  if (clampedLevel < COUNTRY_SCOPE_MIN_LEVEL) {
    useCountryStore.getState().selectCountry(null)
    useCountryEconomicStore.getState().release()
  }
}

export const useZoomStore = create<ZoomState>()((set, get) => ({
    activeLevel: 0,
    transition: null,
    pendingCameraDistance: null,

    setLevel: (id) => {
      const nextLevel = clampLevelToCountryScope(id)
      const current = get().activeLevel
      if (current === nextLevel) return

      set({
        activeLevel: nextLevel,
        transition: null,
      })

      applyLevelSideEffects(nextLevel)
    },

    goToLevel: (id) => {
      const current = get().activeLevel
      const target = clampLevelToCountryScope(id)
      const level = ZOOM_LEVELS[target]
      if (current === target && get().pendingCameraDistance === null) return

      set({
        pendingCameraDistance: level.cameraDistance,
        transition: {
          isTransitioning: true,
          fromLevel: current,
          toLevel: target,
          startedAt: Date.now(),
        },
      })
    },

    zoomIn: () => {
      const { activeLevel } = get()
      const nextId = Math.min(activeLevel + 1, COUNTRY_VIEW_MAX_LEVEL) as ZoomLevelId
      get().goToLevel(nextId)
    },

    zoomOut: () => {
      const { activeLevel } = get()
      const prevId = Math.max(activeLevel - 1, 0) as ZoomLevelId
      get().goToLevel(prevId)
    },

    syncFromCameraDistance: (distance) => {
      const detectedLevel = clampLevelToCountryScope(levelFromCameraDistance(distance))
      const { activeLevel } = get()
      const [min, max] = ZOOM_LEVELS[activeLevel].cameraDistanceRange

      if (
        detectedLevel !== activeLevel &&
        (distance < min - LEVEL_SYNC_HYSTERESIS || distance > max + LEVEL_SYNC_HYSTERESIS)
      ) {
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

applyLevelSideEffects(0)
