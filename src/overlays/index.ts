/**
 * Overlay registry — the single source of truth for all registered overlays.
 *
 * To add a new overlay:
 *  1. Create a file in `src/overlays/definitions/` that exports an object
 *     satisfying the `EconomicOverlay` interface.
 *  2. Import it here and add it to the `OVERLAYS` map.
 *
 * No other file needs to change — the UI and engine discover overlays via
 * `OVERLAYS` and `OVERLAY_LIST`.
 */

export type { EconomicOverlay, OverlayMetric, OverlayColorResult, ColorStop } from './types'
export { overlayEngine, OverlayEngine } from './overlayEngine'

import type { EconomicOverlay, OverlayMetric } from './types'
import { gdpOverlay }          from './definitions/gdpOverlay'
import { populationOverlay }   from './definitions/populationOverlay'
import { inflationOverlay }    from './definitions/inflationOverlay'
import { interestRateOverlay } from './definitions/interestRateOverlay'

/** All registered overlays, keyed by their metric id. */
export const OVERLAYS: Readonly<Record<OverlayMetric, EconomicOverlay>> = {
  gdp:          gdpOverlay,
  population:   populationOverlay,
  inflation:    inflationOverlay,
  interestRate: interestRateOverlay,
}

/** Ordered list of overlays for rendering in the selector UI. */
export const OVERLAY_LIST: EconomicOverlay[] = [
  gdpOverlay,
  populationOverlay,
  inflationOverlay,
  interestRateOverlay,
]
