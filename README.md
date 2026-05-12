# 🛒 Hệ thống Quản lý Bán hàng Đa kênh

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![OOP](https://img.shields.io/badge/Paradigm-OOP-green)
![Tkinter](https://img.shields.io/badge/UI-Tkinter-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Tests](https://img.shields.io/badge/Tests-Pytest-red)

**Đồ án nhóm – Môn Lập trình Python**  
*Xây dựng hệ thống quản lý bán hàng hoạt động trên nhiều kênh phân phối (online, offline, Shopee, Facebook, TikTok Shop)*

</div>

---

## 📋 Mục lục

- [Giới thiệu](#-giới-thiệu)
- [Kiến trúc & Công nghệ](#-kiến-trúc--công-nghệ)
- [Cấu trúc thư mục](#-cấu-trúc-thư-mục)
- [Nguyên lý OOP](#-nguyên-lý-oop-áp-dụng)
- [Hướng dẫn Cài đặt & Chạy](#-hướng-dẫn-cài-đặt--chạy)
- [Đóng gói file .exe](#-đóng-gói-file-exe)
- [Phân công Nhóm](#-phân-công-nhóm)
- [Ghi chú phát triển](#-ghi-chú-phát-triển)

---

## 🎯 Giới thiệu

**Hệ thống Quản lý Bán hàng Đa kênh** là một ứng dụng desktop Python giúp doanh nghiệp vừa và nhỏ quản lý toàn bộ hoạt động bán hàng tập trung tại một nơi, bất kể nguồn đơn hàng đến từ kênh nào.

### Tính năng cốt lõi

| Tính năng | Mô tả |
|-----------|-------|
| 📦 **Quản lý Sản phẩm** | Thêm, sửa, xóa, tìm kiếm sản phẩm; theo dõi tồn kho theo kênh |
| 👥 **Quản lý Khách hàng** | CRM cơ bản, tích lũy điểm thành viên, lịch sử mua hàng |
| 🧾 **Quản lý Đơn hàng** | Tạo đơn, theo dõi trạng thái, doanh thu theo kênh |
| 📊 **Báo cáo** | Thống kê tổng quan, xuất CSV/TXT |
| 💾 **Lưu trữ File** | JSON / CSV / TXT – không phụ thuộc database |
| 🛡️ **Xử lý lỗi** | Exception handling toàn diện ở mọi thao tác file |

### Kênh bán hàng hỗ trợ

`Online` · `Offline` · `Facebook` · `Shopee` · `TikTok Shop`

---

## 🏗️ Kiến trúc & Công nghệ

### Công nghệ sử dụng

| Công nghệ | Phiên bản | Mục đích |
|-----------|-----------|----------|
| **Python** | ≥ 3.11 | Ngôn ngữ lập trình chính |
| **Tkinter** | Built-in | Giao diện người dùng desktop |
| **json** | Built-in | Lưu trữ dữ liệu chính |
| **csv** | Built-in | Xuất/nhập dữ liệu bảng tính |
| **abc** | Built-in | Abstract Base Class |
| **pathlib** | Built-in | Xử lý đường dẫn file đa nền tảng |
| **logging** | Built-in | Ghi nhật ký hệ thống |
| **pytest** | ≥ 7.0 | Unit testing |
| **PyInstaller** | ≥ 6.0 | Đóng gói thành file .exe |

> ⚠️ **Lưu ý quan trọng**: Dự án **KHÔNG** sử dụng bất kỳ hệ quản trị CSDL nào (SQLite, MySQL...).  
> Toàn bộ dữ liệu được lưu trữ và xử lý thông qua các file JSON/CSV/TXT.

---

## 📁 Cấu trúc thư mục

```
omnichannel-sales-management/
│
├── main.py                          # 🚀 Điểm khởi động ứng dụng
│
├── models/                          # 📐 Tầng Mô hình dữ liệu (Data Layer)
│   ├── __init__.py
│   ├── product.py                   #   → Class Product (Sản phẩm)
│   ├── customer.py                  #   → Class Customer (Khách hàng)
│   └── order.py                     #   → Class Order + OrderItem (Đơn hàng)
│
├── file_handlers/                   # 💾 Tầng Xử lý File (File I/O Layer)
│   ├── __init__.py
│   ├── base_handler.py              #   → Abstract Base Class (ABC)
│   ├── json_handler.py              #   → JsonHandler (kế thừa BaseFileHandler)
│   ├── csv_handler.py               #   → CsvHandler  (kế thừa BaseFileHandler)
│   ├── txt_handler.py               #   → TxtHandler  (kế thừa BaseFileHandler)
│   └── factory.py                   #   → FileHandlerFactory (Factory Pattern)
│
├── data_processing/                 # ⚙️ Tầng Nghiệp vụ (Business Logic Layer)
│   ├── __init__.py
│   ├── base_manager.py              #   → BaseManager (Template Method Pattern)
│   ├── product_manager.py           #   → ProductManager (CRUD + tồn kho)
│   ├── customer_manager.py          #   → CustomerManager (CRUD + điểm tích lũy)
│   └── order_manager.py             #   → OrderManager (CRUD + luồng trạng thái)
│
├── ui/                              # 🖥️ Tầng Giao diện (Presentation Layer)
│   ├── __init__.py
│   └── main_window.py               #   → MainWindow Tkinter (Thành viên 2)
│
├── utils/                           # 🔧 Tiện ích dùng chung
│   ├── __init__.py
│   ├── helpers.py                   #   → generate_id, format_currency, timestamp
│   └── validators.py                #   → validate_email, validate_phone, validate_price
│
├── tests/                           # ✅ Unit Tests
│   ├── __init__.py
│   ├── test_models.py               #   → Tests cho Product, Customer, Order
│   └── test_file_handlers.py        #   → Tests cho Handlers + Factory
│
├── data/                            # 📂 Thư mục lưu file dữ liệu (tự tạo khi chạy)
│   ├── products.json
│   ├── customers.json
│   └── orders.json
│
├── logs/                            # 📝 Log file ứng dụng (tự tạo khi chạy)
│   └── app.log
│
├── exports/                         # 📤 File xuất báo cáo
├── assets/                          # 🖼️ Tài nguyên (icon, ảnh)
│
├── requirements.txt                 # 📦 Danh sách thư viện cần cài
├── build.bat                        # 🔨 Script đóng gói (Windows)
├── build.sh                         # 🔨 Script đóng gói (Linux/macOS)
└── README.md                        # 📖 Tài liệu dự án
```

---

## 🧩 Nguyên lý OOP áp dụng

### 1. Encapsulation (Bao đóng) — `models/`

```python
class Product:
    def __init__(self, name, price, quantity):
        self.__name = name        # Private attribute (name mangling)
        self.__price = price
        self.__quantity = quantity

    @property
    def price(self):              # Getter
        return self.__price

    @price.setter
    def price(self, value):       # Setter với validation
        if value < 0:
            raise ValueError("Giá phải >= 0")
        self.__price = float(value)
```

### 2. Abstraction (Trừu tượng hóa) — `file_handlers/base_handler.py`

```python
from abc import ABC, abstractmethod

class BaseFileHandler(ABC):
    @abstractmethod
    def read(self) -> Any: ...   # Buộc lớp con phải triển khai

    @abstractmethod
    def write(self, data) -> bool: ...
```

### 3. Inheritance + Override — `file_handlers/`

```python
class JsonHandler(BaseFileHandler):   # Kế thừa
    def read(self):                   # Ghi đè (Override)
        with open(self._file_path) as f:
            return json.load(f)

class CsvHandler(BaseFileHandler):    # Kế thừa
    def read(self):                   # Ghi đè (Override)
        ...
```

### 4. Polymorphism (Đa hình) — `file_handlers/factory.py`

```python
handler = FileHandlerFactory.get_handler("data.json")  # → JsonHandler
handler = FileHandlerFactory.get_handler("data.csv")   # → CsvHandler
# Gọi handler.read() giống nhau, hành vi khác nhau = ĐA HÌNH
data = handler.read()
```

### 5. Composition — `models/order.py`

```python
class Order:
    def __init__(self, ...):
        self.__items: list[OrderItem] = []  # Order HAS-A OrderItem
```

### 6. Template Method Pattern — `data_processing/base_manager.py`

```python
class BaseManager:
    def add(self, entity):          # Template method (khung CRUD)
        entities = self._load_all()
        entities.append(entity)
        return self._save_all(entities)

class ProductManager(BaseManager):
    def _from_dict(self, data):     # Hook method (lớp con điền vào)
        return Product.from_dict(data)
```

---

## 🚀 Hướng dẫn Cài đặt & Chạy

### Yêu cầu hệ thống

- **Python** ≥ 3.11 ([tải tại python.org](https://www.python.org/downloads/))
- **Windows 10/11** (hoặc Ubuntu 20.04+, macOS 12+)

### Bước 1 — Clone dự án

```bash
git clone https://github.com/your-username/omnichannel-sales-management.git
cd omnichannel-sales-management
```

### Bước 2 — Tạo môi trường ảo (khuyến nghị)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### Bước 3 — Cài đặt thư viện

```bash
pip install -r requirements.txt
```

> Toàn bộ thư viện cốt lõi (tkinter, json, csv, logging, pathlib) là **built-in**,  
> chỉ cần cài thêm `pytest` và `pyinstaller` cho dev.

### Bước 4 — Chạy ứng dụng

```bash
python main.py
```

### Bước 5 — Chạy Unit Tests

```bash
# Chạy toàn bộ test
python -m pytest tests/ -v

# Chạy test của module cụ thể
python -m pytest tests/test_models.py -v
python -m pytest tests/test_file_handlers.py -v

# Xem coverage
python -m pytest tests/ -v --tb=short
```

---

## 🔨 Đóng gói file .exe

### Windows

```cmd
# Cách 1: Chạy script tự động
build.bat

# Cách 2: Thủ công
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name "OmnichannelSales" main.py
```

### Linux / macOS

```bash
chmod +x build.sh
./build.sh
```

### Kết quả

File thực thi sẽ nằm tại: `dist/OmnichannelSales.exe`

**Lưu ý khi phân phối:** Copy cả thư mục `data/`, `assets/` vào cùng thư mục với file `.exe`.

---

## 👥 Phân công Nhóm

| Thành viên | Vai trò | Nhiệm vụ cụ thể |
|------------|---------|-----------------|
| **Thành viên 1** | 🏗️ **Kiến trúc hệ thống & Xử lý File** | • Thiết kế toàn bộ cấu trúc dự án (project structure)<br>• Xây dựng Data Models: `Product`, `Customer`, `Order` (OOP + Encapsulation)<br>• Xây dựng module `file_handlers/` (ABC, Kế thừa, Override, Factory Pattern)<br>• Viết `BaseManager` và 3 Manager classes<br>• Viết Unit Tests (`pytest`)<br>• Script đóng gói PyInstaller, README |
| **Thành viên 2** | 🖥️ **UI Tkinter & Quản lý người dùng** | • Thiết kế và xây dựng giao diện `ui/` với Tkinter<br>• Màn hình: Đăng nhập, Dashboard, Quản lý SP, Quản lý KH<br>• Form thêm/sửa/xóa, bảng dữ liệu, tìm kiếm<br>• Xử lý sự kiện, validation đầu vào UI<br>• Tích hợp với `data_processing/` để thao tác dữ liệu |
| **Thành viên 3** | 💼 **Nghiệp vụ Bán hàng & Dữ liệu** | • Màn hình quản lý Đơn hàng và luồng xử lý<br>• Nghiệp vụ: tạo đơn, duyệt đơn, giao hàng, hoàn thành<br>• Module báo cáo và thống kê doanh thu<br>• Tích hợp dữ liệu đa kênh (Shopee, FB, TikTok)<br>• Xuất báo cáo CSV/TXT, biểu đồ (nếu có) |

---

## 📝 Ghi chú phát triển

### Luồng dữ liệu

```
UI (Tkinter)
    ↕ gọi phương thức
Manager (ProductManager / CustomerManager / OrderManager)
    ↕ kế thừa từ BaseManager
BaseManager._load_all() / _save_all()
    ↕ sử dụng
FileHandlerFactory → JsonHandler / CsvHandler / TxtHandler
    ↕ đọc/ghi
File hệ thống (data/*.json)
```

### Luồng trạng thái đơn hàng

```
pending → confirmed → shipping → completed
    ↘          ↘           ↘
              cancelled
```

### Thêm định dạng file mới (Open/Closed Principle)

```python
# Không cần sửa code hiện có, chỉ đăng ký thêm:
from file_handlers.factory import FileHandlerFactory
from my_xml_handler import XmlHandler

FileHandlerFactory.register_handler(".xml", XmlHandler)
# Từ đây factory.get_handler("data.xml") sẽ dùng XmlHandler
```

---

<div align="center">

**Nhóm 3 – Môn Lập trình Python**  
*Học kỳ 2 – Năm học 2025–2026*

</div>
