import { useEffect, useMemo, useRef } from 'react'
import * as maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'

import { capitalFlows, countries } from '../../data/mockData'
import { useStore } from '../../store/useStore'
import { MAP_2D_BASE_ZOOM, MAP_2D_ZOOM_MULTIPLIER, mapZoomToWeosLevel, weosLevelToMapZoom } from './zoomConfig'

interface Map2DProps {
  onError?: () => void
}

const countryColor = (score: number) => {
  if (score >= 82) return '#00ff88'
  if (score >= 74) return '#00d4ff'
  if (score >= 68) return '#ff8800'
  return '#ff4444'
}

const MIN_MAP_HOST_SIZE = 80
const DEFAULT_MAP_CENTER: [number, number] = [8, 20]
const DEFAULT_MAP_ZOOM = 1.2
const MAP_INIT_TIMEOUT_MS = 1500

/** CARTO dark-matter raster tiles — no API key required, matches WEOS neon theme */
const BASEMAP_TILE_URL = 'https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
const BASEMAP_ATTRIBUTION =
  '© <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors ' +
  '© <a href="https://carto.com/" target="_blank">CARTO</a>'

const projectBox = (lat: number, lon: number, scale = 4.5) => {
  const lngDelta = Math.max(3, scale * Math.cos((lat * Math.PI) / 180))
  const latDelta = 3.8

  return [
    [lon - lngDelta, lat - latDelta],
    [lon + lngDelta, lat - latDelta],
    [lon + lngDelta, lat + latDelta],
    [lon - lngDelta, lat + latDelta],
    [lon - lngDelta, lat - latDelta],
  ]
}

