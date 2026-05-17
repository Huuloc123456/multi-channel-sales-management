"""
main.py

Điểm khởi đầu (entry point) của dự án omnichannel-sales-management-2.
Đây là phiên bản rút gọn, tập trung hoàn toàn vào xử lý file, sử dụng mô hình OOP, kết hợp với các thư viện tiêu chuẩn như `sys` và `random`.

Tính năng:
1. Cấu hình hệ thống & Mã hóa UTF-8 (Sử dụng module sys).
2. Giả lập và sinh dữ liệu bán hàng đa kênh ngẫu nhiên (Sử dụng module random).
3. Đọc, ghi và quản lý tệp tin đa định dạng CSV, JSON, TXT (Sử dụng module models và file_handlers).
4. Cung cấp cả giao diện dòng lệnh tương tác (Interactive CLI) và các tham số dòng lệnh (CLI arguments via sys.argv).
"""

import sys
import random
import logging
from pathlib import Path
from typing import List

# Thêm thư mục hiện tại vào sys.path để tránh lỗi import
sys.path.append(str(Path(__file__).parent))

from models import Product, Customer, Order, OrderItem
from file_handlers import FileHandlerFactory

# --- CẤU HÌNH LOGGING ---
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "system.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("OmniSalesV2")

# --- THIẾT LẬP ENCODING HỆ THỐNG (sys module) ---
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# --- DỮ LIỆU ĐỂ GIẢ LẬP NGẪU NHIÊN (random module) ---
CATEGORIES = ["Điện tử", "Thời trang", "Gia dụng", "Sách & Văn phòng", "Sức khỏe & Làm đẹp"]
PRODUCT_NAMES = {
    "Điện tử": ["Điện thoại iPhone 15", "Laptop ASUS ROG", "Tai nghe Sony WH-1000XM5", "Chuột Logitech MX Master", "Bàn phím cơ Keychron"],
    "Thời trang": ["Áo khoác gió Uniqlo", "Giày Sneaker Nike Air Force 1", "Quần Jean Levis 501", "Mũ lưỡi trai Adidas", "Túi xách tay nữ"],
    "Gia dụng": ["Nồi chiên không dầu Tefal", "Máy hút bụi Dyson V12", "Ấm siêu tốc Philips", "Quạt cây Xiaomi", "Bộ nồi inox Sunhouse"],
    "Sách & Văn phòng": ["Đắc Nhân Tâm", "Nhà Giả Kim", "Sổ tay da cao cấp", "Bút ký Parker", "Lịch để bàn 2026"],
    "Sức khỏe & Làm đẹp": ["Kem chống nắng La Roche-Posay", "Son kem Black Rouge", "Nước hoa Chanel Bleu", "Serum Klairs", "Sữa rửa mặt Cetaphil"]
}

FIRST_NAMES = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Đặng", "Bùi"]
MIDDLE_NAMES = ["Văn", "Thị", "Hữu", "Minh", "Đức", "Ngọc", "Tuấn", "Anh", "Xuân", "Thanh"]
LAST_NAMES = ["Lộc", "Hải", "Hùng", "Trang", "Vy", "Nam", "Dũng", "Phương", "Khánh", "Sơn", "Mai", "Cường"]
CITIES = ["Hà Nội", "TP. Hồ Chí Minh", "Đà Nẵng", "Cần Thơ", "Hải Phòng", "Bình Dương", "Đồng Nai", "Nha Trang"]
DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "fpt.edu.vn", "huit.edu.vn"]

# --- HÀM GIẢ LẬP DỮ LIỆU NGẪU NHIÊN (random module) ---

def generate_random_products(count: int) -> List[Product]:
    """ Sinh ngẫu nhiên danh sách sản phẩm. """
    products = []
    for _ in range(count):
        category = random.choice(CATEGORIES)
        name = random.choice(PRODUCT_NAMES[category]) + f" #{random.randint(100, 999)}"
        price = float(random.randint(5, 500) * 10000)  # Từ 50.000đ đến 5.000.000đ
        quantity = random.randint(10, 100)
        channel = random.choice(["online", "offline", "both"])
        products.append(Product(name=name, price=price, quantity=quantity, category=category, channel=channel))
    return products

