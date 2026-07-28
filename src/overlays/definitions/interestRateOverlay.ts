import type { EconomicOverlay, ColorStop } from '../types'
import type { CountryEconomicData } from '../../types/country'

const COLOR_SCALE: ColorStop[] = [
  { position: 0,    color: '#0ea5e9', label: '0 %'     },
  { position: 0.20, color: '#38bdf8', label: '2 %'     },
  { position: 0.40, color: '#86efac', label: '5 %'     },
  { position: 0.60, color: '#fbbf24', label: '10 %'    },
  { position: 0.80, color: '#f97316', label: '20 %'    },
  { position: 1,    color: '#dc2626', label: '≥ 30 %'  },
]

/**
 * Interest Rate Overlay
 * Domain: 0 % – 30 % central-bank policy / benchmark rate.
 */
export const interestRateOverlay: EconomicOverlay = {
  id: 'interestRate',
  name: 'Interest Rate',
  description: 'Central-Bank Policy Rate',
  unit: '%',
  domain: [0, 30],
  colorScale: COLOR_SCALE,
  noDataColor: '#1f2937',

  getValue(data: CountryEconomicData): number | null {
    return data.interestRatePercent
  },

  formatValue(value: number | null): string {
    if (value === null) return 'No Data'
    return `${value.toFixed(2)} %`
  },
}
