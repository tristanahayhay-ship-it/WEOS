import type { CountryEconomicData } from '../types/country'

/** The economic metric an overlay visualises */
export type OverlayMetric = 'gdp' | 'population' | 'inflation' | 'interestRate'

/**
 * A single stop in a color-scale gradient.
 * `position` is a normalised 0–1 value within the overlay's domain.
 */
export interface ColorStop {
  position: number
  /** CSS hex color, e.g. "#3b82f6" */
  color: string
  /** Human-readable label for the legend at this stop */
  label: string
}

/** What the engine returns for a single country */
export interface OverlayColorResult {
  /** Hex color representing this country's data */
  color: string
  /** Raw metric value (null when data is unavailable) */
  rawValue: number | null
  /** Display-ready formatted value */
  formattedValue: string
  /** False when the underlying data field is null/missing */
  hasData: boolean
}

/**
 * Contract every economic overlay must satisfy.
 *
 * Adding a new overlay:
 *  1. Create an object that implements this interface.
 *  2. Add it to the `OVERLAYS` map in `src/overlays/index.ts`.
 *
 * See `docs/overlay-engine.md` for the full guide.
 */
export interface EconomicOverlay {
  /** Unique key — must match an `OverlayMetric` value */
  readonly id: OverlayMetric
  /** Display label shown in the selector UI */
  readonly name: string
  /** One-line description used in the legend header */
  readonly description: string
  /** Unit appended to formatted values (e.g. "B USD", "%") */
  readonly unit: string
  /**
   * Value domain [min, max] used to normalise raw data into 0–1 for
   * color-scale interpolation.  Values outside the domain are clamped.
   */
  readonly domain: [number, number]
  /**
   * Ordered color stops.  Must have at least two entries with
   * `position` values of 0 and 1.
   */
  readonly colorScale: ColorStop[]
  /** Color used when the data field is null / missing for a country */
  readonly noDataColor: string
  /**
   * Extract the numeric metric value from a `CountryEconomicData` record.
   * Return `null` when the field is unavailable so the engine can show a
   * No-Data state instead of throwing.
   */
  getValue(data: CountryEconomicData): number | null
  /** Format a raw value for display in the legend / tooltip. */
  formatValue(value: number | null): string
}
