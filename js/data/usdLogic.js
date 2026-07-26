/* =============================================
   WEOS - usdLogic.js
   Logic dòng tiền khi USD mạnh / yếu
   ============================================= */

// --- Định nghĩa nhóm quốc gia ---
const COUNTRY_GROUPS = {
  G7: ["US","DE","JP","GB","FR","IT","CA"],
  BRICS: ["BR","RU","IN","CN","ZA"],
  BRICS_PLUS: ["BR","RU","IN","CN","ZA","EG","ET","AE","SA","IR","AR"],
  EM_ASIA: ["VN","TH","MY","ID","PH","KH","LA","MM"],
  EM_LATAM: ["BR","MX","CO","CL","PE","AR","EC","BO"],
  EM_AFRICA: ["NG","ZA","EG","GH","KE","ET","TZ","CI"],
  EM_EUROPE: ["PL","RO","CZ","HU","TR","RU","UA","BY"],
  OIL_NATIONS: ["SA","AE","KW","QA","OM","BH","NO","RU","NG","VE","IQ","AO","EC"],
  GOLD_CENTERS: ["US","DE","IT","FR","RU","CN","CH","IN","TW","JP","NL","SA"],
  BTC_NODES: ["US","DE","SG","HK","CA","AU","GB","JP"],
  SAFE_HAVEN: ["US","DE","JP","CH","SG","HK"],
  DOLLARIZED: ["EC","SV","PW","MH","FM","TL"],
  EUROZONE: ["DE","FR","IT","ES","NL","BE","AT","FI","IE","PT","GR","SK","SI","LV","LT","EE","CY","MT","LU","MC"],
  YUAN_BLOC: ["CN","MM","LA","KH","PK","KZ","BY"],
  FRONTIER: [] // auto-filled from tier 4
};

// Auto-fill frontier group
if (typeof COUNTRIES_DATA !== 'undefined') {
  COUNTRY_GROUPS.FRONTIER = COUNTRIES_DATA.filter(c => c.gdpTier === 4).map(c => c.code);
}

// --- Cấu hình DXY ---
const DXY_THRESHOLDS = {
  VERY_STRONG: 108,   // DXY > 108: cực mạnh
  STRONG: 104,        // DXY 104-108: mạnh
  NEUTRAL_HIGH: 102,  // DXY 100-104: trung tính cao
  NEUTRAL_LOW: 100,   // DXY 98-100: trung tính thấp
  WEAK: 97,           // DXY 95-98: yếu
  VERY_WEAK: 95       // DXY < 95: cực yếu
};

// --- Luồng khi USD MẠNH (DXY > 104) ---
const USD_STRONG_FLOWS = {
  description: "USD MẠNH: Vốn rút về Mỹ, áp lực tỷ giá EM, vàng giảm",
  inflows: [
    { from:"GLOBAL", to:"US", asset:"Trái phiếu Mỹ", magnitude:9, speed:"fast", color:"#00ff88", description:"Nhà đầu tư toàn cầu mua trái phiếu US Treasury, lợi suất cao" },
    { from:"GLOBAL", to:"US", asset:"USD Cash", magnitude:8, speed:"medium", color:"#00ff88", description:"Tiền mặt USD được giữ vì giá trị tăng" },
    { from:"EM_ASIA",  to:"US", asset:"Cổ phiếu Mỹ", magnitude:7, speed:"fast", color:"#00ff88", description:"Vốn rút khỏi châu Á về S&P 500" },
    { from:"EM_LATAM", to:"US", asset:"Cổ phiếu Mỹ", magnitude:7, speed:"fast", color:"#00ff88", description:"Vốn rút khỏi Latin Mỹ về thị trường Mỹ" },
  ],
  outflows: [
    { from:"EM_ASIA",    to:"US", asset:"Trái phiếu EM", magnitude:8, speed:"fast",   color:"#ff3344", description:"EM châu Á: vốn tháo chạy, đồng tiền mất giá" },
    { from:"EM_AFRICA",  to:"US", asset:"Cổ phiếu EM",  magnitude:6, speed:"medium", color:"#ff3344", description:"Châu Phi: áp lực nợ USD, tháo vốn" },
    { from:"EM_LATAM",   to:"US", asset:"Trái phiếu EM", magnitude:7, speed:"fast",   color:"#ff3344", description:"Latin Mỹ: currency crisis, rút vốn" },
    { from:"GOLD_CENTERS",to:"US",asset:"Vàng",          magnitude:6, speed:"slow",   color:"#ff3344", description:"USD mạnh → vàng giảm, bán vàng lấy USD" },
    { from:"BTC_NODES",  to:"US", asset:"Crypto",        magnitude:7, speed:"fast",   color:"#ff3344", description:"Bitcoin bán để lấy USD yield" },
    { from:"OIL_NATIONS",to:"US", asset:"Dầu thô",       magnitude:5, speed:"slow",   color:"#ff3344", description:"Giá dầu USD chịu áp lực khi dollar mạnh" },
  ]
};

