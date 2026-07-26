/* =============================================
   WEOS - globeInit.js
   Khởi tạo globe.gl - Trái đất 3D với dòng tiền
   ============================================= */

let _globe = null;
let _currentDxy = 101.2;
let _flowMap = {};
let _geoJsonData = null;
let _pointsData = [];
let _isGlobeView = true;
const MAX_PIXEL_RATIO = 1.5;
const POLYGON_LOAD_DELAY_MS = 2000;
const AUTO_ROTATE_SPEED = 0.2;

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
      size: c.code === 'US' ? 0.7 : (c.gdpTier === 1 ? 0.45 : (c.gdpTier === 2 ? 0.38 : 0.28)),
      color: window.COUNTRY_COLORS
        ? window.COUNTRY_COLORS.getCapitalPointColor(c, dxy, flowMap[c.code] || 'neutral')
        : '#ffdd44',
      altitude: c.code === 'US' ? 0.025 : 0.012,
    }));
}

// --- Khởi tạo Globe ---
async function initGlobe(containerId) {
  const container = document.getElementById(containerId || 'globe-container');
  if (!container) {
    console.error('WEOS: Globe container not found');
    return null;
  }

  setLoadingStatus('Khởi tạo Globe 3D...', 70);

  _flowMap = window.COUNTRY_COLORS
    ? window.COUNTRY_COLORS.buildFlowMap(_currentDxy)
    : {};

  const initialArcs = window.FLOW_ARCS
    ? window.FLOW_ARCS.calculateFlowArcs(_currentDxy)
    : [];

  _pointsData = buildCapitalPoints(_currentDxy);

  // --- Tạo Globe instance ---
  const globe = Globe()
    .globeImageUrl('//unpkg.com/three-globe/example/img/earth-night.jpg')
    .backgroundImageUrl('//unpkg.com/three-globe/example/img/night-sky.png')
    // Arcs - mạch máu dòng tiền
    .arcsData(initialArcs)
    .arcColor(d => {
      if (d && d.isDetailArc && d.color) return d.color;
      const alpha = Math.max(0.3, Math.min(0.8, (d?.magnitude || 5) / 10));
      return d && d.flowType === 'in'
        ? `rgba(0,255,136,${alpha})`
        : `rgba(255,51,68,${alpha})`;
    })
    .arcAltitude(d => Math.max(0.1, Math.min((d?.magnitude || 5) * 0.025, 0.35)))
    .arcStroke(d => Math.max(0.15, Math.min((d?.magnitude || 5) * 0.05, 0.5)))
    .arcDashLength(0.6)
    .arcDashGap(0.4)
    .arcDashAnimateTime(d => window.FLOW_ARCS ? window.FLOW_ARCS.getArcDashAnimateTime(d) : 2000)
    .arcLabel(d => `<div class="arc-tooltip">${d.label || ''}</div>`)
    // Points tại thủ đô
    .pointsData(_pointsData)
    .pointColor(d => d.color || '#ffdd44')
    .pointAltitude(d => d.altitude || 0.012)
    .pointRadius(d => d.size || 0.3)
    .pointLabel(d => `<div class="pt-tooltip"><strong>${d.country.name}</strong><br>${d.name}</div>`)
    .onPointClick(d => {
      if (d && d.country) {
        if (window.COUNTRY_POPUP) {
          window.COUNTRY_POPUP.showCountryPopup(d.country, _currentDxy);
        }
        if (window.ZOOM_LEVELS_MGR) {
          window.ZOOM_LEVELS_MGR.zoomToCountry(d.country, globe);
        }
      }
    })
    .onPointHover(d => {
      if (d) {
        showHoverTooltip(d);
      } else {
        hideHoverTooltip();
      }
    })
    (container);

  // --- Globe settings ---
  globe.controls().autoRotate = true;
  globe.controls().autoRotateSpeed = AUTO_ROTATE_SPEED;
  globe.controls().enableDamping = true;
  globe.controls().dampingFactor = 0.05;

  // Bắt đầu theo dõi zoom
  if (window.ZOOM_LEVELS_MGR) {
    window.ZOOM_LEVELS_MGR.handleGlobeZoom(globe);
  }

  _globe = globe;
  // Tối ưu renderer
  try {
    const renderer = globe.renderer();
    if (renderer) {
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, MAX_PIXEL_RATIO));
      renderer.shadowMap.enabled = false;
    }
  } catch (e) {}

  // Lazy load polygons để giảm giật lúc khởi tạo
  setTimeout(async () => {
    if (!_globe) return;
    setLoadingStatus('Đang tải bản đồ địa lý...', 80);
    try {
      const res = await fetch('https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson');
      const geoJson = await res.json();
      _geoJsonData = geoJson;
      applyCountryPolygons(_globe, geoJson);
    } catch (e) {
      console.warn('WEOS: Could not lazy-load GeoJSON polygons', e);
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
      if (!code || typeof COUNTRY_MAP === 'undefined') return 'rgba(30,40,80,0.6)';
      const c = COUNTRY_MAP[code];
      if (!c) return 'rgba(30,40,80,0.6)';
      const dir = _flowMap[code] || 'neutral';
      if (dir === 'in') return 'rgba(0,60,30,0.7)';
      if (dir === 'out') return 'rgba(60,10,10,0.7)';
      const tiers = { 1: 'rgba(20,50,110,0.7)', 2: 'rgba(15,80,45,0.7)', 3: 'rgba(90,70,15,0.7)', 4: 'rgba(80,15,15,0.7)' };
      return tiers[c.gdpTier] || 'rgba(30,40,80,0.6)';
    })
    .polygonSideColor(() => 'rgba(0,0,0,0.2)')
    .polygonStrokeColor(() => '#223344')
    // Flat altitude để giảm animation/geometry load, giúp mượt hơn trên thiết bị yếu
    .polygonAltitude(() => 0.001)
    .polygonLabel(feat => {
      const code = getFeatureCode(feat);
      const c = code && COUNTRY_MAP ? COUNTRY_MAP[code] : null;
      if (!c) return '';
      return `<div class="poly-tooltip"><strong>${c.flag} ${c.name}</strong><br>GDP: $${(c.gdpUSD/1000).toFixed(1)}T | Vàng: ${c.goldReserves}t</div>`;
    })
    .onPolygonClick(feat => {
      const code = getFeatureCode(feat);
      const c = code && COUNTRY_MAP ? COUNTRY_MAP[code] : null;
      if (c && window.COUNTRY_POPUP) {
        window.COUNTRY_POPUP.showCountryPopup(c, _currentDxy);
      }
    });
}

