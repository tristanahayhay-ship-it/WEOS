// WEOS Main Entry Point

console.log('%c🌍 WEOS - World Economic Observation System', 'color: #00d4ff; font-size: 16px; font-weight: bold;');
console.log('%cInitializing...', 'color: #00ff88; font-size: 12px;');

// Document Ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initWEOS);
} else {
  initWEOS();
}

function initWEOS() {
  console.log('✅ DOM Ready - Starting initialization...');
  
  try {
    // 1. Initialize Configuration
    initConfig();
    console.log('✅ Config initialized');
    
    // 2. Initialize Data Manager (already done in constructor)
    console.log('✅ Data Manager ready');
    
    // 3. Initialize UI
    initUI();
    console.log('✅ UI initialized');
    
    // 4. Initialize Globe Visualization
    initGlobe();
    console.log('✅ Globe visualization initialized');
    
    // 5. Start UI Updates
    startUIUpdates();
    console.log('✅ Real-time updates started');
    
    // 6. Setup Keyboard Shortcuts
    setupKeyboardShortcuts();
    console.log('✅ Keyboard shortcuts registered');
    
    // 7. Handle Window Resize
    setupWindowResize();
    console.log('✅ Resize handler ready');
    
    console.log('%c🚀 WEOS Ready!', 'color: #00ff88; font-size: 14px; font-weight: bold;');
    
  } catch (error) {
    console.error('❌ Error during initialization:', error);
  }
}

// Keyboard Shortcuts
function setupKeyboardShortcuts() {
  document.addEventListener('keydown', (e) => {
    // Alt + H: Go to HOME
    if (e.altKey && e.key === 'h') {
      switchPage('home');
      document.querySelector('[data-page="home"]').click();
    }
    // Alt + W: Go to WORLD
    if (e.altKey && e.key === 'w') {
      switchPage('world');
      document.querySelector('[data-page="world"]').click();
    }
    // Alt + M: Go to MACRO
    if (e.altKey && e.key === 'm') {
      switchPage('macro');
      document.querySelector('[data-page="macro"]').click();
    }
    // Alt + R: Reset Globe
    if (e.altKey && e.key === 'r') {
      if (globeViz) globeViz.resetView();
    }
    // Alt + +: Zoom In
    if (e.altKey && e.key === '+') {
      if (globeViz) globeViz.zoomIn();
    }
    // Alt + -: Zoom Out
    if (e.altKey && e.key === '-') {
      if (globeViz) globeViz.zoomOut();
    }
    // Escape: Close Info Panel
    if (e.key === 'Escape') {
      const rightSidebar = document.querySelector('.right-sidebar');
      if (rightSidebar && rightSidebar.classList.contains('active')) {
        rightSidebar.classList.remove('active');
        selectedCountry = null;
      }
    }
  });
}

// Handle Window Resize
function setupWindowResize() {
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      console.log('🔄 Window resized - updating globe...');
      if (globeViz) {
        // Update globe size
        const container = document.getElementById('globeContainer');
        if (container && globe) {
          globe.width(container.clientWidth);
          globe.height(container.clientHeight);
        }
      }
    }, 500);
  });
}

// Global Error Handler
window.addEventListener('error', (event) => {
  console.error('❌ Global Error:', event.error);
});

// Unhandled Promise Rejection
window.addEventListener('unhandledrejection', (event) => {
  console.error('❌ Unhandled Promise Rejection:', event.reason);
});

// Export for console access
window.WEOS = {
  dataManager,
  globeViz,
  switchPage,
  CONFIG,
};

console.log('💡 Tip: Access WEOS via window.WEOS in console');