// --- Luồng khi USD YẾU (DXY < 100) ---
const USD_WEAK_FLOWS = {
  description: "USD YẾU: Vốn chạy vào vàng, EM, crypto, hàng hóa",
  inflows: [
    { from:"US", to:"GOLD_CENTERS", asset:"Vàng",       magnitude:9, speed:"fast",   color:"#00ff88", description:"USD yếu → vàng là trú ẩn, giá vàng tăng mạnh" },
    { from:"US", to:"BTC_NODES",    asset:"Bitcoin",    magnitude:8, speed:"fast",   color:"#00ff88", description:"BTC là hàng rào lạm phát khi USD mất giá" },
    { from:"US", to:"EM_ASIA",      asset:"EM Stocks",  magnitude:7, speed:"medium", color:"#00ff88", description:"Vốn đổ vào thị trường mới nổi Asia" },
    { from:"US", to:"OIL_NATIONS",  asset:"Dầu thô",    magnitude:8, speed:"medium", color:"#00ff88", description:"USD yếu → giá dầu tăng, vốn vào quốc gia dầu mỏ" },
    { from:"US", to:"EM_LATAM",     asset:"Hàng hóa",   magnitude:7, speed:"medium", color:"#00ff88", description:"Copper, soybeans tăng → LatAm hưởng lợi" },
    { from:"US", to:"CN",           asset:"Yuan Assets", magnitude:8, speed:"fast",  color:"#00ff88", description:"USD yếu → CNY mạnh, vốn vào TQ" },
  ],
  outflows: [
    { from:"GLOBAL", to:"SAFE_HAVEN", asset:"Trái phiếu USD", magnitude:7, speed:"slow", color:"#ff3344", description:"Giảm nắm giữ trái phiếu USD, đa dạng hóa dự trữ" },
    { from:"US",     to:"EUROZONE",   asset:"EUR Assets",     magnitude:6, speed:"slow", color:"#ff3344", description:"USD yếu → EUR mạnh, vốn sang Eurozone" },
  ]
};

// --- Luồng trung tính (DXY 100-104) ---
const USD_NEUTRAL_FLOWS = {
  description: "USD TRUNG TÍNH: Thị trường cân bằng, dòng tiền phân tán",
  inflows: [
    { from:"GLOBAL", to:"US",          asset:"Đa dạng hóa",  magnitude:5, speed:"slow",   color:"#00ff88", description:"Cân bằng rủi ro toàn cầu" },
    { from:"US",     to:"EM_ASIA",     asset:"FDI",           magnitude:5, speed:"medium", color:"#00ff88", description:"Đầu tư trực tiếp ổn định vào EM" },
    { from:"US",     to:"GOLD_CENTERS",asset:"Vàng nhỏ lẻ",  magnitude:4, speed:"slow",   color:"#00ff88", description:"Mua vàng phòng thủ ổn định" },
  ],
  outflows: []
};

