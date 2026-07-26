/* =============================================
   WEOS - controls.js
   Nút điều khiển: Globe/Flat, USD slider
   ============================================= */

let _isGlobeMode = true;

function setGlobeView() {
  _isGlobeMode = true;
  const btnGlobe = document.getElementById('btn-globe');
  const btnFlat  = document.getElementById('btn-flat');
  if (btnGlobe) btnGlobe.classList.add('active');
  if (btnFlat)  btnFlat.classList.remove('active');

  if (window.GLOBE_INIT) {
    window.GLOBE_INIT.setGlobeView(true);
  }
}

function setFlatView() {
  _isGlobeMode = false;
  const btnGlobe = document.getElementById('btn-globe');
  const btnFlat  = document.getElementById('btn-flat');
  if (btnGlobe) btnGlobe.classList.remove('active');
  if (btnFlat)  btnFlat.classList.add('active');

  if (window.GLOBE_INIT) {
    window.GLOBE_INIT.setGlobeView(false);
  }

  // Zoom out to see full map
  const globe = window.GLOBE_INIT ? window.GLOBE_INIT.getGlobe() : null;
  if (globe) {
    globe.pointOfView({ altitude: 3.5, lat: 20, lng: 0 }, 1000);
  }
}

function onDxySlider(value) {
  const dxy = parseFloat(value);
  const displayEl = document.getElementById('slider-dxy-display');
  if (displayEl) displayEl.textContent = dxy.toFixed(1);

  if (window.DATA_MANAGER) {
    window.DATA_MANAGER.setDxy(dxy);
  }
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
  switch(e.key) {
    case 'g':
    case 'G':
      setGlobeView();
      break;
    case 'f':
    case 'F':
      setFlatView();
      break;
    case 'Escape':
      if (window.closeCountryPopup) window.closeCountryPopup();
      if (window.ZOOM_LEVELS_MGR) {
        const globe = window.GLOBE_INIT ? window.GLOBE_INIT.getGlobe() : null;
        window.ZOOM_LEVELS_MGR.zoomToGlobal(globe);
      }
      break;
  }
});

// Export global functions
window.setGlobeView = setGlobeView;
window.setFlatView  = setFlatView;
window.onDxySlider  = onDxySlider;

window.CONTROLS = { setGlobeView, setFlatView, onDxySlider };
