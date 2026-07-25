// WEOS Data Manager - Real-time Data Processing

class DataManager {
  constructor() {
    this.countriesData = { ...COUNTRIES_DATA };
    this.globalStats = {
      totalGDP: 0,
      totalPopulation: 0,
      averageInflation: 0,
      averageUnemployment: 0,
      globalGoldReserves: 0,
    };
    this.marketData = {};
    this.flowData = {};
    this.updateTimestamp = Date.now();
    this.init();
  }

  init() {
    console.log('📊 DataManager initialized');
    this.calculateGlobalStats();
    this.startRealTimeUpdates();
  }

  calculateGlobalStats() {
    let totalGDP = 0;
    let totalPopulation = 0;
    let sumInflation = 0;
    let sumUnemployment = 0;
    let totalGold = 0;
    let count = 0;

    for (const [key, country] of Object.entries(this.countriesData)) {
      totalGDP += country.gdp || 0;
      totalPopulation += country.population || 0;
      sumInflation += country.inflation || 0;
      sumUnemployment += country.unemployment || 0;
      totalGold += country.golds || 0;
      count++;
    }

    this.globalStats = {
      totalGDP: totalGDP,
      totalPopulation: totalPopulation,
      averageInflation: (sumInflation / count).toFixed(2),
      averageUnemployment: (sumUnemployment / count).toFixed(2),
      globalGoldReserves: totalGold.toFixed(1),
    };

    console.log('✅ Global stats updated:', this.globalStats);
  }

  getCountryData(countryCode) {
    return this.countriesData[countryCode] || null;
  }

  getAllCountries() {
    return this.countriesData;
  }

  // Simulate real-time market data updates
  startRealTimeUpdates() {
    setInterval(() => {
      this.updateMarketData();
      this.simulateFlowData();
      this.updateTimestamp = Date.now();
    }, CONFIG.UPDATE_INTERVAL.REAL_TIME);
  }

  updateMarketData() {
    const marketIndices = {
      'S&P 500': this.simulatePrice(5480, 0.05),
      'NASDAQ': this.simulatePrice(17894, 0.06),
      'DAX': this.simulatePrice(18456, 0.04),
      'NIKKEI': this.simulatePrice(38945, 0.03),
      'SSE': this.simulatePrice(3045, 0.04),
      'VN-INDEX': this.simulatePrice(1304, 0.05),
      'USD/EUR': this.simulatePrice(0.9234, 0.001),
      'USD/GBP': this.simulatePrice(1.2657, 0.001),
      'USD/JPY': this.simulatePrice(149.5, 0.5),
      'USD/CNY': this.simulatePrice(7.25, 0.05),
      'USD/VND': this.simulatePrice(25450, 50),
      'BTC/USD': this.simulatePrice(67245, 0.5),
      'ETH/USD': this.simulatePrice(3456, 0.2),
      'Gold (USD/oz)': this.simulatePrice(2336, 0.2),
      'Oil (USD/bbl)': this.simulatePrice(82.5, 0.5),
    };

    this.marketData = marketIndices;
  }

  simulatePrice(basePrice, volatility) {
    const change = (Math.random() - 0.5) * 2 * volatility;
    const newPrice = basePrice + change;
    const changePercent = ((newPrice - basePrice) / basePrice * 100).toFixed(2);
    return {
      price: newPrice.toFixed(2),
      change: changePercent,
      isPositive: changePercent >= 0,
    };
  }

  simulateFlowData() {
    this.flowData = {
      globalFDI: (Math.random() * 2 + 1.5).toFixed(2),
      tradeVolume: (Math.random() * 35 + 30).toFixed(1),
      hotMoney: (Math.random() * 500 + 400).toFixed(0),
      goldFlows: (Math.random() * 100 + 50).toFixed(1),
      cryptoMarketCap: (Math.random() * 2 + 1).toFixed(2),
    };
  }

  getMarketData() {
    return this.marketData;
  }

  getFlowData() {
    return this.flowData;
  }

  getGlobalStats() {
    return this.globalStats;
  }

  // Format numbers for display
  formatNumber(num, decimals = 2) {
    if (num >= 1e12) return (num / 1e12).toFixed(decimals) + 'T';
    if (num >= 1e9) return (num / 1e9).toFixed(decimals) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(decimals) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(decimals) + 'K';
    return num.toFixed(decimals);
  }

  // Get countries with highest GDP
  getTopCountriesByGDP(limit = 10) {
    return Object.entries(this.countriesData)
      .sort((a, b) => b[1].gdp - a[1].gdp)
      .slice(0, limit)
      .map(([code, data]) => ({ code, ...data }));
  }

  // Get countries with fastest growth
  getTopCountriesByGrowth(limit = 10) {
    return Object.entries(this.countriesData)
      .sort((a, b) => b[1].gdpGrowth - a[1].gdpGrowth)
      .slice(0, limit)
      .map(([code, data]) => ({ code, ...data }));
  }

  // Get countries with highest gold reserves
  getTopCountriesByGold(limit = 10) {
    return Object.entries(this.countriesData)
      .sort((a, b) => b[1].golds - a[1].golds)
      .slice(0, limit)
      .map(([code, data]) => ({ code, ...data }));
  }
}

// Initialize Data Manager
const dataManager = new DataManager();
