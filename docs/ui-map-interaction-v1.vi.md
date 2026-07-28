# Quy chuẩn tương tác UI bản đồ WEOS v1

## Mô hình tương tác
1. **Click quốc gia**: chọn thực thể, đồng bộ panel chi tiết.
2. **Toggle 2D/3D**: đổi engine hiển thị nhưng giữ nguyên ngữ cảnh zoom và thực thể được chọn.
3. **Footer zoom**: điều hướng trực tiếp từ L0 đến L10.
4. **Map animation**: overlay canvas chỉ mang tính tín hiệu thị giác, không can thiệp sự kiện pointer.

## Nguyên tắc thiết kế
- Chủ đề tối, neon cyan/green làm màu dẫn hướng.
- Panel dùng glassmorphism, bo tròn lớn, viền cyan mờ.
- Thông tin chính luôn hiển thị bằng tiếng Việt.
- Ưu tiên đọc nhanh: nhãn ngắn, số lớn, trạng thái màu rõ.

## Hiệu năng
- Chỉ render dữ liệu 3D cần thiết.
- Dùng memo cho lớp bản đồ và panel tính toán nặng.
- Tránh animation DOM dày đặc, ưu tiên canvas hoặc WebGL.
