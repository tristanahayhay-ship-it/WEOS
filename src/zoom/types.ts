import type { OverlayMetric } from '../overlays/types'
import type { FlowType } from '../flows/types'

/**
 * Hierarchy of zoom levels in WEOS Zoom Level Standard V1.0.
 *
 * 0  = Trái Đất Toàn Cầu
 * 1  = Lục địa
 * 2  = Quốc gia
 * 3  = Tỉnh/Bang
 * 4  = Thành phố
 * 5  = Khu tài chính
 * 6  = Tổ chức
 * 7  = Doanh nghiệp
 * 8  = Nhà máy / Cơ sở
 * 9  = Mạng lưới logistics
 * 10 = Dữ liệu thời gian thực
 */
export type ZoomLevelId = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10

export type ZoomDataLayerId =
  | 'global_earth'
  | 'continent'
  | 'country'
  | 'province_state'
  | 'city'
  | 'financial_district'
  | 'institution'
  | 'corporation'
  | 'facility'
  | 'logistics_network'
  | 'realtime_data'

export interface ZoomDataLayerSpec {
  id: ZoomDataLayerId
  label: string
  semanticItems: readonly string[]
}

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
  dataLayer: ZoomDataLayerSpec

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
