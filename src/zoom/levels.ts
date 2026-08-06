import type { ZoomLevelId, ZoomLevelMetadata, ZoomDataLayerSpec } from './types'

/**
 * Canonical zoom-level definitions for WEOS Zoom Level Standard V1.0.
 *
 * Camera distances are in Three.js scene units where EARTH_RADIUS = 1.0.
 * GlobeEngine orbit band:
 *   minDistance = 1.75
 *   maxDistance = 5.5
 */
export const ZOOM_LEVELS: Record<ZoomLevelId, ZoomLevelMetadata> = {
  0: {
    id: 0,
    name: 'Trái Đất Toàn Cầu',
    label: 'Cấp 0 — Trái Đất Toàn Cầu',
    cameraDistance: 5.15,
    cameraDistanceRange: [4.8, 5.5],
    showBoundaries: true,
    showCountryLayer: false,
    overlay: { visible: true, metric: 'gdp' },
    flow: { visible: true, visibleTypes: ['trade', 'investment', 'debt', 'aid'] },
    panel: { showCountryPanel: false },
    dataLayer: {
      id: 'global_earth',
      label: 'Dòng dữ liệu Trái Đất Toàn Cầu',
      semanticItems: [
        'Capital Flow toàn cầu',
        'Dòng tiền giữa các trung tâm tài chính',
        'GDP Heatmap',
        'DXY',
        'Gold',
        'Oil',
        'VIX',
        'US10Y',
        'Tin tức toàn cầu',
        'AI Summary',
        'Geopolitical Risk',
        'Weather Risk',
        'Shipping Risk',
      ],
    },
    transitionDuration: 1200,
  },
  1: {
    id: 1,
    name: 'Lục địa',
    label: 'Cấp 1 — Lục địa',
    cameraDistance: 4.5,
    cameraDistanceRange: [4.2, 4.8],
    showBoundaries: true,
    showCountryLayer: true,
    overlay: { visible: true, metric: 'gdp' },
    flow: { visible: true, visibleTypes: ['trade', 'investment', 'debt'] },
    panel: { showCountryPanel: false },
    dataLayer: {
      id: 'continent',
      label: 'Dòng dữ liệu Lục địa',
      semanticItems: [
        'GDP khu vực',
        'Xuất nhập khẩu',
        'Capital Flow nội vùng',
        'Các trung tâm tài chính',
        'Chuỗi cung ứng',
        'Tuyến vận tải',
        'Chỉ số kinh tế khu vực',
        'AI phân tích khu vực',
      ],
    },
    transitionDuration: 1100,
  },
  2: {
    id: 2,
    name: 'Quốc gia',
    label: 'Cấp 2 — Quốc gia',
    cameraDistance: 3.9,
    cameraDistanceRange: [3.6, 4.2],
    showBoundaries: true,
    showCountryLayer: true,
    overlay: { visible: false },
    flow: { visible: true, visibleTypes: ['trade', 'investment'] },
    panel: { showCountryPanel: true },
    dataLayer: {
      id: 'country',
      label: 'Dòng dữ liệu Quốc gia',
      semanticItems: [
        'GDP',
        'CPI',
        'PPI',
        'Lãi suất',
        'Ngân hàng trung ương',
        'Tỷ giá',
        'Chứng khoán',
        'Vàng',
        'Xuất nhập khẩu',
        'Dòng vốn',
        'Bản đồ kinh tế',
        'AI Insight',
      ],
    },
    transitionDuration: 1000,
  },
  3: {
    id: 3,
    name: 'Tỉnh/Bang',
    label: 'Cấp 3 — Tỉnh/Bang',
    cameraDistance: 3.35,
    cameraDistanceRange: [3.1, 3.6],
    showBoundaries: true,
    showCountryLayer: true,
    overlay: { visible: false },
    flow: { visible: false },
    panel: { showCountryPanel: false },
    dataLayer: {
      id: 'province_state',
      label: 'Dòng dữ liệu Tỉnh/Bang',
      semanticItems: [
        'GDP bang/tỉnh',
        'Thuế',
        'Dân số',
        'Logistics',
        'Nhà máy',
        'Công nghệ',
        'Khu công nghiệp',
        'AI phân tích',
      ],
    },
    transitionDuration: 950,
  },
  4: {
    id: 4,
    name: 'Thành phố',
    label: 'Cấp 4 — Thành phố',
    cameraDistance: 2.9,
    cameraDistanceRange: [2.7, 3.1],
    showBoundaries: true,
    showCountryLayer: true,
    overlay: { visible: false },
    flow: { visible: false },
    panel: { showCountryPanel: false },
    dataLayer: {
      id: 'city',
      label: 'Dòng dữ liệu Thành phố',
      semanticItems: [
        'GDP thành phố',
        'Bất động sản',
        'Cảng',
        'Sân bay',
        'Metro',
        'Trung tâm thương mại',
        'Logistics',
        'Khu tài chính',
      ],
    },
    transitionDuration: 900,
  },
  5: {
    id: 5,
    name: 'Khu tài chính',
    label: 'Cấp 5 — Khu tài chính',
    cameraDistance: 2.52,
    cameraDistanceRange: [2.35, 2.7],
    showBoundaries: true,
    showCountryLayer: true,
    overlay: { visible: false },
    flow: { visible: false },
    panel: { showCountryPanel: false },
    dataLayer: {
      id: 'financial_district',
      label: 'Dòng dữ liệu Khu tài chính',
      semanticItems: [
        'Node: JPMorgan',
        'Node: Goldman Sachs',
        'Node: Citigroup',
        'Node: BlackRock',
        'Node: Morgan Stanley',
        'Node: Nasdaq',
        'Node: NYSE',
        'Chi tiết node: Tổng tài sản',
        'Chi tiết node: Dòng vốn',
        'Chi tiết node: Rủi ro',
        'Chi tiết node: Tin tức',
        'Chi tiết node: AI Insight',
      ],
    },
    transitionDuration: 850,
  },
  6: {
    id: 6,
    name: 'Tổ chức',
    label: 'Cấp 6 — Tổ chức',
    cameraDistance: 2.22,
    cameraDistanceRange: [2.1, 2.35],
    showBoundaries: false,
    showCountryLayer: false,
    overlay: { visible: false },
    flow: { visible: false },
    panel: { showCountryPanel: false },
    dataLayer: {
      id: 'institution',
      label: 'Dòng dữ liệu Tổ chức',
      semanticItems: [
        'Balance Sheet',
        'Interest Rate',
        'QE',
        'QT',
        'Repo',
        'Reverse Repo',
        'Dollar Liquidity',
        'Meeting',
        'FOMC',
        'AI Analysis',
      ],
    },
    transitionDuration: 800,
  },
  7: {
    id: 7,
    name: 'Doanh nghiệp',
    label: 'Cấp 7 — Doanh nghiệp',
    cameraDistance: 2.02,
    cameraDistanceRange: [1.95, 2.1],
    showBoundaries: false,
    showCountryLayer: false,
    overlay: { visible: false },
    flow: { visible: false },
    panel: { showCountryPanel: false },
    dataLayer: {
      id: 'corporation',
      label: 'Dòng dữ liệu Doanh nghiệp',
      semanticItems: [
        'Stock',
        'Revenue',
        'Profit',
        'Market Cap',
        'Employees',
        'Cash',
        'Debt',
        'R&D',
        'ESG',
        'Supply Chain',
        'AI Analysis',
      ],
    },
    transitionDuration: 750,
  },
  8: {
    id: 8,
    name: 'Nhà máy / Cơ sở',
    label: 'Cấp 8 — Nhà máy / Cơ sở',
    cameraDistance: 1.9,
    cameraDistanceRange: [1.85, 1.95],
    showBoundaries: false,
    showCountryLayer: false,
    overlay: { visible: false },
    flow: { visible: false },
    panel: { showCountryPanel: false },
    dataLayer: {
      id: 'facility',
      label: 'Dòng dữ liệu Nhà máy / Cơ sở',
      semanticItems: [
        'Công suất',
        'Nhà cung cấp',
        'Điện năng',
        'LNG',
        'Carbon',
        'Kho',
        'Robot',
        'Container',
        'Warehouse',
        'Logistics',
      ],
    },
    transitionDuration: 700,
  },
  9: {
    id: 9,
    name: 'Mạng lưới logistics',
    label: 'Cấp 9 — Mạng lưới logistics',
    cameraDistance: 1.82,
    cameraDistanceRange: [1.79, 1.85],
    showBoundaries: false,
    showCountryLayer: false,
    overlay: { visible: false },
    flow: { visible: true, visibleTypes: ['trade', 'investment'] },
    panel: { showCountryPanel: false },
    dataLayer: {
      id: 'logistics_network',
      label: 'Dòng dữ liệu Mạng lưới logistics',
      semanticItems: [
        'Shipping',
        'Container',
        'Air Cargo',
        'LNG',
        'Pipeline',
        'Railway',
        'Highway',
        'Choke Point',
        'Satellite Tracking',
        'AI Logistics',
      ],
    },
    transitionDuration: 650,
  },
  10: {
    id: 10,
    name: 'Dữ liệu thời gian thực',
    label: 'Cấp 10 — Dữ liệu thời gian thực',
    cameraDistance: 1.77,
    cameraDistanceRange: [1.75, 1.79],
    showBoundaries: false,
    showCountryLayer: false,
    overlay: { visible: false },
    flow: { visible: true, visibleTypes: ['trade', 'investment', 'debt', 'aid'] },
    panel: { showCountryPanel: false },
    dataLayer: {
      id: 'realtime_data',
      label: 'Dòng dữ liệu thời gian thực',
      semanticItems: [
        'Stock',
        'Bond',
        'Forex',
        'Crypto',
        'Commodity',
        'News',
        'Order Book',
        'Trade Feed',
        'AI Signals',
        'Alert',
        'Notification',
        'Market Scanner',
        'Economic Calendar',
      ],
    },
    transitionDuration: 600,
  },
}

