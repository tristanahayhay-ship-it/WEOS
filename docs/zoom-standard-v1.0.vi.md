# Chuẩn zoom WEOS v1.0

## Mục tiêu
WEOS sử dụng 11 cấp zoom từ L0 đến L10 để ánh xạ cùng một mô hình dữ liệu vào nhiều lớp quan sát khác nhau. Chuẩn này giúp dashboard chuyển mượt giữa bức tranh vĩ mô và dữ liệu mô phỏng thời gian thực.

## Quy ước cấp độ
- **L0 Hệ thống**: chu kỳ thanh khoản, rủi ro và luồng vốn toàn cầu.
- **L1 Cụm vĩ mô**: các cụm Bắc Mỹ, Châu Âu, Đông Á, ASEAN, Trung Đông.
- **L2 Lục địa**: so sánh cân bằng tăng trưởng giữa lục địa.
- **L3 Quốc gia**: hồ sơ đầy đủ từng quốc gia, chỉ số vĩ mô lõi.
- **L4 Hành lang**: luồng cung ứng, logistics, nearshoring.
- **L5 Tỉnh**: cực sản xuất, cụm cảng, khu công nghiệp.
- **L6 Đô thị**: siêu đô thị, trung tâm tài chính, thành phố cảng.
- **L7 Định chế**: ngân hàng trung ương, sovereign fund, ngân hàng thương mại.
- **L8 Doanh nghiệp**: công ty dẫn dắt chuỗi cung ứng và vốn hóa.
- **L9 Cơ sở**: nhà máy, cảng, trung tâm dữ liệu, kho LNG.
- **L10 Thời gian thực**: tape giao dịch, sổ lệnh, FX, crypto, hàng hóa.

## Hành vi UI
1. Khi zoom tăng, panel chi tiết mở thêm nhóm metric thay vì thay toàn bộ layout.
2. Mọi chuyển cảnh cần giữ tối thiểu 60fps.
3. Các lớp dữ liệu mới xuất hiện theo nguyên tắc cộng dồn, tránh làm người dùng mất ngữ cảnh.
