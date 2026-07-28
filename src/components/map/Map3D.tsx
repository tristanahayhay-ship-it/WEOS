import { useEffect, useMemo, useRef } from 'react'
import { MapboxOverlay } from '@deck.gl/mapbox'
import { ArcLayer, ScatterplotLayer } from '@deck.gl/layers'
import * as maplibregl from 'maplibre-gl'

import { capitalFlows, countries, financialCenters } from '../../data/mockData'
import { useStore } from '../../store/useStore'
import type { CapitalFlow, FinancialCenter, GeoEntity } from '../../types'

interface Map3DProps {
  onError?: () => void
}

const GLOBE_CENTER: [number, number] = [110, 20]
const GLOBE_ZOOM = 1.2
const MIN_MAP_HOST_SIZE = 80

/** CARTO dark-matter tiles — no API key, dark theme matches WEOS neon palette */
const BASEMAP_TILE_URL = 'https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
const BASEMAP_ATTRIBUTION =
  '© <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors ' +
  '© <a href="https://carto.com/" target="_blank">CARTO</a>'

const countryColor = (score: number): [number, number, number, number] => {
  if (score >= 82) return [0, 255, 136, 180]
  if (score >= 74) return [0, 212, 255, 170]
  if (score >= 68) return [255, 136, 0, 160]
  return [255, 68, 68, 170]
}

export function Map3D({ onError }: Map3DProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<maplibregl.Map | null>(null)
  const overlayRef = useRef<MapboxOverlay | null>(null)
  const isCreatingRef = useRef(false)
  const selectEntity = useStore((state) => state.selectEntity)

  const layers = useMemo(
    () => [
      new ScatterplotLayer<GeoEntity>({
        id: 'country-layer',
        data: countries,
        pickable: true,
        opacity: 0.9,
        stroked: true,
        filled: true,
        radiusMinPixels: 5,
        radiusMaxPixels: 40,
        lineWidthMinPixels: 1,
        getPosition: (country) => [country.coordinates.lon, country.coordinates.lat],
        getRadius: (country) => 80000 + country.coreMetrics.gdp * 15,
        getFillColor: (country) => countryColor(country.economicHealth),
        getLineColor: [165, 243, 252, 180],
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
        getSourceColor: [0, 212, 255, 180],
        getTargetColor: [0, 255, 136, 190],
        getWidth: (flow) => Math.max(1, flow.value / 85),
      }),
      new ScatterplotLayer<FinancialCenter>({
        id: 'financial-centers',
        data: financialCenters,
        pickable: false,
        radiusUnits: 'meters',
        getPosition: (center) => [center.coordinates.lon, center.coordinates.lat],
        getRadius: (center) => center.intensity * 4200,
        getFillColor: [255, 136, 0, 160],
        getLineColor: [255, 255, 255, 120],
        stroked: true,
      }),
    ],
    [selectEntity],
  )

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
            { id: 'weos-background', type: 'background', paint: { 'background-color': '#07111e' } },
            { id: 'basemap-tiles', type: 'raster', source: 'carto-dark', paint: { 'raster-opacity': 0.72 } },
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

        // Mount deck.gl overlay so layers render on top of the MapLibre basemap
        const overlay = new MapboxOverlay({
          layers,
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
    } catch (err) {
      console.error('[WEOS Map3D] Failed to initialise globe map:', err)
      onError?.()
    } finally {
      isCreatingRef.current = false
    }

    return () => {
      mapRef.current?.remove()
      mapRef.current = null
      overlayRef.current = null
      isCreatingRef.current = false
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return <div ref={containerRef} className="deck-host" />
}
