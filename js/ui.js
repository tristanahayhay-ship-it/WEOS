// WEOS UI Management

// Current page tracking
let currentPage = 'home';

// Initialize UI
function initUI() {
  console.log('🎨 Initializing UI...');
  setupMenuListeners();
  setupClockUpdate();
  setupFPSCounter();
  setupClosePanel();
  setupTabButtons();
}

// Menu Navigation
function setupMenuListeners() {
  const menuItems = document.querySelectorAll('.menu-item');
  
  menuItems.forEach(item => {
    item.addEventListener('click', () => {
      const page = item.getAttribute('data-page');
      switchPage(page);
      
      // Update active state
      menuItems.forEach(m => m.classList.remove('active'));
      item.classList.add('active');
    });
  });
}

// Page Switching
function switchPage(pageName) {
  const pages = document.querySelectorAll('.page');
  
  pages.forEach(page => {
    page.style.display = 'none';
  });
  
  const targetPage = document.getElementById(`${pageName}-page`);
  if (targetPage) {
    targetPage.style.display = 'flex';
    currentPage = pageName;
    console.log(`📄 Switched to ${pageName} page`);
    
    // Handle page-specific logic
    handlePageSwitch(pageName);
  }
}

function handlePageSwitch(pageName) {
  switch(pageName) {
    case 'home':
      if (!globeViz) {
        initGlobe();
      }
      break;
    case 'world':
      // Initialize world globe if needed
      break;
    case 'macro':
      updateMacroPage();
      break;
    case 'market':
      updateMarketPage();
      break;
    case 'flow':
      updateFlowPage();
      break;
    case 'settings':
      // Settings page loaded
      break;
  }
}

// Update Clock
function setupClockUpdate() {
  function updateClock() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit',
      timeZone: 'UTC'
    });
    const dateStr = now.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: '2-digit', 
      day: '2-digit'
    });
    
    document.getElementById('currentTime').textContent = timeStr + ' UTC';
    document.getElementById('updateTime').textContent = `Cập nhật: ${timeStr}`;
    document.getElementById('currentDate').textContent = dateStr;
  }
  
  updateClock();
  setInterval(updateClock, 1000);
}

// FPS Counter
function setupFPSCounter() {
  let lastTime = performance.now();
  let frames = 0;
  let fps = 0;
  
  function calculateFPS() {
    const currentTime = performance.now();
    frames++;
    
    if (currentTime >= lastTime + 1000) {
      fps = frames;
      document.querySelector('.fps-counter').textContent = `FPS: ${fps}`;
      frames = 0;
      lastTime = currentTime + 1000;
    }
    
    requestAnimationFrame(calculateFPS);
  }
  
  calculateFPS();
}

// Close Right Sidebar
function setupClosePanel() {
  const closeBtn = document.querySelector('.close-panel');
  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      const rightSidebar = document.querySelector('.right-sidebar');
      rightSidebar.classList.remove('active');
      selectedCountry = null;
    });
  }
}

// Update Info Panel with Country Data
function updateInfoPanel(countryData, countryCode) {
  document.getElementById('countryName').textContent = countryData.name;
  document.getElementById('countryFlag').textContent = countryData.flag;
  
  // Overview section
  document.getElementById('infGDP').textContent = `$${dataManager.formatNumber(countryData.gdp)}T`;
  document.getElementById('infGDPGrowth').textContent = `${countryData.gdpGrowth.toFixed(2)}%`;
  document.getElementById('infInflation').textContent = `${countryData.inflation.toFixed(2)}%`;
  document.getElementById('infPopulation').textContent = `${dataManager.formatNumber(countryData.population)}M`;
  document.getElementById('infUnemployment').textContent = `${countryData.unemployment.toFixed(2)}%`;
  
  // Market data
  updateCountryMarkets(countryCode, countryData);
}

function updateCountryMarkets(countryCode, countryData) {
  const marketList = document.getElementById('countryMarkets');
  let html = '';
  
  const marketIndices = {
    'US': ['S&P 500', 'NASDAQ'],
    'CN': ['SSE'],
    'JP': ['NIKKEI'],
    'VN': ['VN-INDEX'],
    'GB': ['FTSE 100'],
    'DE': ['DAX'],
  };
  
  const indices = marketIndices[countryCode] || [];
  const marketData = dataManager.getMarketData();
  
  if (indices.length > 0) {
    indices.forEach(index => {
      const data = marketData[index];
      if (data) {
        const changeClass = data.isPositive ? 'positive' : 'negative';
        const changeSymbol = data.isPositive ? '+' : '';
        html += `
          <div class="market-item">
            <span class="symbol">${index}</span>
            <span class="value">${data.price}</span>
            <span class="change ${changeClass}">${changeSymbol}${data.change}%</span>
          </div>
        `;
      }
    });
  } else {
    html = '<p class="placeholder">Chưa có dữ liệu</p>';
  }
  
  marketList.innerHTML = html;
}

// Update MACRO Page
function updateMacroPage() {
  const stats = dataManager.getGlobalStats();
  
  document.getElementById('globalGDP').textContent = `$${dataManager.formatNumber(stats.totalGDP)}T`;
  document.getElementById('globalInflation').textContent = `${stats.averageInflation}%`;
  document.getElementById('globalUnemployment').textContent = `${stats.averageUnemployment}%`;
  document.getElementById('globalPopulation').textContent = `${dataManager.formatNumber(stats.totalPopulation)}B`;
}

// Update MARKET Page
function updateMarketPage() {
  const marketData = dataManager.getMarketData();
  const marketDataDiv = document.getElementById('marketData');
  
  let html = '';
  for (const [symbol, data] of Object.entries(marketData)) {
    const changeClass = data.isPositive ? 'positive' : 'negative';
    const changeSymbol = data.isPositive ? '+' : '';
    html += `
      <div class="market-item">
        <span class="symbol">${symbol}</span>
        <span class="value">${data.price}</span>
        <span class="change ${changeClass}">${changeSymbol}${data.change}%</span>
      </div>
    `;
  }
  
  marketDataDiv.innerHTML = html;
}

// Setup Market Tabs
function setupTabButtons() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const market = btn.getAttribute('data-market');
      
      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      
      console.log(`Switched to ${market} market`);
    });
  });
}

// Update FLOW Page
function updateFlowPage() {
  const flowData = dataManager.getFlowData();
  
  const stats = document.querySelectorAll('.flow-stat');
  const statsObj = [
    { label: 'FDI Toàn Cầu:', value: `$${flowData.globalFDI}T` },
    { label: 'Thương Mại Quốc Tế:', value: `$${flowData.tradeVolume}T` },
    { label: 'Dòng Vốn Nóng:', value: `$${flowData.hotMoney}B` },
    { label: 'Dự Trữ Vàng Toàn Cầu:', value: `$${flowData.goldFlows}B` },
  ];
  
  stats.forEach((stat, index) => {
    if (statsObj[index]) {
      stat.innerHTML = `<label>${statsObj[index].label}</label><span class="value">${statsObj[index].value}</span>`;
    }
  });
}

// Real-time data update loop
function startUIUpdates() {
  setInterval(() => {
    if (currentPage === 'macro') {
      updateMacroPage();
    } else if (currentPage === 'market') {
      updateMarketPage();
    } else if (currentPage === 'flow') {
      updateFlowPage();
    }
    
    // Update info panel if country selected
    if (selectedCountry) {
      const countryData = dataManager.getCountryData(selectedCountry);
      if (countryData) {
        updateCountryMarkets(selectedCountry, countryData);
      }
    }
  }, 5000);
}
