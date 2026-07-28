import type { EconomicOverlay, ColorStop } from '../types'
import type { CountryEconomicData } from '../../types/country'

const COLOR_SCALE: ColorStop[] = [
  { position: 0,    color: '#0f172a', label: '< 1 M'    },
  { position: 0.15, color: '#14532d', label: '5 M'      },
  { position: 0.35, color: '#16a34a', label: '50 M'     },
  { position: 0.55, color: '#86efac', label: '200 M'    },
  { position: 0.70, color: '#fde68a', label: '500 M'    },
  { position: 0.85, color: '#f97316', label: '800 M'    },
  { position: 1,    color: '#dc2626', label: '≥ 1.4 B'  },
]

const MILLION  = 1_000_000
const BILLION  = 1_000_000_000

/**
 * Population Overlay
 * Domain: 0 – 1 400 000 000 (1.4 billion)
 */
export const populationOverlay: EconomicOverlay = {
  id: 'population',
  name: 'Population',
  description: 'Total Population',
  unit: 'people',
  domain: [0, 1_400_000_000],
  colorScale: COLOR_SCALE,
  noDataColor: '#1f2937',

  getValue(data: CountryEconomicData): number | null {
    return data.population
  },

  formatValue(value: number | null): string {
    if (value === null) return 'No Data'
    if (value >= BILLION) return `${(value / BILLION).toFixed(2)} B`
    if (value >= MILLION) return `${(value / MILLION).toFixed(1)} M`
    return value.toLocaleString('en-US')
  },
}
