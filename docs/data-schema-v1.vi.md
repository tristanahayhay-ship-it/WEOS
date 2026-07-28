# Lược đồ dữ liệu WEOS v1

## Thực thể chính
`GeoEntity` là đối tượng hạt nhân cho tất cả lớp địa lý và tổ chức. Trường bắt buộc gồm:
- `id`, `type`, `name`, `code`
- `continent`, `coordinates`
- `economicHealth`, `description`, `population`, `color`
- `coreMetrics`
- `metricGroups`

## Dòng vốn
`CapitalFlow` mô tả hành lang vốn giữa hai thực thể:
- `from`, `to`
- `value` (tỷ USD)
- `direction`, `speed`, `category`
- `timestamp`

## Tín hiệu thời gian thực
- `TickerRow`: bảng giá cổ phiếu mô phỏng.
- `ForexRow`: tỷ giá ngoại hối.
- `CommodityRow`: crypto hoặc hàng hóa.
- `TradeFeedItem`: tape giao dịch và logistics.
- `OrderBookLevel`: sổ lệnh hai chiều.

## Nội dung AI
- `AIInsight`: nhận định, độ tin cậy, hướng tín hiệu.
- `AlertItem`: cảnh báo có thể xác nhận.
- `NewsItem`: nguồn tin, khu vực tác động, mức ảnh hưởng.

## Nhóm chỉ tiêu
WEOS chuẩn hóa 20 nhóm metric cho mỗi quốc gia: GDP, tăng trưởng, lạm phát, lao động, lãi suất, thương mại, dòng vốn, ngân hàng, sản xuất, dịch vụ, tiêu dùng, năng lượng, logistics, tài khóa, nợ công, đổi mới, kinh tế số, chuyển dịch xanh, ổn định hệ thống, tâm lý thị trường.
