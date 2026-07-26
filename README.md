# 🌍 WEOS - World Economic Operating System

**Bản đồ kinh tế vĩ mô thế giới thời gian thực** — dòng tiền toàn cầu trực quan hóa trên địa cầu 3D.

[![Deploy to GitHub Pages](https://github.com/tristanahayhay-ship-it/WEOS/actions/workflows/deploy.yml/badge.svg)](https://github.com/tristanahayhay-ship-it/WEOS/actions/workflows/deploy.yml)

---

## 🔴 Live Demo

**[→ Xem bản đồ tại đây](https://tristanahayhay-ship-it.github.io/WEOS/)**

---

## 🩸 Tính năng

| Tính năng | Mô tả |
|-----------|-------|
| 🌍 **Globe 3D** | Địa cầu đêm NASA, nền vũ trụ đen, xoay tự động |
| 🩸 **Mạch máu dòng tiền** | Arc lines xanh/đỏ chạy động từ 195 quốc gia về Washington DC |
| 📊 **DXY Realtime** | Chỉ số sức mạnh USD từ API tỷ giá |
| 🎛️ **USD Slider** | Kéo thay đổi DXY → globe cập nhật dòng tiền ngay lập tức |
| 💰 **195 quốc gia** | Màu theo GDP tier, dự trữ vàng, tương quan USD |
| 🔍 **Zoom levels** | Global → Region → Country → City → Micro |
| 📡 **Dữ liệu thật** | Forex, Bitcoin, Ethereum, Vàng cập nhật mỗi 10-15 giây |
| 🇻🇳 **Tiếng Việt** | Toàn bộ giao diện tiếng Việt |

---

## 🎨 Đọc bản đồ

```
🟢 Đường XANH = Tiền đang VÀO (đầu tư, FDI, vốn chảy đến)
🔴 Đường ĐỎ   = Tiền đang RA  (tháo vốn, flee to safety)

Độ dày đường = Lượng vốn (to = nhiều tiền)
Tốc độ chạy  = Mức độ khẩn cấp (nhanh = đang gấp rút)
```

### Màu quốc gia:
| Màu | Ý nghĩa |
|-----|---------|
| 🔵 Xanh đậm | G7 / Phát triển (US, DE, JP, GB...) |
| 🟢 Xanh lá | BRICS / Mới nổi lớn (CN, IN, BR, RU...) |
| 🟡 Vàng đất | Thị trường mới nổi (VN, TH, MY...) |
| 🔴 Đỏ đậm | Thị trường biên giới |

---

## 💡 Khi USD MẠNH (DXY > 104)

```
🔴 Vốn tháo khỏi: Châu Á mới nổi, EM Bonds, Vàng, Crypto
🟢 Tiền chảy về: US Treasury, USD Cash, S&P 500
```

## 💡 Khi USD YẾU (DXY < 100)

```
🟢 Vốn chảy vào: Vàng, Bitcoin, EM Stocks, Dầu thô, Hàng hóa
🔴 Rút khỏi: Trái phiếu USD, Giảm dự trữ USD
```

---

## 🛠️ Tech Stack

- **[globe.gl](https://globe.gl)** — 3D WebGL globe
- **Three.js** — 3D rendering
- **D3.js** — data utilities
- **Vanilla JS** — không cần build tool
- **GitHub Pages** — hosting miễn phí

---

## 📡 APIs sử dụng (miễn phí, không cần key)

| API | Dữ liệu | Tần suất |
|-----|---------|----------|
| [open.er-api.com](https://open.er-api.com) | Tỷ giá 195 đồng tiền | 10 giây |
| [CoinGecko](https://coingecko.com/api) | Bitcoin, Ethereum, Vàng | 15 giây |
| [Natural Earth](https://github.com/nvkelso/natural-earth-vector) | GeoJSON 195 nước | 1 lần |
| Mock data | Dầu, S&P500, fallback | Tĩnh |

---

## 🚀 Deploy tự động

Mỗi khi push lên branch `main`, GitHub Actions tự deploy lên GitHub Pages.

```
main branch → GitHub Actions → GitHub Pages
```

---

## 📁 Cấu trúc file

```
WEOS/
├── index.html           # Entry point
├── css/
│   ├── main.css         # Core styles, dark theme
│   └── panels.css       # Dashboard, popup, controls
├── js/
│   ├── app.js           # Main orchestrator
│   ├── data/
│   │   ├── countries.js  # 195 quốc gia
│   │   ├── usdLogic.js   # Logic dòng tiền USD
│   │   └── mockData.js   # Fallback data
│   ├── globe/
│   │   ├── globeInit.js  # Globe.gl setup
│   │   ├── flowArcs.js   # Arc animations
│   │   ├── countryColors.js
│   │   └── zoomLevels.js
│   ├── api/
│   │   ├── dataManager.js
│   │   ├── forex.js
│   │   ├── crypto.js
│   │   └── commodities.js
│   └── ui/
│       ├── dashboard.js
│       ├── countryPopup.js
│       ├── usdMeter.js
│       └── controls.js
└── .github/
    └── workflows/
        └── deploy.yml
```

---

## 🧠 Logic kinh tế

Dự án mô phỏng cơ chế **"Petrodollar recycling"** và **"Dollar Milkshake Theory"**:

1. **USD mạnh** → Lãi suất Mỹ cao → Vốn quốc tế mua Treasury → EM bị rút vốn → Đồng tiền EM mất giá
2. **USD yếu** → Fed cắt lãi suất → Vốn tìm yield cao hơn → EM, Vàng, Crypto hút tiền
3. **Dầu mỏ** luôn định giá bằng USD → Quốc gia dầu mỏ tích lũy USD → "Petrodollar recycling" về Treasury Mỹ

---

*Made with ❤️ for financial education | Dữ liệu chỉ mang tính tham khảo, không phải lời khuyên đầu tư*