// --- Hàm xác định chế độ USD ---
function getUsdMode(dxy) {
  if (dxy >= DXY_THRESHOLDS.VERY_STRONG) return 'very_strong';
  if (dxy >= DXY_THRESHOLDS.STRONG) return 'strong';
  if (dxy >= DXY_THRESHOLDS.NEUTRAL_HIGH) return 'neutral_high';
  if (dxy >= DXY_THRESHOLDS.NEUTRAL_LOW) return 'neutral_low';
  if (dxy >= DXY_THRESHOLDS.WEAK) return 'weak';
  return 'very_weak';
}

function getUsdModeLabel(dxy) {
  const mode = getUsdMode(dxy);
  const labels = {
    very_strong: '🔴 CỰC MẠNH',
    strong:      '🟠 MẠNH',
    neutral_high:'🟡 TRUNG TÍNH CAO',
    neutral_low: '🟡 TRUNG TÍNH',
    weak:        '🟢 YẾU',
    very_weak:   '🟢 CỰC YẾU'
  };
  return labels[mode] || '⚪ N/A';
}

// --- Hàm tính hướng dòng tiền cho từng quốc gia ---
function getCountryFlowDirection(country, dxy) {
  const mode = getUsdMode(dxy);

  // Quốc gia dollarized
  if (COUNTRY_GROUPS.DOLLARIZED.includes(country.code)) return 'neutral';

  // Mỹ luôn là trung tâm
  if (country.code === 'US') return 'center';

  const isEM = country.gdpTier >= 3;
  const isOilNation = COUNTRY_GROUPS.OIL_NATIONS.includes(country.code);
  const isGoldCenter = COUNTRY_GROUPS.GOLD_CENTERS.includes(country.code);
  const correlation = country.usdCorrelation || 0;

  if (mode === 'very_strong' || mode === 'strong') {
    // USD mạnh: EM bị tháo, G7 khác tháo nhẹ
    if (isEM) return 'out';  // vốn tháo khỏi EM
    if (isOilNation && !COUNTRY_GROUPS.SAFE_HAVEN.includes(country.code)) return 'out';
    if (COUNTRY_GROUPS.SAFE_HAVEN.includes(country.code)) return 'in';
    return correlation < -0.5 ? 'out' : 'neutral';
  }

  if (mode === 'weak' || mode === 'very_weak') {
    // USD yếu: EM hút vốn, vàng tăng, crypto tăng
    if (isEM && !COUNTRY_GROUPS.FRONTIER.includes(country.code)) return 'in';
    if (isGoldCenter) return 'in';
    if (isOilNation) return 'in';
    if (COUNTRY_GROUPS.BTC_NODES.includes(country.code)) return 'in';
    if (COUNTRY_GROUPS.SAFE_HAVEN.includes(country.code) && country.code !== 'US') return 'out'; // từ USD
    return correlation < -0.6 ? 'in' : 'neutral';
  }

  // Trung tính
  if (correlation > 0.5) return 'in';
  if (correlation < -0.7) return 'out';
  return Math.random() > 0.6 ? 'in' : 'neutral';
}

// --- Hàm tính magnitude dòng tiền ---
function getFlowMagnitude(country, dxy) {
  const mode = getUsdMode(dxy);
  const base = {1: 4, 2: 5, 3: 6, 4: 4}[country.gdpTier] || 4;
  const gdpFactor = Math.log10(Math.max(country.gdpUSD || 1, 1)) / 5;

  let modifier = 1.0;
  if (mode === 'very_strong' || mode === 'very_weak') modifier = 1.5;
  if (mode === 'strong' || mode === 'weak') modifier = 1.2;

  return Math.min(Math.round((base + gdpFactor * 10) * modifier), 10);
}

