/* =============================================
   WEOS - dataManager.js
   Tổng hợp tất cả APIs, cache, auto-update
   ============================================= */

const DATA_MANAGER = {
  _state: {
    dxy: 101.2,
    dxyPrev: 101.2,
    lastFullUpdate: 0,
    updateCount: 0,
    isInitialized: false,
  },

  // --- Khởi tạo ---
  async init() {
    console.log('WEOS DataManager: Initializing...');
    setLoadingStatus('Đang tải dữ liệu thị trường...', 75);

    try {
      // Fetch all data sources in parallel
      await Promise.allSettled([
        this.fetchAll(),
      ]);

      this._state.isInitialized = true;
      this._state.lastFullUpdate = Date.now();

      // Bắt đầu auto-update
      this.startAutoUpdates();

      setLoadingStatus('Dữ liệu đã sẵn sàng!', 90);
      console.log('WEOS DataManager: Initialized successfully');
    } catch(e) {
      console.error('WEOS DataManager: Init error', e);
      setLoadingStatus('Dùng dữ liệu offline...', 90);
    }
  },

  // --- Fetch tất cả ---
  async fetchAll() {
    const results = await Promise.allSettled([
      window.FOREX        ? window.FOREX.fetchForex()           : Promise.resolve(null),
      window.CRYPTO       ? window.CRYPTO.fetchCrypto()         : Promise.resolve(null),
      window.COMMODITIES  ? window.COMMODITIES.fetchCommodities(): Promise.resolve(null),
    ]);

    // Tính DXY từ forex data
    this.updateDxy();

    this._state.updateCount++;
    this._state.lastFullUpdate = Date.now();

    // Update UI
    this.updateAllUI();

    return results;
  },

  // --- Cập nhật DXY ---
  updateDxy() {
    this._state.dxyPrev = this._state.dxy;

    let newDxy;
    if (window.FOREX) {
      newDxy = window.FOREX.getDxyEstimate();
    } else {
      newDxy = window.MOCK_DATA ? window.MOCK_DATA.markets.dxy.value : 101.2;
    }

  // DXY smoothing constants (exponential moving average)
  // Keeps 70% of previous value + 30% of new estimate for stability
  const DXY_PREV_WEIGHT = 0.7;
  const DXY_NEW_WEIGHT  = 0.3;

    // Smoothing - không để DXY nhảy quá nhiều
    this._state.dxy = (this._state.dxy * DXY_PREV_WEIGHT + newDxy * DXY_NEW_WEIGHT);
    return this._state.dxy;
  },

  // --- Get current DXY ---
  getDxy() {
    return this._state.dxy;
  },

  // --- Update DXY thủ công (từ slider) ---
  setDxy(val) {
    this._state.dxyPrev = this._state.dxy;
    this._state.dxy = parseFloat(val);
    this.onDxyChanged();
  },

  // --- Callback khi DXY thay đổi ---
  onDxyChanged() {
    const dxy = this._state.dxy;

    // Update globe
    if (window.GLOBE_INIT) {
      window.GLOBE_INIT.updateGlobeForDxy(dxy);
    }

    // Update USD meter UI
    if (window.USD_METER_UI) {
      window.USD_METER_UI.updateMeter(dxy);
    }

    // Update flow status
    this.updateFlowStatusUI();

    // Update flow direction text
    if (window.USD_LOGIC) {
      const label = window.USD_LOGIC.getUsdModeLabel(dxy);
      const el = document.getElementById('flow-direction');
      if (el) {
        el.textContent = `${label}: ${window.USD_LOGIC.USD_STRONG_FLOWS.description || 'Phân tích dòng tiền...'}`;
      }
    }
  },

  // --- Update tất cả UI ---
  updateAllUI() {
    this.updateDashboardUI();
    this.updateFlowStatusUI();
    if (window.USD_METER_UI) {
      window.USD_METER_UI.updateMeter(this._state.dxy);
    }
  },

  // --- Update Dashboard UI ---
  updateDashboardUI() {
    // Gold
    const goldPrice  = getCommodityOrMock('gold');
    const goldChange = getCommodityChangeOrMock('gold');
    updateIndicatorRow('gold', formatPrice(goldPrice, '$', '/oz'), goldChange);

    // BTC
    const btcPrice  = getCryptoOrMock('bitcoin');
    const btcChange = getCryptoChangeOrMock('bitcoin');
    updateIndicatorRow('btc', formatPrice(btcPrice, '$'), btcChange);

    // Oil
    const oilPrice  = getCommodityOrMock('oil_wti');
    const oilChange = getCommodityChangeOrMock('oil_wti');
    updateIndicatorRow('oil', formatPrice(oilPrice, '$', '/bbl'), oilChange);

    // ETH
    const ethPrice  = getCryptoOrMock('ethereum');
    const ethChange = getCryptoChangeOrMock('ethereum');
    updateIndicatorRow('eth', formatPrice(ethPrice, '$'), ethChange);

    // S&P500 (mock only)
    const sp500 = window.MOCK_DATA ? window.MOCK_DATA.markets.sp500 : { value: 5870, change: 0.6 };
    updateIndicatorRow('sp500', formatPrice(sp500.value, ''), sp500.change);

    // Update last time
    const timeEl = document.getElementById('last-update-time');
    if (timeEl) timeEl.textContent = new Date().toLocaleTimeString('vi-VN');
  },

  // --- Update Flow Status UI ---
  updateFlowStatusUI() {
    const dxy = this._state.dxy;
    const logic = window.USD_LOGIC;
    if (!logic) return;

    const mode = logic.getUsdMode(dxy);
    const label = logic.getUsdModeLabel(dxy);
    const assets = logic.getSafeHavenAssets(dxy);

    const flowDir = document.getElementById('flow-direction');
    if (flowDir) {
      const isStrong = dxy >= 104;
      const isWeak   = dxy < 100;
      if (isStrong) {
        flowDir.innerHTML = `<span style="color:#ff3344">USD mạnh</span>: Vốn chạy về Mỹ. Mua <strong>${assets.slice(0,2).join(', ')}</strong>`;
      } else if (isWeak) {
        flowDir.innerHTML = `<span style="color:#00ff88">USD yếu</span>: Vốn chảy ra EM & hàng hóa. Mua <strong>${assets.slice(0,2).join(', ')}</strong>`;
      } else {
        flowDir.innerHTML = `<span style="color:#ffcc00">USD trung tính</span>: Dòng tiền cân bằng. Trú ẩn: <strong>${assets.slice(0,2).join(', ')}</strong>`;
      }
    }
  },

  // --- Bắt đầu auto-updates ---
  startAutoUpdates() {
    // Forex: 10 giây
    if (window.FOREX) window.FOREX.startForexAutoUpdate(10000);

    // Crypto: 15 giây
    if (window.CRYPTO) window.CRYPTO.startCryptoAutoUpdate(15000);

    // Commodities: 30 giây
    if (window.COMMODITIES) window.COMMODITIES.startCommoditiesAutoUpdate(30000);

    // Dashboard update: 8 giây
    setInterval(() => {
      this.updateDxy();
      this.updateDashboardUI();
    }, 8000);

    // Full refresh: 1 phút
    setInterval(() => {
      this.fetchAll();
    }, 60000);

    // Listen to API events
    window.addEventListener('weos:forexUpdate',      () => { this.updateDxy(); this.updateDashboardUI(); });
    window.addEventListener('weos:cryptoUpdate',     () => this.updateDashboardUI());
    window.addEventListener('weos:commoditiesUpdate',() => this.updateDashboardUI());
  },

  // --- Lấy dữ liệu quốc gia tổng hợp ---
  getCountryData(countryCode, dxy) {
    const country = typeof COUNTRY_MAP !== 'undefined' ? COUNTRY_MAP[countryCode] : null;
    if (!country) return null;

    const econ  = typeof getCountryEconomics !== 'undefined' ? getCountryEconomics(countryCode) : {};
    const flows = typeof estimateFlows !== 'undefined' ? estimateFlows(country, dxy || this._state.dxy) : { in: 0, out: 0 };
    const forex = window.FOREX ? window.FOREX.getForexRate(country.currency) : null;
    const mockRate = window.MOCK_DATA ? window.MOCK_DATA.forex.rates[country.currency] : null;
    const exRate = forex || mockRate || 1;

    const rateChange = window.FOREX ? window.FOREX.getUsdChange(country.currency) : ((Math.random()-0.5)*0.3).toFixed(2)*1;

    const logic = window.USD_LOGIC;
    const dxyVal = dxy || this._state.dxy;
    const usdMode = logic ? logic.getUsdMode(dxyVal) : 'neutral_low';
    const usdModeLabel = logic ? logic.getUsdModeLabel(dxyVal) : 'N/A';
    const flowDir = logic ? logic.getCountryFlowDirection(country, dxyVal) : 'neutral';
    const safeHaven = logic ? logic.getSafeHavenAssets(dxyVal).slice(0,3).join(', ') : 'Vàng, USD';

    const goldRank = typeof GOLD_RANK_MAP !== 'undefined' ? GOLD_RANK_MAP[countryCode] : null;

    return {
      ...country,
      ...econ,
      exchangeRate: formatExchangeRate(exRate, country.currency),
      rateChange,
      inflow:  flows.in,
      outflow: flows.out,
      dxy:     dxyVal,
      usdMode,
      usdModeLabel,
      flowDirection: flowDir,
      safeHaven,
      goldRank,
      regions: buildRegionData(country, dxyVal, logic),
    };
  },
};

