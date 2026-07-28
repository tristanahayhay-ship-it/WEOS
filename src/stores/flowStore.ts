import { create } from 'zustand'
import type { FlowModel, FlowType } from '../flows/types'
import { MOCK_FLOWS } from '../flows/mockFlows'

const ALL_FLOW_TYPES: FlowType[] = ['trade', 'investment', 'debt', 'aid']

interface FlowState {
  /** All available flows (mock data) */
  flows: FlowModel[]
  /** Types currently shown; a type not in this array is hidden */
  visibleTypes: FlowType[]
  /** Master visibility toggle for the entire flow layer */
  isVisible: boolean
  /** Monotonically increasing time in seconds, driven by FlowCanvas */
  animationTime: number

  /** Show or hide the entire flow layer */
  setVisible: (visible: boolean) => void
  /** Toggle master visibility on/off */
  toggleVisibility: () => void
  /** Toggle a single flow type on or off */
  toggleFlowType: (type: FlowType) => void
  /** Advance the animation clock */
  tick: (delta: number) => void
  /** Return only the flows that are currently visible */
  getFilteredFlows: () => FlowModel[]
}

export const useFlowStore = create<FlowState>((set, get) => ({
  flows: MOCK_FLOWS,
  visibleTypes: [...ALL_FLOW_TYPES],
  isVisible: false,
  animationTime: 0,

  setVisible: (visible) => set({ isVisible: visible }),

  toggleVisibility: () => set((s) => ({ isVisible: !s.isVisible })),

  toggleFlowType: (type) =>
    set((s) => {
      const current = s.visibleTypes
      const next = current.includes(type)
        ? current.filter((t) => t !== type)
        : [...current, type]
      return { visibleTypes: next }
    }),

  tick: (delta) => set((s) => ({ animationTime: s.animationTime + delta })),

  getFilteredFlows: () => {
    const { flows, visibleTypes } = get()
    return flows.filter((f) => visibleTypes.includes(f.flowType))
  },
}))

/** Display configuration for each flow type */
export interface FlowTypeConfig {
  label: string
  /** CSS hex color */
  color: string
  /** Hex number for Three.js Color() */
  colorHex: number
}

export const FLOW_TYPE_CONFIG: Record<FlowType, FlowTypeConfig> = {
  trade:      { label: 'Trade',      color: '#3b82f6', colorHex: 0x3b82f6 },
  investment: { label: 'Investment', color: '#10b981', colorHex: 0x10b981 },
  debt:       { label: 'Debt',       color: '#f59e0b', colorHex: 0xf59e0b },
  aid:        { label: 'Aid',        color: '#a78bfa', colorHex: 0xa78bfa },
}
