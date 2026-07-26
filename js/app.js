// Ứng dụng chính
let flowChart = null;
let updateSpeed = 1000;

// Khởi tạo ứng dụng
window.addEventListener('DOMContentLoaded', () => {
    initGlobe();
    initUI();
    startEconomicEngine(updateSpeed);
});

// Khởi tạo giao diện người dùng
function initUI() {
    setupControlButtons();
    setupIndicators();
    setupSettings();
}

// Thiết lập nút điều khiển
function setupControlButtons() {
    document.getElementById('view-globe').addEventListener('click', () => {
        switchViewMode('globe');
    });
    
    document.getElementById('view-flat').addEventListener('click', () => {
        switchViewMode('flat');
    });
    
    document.getElementById('view-zoom').addEventListener('click', () => {
        switchViewMode('zoom');
    });
}

// Chuyển chế độ xem
function switchViewMode(mode) {
    document.querySelectorAll('.btn').forEach(btn => btn.classList.remove('active'));
    
    if (mode === 'globe') {
        document.getElementById('view-globe').classList.add('active');
        camera.position.z = 2.5;
    } else if (mode === 'flat') {
        document.getElementById('view-flat').classList.add('active');
        camera.position.z = 1.8;
    } else if (mode === 'zoom') {
        document.getElementById('view-zoom').classList.add('active');
        camera.position.z = 1.0;
    }
}

// Thiết lập chỉ số kinh tế
function setupIndicators() {
    updateIndicatorsDisplay();
}

// Cập nhật hiển thị chỉ số
function updateIndicatorsDisplay() {
    const container = document.getElementById('indicators-list');
    container.innerHTML = '';
    
    const indicators = [
        { key: 'usdIndex', label: 'Chỉ Số USD', unit: '' },
        { key: 'oilPrice', label: 'Giá Dầu', unit: '$/bbl' },
        { key: 'goldPrice', label: 'Giá Vàng', unit: '$/oz' },
        { key: 'sp500', label: 'S&P 500', unit: '' },
        { key: 'btcPrice', label: 'Bitcoin', unit: 'USD' },
        { key: 'vixIndex', label: 'VIX Index', unit: '' }
    ];
    
    indicators.forEach(ind => {
        const data = GLOBAL_INDICATORS[ind.key];
        const html = `
            <div class="indicator-item">
                <div class="indicator-name">${ind.label}</div>
                <div class="indicator-value">${data.value.toFixed(2)} ${ind.unit}</div>
                <div class="indicator-change ${data.trend === 'up' ? 'positive' : 'negative'}">
                    ${data.trend === 'up' ? '▲' : '▼'} ${Math.abs(data.change).toFixed(2)}
                </div>
            </div>
        `;
        container.innerHTML += html;
    });
}

// Thiết lập cài đặt
function setupSettings() {
    document.getElementById('toggle-flow').addEventListener('change', (e) => {
        // Bật/tắt hiển thị dòng tiền
        console.log('Toggle flow:', e.target.checked);
    });
    
    document.getElementById('toggle-indicators').addEventListener('change', (e) => {
        // Bật/tắt hiển thị chỉ số
        console.log('Toggle indicators:', e.target.checked);
    });
    
    document.getElementById('toggle-gold-reserves').addEventListener('change', (e) => {
        // Bật/tắt hiển thị dự trữ vàng
        console.log('Toggle gold reserves:', e.target.checked);
    });
    
    document.getElementById('update-speed').addEventListener('change', (e) => {
        updateSpeed = parseInt(e.target.value);
        // Cập nhật tốc độ cập nhật
    });
}

// Cập nhật thông tin quốc gia
function updateCountryInfo(country) {
    const detailedInfo = economicEngine.getCountryDetailedInfo(country.id);
    const infoContainer = document.getElementById('country-info');
    
    const html = `
        <div class="country-stat">
            <span class="country-stat-label">GDP:</span>
            <span class="country-stat-value">${(detailedInfo.gdp / 1000).toFixed(0)}B USD</span>
        </div>
        <div class="country-stat">
            <span class="country-stat-label">Dân số:</span>
            <span class="country-stat-value">${(detailedInfo.population / 1000000).toFixed(1)}M</span>
        </div>
        <div class="country-stat">
            <span class="country-stat-label">Thất nghiệp:</span>
            <span class="country-stat-value">${detailedInfo.unemployment.toFixed(1)}%</span>
        </div>
        <div class="country-stat">
            <span class="country-stat-label">Lạm phát:</span>
            <span class="country-stat-value">${detailedInfo.inflation.toFixed(1)}%</span>
        </div>
        <div class="country-stat">
            <span class="country-stat-label">Dự trữ vàng:</span>
            <span class="country-stat-value">${detailedInfo.goldReserves.toFixed(1)}M oz</span>
        </div>
        <div class="country-stat">
            <span class="country-stat-label">Sức mạnh kinh tế:</span>
            <span class="country-stat-value">${detailedInfo.economicPower}/100</span>
        </div>
        <div class="country-stat">
            <span class="country-stat-label">Dòng tiền ròng:</span>
            <span class="country-stat-value ${detailedInfo.netFlow > 0 ? 'positive' : 'negative'}">
                ${detailedInfo.netFlow > 0 ? '+' : ''}${(detailedInfo.netFlow / 1000).toFixed(0)}B USD
            </span>
        </div>
    `;
    
    infoContainer.innerHTML = html;
    document.getElementById('selected-country').textContent = country.name;
}

// Cập nhật giao diện chung
function updateUI() {
    updateIndicatorsDisplay();
    
    if (selectedCountry) {
        const country = getCountryData(selectedCountry);
        updateCountryInfo(country);
    }
}

// Tạo chart dòng tiền
function createFlowChart() {
    const ctx = document.getElementById('flowChart');
    
    if (flowChart) {
        flowChart.destroy();
    }
    
    flowChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Đầu vào', 'Đầu ra'],
            datasets: [{
                label: 'Dòng tiền (B USD)',
                data: [0, 0],
                backgroundColor: ['#00ff88', '#ff3333']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 212, 255, 0.1)'
                    },
                    ticks: {
                        color: '#00d4ff'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#00d4ff'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}