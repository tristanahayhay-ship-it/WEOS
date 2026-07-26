/* =============================================
   WEOS - globeInit.js
   Địa cầu 3D - Trái tim của WEOS
   ============================================= */

let _globe = null;
let _currentDxy = 101.2;
let _flowMap = {};
let _geoJsonData = null;
let _pointsData = [];
let _isGlobeView = true;

const MAX_PIXEL_RATIO = 1.5;
const POLYGON_LOAD_DELAY_MS = 3000;
const AUTO_ROTATE_SPEED = 0.15;

// --- Tạo points cho thủ đô ---
function buildCapitalPoints(dxy) {
  if (typeof COUNTRIES_DATA === 'undefined') return [];
  const flowMap = _flowMap;
  return COUNTRIES_DATA
    .filter(c => c.lat && c.lng && c.gdpUSD > 0)
    .map(c => ({
      lat: c.lat,
      lng: c.lng,
      country: c,
      direction: flowMap[c.code] || 'neutral',
      name: c.capital,
      code: c.code,
      size: c.code === 'US' ? 0.6 : (c.gdpTier === 1 ? 0.4 : (c.gdpTier === 2 ? 0.32 : 0.22)),
      color: window.COUNTRY_COLORS
        ? window.COUNTRY_COLORS.getCapitalPointColor(c, dxy, flowMap[c.code] || 'neutral')
        : '#ffdd44',
      altitude: c.code === 'US' ? 0.02 : 0.01,
    }));
}

// --- Khởi tạo Globe ---
async function initGlobe(containerId) {
  const container = document.getElementById(containerId || 'globe-container');
  if (!container) { console.error('WEOS: Globe container not found'); return null; }

  setLoadingStatus('Khởi tạo Globe 3D...', 70);

  _flowMap = window.COUNTRY_COLORS ? window.COUNTRY_COLORS.buildFlowMap(_currentDxy) : {};
  const initialArcs = window.FLOW_ARCS ? window.FLOW_ARCS.calculateFlowArcs(_currentDxy) : [];
  _pointsData = buildCapitalPoints(_currentDxy);

  // --- Globe instance ---
  const globe = Globe()
    .globeImageUrl('//unpkg.com/three-globe/example/img/earth-night.jpg')
    .backgroundImageUrl('//unpkg.com/three-globe/example/img/night-sky.png')
    // ===== MẠCH MÁU - ARC LINES =====
    .arcsData(initialArcs)
    .arcColor(d => {
      if (d && d.isDetailArc && d.color) return d.color;
      return window.FLOW_ARCS ? window.FLOW_ARCS.getArcColor(d) : 'rgba(255,51,68,0.5)';
    })
    // Cong cao → nhìn thấy đường cong đẹp qua bầu trời
    .arcAltitude(d => window.FLOW_ARCS ? window.FLOW_ARCS.getArcAltitude(d) : 0.3)
    // Mỏng như sợi chỉ
    .arcStroke(d => window.FLOW_ARCS ? window.FLOW_ARCS.getArcStroke(d) : 0.3)
    // Dash dài = thấy đường rõ, gap nhỏ = chạy liên tục
    .arcDashLength(0.5)
    .arcDashGap(0.5)
    .arcDashAnimateTime(d => window.FLOW_ARCS ? window.FLOW_ARCS.getArcDashAnimateTime(d) : 2000)
    .arcLabel(d => d.label ? `<div class="arc-tooltip">${d.label}</div>` : '')
    // ===== THỦ ĐÔ - DOTS =====
    .pointsData(_pointsData)
    .pointColor(d => d.color || '#ffdd44')
    .pointAltitude(d => d.altitude || 0.01)
    .pointRadius(d => d.size || 0.25)
    .pointLabel(d => `<div class="pt-tooltip"><strong>${d.country.name}</strong><br>${d.name}</div>`)
    .onPointClick(d => {
      if (d && d.country) {
        if (window.COUNTRY_POPUP) window.COUNTRY_POPUP.showCountryPopup(d.country, _currentDxy);
        if (window.ZOOM_LEVELS_MGR) window.ZOOM_LEVELS_MGR.zoomToCountry(d.country, globe);
      }
    })
    .onPointHover(d => d ? showHoverTooltip(d) : hideHoverTooltip())
    (container);

  // Globe settings - tối ưu performance
  globe.controls().autoRotate = true;
  globe.controls().autoRotateSpeed = AUTO_ROTATE_SPEED;
  globe.controls().enableDamping = true;
  globe.controls().dampingFactor = 0.08;

  // Tối ưu renderer ngay
  try {
    const renderer = globe.renderer();
    if (renderer) {
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, MAX_PIXEL_RATIO));
      renderer.shadowMap.enabled = false;
      // Tắt antialias nếu thiết bị yếu
      if (window.devicePixelRatio > 1.5) {
        renderer.setPixelRatio(1);
      }
    }
  } catch (e) {}

  if (window.ZOOM_LEVELS_MGR) window.ZOOM_LEVELS_MGR.handleGlobeZoom(globe);
  _globe = globe;

  // Lazy load polygons sau 3 giây - không block render ban đầu
  setTimeout(async () => {
    if (!_globe) return;
    try {
      const res = await fetch('https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson');
      const geoJson = await res.json();
      _geoJsonData = geoJson;
      applyCountryPolygons(_globe, geoJson);
    } catch (e) {
      console.warn('WEOS: GeoJSON load failed', e);
    }
  }, POLYGON_LOAD_DELAY_MS);

  setLoadingStatus('Globe sẵn sàng!', 90);
  return globe;
}

