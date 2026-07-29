import type { OverlayMetric } from '../overlays/types'
import type { FlowType } from '../flows/types'

/**
 * Hierarchy of zoom levels in WEOS.
 *
 * 0 = Global   — full Earth visible from space
 * 1 = Continent — continental view
 * 2 = Country  — individual country boundaries prominent
 * 3 = City     — city / regional scale
 * 4 = District — financial-district / borough scale
 * 5 = Institution — institution / campus scale
 * 6 = Corporation — individual building / company scale
 */
export type ZoomLevelId = 0 | 1 | 2 | 3 | 4 | 5 | 6

/** Context driven by the zoom level for the overlay layer */
export interface OverlayContext {
  visible: boolean
  metric?: OverlayMetric
}

/** Context driven by the zoom level for the flow layer */
export interface FlowContext {
  visible: boolean
  /** Which flow types should be shown; undefined = keep current selection */
  visibleTypes?: FlowType[]
}

/** Context driven by the zoom level for the UI panel layer */
export interface PanelContext {
  /** Show the country detail panel */
  showCountryPanel: boolean
}

/**
 * Full metadata for one zoom level.
 */
export interface ZoomLevelMetadata {
  id: ZoomLevelId
  /** Short human-readable name shown in the HUD */
  name: string
  /** Longer descriptive label */
  label: string

  // ── Camera ────────────────────────────────────────────────────────────────
  /** Target camera distance from scene origin (Three.js units). */
  cameraDistance: number
  /** [min, max] range of camera distances that belong to this level. */
  cameraDistanceRange: [number, number]

  // ── Scene visibility ──────────────────────────────────────────────────────
  /** Show coast-line / country-boundary geometry */
  showBoundaries: boolean
  /** Show country highlight/selection geometry */
  showCountryLayer: boolean

  // ── Overlay / Flow / Panel context ────────────────────────────────────────
  overlay: OverlayContext
  flow: FlowContext
  panel: PanelContext

  // ── Transition ────────────────────────────────────────────────────────────
  /** Camera-animation duration when jumping directly to this level (ms). */
  transitionDuration: number
}

/** Lightweight transition state tracked by zoomStore */
export interface ZoomTransitionState {
  isTransitioning: boolean
  fromLevel: ZoomLevelId
  toLevel: ZoomLevelId
  /** Unix timestamp (ms) when transition started */
  startedAt: number
}
