import { useStore } from '../../store/useStore'
import { Map2D } from './Map2D'
import { Map3D } from './Map3D'

export function MapContainer() {
  const mapMode = useStore((state) => state.mapMode)

  return <div className="map-frame">{mapMode === '2D' ? <Map2D /> : <Map3D />}</div>
}
