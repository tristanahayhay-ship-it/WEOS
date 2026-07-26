/* =============================================
   WEOS - mockData.js
   Dữ liệu fallback thực tế (khi API bị rate limit)
   Cập nhật: 2025
   ============================================= */

const MOCK_DATA = {
  // --- Tỷ giá ngoại tệ (USD = base) ---
  forex: {
    timestamp: Date.now(),
    base: "USD",
    rates: {
      // Châu Á
      VND: 25430, JPY: 149.5, CNY: 7.24, KRW: 1325, TWD: 31.8,
      HKD: 7.82, SGD: 1.34, THB: 35.2, MYR: 4.72, IDR: 15680,
      PHP: 56.8, INR: 83.4, PKR: 278.5, BDT: 110.2, LKR: 322.5,
      MMK: 2099, KHR: 4090, LAK: 21250, NPR: 133.5, MVR: 15.41,
      BDT2: 110,
      // Trung Đông
      SAR: 3.75, AED: 3.67, KWD: 0.308, QAR: 3.64, OMR: 0.385,
      BHD: 0.376, JOD: 0.709, ILS: 3.72, TRY: 32.5,
      // Châu Âu
      EUR: 0.918, GBP: 0.784, CHF: 0.882, NOK: 10.68, SEK: 10.45,
      DKK: 6.84, PLN: 3.96, CZK: 22.8, HUF: 356, RON: 4.56,
      RUB: 91.5, UAH: 38.2, HRK: 6.92, BGN: 1.795, RSD: 107.5,
      // Châu Mỹ
      CAD: 1.357, MXN: 17.2, BRL: 4.98, ARS: 820, CLP: 935,
      COP: 3920, PEN: 3.73, BOB: 6.91, PYG: 7390,
      // Châu Phi
      ZAR: 18.6, NGN: 1470, EGP: 30.9, GHS: 13.8, KES: 129.5,
      // Châu Đại Dương
      AUD: 1.523, NZD: 1.628, FJD: 2.24, PGK: 3.71,
    }
  },

  // --- Giá Crypto ---
  crypto: {
    timestamp: Date.now(),
    bitcoin: {
      usd: 98500, usd_24h_change: 2.4, usd_market_cap: 1940000000000,
      label: "Bitcoin", symbol: "BTC"
    },
    ethereum: {
      usd: 3420, usd_24h_change: 1.8, usd_market_cap: 411000000000,
      label: "Ethereum", symbol: "ETH"
    },
    solana: {
      usd: 195, usd_24h_change: 3.1, usd_market_cap: 91000000000,
      label: "Solana", symbol: "SOL"
    },
    ripple: {
      usd: 2.35, usd_24h_change: 1.5, usd_market_cap: 134000000000,
      label: "XRP", symbol: "XRP"
    }
  },

  // --- Hàng hóa ---
  commodities: {
    timestamp: Date.now(),
    gold:   { price: 2680, change: 0.8, unit: "USD/oz",   label: "Vàng" },
    silver: { price: 31.2, change: 1.2, unit: "USD/oz",   label: "Bạc" },
    oil_wti:{ price: 71.5, change: -0.5,unit: "USD/bbl",  label: "Dầu WTI" },
    oil_brent:{ price: 75.8,change: -0.3,unit: "USD/bbl", label: "Dầu Brent" },
    copper: { price: 9420, change: 0.6, unit: "USD/tấn",  label: "Đồng" },
    nat_gas:{ price: 2.85, change: -1.2,unit: "USD/MMBtu",label: "Khí đốt" },
  },

  // --- Chỉ số thị trường ---
  markets: {
    timestamp: Date.now(),
    sp500:  { value: 5870, change: 0.6,  label: "S&P 500" },
    nasdaq: { value: 19450, change: 0.9, label: "Nasdaq" },
    dow:    { value: 43400, change: 0.4, label: "Dow Jones" },
    dxy:    { value: 101.2, change: -0.3, label: "DXY Index" },
    vix:    { value: 14.8, change: -5.2,  label: "VIX (Sợ hãi)" },
    tnx:    { value: 4.45, change: 0.02,  label: "10Y Treasury" },
  },

  // --- Chỉ số kinh tế theo quốc gia ---
  countryEconomics: {
    US: { gdpGrowth: 2.8, unemployment: 3.9, inflation: 3.2, tradeBalance: -67.4, interestRate: 5.25, debtGDP: 123, stockIndex: 5870, stockChange: 0.6 },
    CN: { gdpGrowth: 5.2, unemployment: 5.0, inflation: 0.3, tradeBalance: 75.3,  interestRate: 3.45, debtGDP: 83, stockIndex: 3350, stockChange: -0.4 },
    JP: { gdpGrowth: 1.9, unemployment: 2.5, inflation: 2.8, tradeBalance: -8.2,  interestRate: 0.10, debtGDP: 255, stockIndex: 38900, stockChange: 0.8 },
    DE: { gdpGrowth: 0.2, unemployment: 5.7, inflation: 2.3, tradeBalance: 22.4,  interestRate: 4.50, debtGDP: 66, stockIndex: 19450, stockChange: 0.3 },
    GB: { gdpGrowth: 1.1, unemployment: 4.2, inflation: 4.0, tradeBalance: -15.6, interestRate: 5.25, debtGDP: 98, stockIndex: 8080, stockChange: 0.2 },
    FR: { gdpGrowth: 0.9, unemployment: 7.1, inflation: 2.6, tradeBalance: -7.8,  interestRate: 4.50, debtGDP: 111, stockIndex: 7685, stockChange: 0.5 },
    IN: { gdpGrowth: 8.2, unemployment: 7.8, inflation: 5.4, tradeBalance: -21.3, interestRate: 6.50, debtGDP: 82, stockIndex: 72800, stockChange: 0.7 },
    BR: { gdpGrowth: 2.9, unemployment: 7.8, inflation: 4.6, tradeBalance: 8.5,   interestRate: 10.50, debtGDP: 88, stockIndex: 128500, stockChange: -1.2 },
    RU: { gdpGrowth: 3.6, unemployment: 2.9, inflation: 7.4, tradeBalance: 15.2,  interestRate: 16.0, debtGDP: 21, stockIndex: 3200, stockChange: -0.5 },
    VN: { gdpGrowth: 6.4, unemployment: 2.1, inflation: 3.8, tradeBalance: 3.2,   interestRate: 4.50, debtGDP: 37, stockIndex: 1280, stockChange: 0.9 },
    KR: { gdpGrowth: 2.5, unemployment: 2.7, inflation: 3.0, tradeBalance: 5.8,   interestRate: 3.50, debtGDP: 54, stockIndex: 2590, stockChange: 0.4 },
    SA: { gdpGrowth: 3.1, unemployment: 6.0, inflation: 1.7, tradeBalance: 28.4,  interestRate: 6.0, debtGDP: 22, stockIndex: 11650, stockChange: -0.3 },
    TR: { gdpGrowth: 4.5, unemployment: 8.8, inflation: 69.8, tradeBalance: -6.5, interestRate: 40.0, debtGDP: 32, stockIndex: 8900, stockChange: 2.1 },
    MX: { gdpGrowth: 3.2, unemployment: 2.8, inflation: 4.7, tradeBalance: -2.8,  interestRate: 11.0, debtGDP: 49, stockIndex: 53400, stockChange: 0.4 },
    ID: { gdpGrowth: 5.0, unemployment: 5.3, inflation: 2.8, tradeBalance: 2.9,   interestRate: 6.0, debtGDP: 39, stockIndex: 7280, stockChange: 0.3 },
    TH: { gdpGrowth: 2.7, unemployment: 1.0, inflation: 1.2, tradeBalance: 1.8,   interestRate: 2.50, debtGDP: 62, stockIndex: 1420, stockChange: -0.6 },
    MY: { gdpGrowth: 4.3, unemployment: 3.5, inflation: 1.8, tradeBalance: 3.7,   interestRate: 3.0, debtGDP: 65, stockIndex: 1685, stockChange: 0.5 },
    PH: { gdpGrowth: 5.9, unemployment: 4.0, inflation: 4.9, tradeBalance: -3.2,  interestRate: 6.5, debtGDP: 57, stockIndex: 6780, stockChange: 0.3 },
    AU: { gdpGrowth: 2.0, unemployment: 3.9, inflation: 3.6, tradeBalance: 5.2,   interestRate: 4.35, debtGDP: 49, stockIndex: 8050, stockChange: 0.7 },
    CA: { gdpGrowth: 1.5, unemployment: 5.8, inflation: 3.1, tradeBalance: -1.2,  interestRate: 5.0, debtGDP: 102, stockIndex: 21800, stockChange: 0.3 },
    ZA: { gdpGrowth: 1.1, unemployment: 32.1, inflation: 5.3, tradeBalance: 0.8,  interestRate: 8.25, debtGDP: 73, stockIndex: 73600, stockChange: -0.5 },
    NG: { gdpGrowth: 2.9, unemployment: 33.3, inflation: 28.2, tradeBalance: 1.5, interestRate: 18.75, debtGDP: 38, stockIndex: 98700, stockChange: 1.8 },
    EG: { gdpGrowth: 3.8, unemployment: 7.3, inflation: 34.0, tradeBalance: -3.5, interestRate: 21.25, debtGDP: 92, stockIndex: 29800, stockChange: 0.9 },
    AR: { gdpGrowth: -2.5, unemployment: 7.7, inflation: 120.0, tradeBalance: 1.6, interestRate: 40.0, debtGDP: 91, stockIndex: 1250000, stockChange: 5.3 },
    PK: { gdpGrowth: 2.4, unemployment: 6.3, inflation: 20.7, tradeBalance: -2.9, interestRate: 13.0, debtGDP: 74, stockIndex: 67000, stockChange: 0.6 },
    IR: { gdpGrowth: 3.5, unemployment: 9.3, inflation: 45.0, tradeBalance: 5.8,  interestRate: 23.0, debtGDP: 42, stockIndex: 2100000, stockChange: 0.5 },
    SG: { gdpGrowth: 2.1, unemployment: 2.1, inflation: 3.2, tradeBalance: 5.7,   interestRate: 3.5, debtGDP: 132, stockIndex: 3460, stockChange: 0.4 },
  },

  // --- Luồng tiền ước tính theo ngành ---
  sectorFlows: {
    tech:      { in: 45.2, out: 12.3, unit: "tỷ USD/tháng", trend: "up" },
    finance:   { in: 38.7, out: 22.1, unit: "tỷ USD/tháng", trend: "up" },
    commodities:{ in: 28.4, out: 8.9, unit: "tỷ USD/tháng", trend: "up" },
    realestate:{ in: 15.6, out: 18.2, unit: "tỷ USD/tháng", trend: "down" },
    bonds_gov: { in: 87.3, out: 32.5, unit: "tỷ USD/tháng", trend: "up" },
    bonds_corp:{ in: 42.1, out: 28.9, unit: "tỷ USD/tháng", trend: "stable" },
    crypto:    { in: 12.8, out: 9.4,  unit: "tỷ USD/tháng", trend: "up" },
    gold:      { in: 22.5, out: 14.1, unit: "tỷ USD/tháng", trend: "up" },
  },

  // --- DXY lịch sử (30 ngày gần nhất, mock) ---
  dxyHistory: [
    99.8, 100.2, 101.5, 102.1, 101.8, 100.5, 99.7, 100.1, 101.0, 101.4,
    102.3, 103.1, 102.8, 101.9, 101.2, 100.8, 101.5, 102.1, 101.7, 100.9,
    100.3, 99.8, 100.5, 101.2, 101.8, 102.4, 101.9, 101.2, 100.8, 101.2
  ]
};