export function Map2D({ onError }: Map2DProps) {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const mapRef = useRef<maplibregl.Map | null>(null)
  const isCreatingMapRef = useRef(false)
  const hasReportedErrorRef = useRef(false)
  const isSyncingZoomRef = useRef(false)
  const selectEntity = useStore((state) => state.selectEntity)
  const zoomLevel = useStore((state) => state.zoomLevel)
  const setZoomLevel = useStore((state) => state.setZoomLevel)

  const countryGeoJson = useMemo(
    () => ({
      type: 'FeatureCollection',
      features: countries.map((country) => ({
        type: 'Feature',
        properties: {
          id: country.id,
          name: country.name,
          code: country.code,
          color: countryColor(country.economicHealth),
          score: country.economicHealth,
        },
        geometry: {
          type: 'Polygon',
          coordinates: [projectBox(country.coordinates.lat, country.coordinates.lon)],
        },
      })),
    }),
    [],
  )

  const flowGeoJson = useMemo(
    () => ({
      type: 'FeatureCollection',
      features: capitalFlows.map((flow) => {
        const fromCountry = countries.find((country) => country.id === flow.from)
        const toCountry = countries.find((country) => country.id === flow.to)
        return {
          type: 'Feature',
          properties: {
            value: flow.value,
            color: flow.value > 120 ? '#00d4ff' : '#00ff88',
          },
          geometry: {
            type: 'LineString',
            coordinates: [
              [fromCountry?.coordinates.lon ?? 0, fromCountry?.coordinates.lat ?? 0],
              [toCountry?.coordinates.lon ?? 0, toCountry?.coordinates.lat ?? 0],
            ],
          },
        }
      }),
    }),
    [],
  )

  useEffect(() => {
    if (!containerRef.current || mapRef.current) {
      return
    }

    const host = containerRef.current
    const reportMapError = () => {
      if (hasReportedErrorRef.current) {
        return
      }
      hasReportedErrorRef.current = true
      onError?.()
    }

    const createMap = () => {
      if (mapRef.current) {
        return
      }
      if (isCreatingMapRef.current) {
        return
      }

      if (host.clientWidth < MIN_MAP_HOST_SIZE || host.clientHeight < MIN_MAP_HOST_SIZE) {
        return
      }

      try {
        isCreatingMapRef.current = true
        const map = new maplibregl.Map({
          container: host,
          style: {
            version: 8,
            sources: {
              /** CARTO dark-matter raster tiles provide the Earth basemap */
              'carto-dark': {
                type: 'raster',
                tiles: [BASEMAP_TILE_URL],
                tileSize: 256,
                attribution: BASEMAP_ATTRIBUTION,
              },
            },
            layers: [
              { id: 'weos-background', type: 'background', paint: { 'background-color': '#07111e' } },
              { id: 'basemap-tiles', type: 'raster', source: 'carto-dark', paint: { 'raster-opacity': 0.72 } },
            ],
          },
          center: DEFAULT_MAP_CENTER,
          zoom: DEFAULT_MAP_ZOOM,
          attributionControl: false,
        })

        mapRef.current = map
        map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), 'top-right')

        let styleLoaded = false
        map.on('load', () => {
          styleLoaded = true
          map.addSource('countries-weos', {
            type: 'geojson',
            data: countryGeoJson as never,
          })
          map.addSource('flows-weos', {
            type: 'geojson',
            data: flowGeoJson as never,
          })

          map.addLayer({
            id: 'flows-line',
            type: 'line',
            source: 'flows-weos',
            paint: {
              'line-color': ['get', 'color'],
              'line-width': ['interpolate', ['linear'], ['get', 'value'], 20, 1.2, 320, 3.8],
              'line-opacity': 0.45,
            },
          })

          map.addLayer({
            id: 'countries-fill',
            type: 'fill',
            source: 'countries-weos',
            paint: {
              'fill-color': ['get', 'color'],
              'fill-opacity': 0.42,
            },
          })

          map.addLayer({
            id: 'countries-outline',
            type: 'line',
            source: 'countries-weos',
            paint: {
              'line-color': '#a5f3fc',
              'line-width': 0.8,
              'line-opacity': 0.4,
            },
          })

          map.on('mousemove', 'countries-fill', () => {
            map.getCanvas().style.cursor = 'pointer'
          })

          map.on('mouseleave', 'countries-fill', () => {
            map.getCanvas().style.cursor = ''
          })

          map.on('click', 'countries-fill', (event: maplibregl.MapLayerMouseEvent) => {
            const feature = event.features?.[0]
            const id = feature?.properties?.id as string | undefined
            const match = countries.find((country) => country.id === id)
            if (match) {
              selectEntity(match)
            }
          })
        })

        map.on('error', (e) => {
          if (!styleLoaded) {
            // Style/source failed to load — this is a critical error, trigger fallback
            console.error('[WEOS Map2D] Style failed to load; activating fallback:', e.error.message)
            reportMapError()
          } else {
            // Post-load error — likely a tile fetch issue. Log for diagnostics but keep map alive.
            console.warn('[WEOS Map2D] Tile or source error (map still functional):', e.error.message)
          }
        })
        map.on('moveend', () => {
          const normalizedLevel = mapZoomToWeosLevel(map.getZoom(), MAP_2D_BASE_ZOOM, MAP_2D_ZOOM_MULTIPLIER)
          if (isSyncingZoomRef.current) {
            isSyncingZoomRef.current = false
            return
          }
          setZoomLevel(normalizedLevel)
        })
        isCreatingMapRef.current = false
      } catch {
        isCreatingMapRef.current = false
        reportMapError()
      }
    }

    const resizeObserver = new ResizeObserver(() => {
      if (mapRef.current) {
        mapRef.current.resize()
        return
      }
      createMap()
    })

    const invalidSizeTimer = window.setTimeout(() => {
      if (!mapRef.current && (host.clientWidth < MIN_MAP_HOST_SIZE || host.clientHeight < MIN_MAP_HOST_SIZE)) {
        reportMapError()
      }
    }, MAP_INIT_TIMEOUT_MS)

    resizeObserver.observe(host)
    createMap()

    return () => {
      window.clearTimeout(invalidSizeTimer)
      resizeObserver.disconnect()
      isCreatingMapRef.current = false
      mapRef.current?.remove()
      mapRef.current = null
    }
  }, [countryGeoJson, flowGeoJson, onError, selectEntity, setZoomLevel])

  useEffect(() => {
    const map = mapRef.current
    if (!map) return

    const targetZoom = weosLevelToMapZoom(zoomLevel, MAP_2D_BASE_ZOOM, MAP_2D_ZOOM_MULTIPLIER)
    if (Math.abs(map.getZoom() - targetZoom) < 0.12) return

    isSyncingZoomRef.current = true
    map.easeTo({ zoom: targetZoom, duration: 700 })
  }, [zoomLevel])

  return <div ref={containerRef} className="maplibre-host" />
}
