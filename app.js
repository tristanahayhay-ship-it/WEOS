// Khởi tạo Quả địa cầu sống động dựa trên phần cứng WebGL
const container = document.getElementById('globe-container');

// ĐÃ SỬA LỖI: Ghép liền tên biến 'SieuBanDoKinhTe' không còn khoảng trắng
const SieuBanDoKinhTe = Globe()(container)
    // Sử dụng liên kết raw chính thức từ thư viện gốc để đảm bảo tải bề mặt Trái Đất mượt mà
    .globeImageUrl('//://githubusercontent.com') 
    .bumpImageUrl('//://githubusercontent.com')
    .backgroundImageUrl('//://githubusercontent.com') 
    .showAtmosphere(true)
    .atmosphereColor("#001133")
    .atmospherePower(2.5);

// 1. CẤU HÌNH HỆ THẦN KINH TRUNG ƯƠNG (Các điểm nút Thủ đô)
SieuBanDoKinhTe
    .labelsData(duLieuHeThanKinhThuDo)
    .labelLat(d => d.lat)
    .labelLng(d => d.lng)
    .labelText(d => `📍 ${d.thudo}`)
    .labelSize(1.2)
    .labelDotRadius(0.6)
    .labelColor(d => {
        if(d.trangThai === 'XANH') return '#00ffcc';
        if(d.trangThai === 'CAM') return '#ffaa00';
        return '#ff3344'; // Đỏ neon cảnh báo hệ thần kinh co rút
    })
    .labelResolution(3)
    // Lắng nghe hành động click chuột vào hệ thần kinh Thủ đô
    .onLabelClick((nutThudo) => {
        hienThiBangChisoHUD(nutThudo);
    });

// 2. CẤU HÌNH HỆ MẠCH MÁU SINH HỌC (Dòng tiền nhảy số từng giây)
function capNhatDoHoaMachMau() {
    SieuBanDoKinhTe
        .arcsData(duLieuMachMauDongTien)
        .arcStartLat(d => d.startLat)
        .arcStartLng(d => d.startLng)
        .arcEndLat(d => d.endLat)
        .arcEndLng(d => d.endLng)
        
        // KIẾN TRÚC SINH HỌC: Đầu tư -> Máu Xanh, Tháo chạy bảo thủ -> Máu Đỏ
        .arcColor(d => d.loaiDongTien === 'DAU_TU' ? '#00ff66' : '#ff2233')
        
        // KIẾN TRÚC SINH HỌC: Tiền bơm/tháo càng mạnh (Volume lớn) -> Mạch máu càng PHÌNH TO
        .arcStroke(d => {
            const doDay = d.volume / 1000000000; // Tỷ lệ thuận theo đơn vị Tỷ USD
            return Math.max(0.4, Math.min(doDay, 4.5)); // Giới hạn độ dày tối đa
        })
        
        // KIẾN TRÚC SINH HỌC: Xung chuyển động của các hạt giọt máu trên đường dây
        .arcDashLength(0.5)
        .arcDashGap(0.3)
        // Thị trường khẩn cấp rút/bơm vốn ào ạt -> Tốc độ chuyển động tăng cực nhanh
        .arcDashAnimateTime(d => d.tocDo === 'GAP_RUT' ? 600 : 2200)
        
        // HIỂN THỊ VI MÔ: Rê chuột vào mạch máu hiện rõ địa điểm và số lượng USD thực tế
        .arcLabel(d => `
            <div style="background: rgba(0,2,10,0.9); padding: 10px; border: 1px solid #00ffcc; border-radius: 6px; font-family: sans-serif;">
                <b style="color: #00ffcc;">📊 NGÀNH: ${d.nganh}</b><br/>
                <span style="color: #fff;">Dòng chảy: ${d.loaiDongTien === 'DAU_TU' ? '🎯 ĐANG ĐẦU TƯ VÀO' : '🚨 THÁO CHẠY PHÒNG THỦ'}</span><br/>
                <b style="color: #ffd700;">Khối lượng dòng tiền: $${d.volume.toLocaleString()} USD</b>
            </div>
        `);
}

