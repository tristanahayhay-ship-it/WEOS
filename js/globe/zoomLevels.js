/* =============================================
   WEOS - zoomLevels.js
   Xử lý zoom levels: global → country → city
   ============================================= */

const ZOOM_LEVELS = {
  GLOBAL:  { altitude: 2.5,  label: 'Toàn Cầu',   description: 'Xem dòng tiền toàn cầu 195 quốc gia' },
  REGION:  { altitude: 1.5,  label: 'Khu Vực',    description: 'Dòng tiền trong khu vực' },
  COUNTRY: { altitude: 0.8,  label: 'Quốc Gia',   description: 'Mạch máu kinh tế từng nước' },
  CITY:    { altitude: 0.3,  label: 'Thành Phố',  description: 'Trung tâm tài chính, khu công nghiệp' },
  MICRO:   { altitude: 0.1,  label: 'Vi Mô',      description: 'Doanh nghiệp, sàn giao dịch, quỹ đầu tư' },
};
const DEFAULT_DXY = 101;

let _currentZoom = 'GLOBAL';
let _zoomAltitude = 2.5;
let _globeRef = null;
let _focusedCountry = null;

function initZoomLevels(globeInstance) {
  _globeRef = globeInstance;
}

function getCurrentZoomLevel() {
  return _currentZoom;
}

function getZoomDescription() {
  return ZOOM_LEVELS[_currentZoom] || ZOOM_LEVELS.GLOBAL;
}

// Xác định zoom level dựa trên altitude của camera
function detectZoomFromAltitude(alt) {
  _zoomAltitude = alt;
  if (alt > 2.0)      return 'GLOBAL';
  if (alt > 1.0)      return 'REGION';
  if (alt > 0.5)      return 'COUNTRY';
  if (alt > 0.15)     return 'CITY';
  return 'MICRO';
}

// Zoom đến quốc gia
function zoomToCountry(country, globeInstance) {
  if (!globeInstance || !country) return;
  _focusedCountry = country;
  const globe = globeInstance;

  globe.pointOfView({
    lat: country.lat,
    lng: country.lng,
    altitude: 0.6
  }, 1000);

  _currentZoom = 'COUNTRY';
  updateArcsForZoom('COUNTRY');
  onZoomChange('COUNTRY', country);
}

// Zoom out về global
function zoomToGlobal(globeInstance) {
  if (!globeInstance) return;
  _focusedCountry = null;
  globeInstance.pointOfView({ altitude: 2.5 }, 1200);
  _currentZoom = 'GLOBAL';
  updateArcsForZoom('GLOBAL');
  onZoomChange('GLOBAL', null);
}

// Callback khi thay đổi zoom
function onZoomChange(newLevel, focusData) {
  _currentZoom = newLevel;
  const zoomInfo = ZOOM_LEVELS[newLevel] || ZOOM_LEVELS.GLOBAL;

  // Dispatch custom event
  window.dispatchEvent(new CustomEvent('weos:zoomChange', {
    detail: { level: newLevel, info: zoomInfo, focusData }
  }));
}

// Điều chỉnh arc theo zoom
function updateArcsForZoom(zoomLevel) {
  const globe = _globeRef;
  if (!globe) return;

  if (zoomLevel === 'COUNTRY' || zoomLevel === 'CITY' || zoomLevel === 'MICRO') {
    const currentCountry = _focusedCountry;
    if (currentCountry) {
      const detailArcs = getCountryDetailArcs(
        currentCountry,
        window.DATA_MANAGER ? window.DATA_MANAGER.getDxy() : DEFAULT_DXY
      );
      const globalArcs = window.FLOW_ARCS ? window.FLOW_ARCS.getCurrentArcs() : [];
      globe.arcsData([...globalArcs, ...detailArcs]);
      return;
    }
  }

  const globalArcs = window.FLOW_ARCS ? window.FLOW_ARCS.getCurrentArcs() : [];
  globe.arcsData(globalArcs);
}

// Hành vi khi người dùng cuộn (zoom)
function handleGlobeZoom(globeInstance) {
  if (!globeInstance) return;
  _globeRef = globeInstance;
  globeInstance.controls().addEventListener('change', () => {
    const pov = globeInstance.pointOfView();
    if (!pov || typeof pov.altitude !== 'number') return;
    const alt = pov.altitude;
    const newLevel = detectZoomFromAltitude(alt);
    if (newLevel !== _currentZoom) {
      _currentZoom = newLevel;
      updateArcsForZoom(newLevel);
      onZoomChange(newLevel, _focusedCountry);
    }
  });
}

