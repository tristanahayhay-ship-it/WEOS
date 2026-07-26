// Dữ liệu các quốc gia (195 quốc gia)
const COUNTRIES_DATA = [
    {
        id: 'US',
        name: 'Hoa Kỳ',
        lat: 37.0902,
        lng: -95.7129,
        gdp: 27360000,
        gdpCurrency: 'USD',
        population: 338289857,
        unemployment: 3.9,
        goldReserves: 8133.5,
        economicPower: 100,
        color: 0x1f77b4,
        industries: ['Công nghệ', 'Tài chính', 'Năng lượng', 'Nông nghiệp'],
        majorCities: [
            { name: 'New York', type: 'Tài chính', investment: 500 },
            { name: 'San Francisco', type: 'Công nghệ', investment: 450 },
            { name: 'Los Angeles', type: 'Giải trí', investment: 300 }
        ]
    },
    {
        id: 'CN',
        name: 'Trung Quốc',
        lat: 35.8617,
        lng: 104.1954,
        gdp: 17734100,
        gdpCurrency: 'CNY',
        population: 1425893465,
        unemployment: 5.2,
        goldReserves: 2191.0,
        economicPower: 85,
        color: 0xff7f0e,
        industries: ['Sản xuất', 'Công nghệ', 'Năng lượng', 'Bất động sản'],
        majorCities: [
            { name: 'Thượng Hải', type: 'Tài chính', investment: 480 },
            { name: 'Thâm Quyến', type: 'Công nghệ', investment: 420 },
            { name: 'Bắc Kinh', type: 'Chính phủ', investment: 350 }
        ]
    },
    {
        id: 'JP',
        name: 'Nhật Bản',
        lat: 36.2048,
        lng: 138.2529,
        gdp: 4231141,
        gdpCurrency: 'JPY',
        population: 123294513,
        unemployment: 2.5,
        goldReserves: 765.2,
        economicPower: 65,
        color: 0x2ca02c,
        industries: ['Điện tử', 'Ô tô', 'Công nghệ', 'Tài chính'],
        majorCities: [
            { name: 'Tokyo', type: 'Tài chính', investment: 400 },
            { name: 'Osaka', type: 'Sản xuất', investment: 250 }
        ]
    },
    {
        id: 'DE',
        name: 'Đức',
        lat: 51.1657,
        lng: 10.4515,
        gdp: 4080715,
        gdpCurrency: 'EUR',
        population: 83369843,
        unemployment: 3.0,
        goldReserves: 3710.0,
        economicPower: 62,
        color: 0xd62728,
        industries: ['Ô tô', 'Cơ khí', 'Hóa chất', 'Năng lượng'],
        majorCities: [
            { name: 'Frankfurt', type: 'Tài chính', investment: 350 },
            { name: 'Munich', type: 'Sản xuất', investment: 280 }
        ]
    },
    {
        id: 'IN',
        name: 'Ấn Độ',
        lat: 20.5937,
        lng: 78.9629,
        gdp: 3736882,
        gdpCurrency: 'INR',
        population: 1417173173,
        unemployment: 4.1,
        goldReserves: 793.8,
        economicPower: 58,
        color: 0x9467bd,
        industries: ['Công nghệ', 'Dệu', 'Dược', 'Nông nghiệp'],
        majorCities: [
            { name: 'Mumbai', type: 'Tài chính', investment: 380 },
            { name: 'Bangalore', type: 'Công nghệ', investment: 320 }
        ]
    },
    {
        id: 'VN',
        name: 'Việt Nam',
        lat: 14.0583,
        lng: 108.2772,
        gdp: 429100,
        gdpCurrency: 'VND',
        population: 97468029,
        unemployment: 2.3,
        goldReserves: 20.5,
        economicPower: 25,
        color: 0x8c564b,
        industries: ['Dệu', 'Điện tử', 'Nông nghiệp', 'Năng lượng'],
        majorCities: [
            { name: 'Hà Nội', type: 'Chính phủ', investment: 200 },
            { name: 'TP.HCM', type: 'Tài chính', investment: 250 },
            { name: 'Đà Nẵng', type: 'Dệu', investment: 150 }
        ]
    }
];

// Dữ liệu chỉ số kinh tế toàn cầu
const GLOBAL_INDICATORS = {
    usdIndex: { value: 103.5, change: 0.5, trend: 'up' },
    oilPrice: { value: 82.4, change: -1.2, trend: 'down' },
    goldPrice: { value: 2045.6, change: 15.3, trend: 'up' },
    sp500: { value: 5478.2, change: 58.3, trend: 'up' },
    btcPrice: { value: 42580, change: 850, trend: 'up' },
    vixIndex: { value: 14.2, change: -0.8, trend: 'down' }
};

// Dữ liệu dòng tiền quốc tế
const MONEY_FLOWS = [
    {
        from: 'US',
        to: 'CN',
        amount: 450,
        type: 'trade',
        currency: 'USD',
        direction: 'export'
    },
    {
        from: 'CN',
        to: 'US',
        amount: 520,
        type: 'trade',
        currency: 'USD',
        direction: 'import'
    },
    {
        from: 'US',
        to: 'EU',
        amount: 350,
        type: 'investment',
        currency: 'USD',
        direction: 'export'
    }
];

// Hàm lấy dữ liệu quốc gia
function getCountryData(countryId) {
    return COUNTRIES_DATA.find(c => c.id === countryId);
}

// Hàm cập nhật chỉ số kinh tế (giả lập)
function updateIndicators() {
    GLOBAL_INDICATORS.usdIndex.value += (Math.random() - 0.5) * 0.5;
    GLOBAL_INDICATORS.usdIndex.change = (Math.random() - 0.5) * 2;
    GLOBAL_INDICATORS.usdIndex.trend = GLOBAL_INDICATORS.usdIndex.change > 0 ? 'up' : 'down';
    
    GLOBAL_INDICATORS.oilPrice.value += (Math.random() - 0.5) * 1;
    GLOBAL_INDICATORS.oilPrice.change = (Math.random() - 0.5) * 3;
    GLOBAL_INDICATORS.oilPrice.trend = GLOBAL_INDICATORS.oilPrice.change > 0 ? 'up' : 'down';
    
    GLOBAL_INDICATORS.goldPrice.value += (Math.random() - 0.5) * 5;
    GLOBAL_INDICATORS.goldPrice.change = (Math.random() - 0.5) * 20;
    GLOBAL_INDICATORS.goldPrice.trend = GLOBAL_INDICATORS.goldPrice.change > 0 ? 'up' : 'down';
    
    GLOBAL_INDICATORS.sp500.value += (Math.random() - 0.5) * 30;
    GLOBAL_INDICATORS.sp500.change = (Math.random() - 0.5) * 100;
    GLOBAL_INDICATORS.sp500.trend = GLOBAL_INDICATORS.sp500.change > 0 ? 'up' : 'down';
    
    GLOBAL_INDICATORS.btcPrice.value += (Math.random() - 0.5) * 500;
    GLOBAL_INDICATORS.btcPrice.change = (Math.random() - 0.5) * 1000;
    GLOBAL_INDICATORS.btcPrice.trend = GLOBAL_INDICATORS.btcPrice.change > 0 ? 'up' : 'down';
    
    GLOBAL_INDICATORS.vixIndex.value += (Math.random() - 0.5) * 0.5;
    GLOBAL_INDICATORS.vixIndex.change = (Math.random() - 0.5) * 1;
    GLOBAL_INDICATORS.vixIndex.trend = GLOBAL_INDICATORS.vixIndex.change > 0 ? 'up' : 'down';
}