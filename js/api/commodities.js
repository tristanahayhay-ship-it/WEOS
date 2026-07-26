/* =============================================
   WEOS - commodities.js
   Hàng hóa: Vàng, Dầu từ APIs miễn phí
   ============================================= */

// Metals API (no-key, CORS-friendly)
const METALS_API_URL = 'https://api.metalpriceapi.com/v1/latest?api_key=demo&base=USD&currencies=XAU,XAG';

// Fallback: frankfurter.app (gold not supported but EUR/USD)
let _commoditiesData = null;
let _lastUpdate = 0;
let _timer = null;

// CoinGecko cũng có giá vàng
const GOLD_COINGECKO_URL = 'https://api.coingecko.com/api/v3/simple/price?ids=gold&vs_currencies=usd&include_24hr_change=true';

async function fetchCommodities() {
  let goldPrice = null;
  let goldChange = 0;

  // Thử lấy giá vàng từ CoinGecko (paxos gold hoặc tether gold)
  try {
    const res = await fetch('https://api.coingecko.com/api/v3/simple/price?ids=tether-gold,pax-gold&vs_currencies=usd&include_24hr_change=true');
    const json = await res.json();
    const tgold = json['tether-gold'] || json['pax-gold'];
    if (tgold && tgold.usd) {
      goldPrice = tgold.usd;
      goldChange = tgold.usd_24h_change || 0;
    }
  } catch(e) {}

  // Fallback: mock
  if (!goldPrice) {
    const mock = window.MOCK_DATA ? window.MOCK_DATA.commodities : null;
    goldPrice  = mock ? mock.gold.price  : 2680;
    goldChange = mock ? mock.gold.change : 0.5;
  }

  _commoditiesData = {
    timestamp: Date.now(),
    gold: {
      price: goldPrice,
      change: goldChange,
      unit: 'USD/oz',
      label: 'Vàng'
    },
    // Oil and others from mock (free real-time oil APIs require keys)
    oil_wti:    window.MOCK_DATA ? { ...window.MOCK_DATA.commodities.oil_wti,   change: simulateChange(window.MOCK_DATA.commodities.oil_wti.price,   0.8) } : { price: 71.5,  change: 0, unit: 'USD/bbl', label: 'Dầu WTI' },
    oil_brent:  window.MOCK_DATA ? { ...window.MOCK_DATA.commodities.oil_brent, change: simulateChange(window.MOCK_DATA.commodities.oil_brent.price, 0.8) } : { price: 75.8,  change: 0, unit: 'USD/bbl', label: 'Dầu Brent' },
    silver:     window.MOCK_DATA ? { ...window.MOCK_DATA.commodities.silver,    change: simulateChange(window.MOCK_DATA.commodities.silver.price,    1.5) } : { price: 31.2,  change: 0, unit: 'USD/oz', label: 'Bạc' },
    copper:     window.MOCK_DATA ? { ...window.MOCK_DATA.commodities.copper,    change: simulateChange(window.MOCK_DATA.commodities.copper.price,    0.6) } : { price: 9420,  change: 0, unit: 'USD/tấn', label: 'Đồng' },
    nat_gas:    window.MOCK_DATA ? { ...window.MOCK_DATA.commodities.nat_gas,   change: simulateChange(window.MOCK_DATA.commodities.nat_gas.price,   2.0) } : { price: 2.85,  change: 0, unit: 'USD/MMBtu', label: 'Khí đốt' },
    source: goldChange !== 0 ? 'coingecko+mock' : 'mock'
  };

  _lastUpdate = Date.now();
  window.dispatchEvent(new CustomEvent('weos:commoditiesUpdate', { detail: _commoditiesData }));
  return _commoditiesData;
}

// Giả lập thay đổi nhỏ (±volatility%) cho dữ liệu mock
function simulateChange(basePrice, volatility) {
  return ((Math.random() - 0.48) * volatility).toFixed(2) * 1;
}

function getCommodityPrice(key) {
  if (_commoditiesData && _commoditiesData[key]) return _commoditiesData[key].price;
  if (window.MOCK_DATA && window.MOCK_DATA.commodities && window.MOCK_DATA.commodities[key]) {
    return window.MOCK_DATA.commodities[key].price;
  }
  return null;
}

function getCommodityChange(key) {
  if (_commoditiesData && _commoditiesData[key]) return _commoditiesData[key].change;
  return 0;
}

function startCommoditiesAutoUpdate(intervalMs) {
  if (_timer) clearInterval(_timer);
  _timer = setInterval(fetchCommodities, intervalMs || 30000);
}

function stopCommoditiesAutoUpdate() {
  if (_timer) { clearInterval(_timer); _timer = null; }
}

function getCommoditiesData() { return _commoditiesData; }

window.COMMODITIES = {
  fetchCommodities,
  getCommodityPrice,
  getCommodityChange,
  startCommoditiesAutoUpdate,
  stopCommoditiesAutoUpdate,
  getCommoditiesData,
};
