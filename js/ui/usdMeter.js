/* =============================================
   WEOS - usdMeter.js
   Đồng hồ DXY USD Strength indicator
   ============================================= */

function updateUsdMeter(dxy) {
  const dxyEl    = document.getElementById('dxy-value');
  const fillEl   = document.getElementById('gauge-fill');
  const statusEl = document.getElementById('usd-status');
  const sliderDisp = document.getElementById('slider-dxy-display');
  const sliderEl = document.getElementById('usd-slider');

  if (!dxyEl) return;

  const dxyNum = parseFloat(dxy) || 101.2;

  // Update DXY number display
  dxyEl.textContent = dxyNum.toFixed(1);

  // Color DXY number
  if (dxyNum >= 104) {
    dxyEl.style.color = '#ff3344';
  } else if (dxyNum <= 100) {
    dxyEl.style.color = '#00ff88';
  } else {
    dxyEl.style.color = '#ffcc00';
  }

  // Update gauge fill (85 to 115 range)
  const pct = Math.max(0, Math.min(100, ((dxyNum - 85) / 30) * 100));
  if (fillEl) {
    fillEl.style.width = pct + '%';
    if (dxyNum >= 104) {
      fillEl.classList.add('strong');
    } else {
      fillEl.classList.remove('strong');
    }
  }

  // Update status badge
  if (statusEl) {
    const logic = window.USD_LOGIC;
    if (logic) {
      const label = logic.getUsdModeLabel(dxyNum);
      statusEl.textContent = label;
      const mode = logic.getUsdMode(dxyNum);
      statusEl.className = 'usd-status-badge';
      if (mode === 'very_strong' || mode === 'strong') {
        statusEl.classList.add('strong');
      } else if (mode === 'very_weak' || mode === 'weak') {
        statusEl.classList.add('weak');
      } else {
        statusEl.classList.add('neutral');
      }
    } else {
      statusEl.textContent = dxyNum >= 104 ? '🔴 USD MẠNH' : dxyNum < 100 ? '🟢 USD YẾU' : '🟡 USD TRUNG TÍNH';
    }
  }

  // Sync slider display
  if (sliderDisp) sliderDisp.textContent = dxyNum.toFixed(1);
  if (sliderEl && !sliderEl.matches(':active')) {
    sliderEl.value = dxyNum;
  }
}

window.USD_METER_UI = {
  updateMeter: updateUsdMeter
};
