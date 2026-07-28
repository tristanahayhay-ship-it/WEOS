import { useEffect, useMemo, useRef } from 'react'
import * as maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'

import { capitalFlows, countries } from '../../data/mockData'
import { useStore } from '../../store/useStore'
import { ZoomLevel } from '../../types'

const countryColor = (score: number) => {
  if (score >= 82) return '#00ff88'
  if (score >= 74) return '#00d4ff'
  if (score >= 68) return '#ff8800'
  return '#ff4444'
}

const WEOS_BASE_MAPLIBRE_ZOOM = 1
const WEOS_ZOOM_MULTIPLIER = 1.7

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

export function Map2D() {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const mapRef = useRef<maplibregl.Map | null>(null)
  const selectEntity = useStore((state) => state.selectEntity)
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

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
      center: [12, 22],
      zoom: 1.35,
      attributionControl: false,
    })

    mapRef.current = map
    map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), 'top-right')

    map.on('load', () => {
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

    map.on('moveend', () => {
      const normalizedLevel = Math.max(
        0,
        Math.min(
          10,
          Math.round((map.getZoom() - WEOS_BASE_MAPLIBRE_ZOOM) * WEOS_ZOOM_MULTIPLIER),
        ),
      )
      setZoomLevel(normalizedLevel as ZoomLevel)
    })

    return () => {
      map.remove()
      mapRef.current = null
    }
  }, [countryGeoJson, flowGeoJson, selectEntity, setZoomLevel])

  return <div ref={containerRef} className="maplibre-host" />
}
