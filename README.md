# 🌍 WEOS - World Economic Observation System

**Hệ Thống Quan Sát Kinh Tế Toàn Cầu Sống Động**

## 📖 Mô Tả Dự Án

WEOS là một hệ thống trực quan hóa kinh tế toàn cầu 3D thời gian thực, được thiết kế để:

- 🌐 **Hiển thị 195 quốc gia** trên bản đồ thế giới 3D động
- 💰 **Theo dõi dòng tiền** toàn cầu (FDI, thương mại, vốn nóng)
- 📊 **Cập nhật chỉ số kinh tế** theo thời gian thực (GDP, lạm suất, thất nghiệp...)
- 📈 **Hiển thị thị trường tài chính** (chứng khoán, forex, crypto, hàng hóa)
- 🔗 **Kết nối các nền kinh tế** với các dòng dữ liệu xanh (đầu tư) và đỏ (rút tiền)
- 🧬 **Sống động như một sinh vật** - Nền kinh tế toàn cầu được coi là một hệ thống sống động

## 🎯 Tính Năng Chính

### 1. **HOME - Trái Đất 3D Tương Tác**
- Globe 3D xoay được, có thể zoom vào/ra
- 195 quốc gia được hiển thị dưới dạng điểm sáng
- Kích thước điểm = GDP quốc gia
- Màu sắc = Hướng tăng trưởng (xanh = tăng, đỏ = giảm)
- Click vào quốc gia để xem chi tiết

### 2. **WORLD - Bản Đồ Toàn Cầu**
- Chế độ xem bản đồ 2D/3D
- Lưới quốc gia với thông tin kinh tế
- Tìm kiếm và lọc quốc gia

### 3. **MACRO - Kinh Tế Vĩ Mô**
- GDP Toàn Cầu
- Lạm Suất Trung Bình
- Thất Nghiệp Trung Bình
- Tổng Dân Số Thế Giới
- Biểu đồ theo thời gian thực

### 4. **MARKET - Thị Trường Tài Chính**
- **Chứng Khoán:** S&P 500, NASDAQ, DAX, NIKKEI, SSE, VN-INDEX
- **Forex:** USD/EUR, USD/GBP, USD/JPY, USD/CNY, USD/VND
- **Crypto:** BTC/USD, ETH/USD, BNB/USD
- **Hàng Hóa:** Vàng, Dầu, Khí Tự Nhiên
- Cập nhật giá theo giây
- Hiển thị xu hướng (+/- %)

### 5. **FLOW - Dòng Tiền Toàn Cầu**
- Visualize FDI (Foreign Direct Investment)
- Thương mại quốc tế
- Dòng vốn nóng
- Dự trữ vàng
- Vốn hóa thị trường crypto

### 6. **SETTINGS - Cài Đặt**
- Chế độ tối/sáng
- Hiệu ứng 3D
- Tần suất cập nhật dữ liệu
- Loại tiền tệ (USD, EUR, CNY, VND)

## 🏗️ Kiến Trúc Dự Án

```
WEOS/
├── index.html              # Trang chính HTML
├── css/
│   └── styles.css          # CSS styling (dark theme)
├── js/
│   ├── config.js           # Cấu hình chung
│   ├── countryData.js      # Dữ liệu 195 quốc gia
│   ├── dataManager.js      # Quản lý dữ liệu real-time
│   ├── visualization.js    # Globe 3D visualization
│   ├── ui.js               # Quản lý giao diện
│   └── main.js             # Entry point
├── _config.yml             # GitHub Pages config
├── .nojekyll               # Disable Jekyll
├── package.json            # NPM dependencies
└── README.md               # Documentation
```

## 🚀 Cách Sử Dụng

### Chạy trên GitHub Pages

1. Dự án đã được cấu hình sẵn cho GitHub Pages
2. Truy cập: `https://tristanahayhay-ship-it.github.io/WEOS/`
3. Hoặc clone local:

```bash
git clone https://github.com/tristanahayhay-ship-it/WEOS.git
cd WEOS
# Mở index.html trong trình duyệt
```

### Sử Dụng Giao Diện

**Thanh Menu (Bên Trái):**
- 🏠 **HOME** - Xem Globe 3D
- 🌍 **WORLD** - Bản đồ toàn cầu
- 📊 **MACRO** - Chỉ số kinh tế vĩ mô
- 📈 **MARKET** - Thị trường tài chính
- 💰 **FLOW** - Dòng tiền toàn cầu
- ⚙️ **SETTINGS** - Cài đặt

**Phím Tắt (Keyboard Shortcuts):**
- `Alt + H` - Trang chủ
- `Alt + W` - Bản đồ thế giới
- `Alt + M` - Kinh tế vĩ mô
- `Alt + +` - Zoom vào
- `Alt + -` - Zoom ra
- `Alt + R` - Reset view
- `Esc` - Đóng info panel

**Chuột (Mouse Controls):**
- **Drag** - Xoay globe
- **Scroll** - Zoom vào/ra
- **Click** - Chọn quốc gia

## 💾 Dữ Liệu

