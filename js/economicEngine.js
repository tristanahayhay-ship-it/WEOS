// Engine tính toán kinh tế và dòng tiền
class EconomicEngine {
    constructor() {
        this.indicators = { ...GLOBAL_INDICATORS };
        this.countryStates = {};
        this.moneyFlows = [];
        this.updateInterval = 1000;
        
        // Khởi tạo trạng thái các quốc gia
        COUNTRIES_DATA.forEach(country => {
            this.countryStates[country.id] = {
                gdp: country.gdp,
                unemployment: country.unemployment,
                inflation: 2.5 + Math.random() * 2,
                interestRate: 3.5 + Math.random() * 2,
                currencyStrength: 100,
                investmentInflow: 0,
                investmentOutflow: 0
            };
        });
    }
    
    // Cập nhật chỉ số kinh tế theo USD
    updateIndicators() {
        updateIndicators();
    }
    
    // Tính toán tác động USD đến các nước
    calculateUSDImpact() {
        const usdChange = this.indicators.usdIndex.change / 100;
        
        COUNTRIES_DATA.forEach(country => {
            const state = this.countryStates[country.id];
            
            if (usdChange > 0) {
                // USD mạnh - đầu tư rút khỏi các nước
                state.investmentOutflow += country.gdp * 0.01 * usdChange;
                state.currencyStrength -= 2 * usdChange;
            } else {
                // USD yếu - đầu tư vào các nước
                state.investmentInflow += country.gdp * 0.01 * Math.abs(usdChange);
                state.currencyStrength += 2 * Math.abs(usdChange);
            }
        });
    }
    
    // Tính toán dòng tiền giữa các nước
    calculateMoneyFlows() {
        const flows = [];
        
        // Dòng tiền dựa trên nhu cầu
        COUNTRIES_DATA.forEach(fromCountry => {
            COUNTRIES_DATA.forEach(toCountry => {
                if (fromCountry.id !== toCountry.id) {
                    const flow = this.calculateBilateralFlow(fromCountry, toCountry);
                    if (flow.amount > 0) {
                        flows.push(flow);
                    }
                }
            });
        });
        
        this.moneyFlows = flows;
        return flows;
    }
    
    // Tính dòng tiền hai chiều
    calculateBilateralFlow(from, to) {
        // Dựa trên GDP, khoảng cách, mối quan hệ thương mại
        const gdpRatio = from.gdp / to.gdp;
        const baseFlow = from.gdp * 0.001 * gdpRatio;
        
        const usdInfluence = this.indicators.usdIndex.change / 100;
        const adjustedFlow = baseFlow * (1 + usdInfluence);
        
        return {
            from: from.id,
            to: to.id,
            amount: Math.abs(adjustedFlow),
            direction: usdInfluence > 0 ? 'outflow' : 'inflow',
            type: Math.random() > 0.5 ? 'trade' : 'investment'
        };
    }
    
    // Cập nhật toàn bộ hệ thống kinh tế
    update() {
        this.updateIndicators();
        this.calculateUSDImpact();
        this.calculateMoneyFlows();
    }
    
    // Lấy thông tin chi tiết quốc gia
    getCountryDetailedInfo(countryId) {
        const country = getCountryData(countryId);
        const state = this.countryStates[countryId];
        
        return {
            ...country,
            ...state,
            netFlow: state.investmentInflow - state.investmentOutflow
        };
    }
}

// Khởi tạo engine
const economicEngine = new EconomicEngine();

// Bắt đầu cập nhật
function startEconomicEngine(interval = 1000) {
    economicEngine.updateInterval = interval;
    setInterval(() => {
        economicEngine.update();
        updateUI();
    }, interval);
}