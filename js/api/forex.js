/* =============================================
   WEOS - forex.js
   Tỷ giá ngoại tệ từ API ExchangeRate-API (free)
   ============================================= */

const FOREX_API_URL = 'https://open.er-api.com/v6/latest/USD';
const FOREX_BACKUP_URL = 'https://api.exchangerate-api.com/v4/latest/USD';

let _forexData = null;
let _forexLastUpdate = 0;
let _forexUpdateTimer = null;

async function fetchForex() {
  try {
    const res = await fetch(FOREX_API_URL);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();

    if (json.rates) {
      _forexData = {
        timestamp: Date.now(),
        base: 'USD',
        rates: json.rates,
        source: 'open.er-api.com'
      };
      _forexLastUpdate = Date.now();
      window.dispatchEvent(new CustomEvent('weos:forexUpdate', { detail: _forexData }));
      return _forexData;
    }
  } catch(e) {
    console.warn('WEOS Forex: Primary API failed, trying backup...', e.message);
  }

  // Fallback
  try {
    const res2 = await fetch(FOREX_BACKUP_URL);
    const json2 = await res2.json();
    if (json2.rates) {
      _forexData = {
        timestamp: Date.now(),
        base: 'USD',
        rates: json2.rates,
        source: 'exchangerate-api.com backup'
      };
      _forexLastUpdate = Date.now();
      window.dispatchEvent(new CustomEvent('weos:forexUpdate', { detail: _forexData }));
      return _forexData;
    }
  } catch(e2) {
    console.warn('WEOS Forex: Backup also failed, using mock data');
  }

  // Use mock data
  if (window.MOCK_DATA && window.MOCK_DATA.forex) {
    _forexData = { ...window.MOCK_DATA.forex, source: 'mock' };
    _forexLastUpdate = Date.now();
    window.dispatchEvent(new CustomEvent('weos:forexUpdate', { detail: _forexData }));
    return _forexData;
  }

  return null;
}

function getForexRate(currency) {
  if (!_forexData || !_forexData.rates) {
    return window.MOCK_DATA ? window.MOCK_DATA.forex.rates[currency] : null;
  }
  return _forexData.rates[currency];
}

function getUsdChange(currency) {
  // Tính % thay đổi - dùng mock nếu không có lịch sử
  const rate = getForexRate(currency);
  if (!rate) return 0;
  // Mock small variation
  return ((Math.random() - 0.5) * 0.5).toFixed(2) * 1;
}

// DXY estimation constants (based on ICE DXY formula weights)
// EUR: 57.6%, JPY: 13.6%, GBP: 11.9%, CAD: 9.1%, SEK: 4.2%, CHF: 3.6%
const DXY_BASE = 101.0;
const EUR_WEIGHT = -30;      // EUR/USD inversely correlated with DXY
const JPY_WEIGHT = 50;       // JPY strength vs USD baseline
const EUR_BASELINE = 1.08;   // EUR/USD midpoint baseline
const JPY_BASELINE = 0.0067; // USD/JPY 100-unit baseline

function getDxyEstimate() {
  // Ước tính DXY từ các cặp tiền chính
  // DXY = 0.576*EUR + 0.136*JPY + 0.119*GBP + 0.091*CAD + 0.042*SEK + 0.036*CHF
  if (!_forexData || !_forexData.rates) {
    return window.MOCK_DATA ? window.MOCK_DATA.markets.dxy.value : 101.2;
  }

  const r = _forexData.rates;
  if (!r.EUR || !r.JPY) return 101.2;

  const eurUsd = 1 / r.EUR;   // EUR/USD rate
  const jpyUsd = r.JPY / 100; // Normalize JPY per 100 units

  // Simplified DXY: deviation from expected baseline using dominant EUR and JPY components
  const deviation = (eurUsd - EUR_BASELINE) * EUR_WEIGHT + (jpyUsd - JPY_BASELINE) * JPY_WEIGHT;
  return Math.max(85, Math.min(115, DXY_BASE + deviation));
}

function startForexAutoUpdate(intervalMs) {
  if (_forexUpdateTimer) clearInterval(_forexUpdateTimer);
  _forexUpdateTimer = setInterval(fetchForex, intervalMs || 10000);
}

function stopForexAutoUpdate() {
  if (_forexUpdateTimer) {
    clearInterval(_forexUpdateTimer);
    _forexUpdateTimer = null;
  }
}

function getForexData() { return _forexData; }
function getForexAge() { return Date.now() - _forexLastUpdate; }

window.FOREX = {
  fetchForex,
  getForexRate,
  getUsdChange,
  getDxyEstimate,
  startForexAutoUpdate,
  stopForexAutoUpdate,
  getForexData,
  getForexAge,
};
