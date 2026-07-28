import { Component, type ErrorInfo, type ReactNode, useEffect, useState } from 'react'

import { useStore } from '../../store/useStore'
import { Map2D } from './Map2D'
import { Map3D } from './Map3D'

interface MapRenderBoundaryProps {
  onError: () => void
  children: ReactNode
}

const MAP_3D_FALLBACK_MESSAGE = 'Không thể hiển thị 3D, đã chuyển sang bản đồ 2D.'

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
    if (mapMode === '3D') {
      setMapErrorMessage(null)
    }
  }, [mapMode])

  const activeMapMode = mapMode

  const handle3DMapError = () => {
    setMapErrorMessage(MAP_3D_FALLBACK_MESSAGE)
    setMapMode('2D')
  }

  const handle2DMapError = () => {
    setMapErrorMessage('Không thể tải bản đồ toàn cầu. Vui lòng thử lại.')
  }

  return (
    <div className="map-frame">
      <MapRenderBoundary key={activeMapMode} onError={activeMapMode === '3D' ? handle3DMapError : handle2DMapError}>
        {activeMapMode === '2D' ? <Map2D onError={handle2DMapError} /> : <Map3D onError={handle3DMapError} />}
      </MapRenderBoundary>
      {mapErrorMessage ? <p className="map-error-banner">{mapErrorMessage}</p> : null}
    </div>
  )
}