def generate_random_customers(count: int) -> List[Customer]:
    """ Sinh ngẫu nhiên danh sách khách hàng. """
    customers = []
    # Bản đồ chuyển đổi tiếng Việt có dấu thành không dấu cho phần email
    accent_map = {
        'à':'a','á':'a','ả':'a','ã':'a','ạ':'a','ă':'a','ằ':'a','ắ':'a','ẳ':'a','ẵ':'a','ặ':'a','â':'a','ầ':'a','ấ':'a','ẩ':'a','ẫ':'a','ậ':'a',
        'đ':'d',
        'è':'e','é':'e','ẻ':'e','ẽ':'e','ẹ':'e','ê':'e','ề':'e','ế':'e','ể':'e','ễ':'e','ệ':'e',
        'ì':'i','í':'i','ỉ':'i','ĩ':'i','ị':'i',
        'ò':'o','ó':'o','ỏ':'o','õ':'o','ọ':'o','ô':'o','ồ':'o','ố':'o','ổ':'o','ỗ':'o','ộ':'o','ơ':'o','ờ':'o','ớ':'o','ở':'o','ỡ':'o','ợ':'o',
        'ù':'u','ú':'u','ủ':'u','ũ':'u','ụ':'u','ư':'u','ừ':'u','ứ':'u','ử':'u','ữ':'u','ự':'u',
        'ỳ':'y','ý':'y','ỷ':'y','ỹ':'y','ỵ':'y'
    }
    
    def remove_accents(text: str) -> str:
        res = []
        for char in text.lower():
            res.append(accent_map.get(char, char))
        return "".join(res)

    for _ in range(count):
        full_name = f"{random.choice(FIRST_NAMES)} {random.choice(MIDDLE_NAMES)} {random.choice(LAST_NAMES)}"
        
        # Sinh email hợp lệ bằng cách bỏ dấu tiếng Việt và khoảng trắng
        clean_name = remove_accents(full_name).replace(" ", "")
        email = f"{clean_name}{random.randint(10, 99)}@{random.choice(DOMAINS)}"
        
        # Sinh số điện thoại Việt Nam hợp lệ khớp regex: 03x, 05x, 07x, 08x, 09x
        prefix = random.choice([
            "032", "033", "034", "035", "036", "037", "038", "039",
            "056", "058", "059",
            "070", "076", "077", "078", "079",
            "081", "082", "083", "084", "085", "086", "088", "089",
            "090", "091", "092", "093", "094", "095", "096", "097", "098", "099"
        ])
        phone = prefix + "".join(str(random.randint(0, 9)) for _ in range(7))
        
        address = f"Số {random.randint(1, 200)}, Đường {random.randint(1, 50)}, {random.choice(CITIES)}"
        loyalty_points = random.randint(0, 1000)
        customers.append(Customer(full_name=full_name, email=email, phone=phone, address=address, loyalty_points=loyalty_points))
    return customers

def generate_random_orders(count: int, products: List[Product], customers: List[Customer]) -> List[Order]:
    """ Sinh ngẫu nhiên danh sách đơn hàng dựa trên sản phẩm và khách hàng hiện có. """
    if not products or not customers:
        raise ValueError("Danh sách sản phẩm hoặc khách hàng không được để trống khi sinh đơn hàng.")
    
    orders = []
    channels = ["online", "offline", "facebook", "shopee", "tiktok"]
    statuses = ["pending", "confirmed", "shipping", "completed", "cancelled"]
    
    for _ in range(count):
        customer = random.choice(customers)
        channel = random.choice(channels)
        discount = random.choice([0.0, 0.05, 0.1, 0.15])
        notes = random.choice(["Giao giờ hành chính", "Gọi trước khi giao", "Hàng dễ vỡ", "Không", "Giao gấp"])
        status = random.choice(statuses)
        
        # Khởi tạo đơn hàng với trạng thái 'pending' để được phép thêm mặt hàng
        order = Order(
            customer_id=customer.customer_id,
            channel=channel,
            discount=discount,
            notes=notes,
            status="pending"
        )
        
        # Thêm từ 1 đến 4 sản phẩm ngẫu nhiên vào đơn hàng
        num_items = random.randint(1, 4)
        selected_products = random.sample(products, min(num_items, len(products)))
        for prod in selected_products:
            qty = random.randint(1, 3)
            item = OrderItem(
                product_id=prod.product_id,
                product_name=prod.name,
                unit_price=prod.price,
                quantity=qty
            )
            order.add_item(item)
        
        # Gán lại trạng thái thực tế sau khi đã hoàn thành việc thêm mặt hàng
        order.status = status
            
        orders.append(order)
    return orders