// --- Cấu hình màu nước theo tình trạng ---
const FLOW_COLORS = {
  in:      { arc: '#00ff88', glow: 'rgba(0,255,136,0.6)',  label: 'Tiền VÀO' },
  out:     { arc: '#ff3344', glow: 'rgba(255,51,68,0.6)',  label: 'Tiền RA' },
  neutral: { arc: '#4488ff', glow: 'rgba(68,136,255,0.4)', label: 'Trung tính' },
  center:  { arc: '#ffffff', glow: 'rgba(255,255,255,0.8)', label: 'Trung tâm USD' },
};

// --- Giải thích tại sao quốc gia xanh/đỏ ---
function getFlowReason(country, dxy) {
  const mode = getUsdMode(dxy);
  const dir = getCountryFlowDirection(country, dxy);

  const reasons = {
    very_strong: {
      out: `USD cực mạnh (DXY ${dxy.toFixed(1)}): ${country.currency} mất giá, nhà đầu tư nước ngoài rút vốn về Mỹ. EM bonds bán tháo.`,
      in:  `Tài sản trú ẩn USD: trái phiếu Mỹ hấp dẫn hơn.`,
    },
    strong: {
      out: `USD mạnh: đồng ${country.currency} suy yếu, áp lực trả nợ ngoại tệ. Vốn đổ về trái phiếu Mỹ yield cao.`,
      in:  `Đồng tiền bền vững, hưởng lợi từ USD mạnh.`,
    },
    neutral_high: {
      out: `USD trung tính: Thị trường thận trọng, EM chịu áp lực nhẹ.`,
      in:  `Cân bằng, vốn ổn định.`,
    },
    neutral_low: {
      out: `USD đang giảm nhẹ: Chờ đợi tín hiệu rõ hơn.`,
      in:  `Cơ hội đầu tư EM xuất hiện.`,
    },
    weak: {
      in:  `USD yếu: ${country.currency} tăng giá tương đối, hàng xuất khẩu rẻ hơn, vốn FDI chảy vào.`,
      out: `USD yếu nhưng nước này phụ thuộc vào USD: áp lực lạm phát nhập khẩu.`,
    },
    very_weak: {
      in:  `USD cực yếu: Dòng vốn ồ ạt vào EM, hàng hóa, tài sản thực. ${country.name} hưởng lợi.`,
      out: `USD cực yếu: Không chắc chắn, tháo vốn phòng thủ.`,
    },
  };

  return (reasons[mode] && reasons[mode][dir]) || `Dòng tiền ${dir === 'in' ? 'vào' : 'ra'} theo xu thế DXY ${dxy.toFixed(1)}`;
}

// --- Tài sản trú ẩn theo chế độ USD ---
function getSafeHavenAssets(dxy) {
  const mode = getUsdMode(dxy);
  const assets = {
    very_strong: ["US Treasury","USD","S&P 500","Money Market"],
    strong:      ["US Treasury","USD","Nasdaq","REITs Mỹ"],
    neutral_high:["US Treasury","Vàng","S&P 500","Bitcoin"],
    neutral_low: ["Vàng","Bitcoin","EM ETF","Hàng hóa"],
    weak:        ["Vàng","Bitcoin","Ethereum","Cổ phiếu EM","Dầu thô"],
    very_weak:   ["Vàng","Bitcoin","BTC ETF","MSCI EM","Dầu BRENT","Đồng"],
  };
  return assets[mode] || ["Đa dạng hóa"];
}

// Xuất ra global
window.USD_LOGIC = {
  getUsdMode,
  getUsdModeLabel,
  getCountryFlowDirection,
  getFlowMagnitude,
  getFlowReason,
  getSafeHavenAssets,
  FLOW_COLORS,
  DXY_THRESHOLDS,
  COUNTRY_GROUPS,
  USD_STRONG_FLOWS,
  USD_WEAK_FLOWS,
  USD_NEUTRAL_FLOWS
};
