// Khởi tạo Quả địa cầu sống động dựa trên phần cứng WebGL
const container = document.getElementById('globe-container');
const SieuBanDoKinh Te = Globe()(container)
    // Thay thế link ảnh sang cụm CDN phân tách mở để tránh bị trình duyệt chặn CORS
    .globeImageUrl('//://githubusercontent.com') 
    .bumpImageUrl('//://githubusercontent.com')
    .backgroundImageUrl('//://githubusercontent.com') 
    .showAtmosphere(true)
    .atmosphereColor("#001133")
    .atmospherePower(2.5);
