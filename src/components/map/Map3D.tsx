import { useEffect, useMemo, useRef } from 'react'
import { MapboxOverlay } from '@deck.gl/mapbox'
import { PathLayer, ScatterplotLayer, TextLayer } from '@deck.gl/layers'
import * as maplibregl from 'maplibre-gl'

import { capitalFlows, countries, financialCenters } from '../../data/mockData'
import { useStore } from '../../store/useStore'
import type { CapitalFlow, Coordinate, FinancialCenter, GeoEntity } from '../../types'
import {
  MAP_3D_BASE_ZOOM,
  MAP_3D_ZOOM_MULTIPLIER,
  ZOOM_SYNC_THRESHOLD,
  ZOOM_TRANSITION_DURATION_MS,
  mapZoomToWeosLevel,
  weosLevelToMapZoom,
} from './zoomConfig'

interface Map3DProps {
  onError?: () => void
}

const GLOBE_CENTER: [number, number] = [110, 20]
const GLOBE_ZOOM = 1.2
const MIN_MAP_HOST_SIZE = 80
const CITY_LABEL_SIZE_SCALE_FACTOR = 20
const CITY_LABEL_FONT = '"SFMono-Regular","Cascadia Code","Fira Code",monospace'
// Mean Earth radius — deck.gl uses meters for altitude, and its globe projection
// internally assumes this same ~6 371 km radius, so matching it keeps arcs on-surface.
const GLOBE_RADIUS_METERS = 6_371_000
const ARC_SURFACE_EPSILON_METERS = 250
const ARC_MAX_ALTITUDE_METERS = 10_000
const ARC_SEGMENTS = 64
const ARC_GLOW_WIDTH_DIVISOR = 36
const ARC_CORE_WIDTH_DIVISOR = 70
const MIN_ARC_RADIUS_METERS = GLOBE_RADIUS_METERS + ARC_SURFACE_EPSILON_METERS
const MAX_ARC_RADIUS_METERS =
  GLOBE_RADIUS_METERS + ARC_SURFACE_EPSILON_METERS + ARC_MAX_ALTITUDE_METERS

/** CARTO dark-matter tiles — no API key, dark theme matches WEOS neon palette */
const BASEMAP_TILE_URL = 'https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
const BASEMAP_ATTRIBUTION =
  '© <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors ' +
  '© <a href="https://carto.com/" target="_blank">CARTO</a>'

const countryColor = (score: number): [number, number, number, number] => {
  if (score >= 82) return [0, 255, 136, 200]
  if (score >= 74) return [0, 212, 255, 190]
  if (score >= 68) return [255, 136, 0, 180]
  return [255, 68, 68, 190]
}

const arcPathColor = (flow: CapitalFlow): [number, number, number, number] => {
  if (flow.direction === 'outbound') return [255, 98, 66, 210]
  if (flow.direction === 'inbound') return [0, 248, 160, 210]
  return [0, 208, 255, 210]
}

const arcPathGlowColor = (flow: CapitalFlow): [number, number, number, number] => {
  if (flow.direction === 'outbound') return [255, 90, 60, 72]
  if (flow.direction === 'inbound') return [0, 248, 140, 72]
  return [0, 208, 255, 72]
}

type GlobePosition = [number, number, number]
type CartesianVector3 = [number, number, number]
type FlowPath = CapitalFlow & {
  path: GlobePosition[]
}

const toRadians = (value: number): number => (value * Math.PI) / 180
const toDegrees = (value: number): number => (value * 180) / Math.PI

const clamp = (value: number, min: number, max: number): number => Math.min(max, Math.max(min, value))

const magnitude = ([x, y, z]: CartesianVector3): number => Math.hypot(x, y, z)
const dotProduct = ([ax, ay, az]: CartesianVector3, [bx, by, bz]: CartesianVector3): number => ax * bx + ay * by + az * bz

const normalize = (vector: CartesianVector3): CartesianVector3 => {
  const length = magnitude(vector)
  // Degenerate zero-length input: return a valid unit vector pointing along the Z-axis
  // (which maps to longitude 90° in the X-Z plane — an arbitrary but safe non-NaN fallback).
  if (length === 0) return [0, 0, 1]
  return [vector[0] / length, vector[1] / length, vector[2] / length]
}

const fromCoordinateToUnitVector = ({ lat, lon }: Coordinate): CartesianVector3 => {
  const latitude = toRadians(lat)
  const longitude = toRadians(lon)
  const cosLatitude = Math.cos(latitude)

  return normalize([
    cosLatitude * Math.cos(longitude),
    Math.sin(latitude),
    cosLatitude * Math.sin(longitude),
  ])
}