// Tạo "kinh mạch" (detail arcs) khi zoom vào quốc gia
function getCountryDetailArcs(country, dxy) {
  const arcs = [];
  if (!country) return arcs;
  const centers = getFinancialCenters(country);
  if (!centers || centers.length === 0) return arcs;

  const capitalLat = country.lat;
  const capitalLng = country.lng;
  const flowDir = window.FLOW_ARCS
    ? (window.USD_LOGIC ? window.USD_LOGIC.getCountryFlowDirection(country, dxy) : 'neutral')
    : 'neutral';

  centers.forEach(center => {
    const color = center.type === 'stock'
      ? 'rgba(255,200,0,0.7)'
      : center.type === 'port'
        ? 'rgba(0,180,255,0.7)'
        : center.type === 'industry'
          ? (flowDir === 'in' ? 'rgba(0,255,136,0.7)' : 'rgba(255,51,68,0.7)')
          : 'rgba(200,200,200,0.5)';

    arcs.push({
      startLat: capitalLat,
      startLng: capitalLng,
      endLat: center.lat,
      endLng: center.lng,
      flowType: flowDir,
      magnitude: center.importance || 5,
      color: color,
      label: `${center.name}: ${center.description}`,
      isDetailArc: true,
    });
  });

  return arcs;
}

