// Dữ liệu Hệ Thần Kinh - Chỉ số vĩ mô điều khiển tại Thủ đô của các nước
const duLieuHeThanKinhThuDo = [
    {
        id: "USA", tenNuoc: "HOA KỲ", thudo: "Washington D.C",
        lat: 38.9072, lng: -77.0369,
        gdp: "+2.4%", cpi: "2.1%", ur: "4.1% (Tăng nhẹ)", ir: "4.75%", gold: "8,133 Tấn",
        trangThai: "XANH" // Hệ thần kinh chỉ đạo dòng tiền bung tỏa ổn định
    },
    {
        id: "VNM", tenNuoc: "VIỆT NAM", thudo: "Hà Nội",
        lat: 21.0285, lng: 105.8542,
        gdp: "+6.8%", cpi: "3.2%", ur: "2.3% (Giảm mạnh)", ir: "4.5%", gold: "9.2 Tấn",
        trangThai: "XANH"
    },
    {
        id: "EU", tenNuoc: "KHỐI LIÊN MINH CHÂU ÂU", thudo: "Frankfurt",
        lat: 50.1109, lng: 8.6821,
        gdp: "+0.8%", cpi: "2.6%", ur: "6.5% (Ổn định)", ir: "3.5%", gold: "10,776 Tấn",
        trangThai: "CAM"
    },
    {
        id: "CHN", tenNuoc: "TRUNG QUỐC", thudo: "Bắc Kinh",
        lat: 39.9042, lng: 116.4074,
        gdp: "+4.5%", cpi: "0.5%", ur: "5.2% (Báo động)", ir: "3.1%", gold: "2,264 Tấn",
        trangThai: "DO" // Hệ thần kinh phát tín hiệu đỏ -> Tháo vốn sản xuất
    }
];

// Dữ liệu Hệ Mạch Máu - Luồng chuyển dịch dòng tiền đa ngành (Cổ phiếu, Vàng, BĐS, Crypto...)
// Quy ước: loaiDongTien 'DAU_TU' -> Mạch máu XANH, 'THAO_TUNG' -> Mạch máu ĐỎ
let duLieuMachMauDongTien = [
    // Động mạch chủ toàn cầu liên quốc gia từ Mỹ đi các nước
    { startLat: 38.9072, startLng: -77.0369, endLat: 21.0285, endLng: 105.8542, nganh: "FDI - Vốn Đầu Tư Nhà Máy", volume: 1540000000, loaiDongTien: "DAU_TU", tocDo: "BINH_THUONG" },
    { startLat: 38.9072, startLng: -77.0369, endLat: 50.1109, endLng: 8.6821, nganh: "Forex - Thị Trường Tiền Tệ", volume: 8450000000, loaiDongTien: "DAU_TU", tocDo: "GAP_RUT" },
    { startLat: 39.9042, startLng: 116.4074, endLat: 38.9072, endLng: -77.0369, nganh: "Trái Phiếu Chính Phủ Mỹ", volume: 4300000000, loaiDongTien: "THAO_TUNG", tocDo: "GAP_RUT" },
    
    // Mao mạch vi mô nội địa tại Việt Nam (Dòng tiền chảy qua các tọa độ địa lý chính xác)
    { startLat: 21.0285, startLng: 105.8542, endLat: 20.9404, endLng: 106.6341, nganh: "Bất Động Sản - Khu Công Nghiệp Hải Phòng", volume: 450000000, loaiDongTien: "DAU_TU", tocDo: "BINH_THUONG" },
    { startLat: 21.0285, startLng: 105.8542, endLat: 10.8231, endLng: 106.6297, nganh: "Cổ Phiếu - Sàn HOSE TP.HCM", volume: 1250000000, loaiDongTien: "DAU_TU", tocDo: "GAP_RUT" },
    { startLat: 10.8231, startLng: 106.6297, endLat: 21.0285, endLng: 105.8542, nganh: "Vàng Vật Chất Trú Ẩn", volume: 320000000, loaiDongTien: "THAO_TUNG", tocDo: "BINH_THUONG" },
    
    // Luồng dịch chuyển Crypto toàn cầu chảy về các Hub máy chủ và ví cá nhân
    { startLat: 37.7749, startLng: -122.4194, endLat: 35.6762, endLng: 139.6503, nganh: "Crypto - Bitcoin Liquidity", volume: 2900000000, loaiDongTien: "DAU_TU", tocDo: "GAP_RUT" }
];
