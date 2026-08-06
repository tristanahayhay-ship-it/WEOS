/** Category of capital / economic flow (legacy — used by FlowPanel/FlowStore) */
export type FlowType = 'trade' | 'investment' | 'debt' | 'aid'

/**
 * Extended semantic category for LOD-aware FlowObjects.
 * Covers additional flow categories visible at deeper zoom levels.
 */
export type FlowDataType =
  | 'trade'
  | 'investment'
  | 'debt'
  | 'aid'
  | 'supply-chain'
  | 'capital'
  | 'data'
  | 'energy'
  | 'partnership'

/** Direction from the perspective of sourceCountry */
export type FlowDirection = 'outbound' | 'inbound' | 'bilateral'

/** Arbitrary key-value metadata attached to a flow */
export type FlowMetadata = Record<string, string | number | boolean | null>

/** Zoom levels at which a FlowObject can be visible (mirrors ZoomLevelId) */
export type FlowLodLevel = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10

/**
 * LOD rules embedded in each FlowObject.
 * Determine when the flow is active and how it relates to flows at adjacent levels.
 */
export interface FlowLodRules {
  /** Zoom levels at which this flow should be rendered */
  visibleAtLevels: FlowLodLevel[]
  /**
   * IDs of child flows that this route splits into when zooming in.
   * When the user zooms past the level boundary, this flow fades out and
   * the children fade in.
   */
  splitIntoIds?: string[]
  /**
   * ID of the parent flow that multiple child flows merge into when zooming out.
   * When the user zooms out past the level boundary, this flow fades out and
   * the parent fades in.
   */
  mergesIntoId?: string
}

/**
 * LOD-aware flow object.
 *
 * Each FlowObject belongs to one or more zoom levels and is created, updated,
 * and destroyed by the FlowEngine as the active zoom level changes.
 * Transitions between levels are animated via the `visibilityState` field.
 */
export interface FlowObject {
  /** Unique identifier */
  id: string
  /** [longitude, latitude] of the flow origin */
  startPoint: [number, number]
  /** [longitude, latitude] of the flow destination */
  endPoint: [number, number]
  /** Semantic category */
  dataType: FlowDataType
  /** Magnitude — USD billions (or arbitrary units at sub-country scales) */
  value: number
  /** CSS hex color string (e.g. '#3b82f6') */
  color: string
  /** Three.js-compatible hex number for Color() (e.g. 0x3b82f6) */
  colorHex: number
  /**
   * Visual thickness factor in [0, 1].
   * Rendered as pulse brightness — higher values produce a brighter, more
   * prominent arc that approximates a thicker line appearance.
   */
  thickness: number
  /** Pulse animation speed multiplier relative to the base speed (1.0 = normal) */
  animationSpeed: number
  /** Display priority — higher = shown first when the engine limits flow count */
  displayPriority: number
  /** LOD rules controlling when this flow is active and how it transitions */
  lodRules: FlowLodRules
  /**
   * Current visibility state in [0, 1].
   * Managed by FlowEngine during fade-in / fade-out transitions.
   * 1 = fully visible, 0 = fully hidden / disposed.
   */
  visibilityState: number
}

/**
 * Legacy flow model — retained for compatibility with FlowPanel and existing
 * store filter logic.  New LOD-aware code should use FlowObject instead.
 */
export interface FlowModel {
  /** Unique identifier */
  id: string
  /** ISO alpha-2 code of the origin country */
  sourceCountry: string
  /** ISO alpha-2 code of the destination country */
  targetCountry: string
  /** Category of flow */
  flowType: FlowType
  /** Magnitude — USD billions */
  value: number
  /** Direction from sourceCountry perspective */
  direction: FlowDirection
  /** ISO 8601 timestamp */
  timestamp: string
  /** Optional descriptive metadata */
  metadata: FlowMetadata
}
