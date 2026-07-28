import { Component, type ErrorInfo, type ReactNode, useEffect, useState } from 'react'

import { useStore } from '../../store/useStore'
import { Map2D } from './Map2D'
import { Map3D } from './Map3D'

interface MapRenderBoundaryProps {
  onError: () => void
  children: ReactNode
}

const MAP_3D_FALLBACK_MESSAGE = '3D globe unavailable — switched to 2D map.'

interface MapRenderBoundaryState {
  hasError: boolean
}

class MapRenderBoundary extends Component<MapRenderBoundaryProps, MapRenderBoundaryState> {
  override state: MapRenderBoundaryState = {
    hasError: false,
  }

  static getDerivedStateFromError() {
    return {
      hasError: true,
    }
  }

  override componentDidCatch(_error: Error, _errorInfo: ErrorInfo) {
    this.props.onError()
  }

  override render() {
    if (this.state.hasError) {
      return null
    }

    return this.props.children
  }
}

export function MapContainer() {
  const mapMode = useStore((state) => state.mapMode)
  const setMapMode = useStore((state) => state.setMapMode)
  const [mapErrorMessage, setMapErrorMessage] = useState<string | null>(null)

  useEffect(() => {
    // Clear stale error when the user switches map modes
    setMapErrorMessage(null)
  }, [mapMode])

  const handle3DMapError = () => {
    setMapErrorMessage(MAP_3D_FALLBACK_MESSAGE)
    setMapMode('2D')
  }

  const handle2DMapError = () => {
    setMapErrorMessage('Basemap unavailable — displaying overlays only.')
  }

  return (
    <div className="map-frame">
      <MapRenderBoundary key={mapMode} onError={mapMode === '3D' ? handle3DMapError : handle2DMapError}>
        {mapMode === '2D' ? <Map2D onError={handle2DMapError} /> : <Map3D onError={handle3DMapError} />}
      </MapRenderBoundary>
      {mapErrorMessage ? <p className="map-error-banner">{mapErrorMessage}</p> : null}
    </div>
  )
}