// Helper để lấy dữ liệu quốc gia, fallback nếu không có
function getCountryEconomics(code) {
  const base = MOCK_DATA.countryEconomics[code];
  if (base) return base;

  // Tạo dữ liệu ngẫu nhiên có tính logic
  const country = COUNTRY_MAP && COUNTRY_MAP[code];
  const tier = country ? country.gdpTier : 4;

  return {
    gdpGrowth:    (Math.random() * 4 + (5 - tier)).toFixed(1) * 1,
    unemployment: (Math.random() * 10 + tier * 2).toFixed(1) * 1,
    inflation:    (Math.random() * 8 + tier * 1.5).toFixed(1) * 1,
    tradeBalance: ((Math.random() - 0.5) * 10).toFixed(1) * 1,
    interestRate: (Math.random() * 8 + tier * 1.5).toFixed(2) * 1,
    debtGDP:      Math.round(Math.random() * 60 + 30),
    stockIndex:   Math.round(Math.random() * 5000 + 500),
    stockChange:  ((Math.random() - 0.5) * 3).toFixed(2) * 1,
  };
}

// Tính lượng tiền vào/ra ước tính (tỷ USD/tháng)
function estimateFlows(country, dxy) {
  const econ = getCountryEconomics(country.code);
  const gdp = country.gdpUSD || 100;
  const baseFlow = gdp * 0.001; // ~0.1% GDP/tháng

  const mode = window.USD_LOGIC ? window.USD_LOGIC.getUsdMode(dxy) : 'neutral_low';
  let multiplier = 1.0;

  if (mode === 'very_strong') multiplier = country.gdpTier >= 3 ? 0.2 : 1.8;
  if (mode === 'strong')      multiplier = country.gdpTier >= 3 ? 0.4 : 1.4;
  if (mode === 'weak')        multiplier = country.gdpTier === 2 ? 1.6 : 0.8;
  if (mode === 'very_weak')   multiplier = country.gdpTier >= 3 ? 2.0 : 0.6;

  const direction = window.USD_LOGIC
    ? window.USD_LOGIC.getCountryFlowDirection(country, dxy)
    : 'neutral';

  const flowIn  = direction === 'in'  ? (baseFlow * multiplier).toFixed(1) * 1 : (baseFlow * 0.3).toFixed(1) * 1;
  const flowOut = direction === 'out' ? (baseFlow * multiplier).toFixed(1) * 1 : (baseFlow * 0.3).toFixed(1) * 1;

  return { in: flowIn, out: flowOut };
}

window.MOCK_DATA = MOCK_DATA;
window.getCountryEconomics = getCountryEconomics;
window.estimateFlows = estimateFlows;
