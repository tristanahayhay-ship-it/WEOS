/* =============================================
   WEOS - crypto.js
   Giá crypto từ CoinGecko API (free, no key)
   ============================================= */

const COINGECKO_URL = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,ripple,cardano&vs_currencies=usd&include_24hr_change=true&include_market_cap=true';

let _cryptoData = null;
let _cryptoLastUpdate = 0;
let _cryptoUpdateTimer = null;

async function fetchCrypto() {
  try {
    const res = await fetch(COINGECKO_URL);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();

    if (json.bitcoin) {
      _cryptoData = {
        timestamp: Date.now(),
        bitcoin:  extractCoin(json.bitcoin,  'Bitcoin',  'BTC'),
        ethereum: extractCoin(json.ethereum, 'Ethereum', 'ETH'),
        solana:   extractCoin(json.solana,   'Solana',   'SOL'),
        ripple:   extractCoin(json.ripple,   'XRP',      'XRP'),
        cardano:  json.cardano ? extractCoin(json.cardano, 'Cardano', 'ADA') : null,
        source: 'coingecko.com'
      };
      _cryptoLastUpdate = Date.now();
      window.dispatchEvent(new CustomEvent('weos:cryptoUpdate', { detail: _cryptoData }));
      return _cryptoData;
    }
  } catch(e) {
    console.warn('WEOS Crypto: CoinGecko failed, using mock data:', e.message);
  }

  // Use mock data
  if (window.MOCK_DATA && window.MOCK_DATA.crypto) {
    _cryptoData = { ...window.MOCK_DATA.crypto, source: 'mock' };
    _cryptoLastUpdate = Date.now();
    window.dispatchEvent(new CustomEvent('weos:cryptoUpdate', { detail: _cryptoData }));
    return _cryptoData;
  }

  return null;
}

function extractCoin(data, label, symbol) {
  return {
    usd: data.usd,
    usd_24h_change: data.usd_24h_change || 0,
    usd_market_cap: data.usd_market_cap || 0,
    label,
    symbol
  };
}

function getCryptoPrice(coinId) {
  if (_cryptoData && _cryptoData[coinId]) {
    return _cryptoData[coinId].usd;
  }
  if (window.MOCK_DATA && window.MOCK_DATA.crypto && window.MOCK_DATA.crypto[coinId]) {
    return window.MOCK_DATA.crypto[coinId].usd;
  }
  return null;
}

function getCryptoChange(coinId) {
  if (_cryptoData && _cryptoData[coinId]) {
    return _cryptoData[coinId].usd_24h_change || 0;
  }
  if (window.MOCK_DATA && window.MOCK_DATA.crypto && window.MOCK_DATA.crypto[coinId]) {
    return window.MOCK_DATA.crypto[coinId].usd_24h_change || 0;
  }
  return 0;
}

function startCryptoAutoUpdate(intervalMs) {
  if (_cryptoUpdateTimer) clearInterval(_cryptoUpdateTimer);
  _cryptoUpdateTimer = setInterval(fetchCrypto, intervalMs || 15000);
}

function stopCryptoAutoUpdate() {
  if (_cryptoUpdateTimer) {
    clearInterval(_cryptoUpdateTimer);
    _cryptoUpdateTimer = null;
  }
}

function getCryptoData() { return _cryptoData; }

window.CRYPTO = {
  fetchCrypto,
  getCryptoPrice,
  getCryptoChange,
  startCryptoAutoUpdate,
  stopCryptoAutoUpdate,
  getCryptoData,
};
