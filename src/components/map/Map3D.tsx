import { useMemo } from 'react'
import { _GlobeView as GlobeView } from '@deck.gl/core'
import { ArcLayer, ScatterplotLayer } from '@deck.gl/layers'
import DeckGL from '@deck.gl/react'

import { capitalFlows, countries, financialCenters } from '../../data/mockData'
import { useStore } from '../../store/useStore'
import type { CapitalFlow, FinancialCenter, GeoEntity } from '../../types'

interface Map3DProps {
  onError?: () => void
}

const DEFAULT_3D_VIEW_STATE = {
  longitude: 12,
  latitude: 20,
  zoom: 0.55,
}

const countryColor = (score: number): [number, number, number, number] => {
  if (score >= 82) return [0, 255, 136, 180]
  if (score >= 74) return [0, 212, 255, 170]
  if (score >= 68) return [255, 136, 0, 160]
  return [255, 68, 68, 170]
}

export function Map3D({ onError }: Map3DProps) {
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

  return (
    <div className="deck-host">
      <DeckGL
        controller
        views={new GlobeView()}
        initialViewState={DEFAULT_3D_VIEW_STATE}
        layers={layers}
        onError={onError}
        style={{ background: 'radial-gradient(circle at 30% 20%, rgba(0,212,255,0.08), rgba(3,7,18,0.92))' }}
      />
    </div>
  )
}