// 3. THUẬT TOÁN MÔ PHỎNG DÒNG TIỀN THEO THỜI GIAN THỰC TỪNG GIÂY
setInterval(() => {
    duLieuMachMauDongTien.forEach(machmau => {
        // Tạo biến động ngẫu nhiên biên độ +/- 5,000,000 USD mỗi giây mô phỏng thị trường khớp lệnh liên tục
        const bienDong = (Math.random() - 0.5) * 10000000;
        machmau.volume = Math.max(100000000, machmau.volume + bienDong);
        
        // Tự động điều chỉnh trạng thái khẩn cấp dựa trên khối lượng tiền giao dịch đột biến
        if (bienDong > 4000000) {
            machmau.tocDo = 'GAP_RUT';
        } else {
            machmau.tocDo = 'BINH_THUONG';
        }
    });
    // Re-render liên tục mà không giật màn hình
    capNhatDoHoaMachMau();
    
    // Cập nhật lại số liệu thời gian thực trên bảng HUD nếu đang mở
    const hud = document.getElementById('hud-thudo');
    if (hud.style.display === 'block') {
        const idHienTai = hud.getAttribute('data-country-id');
        const nutThudo = duLieuHeThanKinhThuDo.find(n => n.id === idHienTai);
        if(nutThudo) capNhatTextHUD(nutThudo);
    }
}, 1000);

// 4. HÀM XỬ LÝ ĐIỀU KHIỂN GIAO DIỆN (HUD & CƠ CHẾ GÓC NHÌN)
function hienThiBangChisoHUD(data) {
    const hud = document.getElementById('hud-thudo');
    hud.setAttribute('data-country-id', data.id);
    hud.style.display = 'block';
    
    // Thay đổi màu viền hệ thần kinh HUD dựa trên tình trạng sức khỏe quốc gia đó
    if(data.trangThai === 'XANH') hud.style.borderLeftColor = '#00ff66';
    else if(data.trangThai === 'CAM') hud.style.borderLeftColor = '#ffaa00';
    else hud.style.borderLeftColor = '#ff3344';

    capNhatTextHUD(data);
}

function capNhatTextHUD(data) {
    document.getElementById('hud-ten-nuoc').innerHTML = `${data.tenNuoc} <span style="font-size: 0.8rem; color: #a0aec0;">(${data.thudo})</span>`;
    document.getElementById('chiso-gdp').className = data.trangThai === 'DO' ? 'gia-tri-am' : 'gia-tri-duong';
    document.getElementById('chiso-gdp').innerText = data.gdp;
    document.getElementById('chiso-cpi').innerText = data.cpi;
    document.getElementById('chiso-ur').innerText = data.ur;
    document.getElementById('chiso-ir').innerText = data.ir;
    document.getElementById('chiso-gold').innerText = data.gold;
}

// Hàm xử lý nút bấm thay đổi góc nhìn Bản đồ hình cầu (3D) sang Bản đồ ngang phẳng (2D)
function doiGocNhin(loaiGocNhin) {
    document.querySelectorAll('.btn').forEach(b => b.classList.remove('active'));
    if (loaiGocNhin === 'plane') {
        document.getElementById('btn-plane').classList.add('active');
        SieuBanDoKinhTe.globeMode('2d'); // Chuyển sang dạng bản đồ phẳng ngang
    } else {
        document.getElementById('btn-sphere').classList.add('active');
        SieuBanDoKinhTe.globeMode('earth'); // Quay về quả địa cầu 3D sinh học
    }
}

// Ẩn dòng thông báo loading khi WebGL tải xong toàn bộ cấu trúc lõi của Trái Đất
setTimeout(() => {
    document.getElementById('loading').style.display = 'none';
    capNhatDoHoaMachMau();
}, 1200);
