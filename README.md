# WEOS — World Economic Operating System

WEOS là ứng dụng Vite + React + TypeScript mô phỏng **Digital Twin of the Global Economy**: một bảng điều khiển tối màu, phong cách neon, hiển thị bản đồ tương tác 2D/3D cùng các tín hiệu vĩ mô và dữ liệu mô phỏng thời gian thực.

## Tính năng chính
- Giao diện tiếng Việt, dark theme và glassmorphism.
- Bản đồ 2D bằng MapLibre GL với đa giác quốc gia và hành lang dòng vốn.
- Bản đồ 3D bằng deck.gl ở chế độ globe.
- 11 cấp zoom từ L0 đến L10, chuyển từ toàn cảnh hệ thống sang mô phỏng tape giao dịch.
- Sidebar trái/phải cho chỉ số thị trường, lịch kinh tế, nhận định AI, cảnh báo và news feed.
- Panel thời gian thực với ticker, FX, crypto, hàng hóa, trade feed và order book.
- Workflow triển khai GitHub Pages tại `.github/workflows/deploy.yml`.

## Cấu trúc
- `src/data/mockData.ts`: dữ liệu mẫu cho quốc gia, dòng vốn, tin tức, cảnh báo.
- `src/store/useStore.ts`: Zustand store điều phối zoom, chế độ bản đồ và cảnh báo.
- `src/components/`: layout, map, panel và UI components.
- `docs/*.vi.md`: chuẩn zoom, schema dữ liệu và tương tác UI.

## Chạy cục bộ
```bash
npm install
npm run dev
```

## Build production
```bash
npm run build
```

## Deploy GitHub Pages
Ứng dụng đã cấu hình `base: '/WEOS/'` trong `vite.config.ts` và workflow Pages tự động build/deploy khi push lên nhánh `main`.
