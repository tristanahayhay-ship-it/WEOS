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

let _currentZoom = 'GLOBAL';
let _zoomAltitude = 2.5;
let _globeRef = null;

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
  const globe = globeInstance;

  globe.pointOfView({
    lat: country.lat,
    lng: country.lng,
    altitude: 0.6
  }, 1000);

  _currentZoom = 'COUNTRY';
  onZoomChange('COUNTRY', country);
}

// Zoom out về global
function zoomToGlobal(globeInstance) {
  if (!globeInstance) return;
  globeInstance.pointOfView({ altitude: 2.5 }, 1200);
  _currentZoom = 'GLOBAL';
  onZoomChange('GLOBAL', null);
}

// Callback khi thay đổi zoom
function onZoomChange(newLevel, focusData) {
  _currentZoom = newLevel;
  const zoomInfo = ZOOM_LEVELS[newLevel] || ZOOM_LEVELS.GLOBAL;

  // Update arc visibility theo zoom
  updateArcsForZoom(newLevel);

  // Dispatch custom event
  window.dispatchEvent(new CustomEvent('weos:zoomChange', {
    detail: { level: newLevel, info: zoomInfo, focusData }
  }));
}

// Điều chỉnh arc theo zoom
function updateArcsForZoom(zoomLevel) {
  // Tại global: hiển thị tất cả arcs chính
  // Tại country: hiển thị arcs nội địa chi tiết hơn
  // Implementation: signal to app.js via event
}

// Hành vi khi người dùng cuộn (zoom)
function handleGlobeZoom(globeInstance) {
  if (!globeInstance) return;

  // Lắng nghe thay đổi camera
  let checkInterval = setInterval(() => {
    try {
      const pov = globeInstance.pointOfView();
      if (pov && pov.altitude) {
        const newLevel = detectZoomFromAltitude(pov.altitude);
        if (newLevel !== _currentZoom) {
          onZoomChange(newLevel, null);
        }
      }
    } catch(e) {}
  }, 500);

  return checkInterval;
}

// Tạo "kinh mạch" (detail arcs) khi zoom vào quốc gia
function getCountryDetailArcs(country, dxy) {
  const arcs = [];
  if (!country) return arcs;

  // Trung tâm tài chính nội địa
  const financialCenters = getFinancialCenters(country);
  const capitalLat = country.lat;
  const capitalLng = country.lng;

  financialCenters.forEach(center => {
    const dxy_val = dxy || 101;
    const logic = window.USD_LOGIC;
    const dir = logic ? logic.getCountryFlowDirection(country, dxy_val) : 'neutral';
    const color = dir === 'in' ? '#00ff88' : dir === 'out' ? '#ff3344' : '#4488ff';

    arcs.push({
      startLat: capitalLat,
      startLng: capitalLng,
      endLat:   center.lat,
      endLng:   center.lng,
      flowType: dir,
      magnitude: 3 + Math.random() * 3,
      label: `${country.capital} → ${center.name}`,
      color: color,
      asset: center.type,
    });
  });

  return arcs;
}

// Trung tâm tài chính / kinh tế chính của quốc gia
function getFinancialCenters(country) {
  const defaultCenters = [
    { name: 'Sở giao dịch chứng khoán', lat: country.lat + 0.15, lng: country.lng + 0.1,  type: 'Chứng khoán' },
    { name: 'Ngân hàng trung ương',      lat: country.lat - 0.1,  lng: country.lng - 0.15, type: 'Ngân hàng' },
    { name: 'Khu công nghiệp',           lat: country.lat + 0.3,  lng: country.lng + 0.3,  type: 'Sản xuất' },
    { name: 'Cảng thương mại',           lat: country.lat - 0.2,  lng: country.lng + 0.25, type: 'Xuất nhập khẩu' },
  ];

  // Thêm trung tâm đặc thù
  const specificCenters = {
    US: [
      { name: 'New York (Wall Street)', lat: 40.7128, lng: -74.0060, type: 'Tài chính' },
      { name: 'Silicon Valley',          lat: 37.3861, lng: -122.0839, type: 'Công nghệ' },
      { name: 'Chicago (Hàng hóa)',      lat: 41.8781, lng: -87.6298, type: 'Hàng hóa' },
      { name: 'Houston (Dầu mỏ)',        lat: 29.7604, lng: -95.3698, type: 'Năng lượng' },
    ],
    CN: [
      { name: 'Shanghai (Tài chính)',    lat: 31.2304, lng: 121.4737, type: 'Tài chính' },
      { name: 'Shenzhen (Công nghệ)',    lat: 22.5431, lng: 114.0579, type: 'Công nghệ' },
      { name: 'Guangzhou (Xuất khẩu)',   lat: 23.1291, lng: 113.2644, type: 'Xuất khẩu' },
    ],
    JP: [
      { name: 'Tokyo (Tài chính)',       lat: 35.6762, lng: 139.6503, type: 'Tài chính' },
      { name: 'Osaka (Công nghiệp)',     lat: 34.6937, lng: 135.5023, type: 'Công nghiệp' },
    ],
    GB: [
      { name: 'London City (Tài chính)', lat: 51.5155, lng: -0.0922, type: 'Tài chính' },
      { name: 'Manchester (Công nghiệp)',lat: 53.4808, lng: -2.2426, type: 'Công nghiệp' },
    ],
    DE: [
      { name: 'Frankfurt (Tài chính)',   lat: 50.1109, lng: 8.6821,  type: 'Tài chính' },
      { name: 'Hamburg (Cảng)',          lat: 53.5511, lng: 9.9937,  type: 'Thương mại' },
    ],
    VN: [
      { name: 'Hồ Chí Minh',            lat: 10.8231, lng: 106.6297, type: 'Kinh tế' },
      { name: 'Hải Phòng (Cảng)',        lat: 20.8449, lng: 106.6881, type: 'Xuất khẩu' },
      { name: 'Bình Dương (KCN)',        lat: 11.0686, lng: 106.6522, type: 'Sản xuất' },
    ],
  };

  return specificCenters[country.code] || defaultCenters;
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