/** Ordered array of levels from outermost to innermost */
export const ZOOM_LEVEL_LIST: ZoomLevelMetadata[] = [
  ZOOM_LEVELS[0],
  ZOOM_LEVELS[1],
  ZOOM_LEVELS[2],
  ZOOM_LEVELS[3],
  ZOOM_LEVELS[4],
  ZOOM_LEVELS[5],
  ZOOM_LEVELS[6],
  ZOOM_LEVELS[7],
  ZOOM_LEVELS[8],
  ZOOM_LEVELS[9],
  ZOOM_LEVELS[10],
]

export function dataLayerFromLevel(level: ZoomLevelId): ZoomDataLayerSpec {
  return ZOOM_LEVELS[level].dataLayer
}

export function dataLayerFromCameraDistance(distance: number): ZoomDataLayerSpec {
  return dataLayerFromLevel(levelFromCameraDistance(distance))
}

/**
 * Determine which zoom level a given camera distance belongs to.
 * Falls back to level 0 when no range matches.
 */
export function levelFromCameraDistance(distance: number): ZoomLevelId {
  for (const level of ZOOM_LEVEL_LIST) {
    const [min, max] = level.cameraDistanceRange
    if (distance >= min && distance <= max) return level.id
  }
  // Closer than the innermost band.
  if (distance < ZOOM_LEVELS[10].cameraDistanceRange[0]) return 10
  // Farther than the outermost band.
  if (distance > ZOOM_LEVELS[0].cameraDistanceRange[1]) return 0
  // In case of any accidental future gap between ranges, choose nearest band.
  for (let index = 0; index < ZOOM_LEVEL_LIST.length - 1; index += 1) {
    const outer = ZOOM_LEVEL_LIST[index]!
    const inner = ZOOM_LEVEL_LIST[index + 1]!
    const gapDistanceFar = outer.cameraDistanceRange[0]
    const gapDistanceClose = inner.cameraDistanceRange[1]
    if (gapDistanceClose < gapDistanceFar && distance < gapDistanceFar && distance > gapDistanceClose) {
      return distance > (outer.cameraDistanceRange[0] + inner.cameraDistanceRange[1]) / 2
        ? outer.id
        : inner.id
    }
  }
  return 0
}
