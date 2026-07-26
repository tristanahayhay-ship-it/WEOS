/* =============================================
   WEOS - countryPopup.js
   Click thủ đô → popup chi tiết tiếng Việt
   ============================================= */

let _currentCountry = null;

function showCountryPopup(country, dxy) {
  _currentCountry = country;
  const dxyVal = dxy || (window.DATA_MANAGER ? window.DATA_MANAGER.getDxy() : 101.2);

  const popupEl  = document.getElementById('country-popup');
  const contentEl = document.getElementById('popup-content');
  if (!popupEl || !contentEl) return;

  // Lấy data từ data manager
  const data = window.DATA_MANAGER
    ? window.DATA_MANAGER.getCountryData(country.code, dxyVal)
    : buildFallbackData(country, dxyVal);

  contentEl.innerHTML = renderCountryPopup(country, data);
  popupEl.classList.remove('hidden');

  // Stop globe auto-rotate
  const globe = window.GLOBE_INIT ? window.GLOBE_INIT.getGlobe() : null;
  if (globe && globe.controls) {
    globe.controls().autoRotate = false;
  }
}

function closeCountryPopup() {
  const popupEl = document.getElementById('country-popup');
  if (popupEl) popupEl.classList.add('hidden');
  _currentCountry = null;

  // Resume globe auto-rotate
  const globe = window.GLOBE_INIT ? window.GLOBE_INIT.getGlobe() : null;
  if (globe && globe.controls) {
    globe.controls().autoRotate = true;
  }
}

function renderCountryPopup(country, data) {
  if (!data) return '<p style="color:#888">Không có dữ liệu</p>';

  const dir = data.flowDirection || 'neutral';
  const dirColor = dir === 'in' ? '#00ff88' : dir === 'out' ? '#ff3344' : '#4488ff';
  const dirLabel = dir === 'in' ? '🟢 Tiền VÀO' : dir === 'out' ? '🔴 Tiền RA' : '🔵 Trung tính';

  const goldRankText = data.goldRank ? `#${data.goldRank} thế giới` : 'N/A';
  const gdpGrowthClass = (data.gdpGrowth || 0) > 0 ? 'up' : 'down';
  const rateChangeClass = (data.rateChange || 0) > 0 ? 'up' : 'down';
  const inflowBig  = (data.inflow  || 0) > 10;
  const outflowBig = (data.outflow || 0) > 10;

  const regions = Array.isArray(data.regions) ? data.regions : [];

  return `
    <div class="popup-header">
      <span class="country-flag">${country.flag || '🌐'}</span>
      <div>
        <h2>${country.name}</h2>
        <span class="capital-label">🏛️ ${country.capital || 'N/A'}</span>
      </div>
    </div>

    <!-- LUỒNG TIỀN HIỆN TẠI -->
    <div style="text-align:center;padding:8px;margin-bottom:12px;background:rgba(0,0,30,0.6);border-radius:8px;border:1px solid ${dirColor}40;">
      <span style="font-size:15px;color:${dirColor};font-weight:700">${dirLabel}</span><br>
      <small style="color:#888">DXY: ${data.dxy ? data.dxy.toFixed(1) : '--'} | ${data.usdModeLabel || ''}</small>
    </div>

    <!-- HỆ THẦN KINH KINH TẾ -->
    <div class="popup-section">
      <h3>🧠 HỆ THẦN KINH KINH TẾ</h3>
      ${makeIndicator('GDP', '$' + formatBillions(country.gdpUSD) + ' tỷ USD', data.gdpGrowth, '%/năm')}
      ${makeIndicator(country.currency + '/USD', data.exchangeRate || '--', data.rateChange, '%')}
      ${makeIndicator('Dự trữ vàng', country.goldReserves + ' tấn', null, goldRankText)}
      ${makeIndicator('Thất nghiệp', (data.unemployment || '--') + '%', null, '')}
      ${makeIndicator('Lạm phát (CPI)', (data.inflation || '--') + '%', null, '')}
      ${makeIndicator('Cán cân TM', formatTradeBalance(data.tradeBalance), null, 'tỷ USD/tháng')}
      ${makeIndicator('Lãi suất CB', (data.interestRate || '--') + '%', null, '')}
      ${makeIndicator('Nợ công/GDP', (data.debtGDP || '--') + '%', null, '')}
    </div>

    <!-- MẠCH MÁU DÒNG TIỀN -->
    <div class="popup-section">
      <h3>🩸 MẠCH MÁU DÒNG TIỀN</h3>
      <div class="flow-indicator">
        <span class="flow-dot-in">●</span>
        <span>Tiền VÀO: <strong>$${formatBillions(data.inflow)} tỷ/tháng</strong></span>
        ${inflowBig ? '<span style="color:#00ff88;font-size:10px">▲▲ MẠNH</span>' : ''}
      </div>
      <div class="flow-indicator">
        <span class="flow-dot-out">●</span>
        <span>Tiền RA: <strong>$${formatBillions(data.outflow)} tỷ/tháng</strong></span>
        ${outflowBig ? '<span style="color:#ff3344;font-size:10px">▼▼ MẠNH</span>' : ''}
      </div>
      <div class="flow-indicator" style="margin-top:6px">
        <span>🛡️ Tài sản trú ẩn:</span>
        <span style="color:#ffcc00;margin-left:4px">${data.safeHaven || 'N/A'}</span>
      </div>
      <div class="flow-indicator">
        <span>📤 Xuất khẩu chính:</span>
        <span style="color:#88ccff;margin-left:4px">${(country.mainExports || []).slice(0,3).join(', ')}</span>
      </div>
    </div>

    <!-- VÙNG ĐỎ/XANH -->
    <div class="popup-section">
      <h3>🗺️ VÙNG ĐỎ/XANH - NGUYÊN NHÂN</h3>
      ${regions.length > 0
        ? regions.map(r => `
          <div class="region-item ${r.status}">
            ${r.status === 'green' ? '🟢' : r.status === 'red' ? '🔴' : '🔵'}
            <strong>${r.name}</strong>: ${r.reason}
          </div>
        `).join('')
        : '<div class="region-item neutral">🔵 Thị trường ổn định</div>'
      }
    </div>

    <!-- CHỈ SỐ CHỨNG KHOÁN -->
    ${data.stockIndex ? `
    <div class="popup-section">
      <h3>📈 THỊ TRƯỜNG CHỨNG KHOÁN</h3>
      ${makeIndicator('Chỉ số', data.stockIndex.toLocaleString('vi-VN'), data.stockChange, '%')}
      ${makeIndicator('Tăng trưởng GDP', (data.gdpGrowth || '--') + '%/năm', null, '')}
    </div>
    ` : ''}

    <!-- ZOOM INFO -->
    <div style="text-align:center;padding:8px;margin-top:4px">
      <small style="color:#446;font-size:10px">Click vào globe để zoom vào ${country.name}</small>
    </div>
  `;
}

