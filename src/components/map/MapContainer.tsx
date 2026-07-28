import { Component, type ErrorInfo, type ReactNode, useEffect, useMemo, useState } from 'react'

import { useStore } from '../../store/useStore'
import { Map2D } from './Map2D'
import { Map3D } from './Map3D'

interface MapRenderBoundaryProps {
  onError: () => void
  children: ReactNode
}

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
  const [force2DMode, setForce2DMode] = useState(false)

  useEffect(() => {
    if (mapMode === '3D') {
      setForce2DMode(false)
      setMapErrorMessage(null)
      return
    }

    if (force2DMode) {
      setMapErrorMessage('Không thể hiển thị 3D, đã chuyển sang bản đồ 2D.')
    }
  }, [force2DMode, mapMode])

  const activeMapMode = useMemo(() => (mapMode === '3D' && !force2DMode ? '3D' : '2D'), [force2DMode, mapMode])

  const handle3DMapError = () => {
    setForce2DMode(true)
    setMapErrorMessage('Không thể hiển thị 3D, đã chuyển sang bản đồ 2D.')
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
