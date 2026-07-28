import { create } from 'zustand'

import { alerts, capitalFlows, defaultEntity } from '../data/mockData'
import type { AlertItem, GeoEntity, MapMode } from '../types'
import { ZoomLevel } from '../types'

interface WEOSState {
  zoomLevel: ZoomLevel
  selectedEntity: GeoEntity | null
  mapMode: MapMode
  flows: typeof capitalFlows
  alerts: AlertItem[]
  setZoomLevel: (level: ZoomLevel) => void
  zoomIn: () => void
  zoomOut: () => void
  selectEntity: (entity: GeoEntity | null) => void
  toggleMapMode: () => void
  setMapMode: (mode: MapMode) => void
  acknowledgeAlert: (id: string) => void
  resetFocus: () => void
}

export const useStore = create<WEOSState>((set) => ({
  zoomLevel: ZoomLevel.TongTheHeThong,
  selectedEntity: defaultEntity,
  mapMode: '2D',
  flows: capitalFlows,
  alerts,
  setZoomLevel: (level) => set({ zoomLevel: level }),
  zoomIn: () =>
    set((state) => ({
      zoomLevel: Math.min(state.zoomLevel + 1, ZoomLevel.ThoiGianThuc) as ZoomLevel,
    })),
  zoomOut: () =>
    set((state) => ({
      zoomLevel: Math.max(state.zoomLevel - 1, ZoomLevel.TongTheHeThong) as ZoomLevel,
    })),
  selectEntity: (entity) => set({ selectedEntity: entity }),
  toggleMapMode: () => set((state) => ({ mapMode: state.mapMode === '2D' ? '3D' : '2D' })),
  setMapMode: (mode) => set({ mapMode: mode }),
  acknowledgeAlert: (id) =>
    set((state) => ({
      alerts: state.alerts.map((alert) => (alert.id === id ? { ...alert, acknowledged: true } : alert)),
    })),
  resetFocus: () => set({ selectedEntity: defaultEntity }),
}))
