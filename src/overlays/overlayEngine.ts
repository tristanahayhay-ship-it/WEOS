import type { EconomicOverlay, OverlayColorResult } from './types'
import type { CountryEconomicData } from '../types/country'

/** Parse a 6-digit hex color string into [r, g, b] 0–255 components. */
function hexToRgb(hex: string): [number, number, number] {
  const h = hex.replace('#', '')
  return [
    parseInt(h.slice(0, 2), 16),
    parseInt(h.slice(2, 4), 16),
    parseInt(h.slice(4, 6), 16),
  ]
}

/** Re-encode [r, g, b] 0–255 components as a "#rrggbb" hex string. */
function rgbToHex(r: number, g: number, b: number): string {
  return '#' + [r, g, b].map((c) => Math.round(c).toString(16).padStart(2, '0')).join('')
}

/**
 * Linear-interpolate between two hex colors.
 * @param a  Start color hex
 * @param b  End color hex
 * @param t  Blend factor 0 → a, 1 → b
 */
function lerpHex(a: string, b: string, t: number): string {
  const [r0, g0, b0] = hexToRgb(a)
  const [r1, g1, b1] = hexToRgb(b)
  return rgbToHex(r0 + (r1 - r0) * t, g0 + (g1 - g0) * t, b0 + (b1 - b0) * t)
}

/**
 * Map a normalised 0–1 value through a set of color stops.
 * Stops must be sorted by `position` ascending.
 */
function sampleColorScale(stops: EconomicOverlay['colorScale'], t: number): string {
  const clamped = Math.max(0, Math.min(1, t))

  for (let i = 0; i < stops.length - 1; i++) {
    const lo = stops[i]
    const hi = stops[i + 1]
    if (clamped >= lo.position && clamped <= hi.position) {
      const span = hi.position - lo.position
      const localT = span === 0 ? 0 : (clamped - lo.position) / span
      return lerpHex(lo.color, hi.color, localT)
    }
  }

  // Edge: value past the last stop
  return stops[stops.length - 1].color
}

/**
 * OverlayEngine — stateless utility that maps country data to overlay colors.
 *
 * It is deliberately free of React and Zustand so it can be used anywhere
 * (components, hooks, tests, server utilities).
 */
export class OverlayEngine {
  /**
   * Compute the overlay color and display metadata for a single country.
   *
   * Resilient: if `data` is `null` or the overlay's `getValue` returns `null`,
   * the result uses the overlay's `noDataColor` and `hasData: false` rather
   * than throwing.
   */
  getColor(
    overlay: EconomicOverlay,
    data: CountryEconomicData | null,
  ): OverlayColorResult {
    if (!data) {
      return {
        color: overlay.noDataColor,
        rawValue: null,
        formattedValue: 'No Data',
        hasData: false,
      }
    }

    const rawValue = overlay.getValue(data)

    if (rawValue === null || rawValue === undefined) {
      return {
        color: overlay.noDataColor,
        rawValue: null,
        formattedValue: 'No Data',
        hasData: false,
      }
    }

    const [min, max] = overlay.domain
    const t = max === min ? 0 : (rawValue - min) / (max - min)
    const color = sampleColorScale(overlay.colorScale, t)

    return {
      color,
      rawValue,
      formattedValue: overlay.formatValue(rawValue),
      hasData: true,
    }
  }

  /**
   * Batch-compute colors for all countries in the economic data map.
   * Returns a Map from ISO alpha-2 code → OverlayColorResult.
   */
  getColorMap(
    overlay: EconomicOverlay,
    data: ReadonlyMap<string, CountryEconomicData>,
  ): Map<string, OverlayColorResult> {
    const result = new Map<string, OverlayColorResult>()
    for (const [isoCode, record] of data) {
      result.set(isoCode, this.getColor(overlay, record))
    }
    return result
  }
}

/** Shared singleton — safe to import directly in components and hooks. */
export const overlayEngine = new OverlayEngine()