const fromUnitVectorToCoordinate = ([x, y, z]: CartesianVector3): Coordinate => {
  const normalized = normalize([x, y, z])
  const lon = toDegrees(Math.atan2(normalized[2], normalized[0]))
  const lat = toDegrees(Math.asin(clamp(normalized[1], -1, 1)))
  return { lon, lat }
}

const interpolateGreatCircle = (
  from: CartesianVector3,
  to: CartesianVector3,
  t: number,
): CartesianVector3 => {
  const start = normalize(from)
  const end = normalize(to)
  const dot = clamp(dotProduct(start, end), -1, 1)

  // Threshold ≈ cos(1.8°): vectors this close are treated as identical.
  // Standard SLERP becomes numerically unstable for very small angles (sinOmega → 0),
  // so we fall back to linear interpolation which is accurate enough at sub-2° separation.
  if (dot > 0.9995) {
    return normalize([
      start[0] + (end[0] - start[0]) * t,
      start[1] + (end[1] - start[1]) * t,
      start[2] + (end[2] - start[2]) * t,
    ])
  }

  // Antipodal case (dot ≈ -1): SLERP degenerates because the great-circle path is
  // not unique. We pick an orthogonal axis via component swizzling (Gram-Schmidt step),
  // then rotate around that axis through angle π·t to traverse a well-defined great circle.
  if (dot < -0.9995) {
    const orthogonal = normalize(
      // Choose the component with smaller magnitude to avoid near-zero cross product.
      Math.abs(start[0]) > Math.abs(start[2]) ? [-start[1], start[0], 0] : [0, -start[2], start[1]],
    )
    const theta = Math.PI * t
    return normalize([
      start[0] * Math.cos(theta) + orthogonal[0] * Math.sin(theta),
      start[1] * Math.cos(theta) + orthogonal[1] * Math.sin(theta),
      start[2] * Math.cos(theta) + orthogonal[2] * Math.sin(theta),
    ])
  }

  const omega = Math.acos(dot)
  const sinOmega = Math.sin(omega)
  const sourceWeight = Math.sin((1 - t) * omega) / sinOmega
  const targetWeight = Math.sin(t * omega) / sinOmega

  return normalize([
    start[0] * sourceWeight + end[0] * targetWeight,
    start[1] * sourceWeight + end[1] * targetWeight,
    start[2] * sourceWeight + end[2] * targetWeight,
  ])
}

const toGlobePosition = (
  coordinate: Coordinate,
  altitudeMeters: number = ARC_SURFACE_EPSILON_METERS,
): GlobePosition => [coordinate.lon, coordinate.lat, Math.max(0, altitudeMeters)]

const getCountryCoordinate = (
  countryId: string,
  countryById: Map<string, GeoEntity>,
  missingCountryIds: Set<string>,
): Coordinate => {
  const country = countryById.get(countryId)
  if (country) return country.coordinates

  if (!missingCountryIds.has(countryId)) {
    missingCountryIds.add(countryId)
    console.warn(`[WEOS Map3D] Missing country for flow endpoint: ${countryId}`)
  }

  return { lon: 0, lat: 0 }
}

const buildFlowPath = (
  flow: CapitalFlow,
  countryById: Map<string, GeoEntity>,
  missingCountryIds: Set<string>,
): GlobePosition[] => {
  const sourceCoordinate = getCountryCoordinate(flow.from, countryById, missingCountryIds)
  const targetCoordinate = getCountryCoordinate(flow.to, countryById, missingCountryIds)
  const sourceVector = fromCoordinateToUnitVector(sourceCoordinate)
  const targetVector = fromCoordinateToUnitVector(targetCoordinate)
  const dot = clamp(dotProduct(sourceVector, targetVector), -1, 1)
  const separationRadians = Math.acos(dot)
  const distanceAltitudeMeters = (separationRadians / Math.PI) * ARC_MAX_ALTITUDE_METERS

  const path: GlobePosition[] = []
  for (let step = 0; step <= ARC_SEGMENTS; step += 1) {
    const t = step / ARC_SEGMENTS
    const curve = Math.sin(Math.PI * t)
    const radius = clamp(
      GLOBE_RADIUS_METERS + ARC_SURFACE_EPSILON_METERS + curve * distanceAltitudeMeters,
      MIN_ARC_RADIUS_METERS,
      MAX_ARC_RADIUS_METERS,
    )
    const pointOnArc = interpolateGreatCircle(sourceVector, targetVector, t)
    const coordinateOnArc = fromUnitVectorToCoordinate(pointOnArc)
    path.push(toGlobePosition(coordinateOnArc, radius - GLOBE_RADIUS_METERS))
  }

  return path
}