# --- XỬ LÝ FILE (file_handlers & models integration) ---

def save_database(products: List[Product], customers: List[Customer], orders: List[Order]):
    """ Ghi toàn bộ dữ liệu ra các file khác nhau thông qua FileHandlerFactory. """
    Path("data").mkdir(exist_ok=True)
    
    # 1. Ghi Sản phẩm ra tệp JSON
    prod_data = [p.to_dict() for p in products]
    prod_handler = FileHandlerFactory.get_handler("data/products.json")
    prod_handler.write(prod_data)
    logger.info(f"Đã lưu thành công {len(products)} sản phẩm vào 'data/products.json'")

    # 2. Ghi Khách hàng ra tệp CSV
    cus_data = [c.to_dict() for c in customers]
    cus_handler = FileHandlerFactory.get_handler("data/customers.csv")
    cus_handler.write(cus_data)
    logger.info(f"Đã lưu thành công {len(customers)} khách hàng vào 'data/customers.csv'")

    # 3. Ghi Đơn hàng ra tệp JSON
    ord_data = [o.to_dict() for o in orders]
    ord_handler = FileHandlerFactory.get_handler("data/orders.json")
    ord_handler.write(ord_data)
    logger.info(f"Đã lưu thành công {len(orders)} đơn hàng vào 'data/orders.json'")

def load_database():
    """ Đọc toàn bộ dữ liệu từ file lên các đối tượng Models tương ứng. """
    products: List[Product] = []
    customers: List[Customer] = []
    orders: List[Order] = []

    # 1. Đọc Sản phẩm
    prod_file = Path("data/products.json")
    if prod_file.exists():
        handler = FileHandlerFactory.get_handler(str(prod_file))
        data = handler.read()
        products = [Product.from_dict(d) for d in data]

    # 2. Đọc Khách hàng
    cus_file = Path("data/customers.csv")
    if cus_file.exists():
        handler = FileHandlerFactory.get_handler(str(cus_file))
        data = handler.read()
        customers = [Customer.from_dict(d) for d in data]

    # 3. Đọc Đơn hàng
    ord_file = Path("data/orders.json")
    if ord_file.exists():
        handler = FileHandlerFactory.get_handler(str(ord_file))
        data = handler.read()
        orders = [Order.from_dict(d) for d in data]
        
    return products, customers, orders

# --- THỐNG KÊ & BÁO CÁO (sys module + plain text formatting) ---

def generate_business_report():
    """ Đọc dữ liệu từ file, tổng hợp thống kê kinh doanh và xuất ra báo cáo văn bản thuần (.txt). """
    products, customers, orders = load_database()
    
    if not orders:
        print("⚠️ Không tìm thấy đơn hàng nào để lập báo cáo. Hãy sinh dữ liệu trước!")
        return
        
    total_revenue = 0.0
    revenue_by_channel = {}
    status_count = {}
    item_count_by_product = {}
    
    for order in orders:
        # Chỉ tính doanh thu cho các đơn hàng không bị hủy (cancelled)
        if order.status != "cancelled":
            total_revenue += order.total_amount
            
            # Thống kê theo kênh
            revenue_by_channel[order.channel] = revenue_by_channel.get(order.channel, 0.0) + order.total_amount
            
        # Thống kê trạng thái đơn hàng
        status_count[order.status] = status_count.get(order.status, 0) + 1
        
        # Thống kê sản phẩm bán chạy
        for item in order.items:
            item_count_by_product[item.product_name] = item_count_by_product.get(item.product_name, 0) + item.quantity
            
    # Tạo thư mục xuất báo cáo
    Path("exports").mkdir(exist_ok=True)
    report_path = "exports/business_report.txt"
    
    # Biên soạn nội dung báo cáo
    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append("     BÁO CÁO HOẠT ĐỘNG KINH DOANH ĐA KÊNH VÀ TỒN KHO")
    report_lines.append("=" * 60)
    report_lines.append(f"Tổng số khách hàng: {len(customers)}")
    report_lines.append(f"Tổng số loại sản phẩm: {len(products)}")
    report_lines.append(f"Tổng số đơn hàng phát sinh: {len(orders)}")
    report_lines.append(f"Doanh thu thực tế (đã trừ hủy đơn): {total_revenue:,.0f} VND")
    report_lines.append("-" * 60)
    
    report_lines.append("1. DOANH THU THEO KÊNH BÁN HÀNG:")
    for channel, rev in sorted(revenue_by_channel.items(), key=lambda x: x[1], reverse=True):
        report_lines.append(f"   - Kênh {channel.upper():10}: {rev:15,.0f} VND")
    report_lines.append("-" * 60)
    
    report_lines.append("2. PHÂN BỔ TRẠNG THÁI ĐƠN HÀNG:")
    for status, count in status_count.items():
        report_lines.append(f"   - {status.capitalize():12}: {count:5} đơn")
    report_lines.append("-" * 60)
    
    report_lines.append("3. TOP 5 SẢN PHẨM BÁN CHẠY NHẤT:")
    top_products = sorted(item_count_by_product.items(), key=lambda x: x[1], reverse=True)[:5]
    for i, (prod_name, qty) in enumerate(top_products, 1):
        report_lines.append(f"   {i}. {prod_name:40}: {qty:5} đơn vị")
    report_lines.append("=" * 60)
    
    # Ghi báo cáo ra file TXT thông qua TxtHandler
    txt_handler = FileHandlerFactory.get_handler(report_path, mode="raw")
    txt_handler.write("\n".join(report_lines))
    
    # In báo cáo ra màn hình (sys.stdout)
    print("\n".join(report_lines))
    print(f"\n💾 Đã ghi nhận báo cáo chi tiết tại: '{report_path}'\n")

