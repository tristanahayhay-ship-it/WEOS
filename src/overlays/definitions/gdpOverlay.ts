import type { EconomicOverlay, ColorStop } from '../types'
import type { CountryEconomicData } from '../../types/country'

const BILLION = 1_000

const COLOR_SCALE: ColorStop[] = [
  { position: 0,    color: '#0f172a', label: '< $1 B' },
  { position: 0.15, color: '#1e3a5f', label: '$10 B'  },
  { position: 0.35, color: '#1d4ed8', label: '$100 B' },
  { position: 0.55, color: '#2563eb', label: '$500 B' },
  { position: 0.70, color: '#38bdf8', label: '$1 T'   },
  { position: 0.85, color: '#f0abfc', label: '$5 T'   },
  { position: 1,    color: '#fbbf24', label: '≥ $20 T' },
]

/**
 * GDP Overlay
 * Domain: 0 – 20 000 USD billions (logarithmic feel via non-linear stops)
 */
export const gdpOverlay: EconomicOverlay = {
  id: 'gdp',
  name: 'GDP',
  description: 'Gross Domestic Product',
  unit: 'B USD',
  domain: [0, 20_000],
  colorScale: COLOR_SCALE,
  noDataColor: '#1f2937',

  getValue(data: CountryEconomicData): number | null {
    return data.gdpUsd
  },

  formatValue(value: number | null): string {
    if (value === null) return 'No Data'
    if (value >= BILLION) return `$${(value / BILLION).toFixed(2)} T`
    return `$${value.toFixed(1)} B`
  },
}
