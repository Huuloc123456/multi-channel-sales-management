# Omnichannel Sales Management V2 (File, Random & Sys Only)

Phiên bản rút gọn, tinh chỉnh của Hệ thống Quản lý Bán hàng Đa kênh, tập trung 100% vào việc thực thi xử lý file dữ liệu đa định dạng, áp dụng các nguyên lý lập trình hướng đối tượng (OOP) và sử dụng linh hoạt các thư viện chuẩn `random` và `sys`.

## 📌 Thành phần Project
Dự án được tinh giản chỉ bao gồm các thành phần cốt lõi:
- **`models/`**: Khai báo các thực thể dữ liệu hướng đối tượng (`Product`, `Customer`, `Order`, `OrderItem`).
- **`file_handlers/`**: Module chịu trách nhiệm đọc/ghi dữ liệu có cấu trúc từ các tệp tin CSV, JSON và plain text TXT thông qua mẫu thiết kế **Factory Pattern** linh hoạt.
- **`utils/`**: Bộ công cụ kiểm chuẩn định dạng (email, số điện thoại, giá cả) và sinh mã định danh duy nhất (UUID).
- **`main.py`**: Điểm nhập dữ liệu, kết hợp giả lập sinh dữ liệu đa kênh (`random`) và giao diện CLI điều khiển luồng (`sys`).

---

## 🚀 Hướng dẫn Sử dụng

Chương trình hỗ trợ cả **Giao diện Dòng lệnh Tương tác (Interactive CLI)** và các **Tham số Dòng lệnh trực tiếp (CLI Command)**:

### 1. Giao diện Tương tác CLI
Để khởi động menu tương tác, chỉ cần chạy lệnh sau:
```bash
python main.py
```
Menu sẽ hiển thị các lựa chọn cho phép bạn:
- Sinh và lưu trữ dữ liệu ngẫu nhiên mới (CSV/JSON).
- Đọc file dữ liệu và xuất báo cáo kinh doanh tổng hợp ra định dạng bảng TXT đẹp mắt.
- Khởi chạy kiểm thử tự động toàn diện.
- Xem thông tin cấu hình phần cứng và hệ thống (thông qua `sys` module).

### 2. Các tham số dòng lệnh nhanh (CLI Commands)
Bạn có thể bỏ qua giao diện tương tác và ra lệnh trực tiếp cho chương trình:

- **Giả lập dữ liệu ngẫu nhiên mới**:
  ```bash
  # Cú pháp: python main.py generate [số_lượng_sp] [số_lượng_kh] [số_lượng_đơn]
  python main.py generate 15 8 25
  ```
- **Tổng hợp dữ liệu và xuất báo cáo kinh doanh**:
  ```bash
  python main.py report
  ```
- **Khởi chạy quy trình kiểm thử đầu cuối tự động**:
  ```bash
  python main.py test
  ```
- **Xem hướng dẫn nhanh**:
  ```bash
  python main.py help
  ```

---

## 🛠️ Thiết kế Kỹ thuật cốt lõi

### 1. Xử lý File Đa định dạng (Factory Pattern & Polymorphism)
Nhờ vào mẫu thiết kế Factory, hệ thống tự động xác định trình xử lý file dựa trên phần mở rộng (`.json`, `.csv`, `.txt`):
- **JSON**: Dùng để lưu trữ thông tin sản phẩm và cấu trúc đơn hàng lồng nhau (OrderItem composition).
- **CSV**: Dùng để quản lý thông tin khách hàng, thuận tiện cho việc import/export sang Excel.
- **TXT**: Dùng để ghi nhận logs hệ thống và biên soạn báo cáo bán hàng dạng bảng ASCII.

### 2. Module `random` trong Giả lập Thực tế
Module `random` được ứng dụng để mô phỏng chính xác các hoạt động kinh doanh thực tế:
- Sinh ngẫu nhiên dữ liệu khách hàng với email không dấu hợp lệ và số điện thoại Việt Nam khớp regex kiểm chuẩn.
- Sinh ngẫu nhiên đơn hàng đa kênh (Lazada, Shopee, TikTok, Facebook, Offline) với số lượng sản phẩm, tỷ lệ giảm giá chiết khấu và ghi chú khác nhau.

### 3. Module `sys` trong Quản trị Luồng
Hệ thống sử dụng module `sys` để:
- Điều khiển thoát chương trình an toàn (`sys.exit()`).
- Phân tích và xử lý tham số dòng lệnh CLI (`sys.argv`).
- Thiết lập lại encoding đầu ra của terminal thành UTF-8 đảm bảo hiển thị tiếng Việt có dấu chuẩn xác nhất trên mọi hệ điều hành.