function applyCountryPolygons(globe, geoJson) {
  if (!globe || !geoJson) return;
  globe
    .polygonsData(geoJson.features || [])
    .polygonCapColor(feat => {
      const code = getFeatureCode(feat);
      if (!code || typeof COUNTRY_MAP === 'undefined') return 'rgba(20,30,60,0.5)';
      const c = COUNTRY_MAP[code];
      if (!c) return 'rgba(20,30,60,0.5)';
      const dir = _flowMap[code] || 'neutral';
      if (dir === 'in')  return 'rgba(0,80,40,0.65)';
      if (dir === 'out') return 'rgba(80,10,10,0.65)';
      const tiers = { 1:'rgba(20,50,120,0.6)', 2:'rgba(15,80,50,0.6)', 3:'rgba(80,65,10,0.6)', 4:'rgba(60,15,15,0.55)' };
      return tiers[c.gdpTier] || 'rgba(20,30,60,0.5)';
    })
    .polygonSideColor(() => 'rgba(0,0,0,0.15)')
    .polygonStrokeColor(() => '#1a2a3a')
    .polygonAltitude(() => 0.001)
    .polygonLabel(feat => {
      const code = getFeatureCode(feat);
      const c = code && COUNTRY_MAP ? COUNTRY_MAP[code] : null;
      if (!c) return '';
      return `<div class="poly-tooltip"><strong>${c.flag || ''} ${c.name}</strong><br>GDP: $${(c.gdpUSD/1000).toFixed(1)}T | 🥇 ${c.goldReserves}t</div>`;
    })
    .onPolygonClick(feat => {
      const code = getFeatureCode(feat);
      const c = code && COUNTRY_MAP ? COUNTRY_MAP[code] : null;
      if (c && window.COUNTRY_POPUP) window.COUNTRY_POPUP.showCountryPopup(c, _currentDxy);
    });
}

function getFeatureCode(feat) {
  if (!feat || !feat.properties) return null;
  return feat.properties.ISO_A2 || feat.properties.iso_a2 ||
         feat.properties.ADM0_A3 || feat.properties.ISO_A3 || null;
}

function updateGlobeForDxy(dxy) {
  _currentDxy = dxy;
  if (!_globe) return;

  _flowMap = window.COUNTRY_COLORS ? window.COUNTRY_COLORS.buildFlowMap(dxy) : {};
  window.COUNTRY_COLORS && window.COUNTRY_COLORS.clearColorCache();

  if (window.FLOW_ARCS) window.FLOW_ARCS.updateFlowArcs(dxy, _globe);

  _pointsData = buildCapitalPoints(dxy);
  _globe.pointsData(_pointsData);

  if (_geoJsonData) {
    _globe.polygonCapColor(feat => {
      const code = getFeatureCode(feat);
      if (!code || typeof COUNTRY_MAP === 'undefined') return 'rgba(20,30,60,0.5)';
      const c = COUNTRY_MAP[code];
      if (!c) return 'rgba(20,30,60,0.5)';
      const dir = _flowMap[code] || 'neutral';
      if (dir === 'in')  return 'rgba(0,80,40,0.7)';
      if (dir === 'out') return 'rgba(80,10,10,0.7)';
      const tiers = { 1:'rgba(20,50,120,0.6)', 2:'rgba(15,80,50,0.6)', 3:'rgba(80,65,10,0.6)', 4:'rgba(60,15,15,0.55)' };
      return tiers[c.gdpTier] || 'rgba(20,30,60,0.5)';
    });
  }
}

function setGlobeView(isGlobe) {
  _isGlobeView = isGlobe !== false;
  if (!_globe) return;
  if (_isGlobeView) {
    _globe.globeImageUrl('//unpkg.com/three-globe/example/img/earth-night.jpg');
    _globe.controls().autoRotate = true;
  } else {
    _globe.controls().autoRotate = false;
    _globe.pointOfView({ altitude: 3.5 }, 800);
  }
}

function showHoverTooltip(pointData) {
  const tooltip = document.getElementById('hover-tooltip');
  if (!tooltip || !pointData) return;
  const c = pointData.country;
  const dir = pointData.direction;
  const icon = dir === 'in' ? '🟢' : dir === 'out' ? '🔴' : '🔵';
  const label = dir === 'in' ? 'Tiền VÀO' : dir === 'out' ? 'Tiền RA' : 'Trung tính';
  tooltip.innerHTML = `<strong>${c.flag || ''} ${c.name}</strong><br>${icon} ${label}<br>GDP: $${(c.gdpUSD/1000).toFixed(1)}T | 🥇${c.goldReserves}t<br><small>Click để xem chi tiết</small>`;
  tooltip.classList.remove('hidden');
  document.addEventListener('mousemove', _posTooltip, { once: true });
}

function _posTooltip(e) {
  const tooltip = document.getElementById('hover-tooltip');
  if (!tooltip) return;
  tooltip.style.left = `${Math.min(e.clientX + 15, window.innerWidth - 240)}px`;
  tooltip.style.top  = `${Math.max(e.clientY - 10, 10)}px`;
}

function hideHoverTooltip() {
  const el = document.getElementById('hover-tooltip');
  if (el) el.classList.add('hidden');
}

function getGlobe() { return _globe; }
function getCurrentDxy() { return _currentDxy; }
function setCurrentDxy(v) { _currentDxy = v; }
function getFlowMap() { return _flowMap; }

function setLoadingStatus(msg, pct) {
  const s = document.getElementById('loading-status');
  const b = document.getElementById('loading-bar');
  if (s) s.textContent = msg;
  if (b && pct !== undefined) b.style.width = pct + '%';
}

window.GLOBE_INIT = {
  initGlobe,
  updateGlobeForDxy,
  setGlobeView,
  getGlobe,
  getCurrentDxy,
  setCurrentDxy,
  getFlowMap,
  setLoadingStatus,
  getFeatureCode,
};
