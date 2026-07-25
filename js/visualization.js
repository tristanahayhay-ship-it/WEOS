// WEOS 3D Globe Visualization

let globe = null;
let scene = null;
let canvas = null;
let currentZoom = 300;
let isAutoRotate = true;
let selectedCountry = null;

class GlobeVisualization {
  constructor(containerId) {
    this.containerId = containerId;
    this.container = document.getElementById(containerId);
    this.init();
  }

  init() {
    console.log('🌍 Initializing 3D Globe...');
    
    // Create Globe
    globe = Globe()
      .globeImageUrl('https://unpkg.com/three-globe/example/img/earth-night.jpg')
      .bumpImageUrl('https://unpkg.com/three-globe/example/img/earth_bump.jpg')
      .backgroundImageUrl('https://unpkg.com/three-globe/example/img/night-sky.png')
      .pointOfViewDistance(300)
      .pointOfViewAltitude(0.5)
      .pointOfViewLat(20)
      .pointOfViewLng(0)
      .pointOfViewAltitude(1.5)
      (this.container);

    // Setup scene, camera, renderer (from globe.gl)
    scene = globe.scene();
    canvas = globe.canvas();

    // Auto-rotate
    if (isAutoRotate) {
      setInterval(() => {
        globe.pointOfViewLng(globe.pointOfViewLng() + 0.1);
      }, 50);
    }

    // Add countries with data visualization
    this.addCountriesData();
    this.setupMouseEvents();
    
    console.log('✅ Globe initialized successfully');
  }

  addCountriesData() {
    const countries = dataManager.getAllCountries();
    const points = [];
    const links = [];

    // Get country coordinates (simplified)
    const coordinates = this.getCountryCoordinates();

    for (const [code, data] of Object.entries(countries)) {
      const coords = coordinates[code];
      if (coords) {
        // Size based on GDP
        const size = (data.gdp / 1000) * 0.5;
        
        // Color based on growth
        let color = CONFIG.COLORS.NEUTRAL;
        if (data.gdpGrowth > 3) color = CONFIG.COLORS.CASH_IN;
        if (data.gdpGrowth < 0) color = CONFIG.COLORS.CASH_OUT;

        points.push({
          lat: coords.lat,
          lng: coords.lng,
          size: Math.max(size, 0.5),
          color: color,
          country: code,
          data: data,
        });
      }
    }

    // Add points to globe
    globe
      .pointsData(points)
      .pointAltitude(d => d.size)
      .pointColor(d => d.color)
      .pointLabel(d => `${d.data.name}<br/>GDP: $${d.data.gdp}T<br/>Growth: ${d.data.gdpGrowth}%`)
      .onPointClick(d => this.selectCountry(d));

    // Add links between major economies
    const topCountries = dataManager.getTopCountriesByGDP(15);
    for (let i = 0; i < topCountries.length - 1; i++) {
      for (let j = i + 1; j < topCountries.length; j++) {
        const from = topCountries[i];
        const to = topCountries[j];
        const fromCoords = coordinates[from.code];
        const toCoords = coordinates[to.code];
        
        if (fromCoords && toCoords) {
          // Trade volume determines link width
          const tradeVolume = (Math.random() * 500 + 100);
          links.push({
            source: { lat: fromCoords.lat, lng: fromCoords.lng },
            target: { lat: toCoords.lat, lng: toCoords.lng },
            value: tradeVolume,
          });
        }
      }
    }

    // Add links to globe
    globe
      .linksData(links)
      .linkColor(d => Math.random() > 0.5 ? CONFIG.COLORS.CASH_IN : CONFIG.COLORS.CASH_OUT)
      .linkWidth(d => Math.sqrt(d.value) * 0.1)
      .linkOpacity(0.3);
  }

  getCountryCoordinates() {
    return {
      'US': { lat: 37.0902, lng: -95.7129 },
      'CN': { lat: 35.8617, lng: 104.1954 },
      'DE': { lat: 51.1657, lng: 10.4515 },
      'JP': { lat: 36.2048, lng: 138.2529 },
      'IN': { lat: 20.5937, lng: 78.9629 },
      'GB': { lat: 55.3781, lng: -3.4360 },
      'FR': { lat: 46.2276, lng: 2.2137 },
      'BR': { lat: -14.2350, lng: -51.9253 },
      'IT': { lat: 41.8719, lng: 12.5674 },
      'CA': { lat: 56.1304, lng: -106.3468 },
      'KR': { lat: 35.9078, lng: 127.7669 },
      'SG': { lat: 1.3521, lng: 103.8198 },
      'HK': { lat: 22.3193, lng: 114.1694 },
      'VN': { lat: 14.0583, lng: 108.2772 },
      'TH': { lat: 15.8700, lng: 100.9925 },
      'ID': { lat: -0.7893, lng: 113.9213 },
      'PH': { lat: 12.8797, lng: 121.7740 },
      'MY': { lat: 4.2105, lng: 101.6964 },
      'AU': { lat: -25.2744, lng: 133.7751 },
      'ZA': { lat: -30.5595, lng: 22.9375 },
      'EG': { lat: 26.8206, lng: 30.8025 },
      'SA': { lat: 23.8859, lng: 45.0792 },
      'AE': { lat: 23.4241, lng: 53.8478 },
      'IL': { lat: 31.0461, lng: 34.8516 },
      'RU': { lat: 61.5240, lng: 105.3188 },
    };
  }

  selectCountry(point) {
    selectedCountry = point.country;
    console.log('🎯 Selected country:', selectedCountry, point.data);
    
    // Highlight selected point
    this.highlightCountry(selectedCountry);
    
    // Update info panel
    updateInfoPanel(point.data, selectedCountry);
    
    // Show right sidebar
    const rightSidebar = document.querySelector('.right-sidebar');
    if (rightSidebar) {
      rightSidebar.classList.add('active');
    }
  }

  highlightCountry(countryCode) {
    // Flash effect for selected country
    const points = globe.pointsData();
    points.forEach(p => {
      if (p.country === countryCode) {
        p.color = CONFIG.COLORS.GOLD;
      }
    });
    globe.pointsData([...points]);
  }

  zoomIn() {
    currentZoom *= 0.8;
    globe.pointOfViewDistance(currentZoom);
  }

  zoomOut() {
    currentZoom *= 1.2;
    globe.pointOfViewDistance(currentZoom);
  }

  resetView() {
    currentZoom = 300;
    globe.pointOfViewDistance(currentZoom);
    globe.pointOfViewLat(20);
    globe.pointOfViewLng(0);
  }

  setupMouseEvents() {
    // Mouse wheel zoom
    this.container.addEventListener('wheel', (e) => {
      e.preventDefault();
      if (e.deltaY < 0) {
        this.zoomIn();
      } else {
        this.zoomOut();
      }
    });
  }

  updateData() {
    // Refresh globe data with latest values
    this.addCountriesData();
  }
}

// Initialize visualization when page loads
let globeViz = null;

function initGlobe() {
  globeViz = new GlobeVisualization('globeContainer');
}
