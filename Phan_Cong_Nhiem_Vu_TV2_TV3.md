# 📋 PHÂN CÔNG NHIỆM VỤ DỰ ÁN: HỆ THỐNG QUẢN LÝ BÁN HÀNG ĐA KÊNH

**Vai trò:** Project Manager / Tech Lead (Thành viên 1)
**Dự án:** Hệ thống quản lý bán hàng đa kênh (Python OOP + Tkinter + File Storage)

---

## 🌟 TỔNG QUAN HIỆN TRẠNG (Dành cho toàn team)

Dự án của chúng ta áp dụng **triệt để lập trình hướng đối tượng (OOP)** và **TUYỆT ĐỐI KHÔNG sử dụng Hệ quản trị cơ sở dữ liệu** (chỉ lưu trữ bằng file JSON, CSV, TXT).

**Thành viên 1 (Tech Lead)** đã hoàn thiện xong **Kiến trúc cốt lõi** bao gồm:

1. **Các lớp Đối tượng (Data Models)**: `Product`, `Customer`, `Order`, `OrderItem`.
2. **Module Xử lý File**: `FileHandlerFactory`, `JsonHandler`, `CsvHandler`, `TxtHandler`.
3. **Module Xử lý Nghiệp vụ (Managers)**: `ProductManager`, `CustomerManager`, `OrderManager` (Cung cấp sẵn các hàm tương đương `read_data` và `write_data` qua các phương thức CRUD chuẩn mực như `get_all()`, `add()`, `update()`, `delete()`).
4. **Tiện ích (Utils)**: Format tiền tệ, tạo ID, hàm validate email/SĐT...

> ⚠️ **QUY TẮC TỐI THƯỢNG:**
> Cả Thành viên 2 và Thành viên 3 **KHÔNG ĐƯỢC PHÉP** tự viết code đọc/ghi file trực tiếp (như dùng `open()`, `json.dump()`). Tất cả thao tác truy xuất dữ liệu **BẮT BUỘC** phải gọi qua các class Manager (`ProductManager`, `CustomerManager`, `OrderManager`) mà Thành viên 1 đã cung cấp.

---

## 👨‍💻 PHẦN 1: NHIỆM VỤ CỦA THÀNH VIÊN 2

**Mục tiêu:** Xây dựng UI (Tkinter) & Quản trị Người dùng

### 🎯 Nhiệm vụ cụ thể

* **Khung giao diện chính (Main Window):** Thiết kế thanh Menu điều hướng, thanh trạng thái và bố cục tab (hiện tại file `ui/main_window.py` đã có sẵn bộ khung cơ bản, bạn cần phát triển thêm).
* **Form Đăng nhập / Quản trị:** Tạo màn hình đăng nhập cơ bản để cấp quyền truy cập hệ thống.
* **Màn hình Quản lý Sản phẩm & Khách hàng:**
  * Thiết kế giao diện danh sách (Treeview/Bảng) để hiển thị thông tin.
  * Tạo các form **Thêm / Sửa / Xóa (CRUD)** cho Sản phẩm và Khách hàng.
  * **Kiểm tra tính hợp lệ (Validate) dữ liệu đầu vào** trực tiếp trên giao diện trước khi lưu (Nên tận dụng các hàm trong `utils/validators.py`).

### ⚙️ Quy tắc tích hợp (BẮT BUỘC)

* **Giao diện KHÔNG tự ý xử lý file.**
* **Khi cần hiển thị dữ liệu:** Khởi tạo các Manager tương ứng (VD: `manager = ProductManager()`) và gọi hàm `manager.get_all()` hoặc `manager.search()` (tương đương `read_data()`) để lấy danh sách đối tượng, sau đó parse lên Treeview Tkinter.
* **Khi người dùng bấm "Lưu":** Giao diện phải trích xuất dữ liệu từ các ô nhập liệu, đóng gói thành các **Object** (`Product`, `Customer`) rồi truyền vào hàm `manager.add()` hoặc `manager.update()` (tương đương `write_data()`) để lưu xuống file an toàn.

---> Nhìn vào ảnh ở asset/images để nắm rõ giao diện

---

## 👨‍💻 PHẦN 2: NHIỆM VỤ CỦA THÀNH VIÊN 3

**Mục tiêu:** Nghiệp vụ Bán hàng & Tích hợp Dữ liệu (API/Crawl)

### 🎯 Nhiệm vụ cụ thể

* **Luồng Bán hàng (POS / Tạo đơn):**
  * Viết logic chọn sản phẩm, thêm vào giỏ hàng (khởi tạo các đối tượng `OrderItem`).
  * Tính toán **tổng tiền**, áp dụng **giảm giá** (nếu có).
  * Xuất hóa đơn cho khách hàng (có thể sử dụng `TxtHandler` với hàm `write_report()` để in bill ra file txt).
* **Tích hợp Dữ liệu mẫu (Crawl / API):**
  * Viết script thực hiện gọi API hoặc Crawl dữ liệu (sản phẩm mẫu) từ một nguồn trên Internet để làm giàu kho dữ liệu của hệ thống.

### ⚙️ Quy tắc tích hợp (BẮT BUỘC)

* **Xử lý dữ liệu ngoại lai:** Khi lấy được chuỗi JSON rác từ quá trình API/Crawl, bạn **phải bóc tách và ép kiểu** mớ dữ liệu đó thành danh sách các đối tượng `Product` hợp lệ theo đúng khuôn mẫu Thành viên 1 định nghĩa.
* **Lưu kho:** Dùng File Handler của Thành viên 1 (cụ thể là gọi `ProductManager().add(product)`) để lưu các đối tượng vừa tạo vào kho hệ thống.
* **Chốt đơn:** Khi đơn hàng hoàn tất, phải khởi tạo đối tượng `Order` (chứa danh sách các `OrderItem`), sau đó gọi `OrderManager().add(order)` để ghi xuống file lịch sử giao dịch một cách chuẩn xác.

## 📑 PHẦN 3: TIÊU CHUẨN BÁO CÁO CHUNG

Để chuẩn bị tốt nhất cho buổi bảo vệ đồ án, yêu cầu các thành viên hoàn thành thêm các tài liệu sau:

* **Thành viên 2:** Chuẩn bị **Slide PowerPoint**, tập trung chụp ảnh và trình bày về kiến trúc **giao diện (UI/UX)**, cách điều hướng và tính tiện dụng của ứng dụng.
* **Thành viên 3:** Tổng hợp nội dung **Báo cáo Word**.

> Mọi người bắt tay vào code ở nhánh riêng và pull request khi hoàn thành từng module nhỏ nhé. Cần hỗ trợ về các hàm Manager hay Object Model cứ báo mình!