// --- Helper lấy country code từ GeoJSON feature ---
function getFeatureCode(feat) {
  if (!feat || !feat.properties) return null;
  return feat.properties.ISO_A2 || feat.properties.iso_a2 ||
         feat.properties.ADM0_A3 || feat.properties.ISO_A3 || null;
}

// --- Update globe khi DXY thay đổi ---
function updateGlobeForDxy(dxy) {
  _currentDxy = dxy;
  if (!_globe) return;

  _flowMap = window.COUNTRY_COLORS
    ? window.COUNTRY_COLORS.buildFlowMap(dxy)
    : {};

  window.COUNTRY_COLORS && window.COUNTRY_COLORS.clearColorCache();

  // Update arcs
  if (window.FLOW_ARCS) {
    window.FLOW_ARCS.updateFlowArcs(dxy, _globe);
  }

  // Update points
  _pointsData = buildCapitalPoints(dxy);
  _globe.pointsData(_pointsData);

  // Update polygon colors
  if (_geoJsonData) {
    _globe.polygonCapColor(feat => {
      const code = getFeatureCode(feat);
      if (!code || typeof COUNTRY_MAP === 'undefined') return 'rgba(30,40,80,0.6)';
      const c = COUNTRY_MAP[code];
      if (!c) return 'rgba(30,40,80,0.6)';
      const dir = _flowMap[code] || 'neutral';
      if (dir === 'in')  return 'rgba(0,60,30,0.75)';
      if (dir === 'out') return 'rgba(60,10,10,0.75)';
      const tiers = {1:'rgba(20,50,110,0.7)',2:'rgba(15,80,45,0.7)',3:'rgba(90,70,15,0.7)',4:'rgba(80,15,15,0.7)'};
      return tiers[c.gdpTier] || 'rgba(30,40,80,0.6)';
    });
  }
}

// --- Switch Globe/Flat ---
function setGlobeView(isGlobe) {
  _isGlobeView = isGlobe !== false;
  if (!_globe) return;
  if (_isGlobeView) {
    // Sphere
    _globe.globeImageUrl('//unpkg.com/three-globe/example/img/earth-night.jpg');
    _globe.controls().autoRotate = true;
  } else {
    // Flat map - dừng rotation
    _globe.controls().autoRotate = false;
    _globe.pointOfView({ altitude: 3.5 }, 800);
  }
}

// --- Hover tooltip ---
function showHoverTooltip(pointData) {
  const tooltip = document.getElementById('hover-tooltip');
  if (!tooltip || !pointData) return;

  const c = pointData.country;
  const dir = pointData.direction;
  const dirIcon = dir === 'in' ? '🟢' : dir === 'out' ? '🔴' : '🔵';
  const dirLabel = dir === 'in' ? 'Tiền VÀO' : dir === 'out' ? 'Tiền RA' : 'Trung tính';

  tooltip.innerHTML = `
    <strong>${c.flag} ${c.name}</strong><br>
    ${dirIcon} ${dirLabel}<br>
    GDP: $${(c.gdpUSD/1000).toFixed(1)}T | 🥇${c.goldReserves}t<br>
    <small>Click để xem chi tiết</small>
  `;
  tooltip.classList.remove('hidden');

  // Position tooltip near mouse
  document.addEventListener('mousemove', _posTooltip, { once: true });
}

function _posTooltip(e) {
  const tooltip = document.getElementById('hover-tooltip');
  if (!tooltip) return;
  const x = e.clientX + 15;
  const y = e.clientY - 10;
  tooltip.style.left = `${Math.min(x, window.innerWidth - 240)}px`;
  tooltip.style.top  = `${Math.max(y, 10)}px`;
}

function hideHoverTooltip() {
  const tooltip = document.getElementById('hover-tooltip');
  if (tooltip) tooltip.classList.add('hidden');
}

// --- Getters ---
function getGlobe() { return _globe; }
function getCurrentDxy() { return _currentDxy; }
function setCurrentDxy(v) { _currentDxy = v; }
function getFlowMap() { return _flowMap; }

// --- Loading status helper ---
function setLoadingStatus(msg, pct) {
  const statusEl = document.getElementById('loading-status');
  const barEl    = document.getElementById('loading-bar');
  if (statusEl) statusEl.textContent = msg;
  if (barEl && pct !== undefined) barEl.style.width = pct + '%';
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