type FinancialCenterVisual = FinancialCenter & {
  pointColor: [number, number, number, number]
  labelSize: number
}

const financialCentersWithVisuals: FinancialCenterVisual[] = financialCenters.map((center) => ({
  ...center,
  pointColor: [
    255,
    Math.round(120 + center.intensity * 0.8),
    Math.round(center.intensity * 0.4),
    230,
  ] as [number, number, number, number],
  labelSize: 10 + Math.round(center.intensity / CITY_LABEL_SIZE_SCALE_FACTOR),
}))

export function Map3D({ onError }: Map3DProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<maplibregl.Map | null>(null)
  const overlayRef = useRef<MapboxOverlay | null>(null)
  const isCreatingRef = useRef(false)
  const isSyncingZoomRef = useRef(false)
  const moveEndHandlerRef = useRef<(() => void) | null>(null)
  const missingCountryIdsRef = useRef<Set<string>>(new Set())
  const selectEntity = useStore((state) => state.selectEntity)
  const zoomLevel = useStore((state) => state.zoomLevel)
  const setZoomLevel = useStore((state) => state.setZoomLevel)
  const countryById = useMemo(() => new Map(countries.map((country) => [country.id, country])), [])
  const flowPaths = useMemo(
    () =>
      capitalFlows.map((flow) => ({
        ...flow,
        path: buildFlowPath(flow, countryById, missingCountryIdsRef.current),
      })),
    [countryById],
  )

  const layers = useMemo(
    () => [
      new ScatterplotLayer<GeoEntity>({
        id: 'country-layer',
        data: countries,
        pickable: true,
        opacity: 0.92,
        stroked: true,
        filled: true,
        radiusMinPixels: 6,
        radiusMaxPixels: 44,
        lineWidthMinPixels: 1.5,
        getPosition: (country) => toGlobePosition(country.coordinates),
        getRadius: (country) => 90000 + country.coreMetrics.gdp * 15,
        getFillColor: (country) => countryColor(country.economicHealth),
        getLineColor: [165, 243, 252, 210],
        onClick: (info) => {
          if (info.object) {
            selectEntity(info.object)
          }
        },
      }),
      new PathLayer<FlowPath>({
        id: 'flow-arc-layer-glow',
        data: flowPaths,
        pickable: false,
        getPath: (flow) => flow.path,
        getColor: arcPathGlowColor,
        getWidth: (flow) => Math.max(2.8, flow.value / ARC_GLOW_WIDTH_DIVISOR),
        widthUnits: 'pixels',
        widthMinPixels: 2.8,
        rounded: true,
      }),
      new PathLayer<FlowPath>({
        id: 'flow-arc-layer',
        data: flowPaths,
        pickable: false,
        getPath: (flow) => flow.path,
        getColor: arcPathColor,
        getWidth: (flow) => Math.max(1.2, flow.value / ARC_CORE_WIDTH_DIVISOR),
        widthUnits: 'pixels',
        widthMinPixels: 1.2,
        rounded: true,
      }),
      // Outer halo for financial centers (city lights glow)
      new ScatterplotLayer<FinancialCenterVisual>({
        id: 'financial-centers-halo',
        data: financialCentersWithVisuals,
        pickable: false,
        radiusUnits: 'meters',
        opacity: 0.18,
        getPosition: (center) => toGlobePosition(center.coordinates),
        getRadius: (center) => center.intensity * 18000,
        getFillColor: [255, 180, 60, 255],
        stroked: false,
      }),
      new ScatterplotLayer<FinancialCenterVisual>({
        id: 'financial-centers',
        data: financialCentersWithVisuals,
        pickable: false,
        radiusUnits: 'meters',
        opacity: 0.88,
        getPosition: (center) => toGlobePosition(center.coordinates),
        getRadius: (center) => center.intensity * 5500,
        getFillColor: (center) => center.pointColor,
        getLineColor: [255, 220, 120, 200],
        lineWidthMinPixels: 1,
        stroked: true,
      }),
      new TextLayer<FinancialCenterVisual>({
        id: 'city-labels',
        data: financialCentersWithVisuals,
        pickable: false,
        getPosition: (center) => toGlobePosition(center.coordinates),
        getText: (center) => center.name,
        getSize: (center) => center.labelSize,
        getColor: [220, 240, 255, 230],
        getTextAnchor: 'middle',
        getAlignmentBaseline: 'bottom',
        fontFamily: CITY_LABEL_FONT,
        fontWeight: 600,
        outlineWidth: 2,
        outlineColor: [0, 0, 0, 180],
        getPixelOffset: [0, -18],
        sizeUnits: 'pixels',
        billboard: true,
      }),
    ],
    [flowPaths, selectEntity],
  )
  const layersRef = useRef(layers)
  layersRef.current = layers

  // Keep the deck.gl overlay's layers in sync without recreating the map
  useEffect(() => {
    overlayRef.current?.setProps({ layers })
  }, [layers])

  useEffect(() => {
    const host = containerRef.current
    if (!host || mapRef.current || isCreatingRef.current) return
    if (host.clientWidth < MIN_MAP_HOST_SIZE || host.clientHeight < MIN_MAP_HOST_SIZE) {
      console.warn('[WEOS Map3D] Container too small to initialise globe map')
      onError?.()
      return
    }

    isCreatingRef.current = true
    let styleLoaded = false

    try {
      const map = new maplibregl.Map({
        container: host,
        style: {
          version: 8,
          sources: {
            'carto-dark': {
              type: 'raster',
              tiles: [BASEMAP_TILE_URL],
              tileSize: 256,
              attribution: BASEMAP_ATTRIBUTION,
            },
          },
          layers: [
            { id: 'weos-background', type: 'background', paint: { 'background-color': '#040810' } },
            {
              id: 'basemap-tiles',
              type: 'raster',
              source: 'carto-dark',
              paint: {
                'raster-opacity': 0.88,
                'raster-brightness-min': 0.04,
                'raster-brightness-max': 0.82,
                'raster-contrast': 0.22,
                'raster-saturation': 0.12,
              },
            },
          ],
        },
        center: GLOBE_CENTER,
        zoom: GLOBE_ZOOM,
        attributionControl: false,
      })

      mapRef.current = map

      map.on('load', () => {
        styleLoaded = true
        // Switch to vertical-perspective (globe-like) projection once the style is ready
        map.setProjection({ type: 'vertical-perspective' })
        // Provide built-in zoom/rotation controls for the 3D globe interaction pass
        map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), 'top-right')

        // Mount deck.gl overlay so layers render on top of the MapLibre basemap
        const overlay = new MapboxOverlay({
          layers: layersRef.current,
          onError: (err: unknown) => {
            console.error('[WEOS Map3D] deck.gl overlay error:', err)
            onError?.()
          },
        })
        // MapboxOverlay.onAdd signature accepts `unknown` map; cast for MapLibre's addControl
        map.addControl(overlay as unknown as maplibregl.IControl)
        overlayRef.current = overlay
      })

      map.on('error', (e) => {
        if (!styleLoaded) {
          console.error('[WEOS Map3D] Style failed to load; triggering 2D fallback:', e.error.message)
          onError?.()
        } else {
          console.warn('[WEOS Map3D] Tile/source error (globe still functional):', e.error.message)
        }
      })

      const handleMoveEnd = () => {
        const normalizedLevel = mapZoomToWeosLevel(map.getZoom(), MAP_3D_BASE_ZOOM, MAP_3D_ZOOM_MULTIPLIER)
        if (isSyncingZoomRef.current) {
          isSyncingZoomRef.current = false
          return
        }
        setZoomLevel(normalizedLevel)
      }
      moveEndHandlerRef.current = handleMoveEnd
      map.on('moveend', handleMoveEnd)
    } catch (err) {
      console.error('[WEOS Map3D] Failed to initialise globe map:', err)
      onError?.()
    } finally {
      isCreatingRef.current = false
    }

    return () => {
      if (moveEndHandlerRef.current) {
        mapRef.current?.off('moveend', moveEndHandlerRef.current)
      }
      mapRef.current?.remove()
      mapRef.current = null
      overlayRef.current = null
      moveEndHandlerRef.current = null
      isCreatingRef.current = false
    }
  }, [onError, setZoomLevel])

  useEffect(() => {
    const map = mapRef.current
    if (!map) return

    const targetZoom = weosLevelToMapZoom(zoomLevel, MAP_3D_BASE_ZOOM, MAP_3D_ZOOM_MULTIPLIER)
    if (Math.abs(map.getZoom() - targetZoom) < ZOOM_SYNC_THRESHOLD) return

    isSyncingZoomRef.current = true
    map.easeTo({ zoom: targetZoom, duration: ZOOM_TRANSITION_DURATION_MS })
  }, [zoomLevel])

  return <div ref={containerRef} className="deck-host" />
}
