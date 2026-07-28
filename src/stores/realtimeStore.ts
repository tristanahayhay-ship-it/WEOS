import { create } from 'zustand'
import {
  ECONOMIC_SOURCE_IDS,
  ECONOMIC_SOURCE_NAMES,
  createEmptyEconomicSourceState,
  type EconomicDataPoint,
  type EconomicSourceId,
  type EconomicSourceState,
} from '../types/economic'

export interface RealtimeStoreState {
  records: Record<string, EconomicDataPoint>
  sourceState: Record<EconomicSourceId, EconomicSourceState>
  lastPipelineRunAt: string | null
  getRecordsBySource: (source: EconomicSourceId) => EconomicDataPoint[]
  getRecordsByCountry: (countryCode: string) => EconomicDataPoint[]
  replaceSourceRecords: (source: EconomicSourceId, records: EconomicDataPoint[]) => void
  setSourceState: (source: EconomicSourceId, state: Partial<EconomicSourceState>) => void
  setLastPipelineRunAt: (timestamp: string | null) => void
  resetRealtimeData: () => void
}

const createInitialSourceState = (): Record<EconomicSourceId, EconomicSourceState> => ({
  worldBank: createEmptyEconomicSourceState(ECONOMIC_SOURCE_NAMES.worldBank),
  fred: createEmptyEconomicSourceState(ECONOMIC_SOURCE_NAMES.fred),
  imf: createEmptyEconomicSourceState(ECONOMIC_SOURCE_NAMES.imf),
  oecd: createEmptyEconomicSourceState(ECONOMIC_SOURCE_NAMES.oecd),
})

export const useRealtimeStore = create<RealtimeStoreState>((set, get) => ({
  records: {},
  sourceState: createInitialSourceState(),
  lastPipelineRunAt: null,

  getRecordsBySource: (source) => Object.values(get().records).filter((record) => record.source === source),

  getRecordsByCountry: (countryCode) =>
    Object.values(get().records).filter((record) => record.countryCode === countryCode),

  replaceSourceRecords: (source, records) =>
    set((state) => {
      const nextRecords = Object.fromEntries(
        Object.entries(state.records).filter(([, record]) => record.source !== source),
      ) as Record<string, EconomicDataPoint>

      for (const record of records) {
        nextRecords[record.key] = record
      }

      return { records: nextRecords }
    }),

  setSourceState: (source, nextState) =>
    set((state) => ({
      sourceState: {
        ...state.sourceState,
        [source]: {
          ...state.sourceState[source],
          ...nextState,
        },
      },
    })),

  setLastPipelineRunAt: (timestamp) => set({ lastPipelineRunAt: timestamp }),

  resetRealtimeData: () =>
    set({
      records: {},
      sourceState: createInitialSourceState(),
      lastPipelineRunAt: null,
    }),
}))

export const realtimeSourceIds = ECONOMIC_SOURCE_IDS