### Nguồn Dữ Liệu Real-Time

- **Chỉ số kinh tế:** World Bank API
- **Thị trường chứng khoán:** Yahoo Finance API
- **Forex:** Exchange Rate API
- **Crypto:** CoinGecko API
- **Tin tức:** News API

### Dữ Liệu Hiện Có

- 20+ quốc gia chính với dữ liệu chi tiết
- GDP, Tăng trưởng, Lạm suất, Thất nghiệp
- Dự trữ vàng
- Chỉ số thị trường
- Cập nhật mỗi giây

## 🛠️ Công Nghệ Sử Dụng

- **Frontend:** HTML5, CSS3, JavaScript (ES6+)
- **3D Globe:** [globe.gl](https://github.com/vasturiano/globe.gl) (Three.js)
- **Charts:** [Lightweight Charts](https://tradingview.github.io/lightweight-charts/)
- **Data:** REST APIs + Mock Data
- **Deployment:** GitHub Pages

## 📊 Cấu Trúc Dữ Liệu

### Country Data
```javascript
{
  name: 'Tên Quốc Gia',
  code: 'CODE',
  flag: '🇻🇳',
  gdp: 1000,              // Tỷ USD
  gdpGrowth: 2.5,         // %
  inflation: 3.2,         // %
  unemployment: 3.7,      // %
  population: 339,        // Triệu
  gdpPerCapita: 80600,    // USD
  golds: 261.5,           // Tấn
  fdi: 380,               // Tỷ USD
}
```

### Market Data
```javascript
{
  price: '5480.16',
  change: '2.45',         // %
  isPositive: true,
}
```

## 🎨 Giao Diện

### Bảng Màu
- **Background:** #0a0e27 (Dark Blue)
- **Primary Text:** #e0e6ff (Light Blue)
- **Accent 1:** #00d4ff (Cyan)
- **Accent 2:** #00ff88 (Green - Investment)
- **Accent 3:** #ff4444 (Red - Withdrawal)
- **Accent 4:** #ffa500 (Gold - Reserves)

### Responsive Design
- Desktop: Full layout với 3 cột
- Tablet: Sidebar thu gọn
- Mobile: Single column (Future upgrade)

## 📈 Kế Hoạch Phát Triển

### Phase 1 ✅ (Hiện Tại)
- [x] Globe 3D cơ bản
- [x] Menu điều hướng
- [x] Hiển thị dữ liệu quốc gia
- [x] Thị trường tài chính
- [x] Giao diện responsive

### Phase 2 🚧 (Sắp Tới)
- [ ] Kết nối API thực tế
- [ ] Biểu đồ theo thời gian thực
- [ ] Dòng tiền động (animated flows)
- [ ] Tìm kiếm quốc gia
- [ ] So sánh quốc gia

### Phase 3 📋 (Tương Lai)
- [ ] Chế độ sandbox (mô phỏng kinh tế)
- [ ] Export dữ liệu (CSV, JSON)
- [ ] Chia sẻ snapshot bản đồ
- [ ] Dashboard cá nhân
- [ ] API công khai

## 🔧 Phát Triển Cục Bộ

### Yêu Cầu
- Modern web browser (Chrome, Firefox, Safari, Edge)
- (Optional) Live Server extension

### Cài Đặt
```bash
# Clone repository
git clone https://github.com/tristanahayhay-ship-it/WEOS.git
cd WEOS

# Sử dụng Live Server
python -m http.server 8000
# Hoặc
php -S localhost:8000

# Mở http://localhost:8000
```

## 🐛 Troubleshooting

### Globe không hiển thị
- Kiểm tra console (F12) cho lỗi
- Đảm bảo Three.js được load
- Reload page (Ctrl + Shift + R)

### Dữ liệu không cập nhật
- Kiểm tra kết nối internet
- Mở DevTools > Network tab
- Kiểm tra CORS issues

### Hiệu suất chậm
- Giảm tần suất cập nhật (Settings)
- Vô hiệu hóa hiệu ứng 3D
- Sử dụng trình duyệt khác

## 📝 Ghi Chú

- Dữ liệu quốc gia hiện tại là mô phỏng
- Sẽ được thay thế bằng API thực tế
- Cập nhật theo thời gian thực mỗi giây
- Hỗ trợ tiếng Việt 100%

## 🤝 Đóng Góp

Nếu bạn muốn đóng góp vào dự án:

1. Fork repository
2. Tạo branch mới (`git checkout -b feature/YourFeature`)
3. Commit changes (`git commit -m 'Add YourFeature'`)
4. Push to branch (`git push origin feature/YourFeature`)
5. Open Pull Request

## 📄 License

MIT License - Xem file LICENSE để chi tiết

## 📧 Liên Hệ

- **Author:** tristanahayhay
- **Email:** tristanahayhay@gmail.com
- **GitHub:** https://github.com/tristanahayhay-ship-it

---

**Made with ❤️ for Global Economic Analysis**

🌍 *"Nhìn thấy dòng tiền toàn cầu chảy như máu của Trái Đất"* 💰
