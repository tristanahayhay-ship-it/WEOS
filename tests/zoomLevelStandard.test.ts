import { expect, test } from '@playwright/test'
import {
  ZOOM_LEVELS,
  ZOOM_LEVEL_LIST,
  dataLayerFromCameraDistance,
  dataLayerFromLevel,
  levelFromCameraDistance,
} from '../src/zoom/levels'
import type { ZoomDataLayerId, ZoomLevelId } from '../src/zoom/types'
import { useZoomStore } from '../src/stores/zoomStore'

const EXPECTED_STANDARD: Array<{ id: ZoomLevelId; name: string; layerId: ZoomDataLayerId }> = [
  { id: 0, name: 'Trái Đất Toàn Cầu', layerId: 'global_earth' },
  { id: 1, name: 'Lục địa', layerId: 'continent' },
  { id: 2, name: 'Quốc gia', layerId: 'country' },
  { id: 3, name: 'Tỉnh/Bang', layerId: 'province_state' },
  { id: 4, name: 'Thành phố', layerId: 'city' },
  { id: 5, name: 'Khu tài chính', layerId: 'financial_district' },
  { id: 6, name: 'Tổ chức', layerId: 'institution' },
  { id: 7, name: 'Doanh nghiệp', layerId: 'corporation' },
  { id: 8, name: 'Nhà máy / Cơ sở', layerId: 'facility' },
  { id: 9, name: 'Mạng lưới logistics', layerId: 'logistics_network' },
  { id: 10, name: 'Dữ liệu thời gian thực', layerId: 'realtime_data' },
]

test.describe('WEOS Zoom Level Standard V1.0', () => {
  test.beforeEach(() => {
    useZoomStore.setState({
      activeLevel: 0,
      activeDataLayerId: ZOOM_LEVELS[0].dataLayer.id,
      transition: null,
      pendingCameraDistance: null,
    })
  })

  test('uses exactly 11 ordered levels with required Vietnamese names', () => {
    expect(ZOOM_LEVEL_LIST).toHaveLength(11)
    for (const expected of EXPECTED_STANDARD) {
      const meta = ZOOM_LEVELS[expected.id]
      expect(meta.id).toBe(expected.id)
      expect(meta.name).toBe(expected.name)
      expect(meta.label).toContain(`Cấp ${expected.id}`)
    }
  })

  test('maps each level to the required deterministic semantic data layer', () => {
    for (const expected of EXPECTED_STANDARD) {
      const layer = dataLayerFromLevel(expected.id)
      expect(layer.id).toBe(expected.layerId)
      expect(layer.semanticItems.length).toBeGreaterThan(0)
    }
  })

  test('switches active data layer by zoom level only', () => {
    for (const expected of EXPECTED_STANDARD) {
      useZoomStore.getState().setLevel(expected.id)
      const state = useZoomStore.getState()
      expect(state.activeLevel).toBe(expected.id)
      expect(state.activeDataLayerId).toBe(expected.layerId)
    }
  })

  test('resolves the correct level and data layer from camera distance ranges', () => {
    for (const expected of EXPECTED_STANDARD) {
      const [min, max] = ZOOM_LEVELS[expected.id].cameraDistanceRange
      const midpoint = (min + max) / 2
      expect(levelFromCameraDistance(midpoint)).toBe(expected.id)
      expect(dataLayerFromCameraDistance(midpoint).id).toBe(expected.layerId)
    }
  })
})
