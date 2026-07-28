import { ZoomLevel } from '../../types'

const clampZoomLevel = (value: number) =>
  Math.max(ZoomLevel.TongTheHeThong, Math.min(ZoomLevel.ThoiGianThuc, Math.round(value))) as ZoomLevel

export const MAP_2D_BASE_ZOOM = 1
export const MAP_2D_ZOOM_MULTIPLIER = 1.7
export const MAP_3D_BASE_ZOOM = 1.2
export const MAP_3D_ZOOM_MULTIPLIER = 2
export const ZOOM_SYNC_THRESHOLD = 0.12
export const ZOOM_TRANSITION_DURATION_MS = 700

export const mapZoomToWeosLevel = (zoom: number, baseZoom: number, multiplier: number) =>
  clampZoomLevel((zoom - baseZoom) * multiplier)

export const weosLevelToMapZoom = (zoomLevel: ZoomLevel, baseZoom: number, multiplier: number) =>
  baseZoom + zoomLevel / multiplier
