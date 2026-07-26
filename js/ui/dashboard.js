/* =============================================
   WEOS - dashboard.js
   Panel chỉ số toàn cầu góc phải
   ============================================= */

// Dashboard tự update qua events từ dataManager.js
// File này chủ yếu chứa render helpers

function renderDashboard() {
  const dxy = window.DATA_MANAGER ? window.DATA_MANAGER.getDxy() : 101.2;
  if (window.DATA_MANAGER) {
    window.DATA_MANAGER.updateAllUI();
  }
}

// Listen to data events và tự re-render
window.addEventListener('weos:forexUpdate',       renderDashboard);
window.addEventListener('weos:cryptoUpdate',      renderDashboard);
window.addEventListener('weos:commoditiesUpdate', renderDashboard);

window.DASHBOARD = { renderDashboard };
