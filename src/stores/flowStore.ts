import { create } from 'zustand'
import type { FlowModel, FlowType } from '../flows/types'
import type { FlowSnapshot } from '../flows/FlowEngine'
import { MOCK_FLOWS } from '../flows/mockFlows'
import { FlowEngine } from '../flows/FlowEngine'
import type { ZoomLevelId } from '../zoom/types'

const ALL_FLOW_TYPES: FlowType[] = ['trade', 'investment', 'debt', 'aid']

/** Lazily-created singleton FlowEngine, shared with FlowCanvas */
let engineSingleton: FlowEngine | null = null

function getEngine(): FlowEngine {
  if (!engineSingleton) {
    // Level 0 matches the zoomStore's own initial `activeLevel: 0`.
    // zoomStore imports flowStore (to call setLodLevel via applyLevelSideEffects),
    // so flowStore cannot import zoomStore without creating a circular dependency.
    // The first call to applyLevelSideEffects at startup will confirm the level.
    engineSingleton = new FlowEngine(0)
  }
  return engineSingleton
}

interface FlowState {
  /** All available flows (legacy mock data, kept for FlowPanel compatibility) */
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
  /** Return only the flows that are currently visible (legacy path) */
  getFilteredFlows: () => FlowModel[]

  /**
   * Notify the LOD engine that the zoom level has changed.
   * Called by zoomStore.applyLevelSideEffects after updating overlay/visibility.
   */
  setLodLevel: (id: ZoomLevelId) => void

  /**
   * Retrieve the LOD engine's snapshot for the current animation frame.
   * Advances the engine's internal fade timers by `delta` seconds.
   */
  tickLodEngine: (delta: number) => FlowSnapshot[]

  /**
   * Returns the LOD engine instance so FlowCanvas can query `hasChanged()`.
   */
  getLodEngine: () => FlowEngine
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

  setLodLevel: (id) => {
    getEngine().setLevel(id)
  },

  tickLodEngine: (delta) => {
    const engine = getEngine()
    engine.tick(delta)
    return engine.getSnapshot()
  },

  getLodEngine: () => getEngine(),
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
