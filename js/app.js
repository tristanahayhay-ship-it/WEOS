/* =============================================
   WEOS - app.js
   Main orchestrator - Bản Đồ Kinh Tế Thế Giới
   ============================================= */

(async function initWEOS() {
  console.log('🌍 WEOS: World Economic Operating System - Starting...');

  setLoadingStatus('Khởi tạo WEOS...', 10);
  await sleep(100);

  setLoadingStatus('Đang tải dữ liệu 195 quốc gia...', 20);
  await sleep(50);

  // Verify data loaded
  if (typeof COUNTRIES_DATA === 'undefined') {
    console.error('WEOS: COUNTRIES_DATA not loaded!');
    setLoadingStatus('Lỗi tải dữ liệu quốc gia!', 100);
    return;
  }
  console.log(`WEOS: Loaded ${COUNTRIES_DATA.length} countries`);

  // 1. Init Globe
  setLoadingStatus('Khởi tạo địa cầu 3D...', 35);
  const globe = await window.GLOBE_INIT.initGlobe('globe-container');

  if (!globe) {
    console.error('WEOS: Globe init failed!');
    setLoadingStatus('Lỗi khởi tạo globe!', 100);
    return;
  }

  // 2. Init Data Manager (fetch APIs)
  setLoadingStatus('Đang kết nối APIs...', 75);
  await window.DATA_MANAGER.init();

  // 3. Initial DXY & Arc update
  setLoadingStatus('Tính toán dòng tiền...', 85);
  const initialDxy = window.DATA_MANAGER.getDxy();
  window.GLOBE_INIT.setCurrentDxy(initialDxy);
  window.GLOBE_INIT.updateGlobeForDxy(initialDxy);

  // 4. Start arc auto-update
  window.FLOW_ARCS.startArcAutoUpdate(
    () => window.GLOBE_INIT.getGlobe(),
    () => window.DATA_MANAGER.getDxy()
  );

  // 5. Sync slider with real DXY
  const sliderEl = document.getElementById('usd-slider');
  if (sliderEl) {
    sliderEl.value = Math.max(85, Math.min(115, initialDxy));
    const displayEl = document.getElementById('slider-dxy-display');
    if (displayEl) displayEl.textContent = initialDxy.toFixed(1);
  }

  // 6. Initial UI render
  window.USD_METER_UI.updateMeter(initialDxy);
  window.DATA_MANAGER.updateAllUI();

  setLoadingStatus('WEOS sẵn sàng! 🌍', 100);
  await sleep(600);

  // Hide loading overlay
  const overlay = document.getElementById('loading-overlay');
  if (overlay) {
    overlay.classList.add('fade-out');
    setTimeout(() => { overlay.style.display = 'none'; }, 800);
  }

  // 7. Animate globe entrance
  setTimeout(() => {
    const g = window.GLOBE_INIT.getGlobe();
    if (g) {
      g.pointOfView({ lat: 20, lng: 0, altitude: 2.8 }, 0);
      setTimeout(() => {
        g.pointOfView({ lat: 20, lng: 0, altitude: 2.4 }, 2000);
      }, 500);
    }
  }, 200);

  // 8. Show welcome hint after 3 seconds
  setTimeout(() => {
    showWelcomeHint();
  }, 3000);

  // 9. Listen to data events for globe updates
  window.addEventListener('weos:forexUpdate', () => {
    const dxy = window.DATA_MANAGER.getDxy();
    window.GLOBE_INIT.updateGlobeForDxy(dxy);
    window.USD_METER_UI.updateMeter(dxy);
  });

  // 10. Live DXY update every 8 seconds (with slight variation for realism)
  setInterval(() => {
    const currentDxy = window.DATA_MANAGER.getDxy();
    // Add small random walk
    const noise = (Math.random() - 0.495) * 0.15;
    const newDxy = Math.max(88, Math.min(112, currentDxy + noise));
    window.DATA_MANAGER.setDxy(newDxy);
  }, 8000);

  console.log('✅ WEOS: Fully initialized');
  console.log(`📊 DXY: ${initialDxy.toFixed(2)} | Countries: ${COUNTRIES_DATA.length}`);
})();

// --- Utilities ---
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function showWelcomeHint() {
  const tooltip = document.getElementById('hover-tooltip');
  if (!tooltip) return;
  tooltip.innerHTML = `
    <strong>🌍 Chào mừng đến WEOS</strong><br>
    • Click vào thủ đô (●) để xem chi tiết kinh tế<br>
    • Kéo slider để điều chỉnh sức mạnh USD<br>
    • Đường <span style="color:#00ff88">xanh</span> = tiền VÀO, <span style="color:#ff3344">đỏ</span> = tiền RA<br>
    <small style="color:#446">Nhấn ESC để quay về toàn cầu</small>
  `;
  tooltip.classList.remove('hidden');
  tooltip.style.left = '50%';
  tooltip.style.top  = '50%';
  tooltip.style.transform = 'translate(-50%, -50%)';
  tooltip.style.maxWidth = '300px';
  tooltip.style.zIndex = '300';

  setTimeout(() => {
    tooltip.classList.add('hidden');
    tooltip.style.transform = '';
  }, 5000);
}

// --- Global error handler ---
window.addEventListener('error', (e) => {
  console.error('WEOS Error:', e.message, e.filename, e.lineno);
});

window.addEventListener('unhandledrejection', (e) => {
  console.warn('WEOS Unhandled Promise:', e.reason);
});