function makeIndicator(label, value, change, unit) {
  let changeHtml = '';
  if (change !== null && change !== undefined) {
    const pct = parseFloat(change) || 0;
    const cls = pct >= 0 ? 'up' : 'down';
    const icon = pct >= 0 ? '▲' : '▼';
    changeHtml = `<span class="change ${cls}">${icon} ${Math.abs(pct).toFixed(2)}${unit || ''}</span>`;
  } else if (unit) {
    changeHtml = `<span style="color:#446;font-size:10px">${unit}</span>`;
  }
  return `
    <div class="popup-indicator">
      <span class="label">${label}</span>
      <span class="value">${value}</span>
      ${changeHtml}
    </div>
  `;
}

function formatBillions(val) {
  if (val === null || val === undefined || isNaN(val)) return '0';
  if (val >= 1000) return (val / 1000).toFixed(1) + 'N';
  return parseFloat(val).toFixed(1);
}

function formatTradeBalance(val) {
  if (val === null || val === undefined || isNaN(val)) return '--';
  const sign = val >= 0 ? '+' : '';
  return sign + parseFloat(val).toFixed(1);
}

function buildFallbackData(country, dxy) {
  const econ  = typeof getCountryEconomics !== 'undefined' ? getCountryEconomics(country.code) : {};
  const flows = typeof estimateFlows !== 'undefined' ? estimateFlows(country, dxy) : { in: 0.5, out: 0.5 };
  const logic = window.USD_LOGIC;
  return {
    ...econ,
    ...country,
    exchangeRate: '--',
    rateChange: 0,
    dxy,
    usdMode: logic ? logic.getUsdMode(dxy) : 'neutral_low',
    usdModeLabel: logic ? logic.getUsdModeLabel(dxy) : '--',
    flowDirection: logic ? logic.getCountryFlowDirection(country, dxy) : 'neutral',
    safeHaven: logic ? logic.getSafeHavenAssets(dxy).slice(0,3).join(', ') : 'Vàng',
    inflow:  flows.in,
    outflow: flows.out,
    goldRank: typeof GOLD_RANK_MAP !== 'undefined' ? GOLD_RANK_MAP[country.code] : null,
    regions: [],
  };
}

window.COUNTRY_POPUP = {
  showCountryPopup,
  closeCountryPopup,
  renderCountryPopup,
};

// Global function for HTML onclick
window.closeCountryPopup = closeCountryPopup;