// --- Helper functions ---
function getCommodityOrMock(key) {
  return window.COMMODITIES && window.COMMODITIES.getCommodityPrice(key)
    || (window.MOCK_DATA && window.MOCK_DATA.commodities[key] ? window.MOCK_DATA.commodities[key].price : null);
}
function getCommodityChangeOrMock(key) {
  return window.COMMODITIES ? window.COMMODITIES.getCommodityChange(key)
    : (window.MOCK_DATA && window.MOCK_DATA.commodities[key] ? window.MOCK_DATA.commodities[key].change : 0);
}
function getCryptoOrMock(coinId) {
  return window.CRYPTO && window.CRYPTO.getCryptoPrice(coinId)
    || (window.MOCK_DATA && window.MOCK_DATA.crypto[coinId] ? window.MOCK_DATA.crypto[coinId].usd : null);
}
function getCryptoChangeOrMock(coinId) {
  return window.CRYPTO ? window.CRYPTO.getCryptoChange(coinId)
    : (window.MOCK_DATA && window.MOCK_DATA.crypto[coinId] ? window.MOCK_DATA.crypto[coinId].usd_24h_change : 0);
}

function updateIndicatorRow(id, value, change) {
  const valEl = document.getElementById(`val-${id}`);
  const chgEl = document.getElementById(`chg-${id}`);
  if (valEl && value !== null) valEl.textContent = value;
  if (chgEl && change !== null && change !== undefined) {
    const pct = parseFloat(change);
    chgEl.textContent = (pct >= 0 ? '▲' : '▼') + Math.abs(pct).toFixed(2) + '%';
    chgEl.className = 'ind-change ' + (pct >= 0 ? 'up' : 'down');
  }
}

