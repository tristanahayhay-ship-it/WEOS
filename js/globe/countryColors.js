/* =============================================
   WEOS - countryColors.js
   Màu sắc quốc gia theo GDP tier, dòng tiền, vàng
   ============================================= */

// Màu base theo GDP tier
const TIER_COLORS = {
  1: { fill: '#1a4a8a', border: '#2266bb', label: 'G7 / Phát triển' },    // xanh đậm
  2: { fill: '#1a6b3d', border: '#22994f', label: 'BRICS / Mới nổi lớn' }, // xanh lá
  3: { fill: '#7a5510', border: '#aa7718', label: 'Mới nổi' },              // vàng đất
  4: { fill: '#6a1515', border: '#9a2222', label: 'Biên giới' },            // đỏ đậm
};

// Màu khi có dòng tiền vào/ra
const FLOW_OVERLAY = {
  in:      { fill: '#003322', border: '#00ff88', opacity: 0.85 },
  out:     { fill: '#220011', border: '#ff3344', opacity: 0.85 },
  neutral: { fill: null,       border: null,       opacity: 0.7  },
  center:  { fill: '#001133', border: '#ffffff',   opacity: 0.95 },
};

// Cache màu đã tính
const colorCache = {};

function getCountryBaseColor(country) {
  const tier = country.gdpTier || 4;
  return TIER_COLORS[tier] || TIER_COLORS[4];
}

function getCountryColor(country, dxy, direction) {
  const key = `${country.code}_${dxy}_${direction}`;
  if (colorCache[key]) return colorCache[key];

  const tier = getCountryBaseColor(country);
  const flow = FLOW_OVERLAY[direction] || FLOW_OVERLAY.neutral;

  let fillColor = flow.fill || tier.fill;
  let borderColor = flow.border || tier.border;

  // Thêm màu vàng nếu dự trữ vàng cao
  if (country.goldReserves > 500) {
    // Top gold holders get golden tint
    fillColor = blendColors(fillColor, '#332200', 0.3);
    borderColor = blendColors(borderColor, '#ffd700', 0.4);
  }

  colorCache[key] = { fill: fillColor, border: borderColor };
  return colorCache[key];
}

// Lấy màu hex cho polygon cap color của globe.gl
function getPolygonCapColor(feat, dxy, flowMap) {
  const code = feat.properties && (feat.properties.ISO_A2 || feat.properties.iso_a2);
  if (!code) return 'rgba(30, 30, 60, 0.7)';

  const country = (typeof COUNTRY_MAP !== 'undefined') ? COUNTRY_MAP[code] : null;
  if (!country) return 'rgba(30, 30, 60, 0.7)';

  const direction = flowMap ? (flowMap[code] || 'neutral') : 'neutral';
  const col = getCountryColor(country, dxy, direction);

  return col.fill + 'cc'; // hex + alpha
}

function getPolygonBorderColor(feat, dxy, flowMap) {
  const code = feat.properties && (feat.properties.ISO_A2 || feat.properties.iso_a2);
  if (!code) return '#222244';

  const country = (typeof COUNTRY_MAP !== 'undefined') ? COUNTRY_MAP[code] : null;
  if (!country) return '#222244';

  const direction = flowMap ? (flowMap[code] || 'neutral') : 'neutral';
  const col = getCountryColor(country, dxy, direction);

  return col.border + '99';
}

// Lấy màu cho điểm thủ đô
function getCapitalPointColor(country, dxy, direction) {
  if (country.code === 'US') return '#ffffff';
  if (country.goldReserves > 500) return '#ffd700';
  if (direction === 'in')  return '#00ff88';
  if (direction === 'out') return '#ff3344';
  return '#4488ff';
}

// Utility: blend 2 hex colors
function blendColors(hex1, hex2, ratio) {
  try {
    const r1 = parseInt(hex1.slice(1,3), 16);
    const g1 = parseInt(hex1.slice(3,5), 16);
    const b1 = parseInt(hex1.slice(5,7), 16);
    const r2 = parseInt(hex2.slice(1,3), 16);
    const g2 = parseInt(hex2.slice(3,5), 16);
    const b2 = parseInt(hex2.slice(5,7), 16);
    const r = Math.round(r1 * (1-ratio) + r2 * ratio);
    const g = Math.round(g1 * (1-ratio) + g2 * ratio);
    const b = Math.round(b1 * (1-ratio) + b2 * ratio);
    return '#' + [r,g,b].map(v => v.toString(16).padStart(2,'0')).join('');
  } catch(e) {
    return hex1;
  }
}

// Tạo flowMap từ danh sách countries và DXY
function buildFlowMap(dxy) {
  const map = {};
  if (typeof COUNTRIES_DATA === 'undefined') return map;
  COUNTRIES_DATA.forEach(c => {
    map[c.code] = window.USD_LOGIC
      ? window.USD_LOGIC.getCountryFlowDirection(c, dxy)
      : 'neutral';
  });
  return map;
}

// Invalidate cache
function clearColorCache() {
  Object.keys(colorCache).forEach(k => delete colorCache[k]);
}

window.COUNTRY_COLORS = {
  getCountryColor,
  getPolygonCapColor,
  getPolygonBorderColor,
  getCapitalPointColor,
  buildFlowMap,
  clearColorCache,
  TIER_COLORS,
};