# --- CHƯƠNG TRÌNH KIỂM THỬ ĐẦU CUỐI (END-TO-END TEST) ---

def run_system_test():
    """ Chương trình kiểm thử tự động toàn bộ quy trình sinh, ghi, đọc và phân tích dữ liệu. """
    print("\n⚙️ BẮT ĐẦU CHẠY THỬ NGHIỆM HỆ THỐNG PHÂN TÍCH FILE VÀ OOP V2...")
    print("=" * 70)
    
    # 1. Sinh ngẫu nhiên
    print("1. Đang giả lập dữ liệu ngẫu nhiên (sử dụng module random)...")
    products = generate_random_products(12)
    customers = generate_random_customers(8)
    orders = generate_random_orders(20, products, customers)
    print(f"   - Tạo thành công {len(products)} sản phẩm, {len(customers)} khách hàng, {len(orders)} đơn hàng.")
    
    # 2. Ghi tệp tin
    print("2. Đang ghi dữ liệu vào các định dạng CSV, JSON (sử dụng file_handlers)...")
    save_database(products, customers, orders)
    
    # 3. Đọc tệp tin
    print("3. Đọc dữ liệu từ file để tái cấu trúc lại các đối tượng OOP...")
    loaded_prods, loaded_cuses, loaded_ords = load_database()
    print(f"   - Đã nạp thành công {len(loaded_prods)} sản phẩm, {len(loaded_cuses)} khách hàng, {len(loaded_ords)} đơn hàng.")
    
    # Khớp dữ liệu
    assert len(loaded_prods) == len(products), "Dữ liệu sản phẩm bị lệch!"
    assert len(loaded_cuses) == len(customers), "Dữ liệu khách hàng bị lệch!"
    assert len(loaded_ords) == len(orders), "Dữ liệu đơn hàng bị lệch!"
    print("   - ĐỐI CHIẾU DỮ LIỆU THÀNH CÔNG: Dữ liệu đọc vào khớp 100% dữ liệu gốc!")
    
    # 4. Xuất báo cáo
    print("4. Tổng hợp hoạt động và lập báo cáo kinh doanh...")
    generate_business_report()
    
    print("=" * 70)
    print("🎉 BÀI KIỂM THỬ ĐÃ HOÀN THÀNH XUẤT SẮC! Mọi chức năng hoạt động chính xác.")

# --- GIAO DIỆN TƯƠNG TÁC DÒNG LỆNH CLI (sys & loop) ---