// Trung tâm tài chính / kinh tế chính của quốc gia
function getFinancialCenters(country) {
  const CENTERS = {
    US: [
      { name: 'NYSE - Phố Wall', lat: 40.7069, lng: -74.0089, type: 'stock', importance: 10, description: 'Sàn CK lớn nhất TG' },
      { name: 'Chicago - Hàng hóa', lat: 41.8781, lng: -87.6298, type: 'industry', importance: 8, description: 'CME Group - Futures' },
      { name: 'Silicon Valley', lat: 37.3861, lng: -122.0839, type: 'industry', importance: 9, description: 'Công nghệ - FDI' },
      { name: 'Houston - Dầu mỏ', lat: 29.7604, lng: -95.3698, type: 'industry', importance: 8, description: 'Trung tâm dầu khí' },
      { name: 'Miami - Tài chính', lat: 25.7617, lng: -80.1918, type: 'stock', importance: 7, description: 'Cầu nối LatAm' },
    ],
    CN: [
      { name: 'Thượng Hải - SSE', lat: 31.2304, lng: 121.4737, type: 'stock', importance: 9, description: 'Sàn CK Thượng Hải' },
      { name: 'Thâm Quyến', lat: 22.5431, lng: 114.0579, type: 'industry', importance: 8, description: 'Trung tâm sản xuất' },
      { name: 'Quảng Châu - Cảng', lat: 23.1291, lng: 113.2644, type: 'port', importance: 8, description: 'Xuất khẩu lớn nhất' },
      { name: 'Hồng Kông', lat: 22.3193, lng: 114.1694, type: 'stock', importance: 9, description: 'Cửa ngõ tài chính' },
    ],
    JP: [
      { name: 'Tokyo - TSE', lat: 35.6762, lng: 139.6503, type: 'stock', importance: 9, description: 'Sàn CK Tokyo' },
      { name: 'Osaka', lat: 34.6937, lng: 135.5023, type: 'industry', importance: 7, description: 'Sản xuất - Kansai' },
      { name: 'Yokohama', lat: 35.4437, lng: 139.6380, type: 'port', importance: 7, description: 'Cảng xuất khẩu' },
    ],
    DE: [
      { name: 'Frankfurt - DAX', lat: 50.1109, lng: 8.6821, type: 'stock', importance: 9, description: 'ECB - Trung tâm tài chính EU' },
      { name: 'Hamburg', lat: 53.5753, lng: 10.0153, type: 'port', importance: 7, description: 'Cảng lớn nhất Đức' },
      { name: 'Munich', lat: 48.1351, lng: 11.5820, type: 'industry', importance: 8, description: 'BMW, Siemens, Allianz' },
    ],
    GB: [
      { name: 'London - LSE', lat: 51.5074, lng: -0.1278, type: 'stock', importance: 10, description: 'Trung tâm tài chính TG' },
      { name: 'Manchester', lat: 53.4808, lng: -2.2426, type: 'industry', importance: 6, description: 'Công nghiệp phía Bắc' },
    ],
    FR: [
      { name: 'Paris - CAC40', lat: 48.8566, lng: 2.3522, type: 'stock', importance: 8, description: 'Euronext Paris' },
      { name: 'Marseille', lat: 43.2965, lng: 5.3698, type: 'port', importance: 6, description: 'Cảng lớn nhất Pháp' },
    ],
    IN: [
      { name: 'Mumbai - BSE', lat: 19.0760, lng: 72.8777, type: 'stock', importance: 9, description: 'Sàn CK Bombay' },
      { name: 'Bangalore', lat: 12.9716, lng: 77.5946, type: 'industry', importance: 8, description: 'Silicon Valley Ấn Độ' },
      { name: 'Chennai', lat: 13.0827, lng: 80.2707, type: 'port', importance: 6, description: 'Cảng - Xuất khẩu ô tô' },
    ],
    BR: [
      { name: 'São Paulo - B3', lat: -23.5505, lng: -46.6333, type: 'stock', importance: 8, description: 'Sàn CK lớn nhất LatAm' },
      { name: 'Rio de Janeiro', lat: -22.9068, lng: -43.1729, type: 'industry', importance: 7, description: 'Dầu mỏ - Petrobras' },
      { name: 'Santos', lat: -23.9608, lng: -46.3336, type: 'port', importance: 7, description: 'Cảng xuất khẩu đậu tương' },
    ],
    RU: [
      { name: 'Moscow - MOEX', lat: 55.7558, lng: 37.6173, type: 'stock', importance: 8, description: 'Sàn CK Moscow' },
      { name: 'St. Petersburg', lat: 59.9311, lng: 30.3609, type: 'port', importance: 6, description: 'Cảng Baltic' },
      { name: 'Norilsk', lat: 69.3558, lng: 88.1893, type: 'industry', importance: 7, description: 'Nickel - Kim loại quý' },
    ],
    SA: [
      { name: 'Riyadh - Tadawul', lat: 24.7136, lng: 46.6753, type: 'stock', importance: 8, description: 'Saudi Aramco' },
      { name: 'Jeddah', lat: 21.3891, lng: 39.8579, type: 'port', importance: 7, description: 'Cảng Biển Đỏ' },
      { name: 'Dhahran - Dầu', lat: 26.2361, lng: 50.0393, type: 'industry', importance: 9, description: 'Aramco Oil Fields' },
    ],
    AU: [
      { name: 'Sydney - ASX', lat: -33.8688, lng: 151.2093, type: 'stock', importance: 7, description: 'Sàn CK Úc' },
      { name: 'Melbourne', lat: -37.8136, lng: 144.9631, type: 'industry', importance: 7, description: 'Tài chính - Dịch vụ' },
      { name: 'Perth - Mining', lat: -31.9505, lng: 115.8605, type: 'industry', importance: 8, description: 'Vàng - Quặng sắt' },
    ],
    CA: [
      { name: 'Toronto - TSX', lat: 43.6532, lng: -79.3832, type: 'stock', importance: 8, description: 'Sàn CK Toronto' },
      { name: 'Vancouver', lat: 49.2827, lng: -123.1207, type: 'port', importance: 7, description: 'Cảng Thái Bình Dương' },
      { name: 'Calgary - Oil', lat: 51.0447, lng: -114.0719, type: 'industry', importance: 8, description: 'Oil Sands Alberta' },
    ],
    KR: [
      { name: 'Seoul - KRX', lat: 37.5665, lng: 126.9780, type: 'stock', importance: 8, description: 'Samsung, Hyundai' },
      { name: 'Busan', lat: 35.1796, lng: 129.0756, type: 'port', importance: 8, description: 'Cảng container lớn' },
    ],
    SG: [
      { name: 'Singapore - SGX', lat: 1.3521, lng: 103.8198, type: 'stock', importance: 9, description: 'Hub tài chính ASEAN' },
      { name: 'Jurong Island', lat: 1.2700, lng: 103.6900, type: 'industry', importance: 8, description: 'Hóa dầu - Lọc dầu' },
    ],
    CH: [
      { name: 'Zurich - SMI', lat: 47.3769, lng: 8.5417, type: 'stock', importance: 9, description: 'UBS, Credit Suisse' },
      { name: 'Geneva', lat: 46.2044, lng: 6.1432, type: 'stock', importance: 8, description: 'Vàng - Tài chính tư nhân' },
    ],
    AE: [
      { name: 'Dubai - DFM', lat: 25.2048, lng: 55.2708, type: 'stock', importance: 8, description: 'Hub tài chính Trung Đông' },
      { name: 'Abu Dhabi - ADNOC', lat: 24.4539, lng: 54.3773, type: 'industry', importance: 9, description: 'Dầu mỏ - ADNOC' },
    ],
    VN: [
      { name: 'TP. Hồ Chí Minh - HoSE', lat: 10.8231, lng: 106.6297, type: 'stock', importance: 7, description: 'Sàn CK lớn nhất VN' },
      { name: 'Bình Dương - KCN', lat: 11.0686, lng: 106.6297, type: 'industry', importance: 7, description: 'Samsung, Foxconn' },
      { name: 'Hải Phòng - Cảng', lat: 20.8449, lng: 106.6881, type: 'port', importance: 7, description: 'Xuất khẩu điện tử' },
      { name: 'Đà Nẵng', lat: 16.0544, lng: 108.2022, type: 'industry', importance: 5, description: 'Du lịch - Dịch vụ' },
    ],
    TH: [
      { name: 'Bangkok - SET', lat: 13.7563, lng: 100.5018, type: 'stock', importance: 7, description: 'Sàn CK Thái Lan' },
      { name: 'Laem Chabang', lat: 13.0846, lng: 100.8820, type: 'port', importance: 7, description: 'Cảng công nghiệp' },
    ],
    ID: [
      { name: 'Jakarta - IDX', lat: -6.2088, lng: 106.8456, type: 'stock', importance: 7, description: 'Sàn CK Indonesia' },
      { name: 'Surabaya', lat: -7.2575, lng: 112.7521, type: 'port', importance: 6, description: 'Cảng xuất khẩu' },
    ],
    MX: [
      { name: 'Mexico City - BMV', lat: 19.4326, lng: -99.1332, type: 'stock', importance: 7, description: 'Sàn CK Mexico' },
      { name: 'Monterrey', lat: 25.6866, lng: -100.3161, type: 'industry', importance: 7, description: 'Sản xuất - Nearshoring' },
    ],
    ZA: [
      { name: 'Johannesburg - JSE', lat: -26.2041, lng: 28.0473, type: 'stock', importance: 7, description: 'Sàn CK lớn nhất Châu Phi' },
      { name: 'Durban', lat: -29.8587, lng: 31.0218, type: 'port', importance: 6, description: 'Cảng lớn nhất SA' },
    ],
    NG: [
      { name: 'Lagos - NSE', lat: 6.5244, lng: 3.3792, type: 'stock', importance: 6, description: 'Sàn CK Nigeria' },
      { name: 'Port Harcourt', lat: 4.8156, lng: 7.0498, type: 'industry', importance: 7, description: 'Dầu mỏ Niger Delta' },
    ],
  };

  return CENTERS[country.code] || [
    {
      name: `Trung tâm tài chính ${country.name}`,
      lat: country.lat + getDeterministicOffset(country, 'lat'),
      lng: country.lng + getDeterministicOffset(country, 'lng'),
      type: 'stock',
      importance: 4,
      description: `GDP: $${country.gdpUSD}B`,
    }
  ];
}

function getDeterministicOffset(country, axis) {
  const code = (country && country.code) || 'XX';
  const seed = `${code}:${axis}`;
  let hash = 0;
  for (let i = 0; i < seed.length; i += 1) {
    hash = ((hash << 5) - hash) + seed.charCodeAt(i);
    hash |= 0;
  }
  return ((Math.abs(hash) % 3000) / 1000) - 1.5;
}

window.ZOOM_LEVELS_MGR = {
  initZoomLevels,
  getCurrentZoomLevel,
  getZoomDescription,
  detectZoomFromAltitude,
  zoomToCountry,
  zoomToGlobal,
  onZoomChange,
  handleGlobeZoom,
  getCountryDetailArcs,
  getFinancialCenters,
  ZOOM_LEVELS,
};
