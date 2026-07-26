/* =============================================
   WEOS - flowArcs.js
   Tính toán và tạo animated arc lines (mạch máu dòng tiền)
   ============================================= */

let _currentArcs = [];
let _arcUpdateTimer = null;

// --- Tạo arcs từ nhóm flow ---
function buildGroupArcs(flowGroup, dxy, existingCountries) {
  const arcs = [];
  const logic = window.USD_LOGIC;
  if (!logic || !existingCountries) return arcs;

  // Map group name -> list of country codes
  function resolveGroup(groupId) {
    const groups = logic.COUNTRY_GROUPS;
    if (groups[groupId]) return groups[groupId];
    // Single country code
    if (typeof COUNTRY_MAP !== 'undefined' && COUNTRY_MAP[groupId]) return [groupId];
    // Comma separated
    if (groupId.includes(',')) return groupId.split(',').map(s => s.trim());
    return [];
  }

  const flowDefs = dxy >= 104
    ? [...logic.USD_STRONG_FLOWS.inflows, ...logic.USD_STRONG_FLOWS.outflows]
    : dxy < 100
      ? [...logic.USD_WEAK_FLOWS.inflows, ...logic.USD_WEAK_FLOWS.outflows]
      : [...logic.USD_NEUTRAL_FLOWS.inflows, ...logic.USD_NEUTRAL_FLOWS.outflows];

  flowDefs.forEach(flowDef => {
    const fromCodes = resolveGroup(flowDef.from);
    const toCodes   = resolveGroup(flowDef.to);

    fromCodes.slice(0, 8).forEach(fromCode => {
      const fromCountry = COUNTRY_MAP[fromCode];
      if (!fromCountry || !fromCountry.lat) return;

      toCodes.slice(0, 3).forEach(toCode => {
        const toCountry = COUNTRY_MAP[toCode];
        if (!toCountry || !toCountry.lat) return;
        if (fromCode === toCode) return;

        const magnitude = flowDef.magnitude + (Math.random() - 0.5);
        const isInflow = flowDef.color === '#00ff88';

        arcs.push({
          startLat: fromCountry.lat + (Math.random() - 0.5) * 2,
          startLng: fromCountry.lng + (Math.random() - 0.5) * 2,
          endLat:   toCountry.lat,
          endLng:   toCountry.lng,
          flowType: isInflow ? 'in' : 'out',
          magnitude: Math.max(1, Math.min(magnitude, 10)),
          asset:     flowDef.asset,
          fromCode,
          toCode,
          label: `${fromCountry.name} → ${toCountry.name}: ${flowDef.asset}`,
          color: flowDef.color,
        });
      });
    });
  });

  return arcs;
}

// --- Arc chính: từng quốc gia → Washington DC ---
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

    const magnitude = logic.getFlowMagnitude(country, dxy);
    if (magnitude < 3) return; // Bỏ qua flows nhỏ để tránh quá tải

    const isIn = direction === 'in';
    const color = isIn ? '#00ff88' : '#ff3344';

    // Thêm jitter nhỏ để arcs không chồng nhau hoàn toàn
    const jitter = 0.5;
    arcs.push({
      startLat: isIn ? country.lat + (Math.random()-0.5)*jitter : US_LAT,
      startLng: isIn ? country.lng + (Math.random()-0.5)*jitter : US_LNG,
      endLat:   isIn ? US_LAT : country.lat + (Math.random()-0.5)*jitter,
      endLng:   isIn ? US_LNG : country.lng + (Math.random()-0.5)*jitter,
      flowType:  direction,
      magnitude: magnitude,
      asset:     logic.getSafeHavenAssets(dxy)[0],
      fromCode:  isIn ? country.code : 'US',
      toCode:    isIn ? 'US' : country.code,
      country:   country.code,
      color:     color,
      label:     `${country.name} ${isIn ? '→ Hoa Kỳ' : '← Hoa Kỳ'}: ${getFlowAssetLabel(country, dxy, direction)}`,
    });
  });

  return arcs;
}

