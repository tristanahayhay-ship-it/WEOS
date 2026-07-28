import { useEffect, useMemo, useRef } from 'react'
import { MapboxOverlay } from '@deck.gl/mapbox'
import { ArcLayer, ScatterplotLayer, TextLayer } from '@deck.gl/layers'
import * as maplibregl from 'maplibre-gl'

import { capitalFlows, countries, financialCenters } from '../../data/mockData'
import { useStore } from '../../store/useStore'
import type { CapitalFlow, FinancialCenter, GeoEntity } from '../../types'
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

/** Arc source color based on flow direction */
const arcSourceColor = (flow: CapitalFlow): [number, number, number, number] => {
  if (flow.direction === 'outbound') return [255, 100, 50, 210]
  if (flow.direction === 'inbound') return [0, 255, 136, 210]
  return [0, 180, 255, 200]
}

/** Arc target color based on flow direction */
const arcTargetColor = (flow: CapitalFlow): [number, number, number, number] => {
  if (flow.direction === 'outbound') return [255, 50, 50, 180]
  if (flow.direction === 'inbound') return [0, 212, 255, 200]
  return [0, 255, 200, 190]
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
  const selectEntity = useStore((state) => state.selectEntity)
  const zoomLevel = useStore((state) => state.zoomLevel)
  const setZoomLevel = useStore((state) => state.setZoomLevel)

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
        getPosition: (country) => [country.coordinates.lon, country.coordinates.lat],
        getRadius: (country) => 90000 + country.coreMetrics.gdp * 15,
        getFillColor: (country) => countryColor(country.economicHealth),
        getLineColor: [165, 243, 252, 210],
        onClick: (info) => {
          if (info.object) {
            selectEntity(info.object)
          }
        },
      }),
      new ArcLayer<CapitalFlow>({
        id: 'flow-arc-layer',
        data: capitalFlows,
        pickable: false,
        getSourcePosition: (flow) => {
          const country = countries.find((item) => item.id === flow.from)
          return [country?.coordinates.lon ?? 0, country?.coordinates.lat ?? 0]
        },
        getTargetPosition: (flow) => {
          const country = countries.find((item) => item.id === flow.to)
          return [country?.coordinates.lon ?? 0, country?.coordinates.lat ?? 0]
        },
        getSourceColor: arcSourceColor,
        getTargetColor: arcTargetColor,
        getWidth: (flow) => Math.max(1.2, flow.value / 70),
        greatCircle: true,
        numSegments: 64,
      }),
      // Outer halo for financial centers (city lights glow)
      new ScatterplotLayer<FinancialCenterVisual>({
        id: 'financial-centers-halo',
        data: financialCentersWithVisuals,
        pickable: false,
        radiusUnits: 'meters',
        opacity: 0.18,
        getPosition: (center) => [center.coordinates.lon, center.coordinates.lat],
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
        getPosition: (center) => [center.coordinates.lon, center.coordinates.lat],
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
        getPosition: (center) => [center.coordinates.lon, center.coordinates.lat],
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
    [selectEntity],
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
