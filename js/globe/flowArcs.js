/* =============================================
   WEOS - flowArcs.js
   Dòng tiền = mạch máu địa cầu
   ============================================= */

let _currentArcs = [];
let _arcUpdateTimer = null;

// Ngưỡng thấp để hiện đủ 195 nước
const MIN_FLOW_MAGNITUDE = 1;
const MAX_VISIBLE_ARCS = 195;
const ARC_UPDATE_INTERVAL_MS = 10000;

// --- Tính arc cho từng quốc gia → Washington DC ---
function buildCountryArcs(dxy) {
  const arcs = [];
  const logic = window.USD_LOGIC;
  if (!logic || typeof COUNTRIES_DATA === 'undefined') return arcs;

  const US_LAT = 38.9072, US_LNG = -77.0369;

  COUNTRIES_DATA.forEach(country => {
    if (country.code === 'US') return;
    if (!country.lat || !country.lng) return;

    const direction = logic.getCountryFlowDirection(country, dxy);
    if (direction === 'neutral') return;

    const magnitude = Math.max(MIN_FLOW_MAGNITUDE, logic.getFlowMagnitude(country, dxy));
    const isIn = direction === 'in';

    // Alpha theo GDP tier: nước lớn đậm hơn, nước nhỏ mờ hơn
    const alpha = country.gdpTier === 1 ? 0.75
                : country.gdpTier === 2 ? 0.6
                : country.gdpTier === 3 ? 0.45
                : 0.3;

    const color = isIn
      ? `rgba(0,255,136,${alpha})`
      : `rgba(255,51,68,${alpha})`;

    const jitter = 0.4;
    arcs.push({
      startLat: isIn ? country.lat + (Math.random()-0.5)*jitter : US_LAT,
      startLng: isIn ? country.lng + (Math.random()-0.5)*jitter : US_LNG,
      endLat:   isIn ? US_LAT : country.lat + (Math.random()-0.5)*jitter,
      endLng:   isIn ? US_LNG : country.lng + (Math.random()-0.5)*jitter,
      flowType:  direction,
      magnitude: magnitude,
      gdpTier:   country.gdpTier,
      color:     color,
      country:   country.code,
      label: `${country.flag || ''} ${country.name} ${isIn ? '→' : '←'} Hoa Kỳ`,
    });
  });

  return arcs;
}

// --- Tính toán tất cả arcs ---
function calculateFlowArcs(dxy) {
  const arcs = buildCountryArcs(dxy);
  arcs.sort((a, b) => b.magnitude - a.magnitude);
  return arcs.slice(0, MAX_VISIBLE_ARCS);
}

// --- Get current arcs ---
function getCurrentArcs() {
  return _currentArcs;
}

// --- Update arcs ---
function updateFlowArcs(dxy, globeInstance) {
  _currentArcs = calculateFlowArcs(dxy);

  const inCount  = _currentArcs.filter(a => a.flowType === 'in').length;
  const outCount = _currentArcs.filter(a => a.flowType === 'out').length;

  ['arc-in-count','inflow-count'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.textContent = id === 'arc-in-count' ? `${inCount} ↑ VÀO` : inCount;
  });
  ['arc-out-count','outflow-count'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.textContent = id === 'arc-out-count' ? `${outCount} ↓ RA` : outCount;
  });

  if (globeInstance) globeInstance.arcsData(_currentArcs);
  return _currentArcs;
}

// --- Auto-update ---
function startArcAutoUpdate(getGlobeInstance, getDxy) {
  if (_arcUpdateTimer) clearInterval(_arcUpdateTimer);
  _arcUpdateTimer = setInterval(() => {
    const globe = getGlobeInstance ? getGlobeInstance() : null;
    const dxy   = getDxy ? getDxy() : 101;
    updateFlowArcs(dxy, globe);
  }, ARC_UPDATE_INTERVAL_MS);
}

function stopArcAutoUpdate() {
  if (_arcUpdateTimer) { clearInterval(_arcUpdateTimer); _arcUpdateTimer = null; }
}

// --- Helpers cho globeInit ---
function getArcColor(arc) {
  return arc.color || (arc.flowType === 'in' ? 'rgba(0,255,136,0.5)' : 'rgba(255,51,68,0.5)');
}

// Cong cao giống airline routes — đủ để nhìn thấy đường cong rõ
function getArcAltitude(arc) {
  const tier = arc.gdpTier || 3;
  // G7 bay cao hơn (dòng tiền lớn), frontier thấp hơn
  const base = tier === 1 ? 0.4 : tier === 2 ? 0.3 : tier === 3 ? 0.2 : 0.15;
  return base;
}

// Rất mỏng — stroke theo tier
function getArcStroke(arc) {
  const tier = arc.gdpTier || 3;
  return tier === 1 ? 0.5 : tier === 2 ? 0.35 : tier === 3 ? 0.25 : 0.15;
}

// Tốc độ: nước lớn chảy nhanh
function getArcDashAnimateTime(arc) {
  const tier = arc.gdpTier || 3;
  return tier === 1 ? 1500 : tier === 2 ? 2000 : tier === 3 ? 2800 : 3500;
}

window.FLOW_ARCS = {
  calculateFlowArcs,
  updateFlowArcs,
  getCurrentArcs,
  startArcAutoUpdate,
  stopArcAutoUpdate,
  getArcColor,
  getArcAltitude,
  getArcStroke,
  getArcDashAnimateTime,
};
