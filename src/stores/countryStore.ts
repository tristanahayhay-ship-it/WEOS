import { create } from 'zustand'
import type { Country } from '../types/country'

interface CountryState {
  /** Country currently under the mouse cursor */
  hoveredCountry: Country | null
  /** Country the user has clicked/selected */
  selectedCountry: Country | null
  /** Whether the right-side information panel is open */
  isPanelOpen: boolean
  /** Screen-space tooltip position, set alongside hoveredCountry */
  tooltipScreenPos: { x: number; y: number } | null

  setHoveredCountry: (country: Country | null, pos?: { x: number; y: number } | null) => void
  selectCountry: (country: Country | null) => void
  closePanel: () => void
}

export const useCountryStore = create<CountryState>((set) => ({
  hoveredCountry: null,
  selectedCountry: null,
  isPanelOpen: false,
  tooltipScreenPos: null,

  setHoveredCountry: (country, pos = null) =>
    set({ hoveredCountry: country, tooltipScreenPos: country ? (pos ?? null) : null }),

  selectCountry: (country) =>
    set({ selectedCountry: country, isPanelOpen: country !== null }),

  closePanel: () => set({ isPanelOpen: false, selectedCountry: null }),
}))
