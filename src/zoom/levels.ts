import type { ZoomLevelId, ZoomLevelMetadata } from './types'

/**
 * Canonical zoom-level definitions for WEOS.
 *
 * Camera distances are in Three.js scene units where EARTH_RADIUS = 1.0.
 * The current GlobeEngine has:
 *   minDistance = 1.75   (closest the user can orbit)
 *   maxDistance = 5.5    (furthest the user can orbit)
 *
 * Each level owns a contiguous [min, max] range of camera distances.
 * The ranges are non-overlapping and together cover the full orbit band.
 *
 * Flow LOD notes:
 *  - Flow is visible at every level; the FlowEngine manages which FlowObjects
 *    are active per level and animates fade-in / fade-out transitions.
 *  - `visibleTypes` in the flow context is retained for the legacy FlowPanel UI.
 */
export const ZOOM_LEVELS: Record<ZoomLevelId, ZoomLevelMetadata> = {
  // ── Level 0: Global ───────────────────────────────────────────────────────
  0: {
    id: 0,
    name: 'Global',
    label: 'Global View — Full Earth',
    cameraDistance: 5.0,
    cameraDistanceRange: [3.8, 5.5],
    showBoundaries: true,
    showCountryLayer: false,
    overlay: {
      visible: false,
    },
    flow: {
      visible: true,
      visibleTypes: ['trade', 'investment', 'debt', 'aid'],
    },
    panel: {
      showCountryPanel: false,
    },
    transitionDuration: 1200,
  },

  // ── Level 1: Continent ────────────────────────────────────────────────────
  1: {
    id: 1,
    name: 'Continent',
    label: 'Continent View',
    cameraDistance: 3.2,
    cameraDistanceRange: [2.8, 3.8],
    showBoundaries: true,
    showCountryLayer: true,
    overlay: {
      visible: true,
      metric: 'gdp',
    },
    flow: {
      visible: true,
      visibleTypes: ['trade', 'investment'],
    },
    panel: {
      showCountryPanel: false,
    },
    transitionDuration: 1000,
  },

  // ── Level 2: Country ──────────────────────────────────────────────────────
  2: {
    id: 2,
    name: 'Country',
    label: 'Country View',
    cameraDistance: 2.5,
    cameraDistanceRange: [2.2, 2.8],
    showBoundaries: true,
    showCountryLayer: true,
    overlay: {
      visible: true,
      metric: 'gdp',
    },
    flow: {
      visible: true,
      visibleTypes: ['trade', 'investment'],
    },
    panel: {
      showCountryPanel: true,
    },
    transitionDuration: 900,
  },

  // ── Level 3: City ─────────────────────────────────────────────────────────
  3: {
    id: 3,
    name: 'City',
    label: 'City View',
    cameraDistance: 2.0,
    cameraDistanceRange: [1.95, 2.2],
    showBoundaries: true,
    showCountryLayer: true,
    overlay: {
      visible: true,
      metric: 'population',
    },
    flow: {
      visible: true,
    },
    panel: {
      showCountryPanel: true,
    },
    transitionDuration: 800,
  },

  // ── Level 4: District ─────────────────────────────────────────────────────
  4: {
    id: 4,
    name: 'District',
    label: 'Financial District View',
    cameraDistance: 1.88,
    cameraDistanceRange: [1.84, 1.95],
    showBoundaries: true,
    showCountryLayer: true,
    overlay: {
      visible: false,
    },
    flow: {
      visible: true,
    },
    panel: {
      showCountryPanel: false,
    },
    transitionDuration: 700,
  },

  // ── Level 5: Institution ──────────────────────────────────────────────────
  5: {
    id: 5,
    name: 'Institution',
    label: 'Institution View',
    cameraDistance: 1.81,
    cameraDistanceRange: [1.78, 1.84],
    showBoundaries: false,
    showCountryLayer: false,
    overlay: {
      visible: false,
    },
    flow: {
      visible: true,
    },
    panel: {
      showCountryPanel: false,
    },
    transitionDuration: 600,
  },

  // ── Level 6: Corporation ──────────────────────────────────────────────────
  6: {
    id: 6,
    name: 'Corporation',
    label: 'Corporation / Building View',
    cameraDistance: 1.76,
    cameraDistanceRange: [1.75, 1.78],
    showBoundaries: false,
    showCountryLayer: false,
    overlay: {
      visible: false,
    },
    flow: {
      visible: true,
    },
    panel: {
      showCountryPanel: false,
    },
    transitionDuration: 500,
  },
}

/** Ordered array of levels from outermost to innermost */
export const ZOOM_LEVEL_LIST: ZoomLevelMetadata[] = [
  ZOOM_LEVELS[0],
  ZOOM_LEVELS[1],
  ZOOM_LEVELS[2],
  ZOOM_LEVELS[3],
  ZOOM_LEVELS[4],
  ZOOM_LEVELS[5],
  ZOOM_LEVELS[6],
]

/**
 * Determine which zoom level a given camera distance belongs to.
 * Falls back to level 0 (global) when no range matches.
 */
export function levelFromCameraDistance(distance: number): ZoomLevelId {
  for (const level of ZOOM_LEVEL_LIST) {
    const [min, max] = level.cameraDistanceRange
    if (distance >= min && distance <= max) return level.id
  }
  // Below closest level — clamp to innermost
  if (distance < ZOOM_LEVELS[6].cameraDistanceRange[0]) return 6
  // Above furthest level — clamp to outermost
  return 0
}
