// WEOS Configuration

const CONFIG = {
  // API Endpoints
  API: {
    WORLD_BANK: 'https://api.worldbank.org/v2',
    FOREX: 'https://api.exchangerate-api.com/v4/latest',
    CRYPTO: 'https://api.coingecko.com/api/v3',
    NEWS: 'https://newsapi.org/v2',
  },

  // Globe Configuration
  GLOBE: {
    width: window.innerWidth,
    height: window.innerHeight,
    autoRotate: true,
    autoRotateSpeed: 0.5,
    polygonCapColor: 'rgba(0, 212, 255, 0.1)',
    polygonSideColor: 'rgba(0, 212, 255, 0.15)',
    polygonStrokeColor: 'rgba(0, 212, 255, 0.3)',
  },

  // Update Intervals (ms)
  UPDATE_INTERVAL: {
    REAL_TIME: 1000,
    FAST: 5000,
    NORMAL: 10000,
    SLOW: 30000,
  },

  // Colors
  COLORS: {
    CASH_IN: '#00ff88',    // Green - Investment flowing in
    CASH_OUT: '#ff4444',   // Red - Capital withdrawal
    NEUTRAL: '#00d4ff',    // Blue - Neutral/stable
    POSITIVE: '#00ff88',   // Green - Growth
    NEGATIVE: '#ff4444',   // Red - Decline
    GOLD: '#ffa500',       // Gold - Reserves/precious metals
    WARNING: '#ffaa00',    // Orange - Warning
  },

  // Economic Indicators
  INDICATORS: {
    GDP: 'GDP',
    GDP_GROWTH: 'GDP Growth',
    INFLATION: 'Inflation (CPI)',
    UNEMPLOYMENT: 'Unemployment',
    POPULATION: 'Population',
    FDI: 'Foreign Direct Investment',
    TRADE: 'Trade Volume',
    DEBT: 'Government Debt',
    GOLD_RESERVES: 'Gold Reserves',
  },

  // Market Indices
  MARKETS: {
    STOCKS: ['S&P 500', 'NASDAQ', 'DAX', 'NIKKEI', 'SSE', 'VN-INDEX'],
    FOREX: ['USD/EUR', 'USD/GBP', 'USD/JPY', 'USD/CNY', 'USD/VND'],
    CRYPTO: ['BTC/USD', 'ETH/USD', 'BNB/USD'],
    COMMODITIES: ['Gold (USD/oz)', 'Oil (USD/bbl)', 'Natural Gas'],
  },

  // Countries Data (Will be loaded from countries.js)
  COUNTRIES: [],

  // Update Frequency
  CURRENT_UPDATE_FREQUENCY: 'REAL_TIME',
};

// Initialize Config
function initConfig() {
  console.log('✅ Config initialized');
  CONFIG.GLOBE.width = window.innerWidth - 320 - 300; // Minus sidebars
  CONFIG.GLOBE.height = window.innerHeight - 50;      // Minus header
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CONFIG;
}