function formatPrice(val, prefix, suffix) {
  if (val === null || val === undefined) return '--';
  prefix = prefix || '';
  suffix = suffix || '';
  if (val >= 1000000) return prefix + (val/1000000).toFixed(2) + 'M' + suffix;
  if (val >= 1000)    return prefix + val.toLocaleString('en-US', { maximumFractionDigits: 0 }) + suffix;
  return prefix + val.toFixed(2) + suffix;
}

function formatExchangeRate(rate, currency) {
  if (!rate) return '--';
  if (rate < 0.01)  return rate.toFixed(6);
  if (rate < 1)     return rate.toFixed(4);
  if (rate < 10)    return rate.toFixed(3);
  if (rate < 1000)  return rate.toFixed(2);
  return Math.round(rate).toLocaleString('vi-VN');
}

function buildRegionData(country, dxy, logic) {
  if (!logic) return [];
  const direction = logic.getCountryFlowDirection(country, dxy);
  const reason = logic.getFlowReason(country, dxy);

  const regions = [];

  // Khu vực kinh tế trong nước
  if (direction === 'in') {
    regions.push({ name: 'Xuất khẩu', status: 'green', reason: `Hàng xuất khẩu cạnh tranh hơn: ${country.mainExports.slice(0,2).join(', ')}` });
    regions.push({ name: 'FDI', status: 'green', reason: 'Đầu tư nước ngoài tăng do lãi suất cạnh tranh' });
    regions.push({ name: 'Dự trữ ngoại hối', status: 'green', reason: 'Tăng tích lũy dự trữ khi vốn chảy vào' });
  } else if (direction === 'out') {
    regions.push({ name: 'Tỷ giá', status: 'red', reason: `${country.currency} mất giá so với USD → nhập khẩu đắt hơn` });
    regions.push({ name: 'Trái phiếu', status: 'red', reason: 'Nhà đầu tư nước ngoài bán tháo bonds nội địa' });
    regions.push({ name: 'Lạm phát nhập khẩu', status: 'red', reason: 'Đồng nội tệ yếu làm giá nhập khẩu tăng' });
  } else {
    regions.push({ name: 'Thị trường', status: 'neutral', reason: 'Ổn định, không có áp lực lớn từ USD' });
  }

  return regions;
}

// Helper cho globeInit.js
function setLoadingStatus(msg, pct) {
  if (window.GLOBE_INIT) {
    window.GLOBE_INIT.setLoadingStatus(msg, pct);
    return;
  }
  const statusEl = document.getElementById('loading-status');
  const barEl    = document.getElementById('loading-bar');
  if (statusEl) statusEl.textContent = msg;
  if (barEl && pct !== undefined) barEl.style.width = pct + '%';
}

window.DATA_MANAGER = DATA_MANAGER;
window.setLoadingStatus = setLoadingStatus;
