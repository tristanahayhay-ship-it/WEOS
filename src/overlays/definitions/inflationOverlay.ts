import type { EconomicOverlay, ColorStop } from '../types'
import type { CountryEconomicData } from '../../types/country'

const COLOR_SCALE: ColorStop[] = [
  { position: 0,    color: '#0ea5e9', label: '0 %'    },
  { position: 0.15, color: '#38bdf8', label: '2 %'    },
  { position: 0.35, color: '#86efac', label: '5 %'    },
  { position: 0.55, color: '#fbbf24', label: '10 %'   },
  { position: 0.75, color: '#f97316', label: '25 %'   },
  { position: 0.90, color: '#dc2626', label: '50 %'   },
  { position: 1,    color: '#7f1d1d', label: '≥ 100 %' },
]

/**
 * Inflation Overlay
 * Domain: 0 % – 100 % annual CPI inflation.
 * Values beyond 100 % are clamped to the top color.
 */
export const inflationOverlay: EconomicOverlay = {
  id: 'inflation',
  name: 'Inflation',
  description: 'Annual CPI Inflation Rate',
  unit: '%',
  domain: [0, 100],
  colorScale: COLOR_SCALE,
  noDataColor: '#1f2937',

  getValue(data: CountryEconomicData): number | null {
    return data.inflationPercent
  },

  formatValue(value: number | null): string {
    if (value === null) return 'No Data'
    return `${value.toFixed(2)} %`
  },
}
