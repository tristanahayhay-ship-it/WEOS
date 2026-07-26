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
    if (typeof COUNTRY_MAP !== 'undefined' && COUNTRY_MAP[groupId]) return [groupId];
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

    // Giảm số lượng: chỉ lấy 3 nước từ mỗi group, 1 đích
    fromCodes.slice(0, 3).forEach(fromCode => {
      const fromCountry = COUNTRY_MAP[fromCode];
      if (!fromCountry || !fromCountry.lat) return;

      toCodes.slice(0, 1).forEach(toCode => {
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
          magnitude: Math.max(1, Math.min(magnitude * 0.4, 4)),
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

    // Tăng ngưỡng lọc để chỉ hiển thị các nước dòng tiền mạnh
    const MIN_FLOW_MAGNITUDE = 5;
    const magnitude = logic.getFlowMagnitude(country, dxy);
    if (magnitude < MIN_FLOW_MAGNITUDE) return;

    const isIn = direction === 'in';
    const color = isIn ? '#00ff88' : '#ff3344';

    const jitter = 0.3;
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

  if (direction === 'out') {
    if (country.gdpTier >= 3) return 'EM Bonds/Stocks';
    return 'Safe Assets';
  }

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

  const allArcs = [...countryArcs, ...groupArcs];

  // Sắp xếp theo magnitude giảm dần
  allArcs.sort((a, b) => b.magnitude - a.magnitude);

  // Giới hạn tối đa 60 arcs - đủ đẹp mà không che địa cầu
  return allArcs.slice(0, 60);
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

// Độ cao arc - thấp, cong nhẹ như airline routes
function getArcAltitude(arc) {
  // magnitude 5-10 → altitude 0.1-0.2 (thấp, không bay quá cao)
  return Math.max(0.08, Math.min((arc.magnitude || 5) * 0.018, 0.22));
}

// Độ dày arc - mỏng như sợi chỉ
function getArcStroke(arc) {
  // magnitude 5-10 → stroke 0.25-0.55 (rất mỏng)
  return Math.max(0.15, Math.min((arc.magnitude || 5) * 0.055, 0.6));
}

// Tốc độ animate (ms)
function getArcDashAnimateTime(arc) {
  const speed = arc.magnitude || 5;
  return Math.round(4000 / (speed / 5));
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