// --- Label asset cho arc ---
function getFlowAssetLabel(country, dxy, direction) {
  const logic = window.USD_LOGIC;
  if (!logic) return 'Vốn';

  const mode = logic.getUsdMode(dxy);
  if (direction === 'out') {
    // EM tháo vốn
    if (country.gdpTier >= 3) return 'EM Bonds/Stocks';
    return 'Safe Assets';
  }

  // Inflow
  const assets = logic.getSafeHavenAssets(dxy);
  if (window.COUNTRY_GROUPS && window.COUNTRY_GROUPS.OIL_NATIONS &&
      window.COUNTRY_GROUPS.OIL_NATIONS.includes(country.code)) return 'Dầu thô';
  if (window.COUNTRY_GROUPS && window.COUNTRY_GROUPS.GOLD_CENTERS &&
      window.COUNTRY_GROUPS.GOLD_CENTERS.includes(country.code)) return 'Vàng';
  if (window.COUNTRY_GROUPS && window.COUNTRY_GROUPS.BTC_NODES &&
      window.COUNTRY_GROUPS.BTC_NODES.includes(country.code)) return 'Bitcoin';
  return assets[0] || 'EM Stocks';
}

// Expose COUNTRY_GROUPS globally
if (typeof window.COUNTRY_GROUPS === 'undefined' && window.USD_LOGIC) {
  window.COUNTRY_GROUPS = window.USD_LOGIC.COUNTRY_GROUPS;
}

// --- Tính toán tất cả arcs ---
function calculateFlowArcs(dxy) {
  const countryArcs = buildCountryArcs(dxy);
  const groupArcs   = buildGroupArcs({}, dxy, typeof COUNTRY_MAP !== 'undefined' ? COUNTRY_MAP : {});

  // Merge & limit total
  const allArcs = [...countryArcs, ...groupArcs];

  // Sắp xếp theo magnitude giảm dần
  allArcs.sort((a, b) => b.magnitude - a.magnitude);

  // Giới hạn tối đa 200 arcs để performance
  return allArcs.slice(0, 200);
}

// --- Get current arcs ---
function getCurrentArcs() {
  return _currentArcs;
}

// --- Update arcs ---
function updateFlowArcs(dxy, globeInstance) {
  _currentArcs = calculateFlowArcs(dxy);

  // Update counters
  const inCount  = _currentArcs.filter(a => a.flowType === 'in').length;
  const outCount = _currentArcs.filter(a => a.flowType === 'out').length;
  const inEl  = document.getElementById('arc-in-count');
  const outEl = document.getElementById('arc-out-count');
  if (inEl)  inEl.textContent  = `${inCount} ↑ VÀO`;
  if (outEl) outEl.textContent = `${outCount} ↓ RA`;

  const inflowCountEl  = document.getElementById('inflow-count');
  const outflowCountEl = document.getElementById('outflow-count');
  if (inflowCountEl)  inflowCountEl.textContent  = inCount;
  if (outflowCountEl) outflowCountEl.textContent = outCount;

  if (globeInstance) {
    globeInstance.arcsData(_currentArcs);
  }

  return _currentArcs;
}

// --- Auto-update arcs ---
function startArcAutoUpdate(getGlobeInstance, getDxy) {
  if (_arcUpdateTimer) clearInterval(_arcUpdateTimer);
  _arcUpdateTimer = setInterval(() => {
    const globe = getGlobeInstance ? getGlobeInstance() : null;
    const dxy   = getDxy ? getDxy() : 101;
    updateFlowArcs(dxy, globe);
  }, 5000);
}

function stopArcAutoUpdate() {
  if (_arcUpdateTimer) {
    clearInterval(_arcUpdateTimer);
    _arcUpdateTimer = null;
  }
}

// Màu arc theo flowType
function getArcColor(arc) {
  return arc.color || (arc.flowType === 'in' ? '#00ff88' : '#ff3344');
}

// Độ cao arc theo magnitude
function getArcAltitude(arc) {
  return Math.max(0.05, (arc.magnitude || 5) * 0.04);
}

// Độ dày arc theo magnitude
function getArcStroke(arc) {
  return Math.max(0.3, (arc.magnitude || 5) * 0.4);
}

// Tốc độ animate (ms)
function getArcDashAnimateTime(arc) {
  const speed = arc.magnitude || 5;
  // Magnitude cao = chảy nhanh
  return Math.round(6000 / (speed / 5));
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