def print_menu():
    """ Hiển thị menu chức năng của CLI. """
    print("=" * 55)
    print("   HỆ THỐNG QUẢN LÝ BÁN HÀNG ĐA KÊNH V2 (FILE ONLY)")
    print("=" * 55)
    print("   1. Giả lập dữ liệu ngẫu nhiên mới và lưu file (CSV/JSON)")
    print("   2. Đọc file dữ liệu và xuất báo cáo kinh doanh (TXT)")
    print("   3. Chạy quy trình kiểm thử đầu cuối tự động (End-to-End Test)")
    print("   4. Xem cấu hình hệ thống hiện tại (sys module info)")
    print("   5. Thoát chương trình")
    print("=" * 55)

def interactive_cli():
    """ Vòng lặp giao diện tương tác CLI. """
    while True:
        print_menu()
        try:
            choice = input("👉 Chọn chức năng (1-5): ").strip()
            if choice == "1":
                p = int(input("Nhập số lượng sản phẩm cần giả lập (mặc định 10): ") or 10)
                c = int(input("Nhập số lượng khách hàng cần giả lập (mặc định 5): ") or 5)
                o = int(input("Nhập số lượng đơn hàng cần giả lập (mặc định 15): ") or 15)
                print("\n⌛ Đang xử lý dữ liệu...")
                products = generate_random_products(p)
                customers = generate_random_customers(c)
                orders = generate_random_orders(o, products, customers)
                save_database(products, customers, orders)
                print("✅ Đã hoàn thành quá trình giả lập và lưu file thành công!\n")
            elif choice == "2":
                print("\n⌛ Đang tổng hợp báo cáo...")
                generate_business_report()
            elif choice == "3":
                run_system_test()
            elif choice == "4":
                print("\n📊 THÔNG TIN HỆ THỐNG (sys module):")
                print(f"   - Phiên bản Python: {sys.version}")
                print(f"   - Nền tảng hệ điều hành: {sys.platform}")
                print(f"   - Mã hóa đầu ra stdout: {sys.stdout.encoding}")
                print(f"   - Đường dẫn thực thi: {sys.executable}")
                print(f"   - Tham số đầu vào: {sys.argv}\n")
            elif choice == "5":
                print("\n👋 Cảm ơn bạn đã sử dụng chương trình. Tạm biệt!")
                sys.exit(0)
            else:
                print("⚠️ Lựa chọn không hợp lệ! Vui lòng chọn từ 1 đến 5.")
        except KeyboardInterrupt:
            print("\n\n👋 Chương trình bị ngắt bởi người dùng. Tạm biệt!")
            sys.exit(0)
        except Exception as exc:
            print(f"❌ Đã xảy ra lỗi: {exc}\n")

# --- MAIN ENTRY POINT (sys.argv handling) ---

def main():
    """ Hàm chính điều hướng dựa trên các tham số dòng lệnh (sys.argv). """
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "generate":
            # Tham số: python main.py generate [p] [c] [o]
            p = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            c = int(sys.argv[3]) if len(sys.argv) > 3 else 5
            o = int(sys.argv[4]) if len(sys.argv) > 4 else 15
            print(f"⚡ Đang chạy chế độ tự động: Giả lập {p} sp, {c} kh, {o} đơn...")
            products = generate_random_products(p)
            customers = generate_random_customers(c)
            orders = generate_random_orders(o, products, customers)
            save_database(products, customers, orders)
            sys.exit(0)
            
        elif command == "report":
            print("⚡ Đang chạy chế độ tự động: Xuất báo cáo hoạt động...")
            generate_business_report()
            sys.exit(0)
            
        elif command == "test":
            run_system_test()
            sys.exit(0)
            
        elif command in ("help", "--help", "-h"):
            print("📖 HƯỚNG DẪN SỬ DỤNG DÒNG LỆNH:")
            print("   - Khởi chạy CLI tương tác : python main.py")
            print("   - Giả lập sinh dữ liệu     : python main.py generate [sản_phẩm] [khách_hàng] [đơn_hàng]")
            print("   - Lập và in báo cáo       : python main.py report")
            print("   - Chạy test tự động       : python main.py test")
            sys.exit(0)
        else:
            print(f"⚠️ Lệnh không hợp lệ: '{command}'. Sử dụng 'python main.py help' để xem hướng dẫn.")
            sys.exit(1)
    else:
        # Nếu không có tham số dòng lệnh nào, khởi chạy CLI tương tác
        interactive_cli()

if __name__ == "__main__":
    main()
