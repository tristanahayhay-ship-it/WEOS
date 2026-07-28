/**
 * Five test countries used by the Sprite↔OverlayCanvas pixel-accuracy experiment.
 * Coordinates are taken verbatim from src/data/countries.ts `center` fields.
 */
export interface DebugCountry {
  name: string
  isoCode: string
  lon: number
  lat: number
  /** Marker colour used in both 3D Mesh and DebugCanvas crosshair. */
  color: string
}

export const DEBUG_COUNTRIES: DebugCountry[] = [
  { name: 'USA',       isoCode: 'US', lon: -100.4, lat:  37.1, color: '#ff4444' },
  { name: 'Brazil',    isoCode: 'BR', lon:  -52.0, lat: -10.0, color: '#ffdd00' },
  { name: 'UK',        isoCode: 'GB', lon:   -2.8, lat:  54.5, color: '#44ff44' },
  { name: 'China',     isoCode: 'CN', lon:  104.2, lat:  35.9, color: '#44ddff' },
  { name: 'Australia', isoCode: 'AU', lon:  133.8, lat: -25.3, color: '#ff44ff' },
]
