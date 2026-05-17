import sys
import random
import os
import json
import datetime
from typing import List

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from file_handlers import (
    JSONFileHandler, CSVFileHandler, TXTFileHandler,
    chuyen_doi_json_sang_csv, chuyen_doi_csv_sang_json, chuyen_doi_json_sang_txt
)
from models import Product, Customer, Order
from repositories import ProductRepository, CustomerRepository, OrderRepository
from utils import get_absolute_path

def kiem_tra_he_thong():
    print("=" * 60)
    print("[SYS] KIEM TRA HE THONG KHOI DONG (sys module):")
    v = sys.version_info
    print(f" -> Phien ban Python: {v.major}.{v.minor}.{v.micro} ({v.releaselevel})")
    print(f" -> He dieu hanh (Platform): {sys.platform}")
    print(f" -> Thu muc goc thuc thi: {sys.path[0]}")
    print("=" * 60)
    print()

os.makedirs(get_absolute_path("data"), exist_ok=True)
os.makedirs(get_absolute_path("exports"), exist_ok=True)

prod_repo = ProductRepository()
cust_repo = CustomerRepository()
order_repo = OrderRepository()

def menu_quan_ly_san_pham():
    while True:
        print("\n--- [CRUD SAN PHAM] ---")
        print("1. Xem danh sach san pham (Read)")
        print("2. Them san pham moi (Create)")
        print("3. Sua doi san pham (Update)")
        print("4. Xoa san pham (Delete)")
        print("0. Quay lai menu chinh")
        
        choice = input("-> Lua chon cua ban: ").strip()
        if choice == "1":
            xem_danh_sach_san_pham()
        elif choice == "2":
            them_san_pham_moi()
        elif choice == "3":
            sua_san_pham()
        elif choice == "4":
            xoa_san_pham()
        elif choice == "0":
            break
        else:
            print("[WARN] Lua chon khong hop le, vui long chon lai!")

def xem_danh_sach_san_pham(shuffled: bool = False):
    products = prod_repo.get_all()
    if not products:
        print("[EMPTY] Danh sach san pham trong!")
        return

    if shuffled:
        products = list(products)
        random.shuffle(products)
        print("[RANDOM] Da xao tron thu tu hien thi bang random.shuffle()!")

    print(f"{'MA SP':12} | {'TEN SAN PHAM':30} | {'DON GIA (VND)':15} | {'TON KHO':8} | {'DANH MUC':15} | {'KENH BAN':10}")
    print("-" * 105)
    for p in products:
        print(f"{p.product_id:12} | {p.name:30} | {p.price:15,.0f} | {p.quantity:8} | {p.category:15} | {p.channel:10}")

def them_san_pham_moi():
    print("\n--- THEM SAN PHAM MOI ---")
    try:
        new_id = f"PRD-{random.randint(1000, 9999)}"
        print(f"-> Ma san pham tu dong sinh: {new_id}")
        
        name = input("Nhap ten san pham: ").strip()
        if not name:
            raise ValueError("Tên sản phẩm không được để trống!")
            
        price = float(input("Nhap don gia (VND): "))
        if price < 0:
            raise ValueError("Đơn giá phải >= 0!")

        quantity = int(input("Nhap so luong ton kho: "))
        if quantity < 0:
            raise ValueError("Số lượng tồn kho phải >= 0!")

        category = input("Nhap danh muc (mac dinh: Chua phan loai): ").strip() or "Chua phan loai"
        
        suggested_channel = random.choice(["online", "offline", "both"])
        channel = input(f"Nhap kenh ban (online/offline/both - Goi y '{suggested_channel}'): ").strip().lower() or suggested_channel
        if channel not in ["online", "offline", "both"]:
            raise ValueError("Kênh bán hàng chỉ nhận các giá trị: online, offline, both")

        new_prod = Product(
            product_id=new_id, name=name, price=price, quantity=quantity, category=category, channel=channel
        )
        prod_repo.create(new_prod)
        print(f"[OK] Them san pham '{name}' thanh cong!")
    except ValueError as e:
        print(f"[FAIL] Loi nhap lieu/Validate: {e}")
    except Exception as e:
        print(f"[FAIL] Da xay ra loi he thong: {e}")

def sua_san_pham():
    print("\n--- SUA THONG TIN SAN PHAM ---")
    xem_danh_sach_san_pham()
    prod_id = input("\n-> Nhap ma san pham can sua: ").strip().upper()
    product = prod_repo.get_by_id(prod_id)
    if not product:
        print(f"[FAIL] Khong tim thay san pham co ma {prod_id}!")
        return

    print(f"[EDIT] Dang chinh sua san pham: {product.name} ({product.product_id})")
    try:
        name = input(f"Nhap ten moi (Bo trong giu nguyen '{product.name}'): ").strip() or product.name
        
        price_in = input(f"Nhap don gia moi (Bo trong giu nguyen '{product.price:,.0f}'): ").strip()
        price = float(price_in) if price_in else product.price
        if price < 0:
            raise ValueError("Đơn giá phải >= 0!")

        qty_in = input(f"Nhap so luong ton kho moi (Bo trong giu nguyen '{product.quantity}'): ").strip()
        quantity = int(qty_in) if qty_in else product.quantity
        if quantity < 0:
            raise ValueError("Số lượng tồn kho phải >= 0!")

        category = input(f"Nhap danh muc moi (Bo trong giu nguyen '{product.category}'): ").strip() or product.category
        channel = input(f"Nhap kenh ban moi (online/offline/both - Bo trong giu nguyen '{product.channel}'): ").strip().lower() or product.channel
        if channel not in ["online", "offline", "both"]:
            raise ValueError("Kênh bán chỉ nhận online/offline/both!")

        prod_repo.update(prod_id, name, price, quantity, category, channel)
        print(f"[OK] Cap nhat san pham {prod_id} thanh cong!")
    except ValueError as e:
        print(f"[FAIL] Loi nhap lieu: {e}")
    except Exception as e:
        print(f"[FAIL] Da xay ra loi: {e}")

def xoa_san_pham():
    print("\n--- XOA SAN PHAM ---")
    xem_danh_sach_san_pham()
    prod_id = input("\n-> Nhap ma san pham can xoa: ").strip().upper()
    product = prod_repo.get_by_id(prod_id)
    if not product:
        print(f"[FAIL] Khong tim thay san pham co ma {prod_id}!")
        return

    confirm = input(f"[WARN] Ban chac chan muon xoa san pham '{product.name}'? (y/n): ").strip().lower()
    if confirm == 'y':
        try:
            prod_repo.delete(prod_id)
            print(f"[OK] Da xoa thanh cong san pham {prod_id} khoi co so du lieu!")
        except Exception as e:
            print(f"[FAIL] Loi khi xoa: {e}")
    else:
        print("[INFO] Da huy thao tac xoa.")

def menu_quan_ly_khach_hang():
    while True:
        print("\n--- [CRUD KHACH HANG] ---")
        print("1. Xem danh sach khach hang (Read)")
        print("2. Them khach hang moi (Create)")
        print("3. Sua doi thong tin khach hang (Update)")
        print("4. Xoa khach hang (Delete)")
        print("0. Quay lai menu chinh")
        
        choice = input("-> Lua chon cua ban: ").strip()
        if choice == "1":
            xem_danh_sach_khach_hang()
        elif choice == "2":
            them_khach_hang_moi()
        elif choice == "3":
            sua_khach_hang()
        elif choice == "4":
            xoa_khach_hang()
        elif choice == "0":
            break
        else:
            print("[WARN] Lua chon khong hop le, vui long chon lai!")

def xem_danh_sach_khach_hang():
    customers = cust_repo.get_all()
    if not customers:
        print("[EMPTY] Danh sach khach hang trong!")
        return

    print(f"{'MA KH':12} | {'HO VA TEN KHACH HANG':25} | {'EMAIL':30} | {'SO DIEN THOAI':12} | {'DIA CHI':30} | {'DIEM TICH LUY'}")
    print("-" * 125)
    for c in customers:
        print(f"{c.customer_id:12} | {c.full_name:25} | {c.email:30} | {c.phone:12} | {c.address:30} | {c.loyalty_points}")

def them_khach_hang_moi():
    print("\n--- THEM KHACH HANG MOI ---")
    try:
        new_id = f"CUS-{random.randint(1000, 9999)}"
        print(f"-> Ma khach hang tu dong sinh: {new_id}")

        full_name = input("Nhap ho va ten: ").strip()
        if not full_name:
            raise ValueError("Họ tên không được rỗng!")
            
        email = input("Nhap dia chi email: ").strip()
        if "@" not in email:
            raise ValueError("Email không hợp lệ (phải chứa ký tự '@')!")
            
        phone = input("Nhap so dien thoai: ").strip()
        if not phone.isdigit() or len(phone) < 9:
            raise ValueError("Số điện thoại không hợp lệ (phải là các chữ số và dài ít nhất 9 ký tự)!")

        address = input("Nhap dia chi: ").strip()
        loyalty_points = int(input("Nhap diem tich luy ban dau (mac dinh 0): ") or 0)

        new_cust = Customer(
            customer_id=new_id, full_name=full_name, email=email, phone=phone, address=address, loyalty_points=loyalty_points
        )
        cust_repo.create(new_cust)
        print(f"[OK] Them khach hang '{full_name}' thanh cong!")
    except ValueError as e:
        print(f"[FAIL] Loi nhap lieu/Validate: {e}")
    except Exception as e:
        print(f"[FAIL] Da xay ra loi: {e}")

def sua_khach_hang():
    print("\n--- SUA THONG TIN KHACH HANG ---")
    xem_danh_sach_khach_hang()
    cust_id = input("\n-> Nhap ma khach hang can sua: ").strip().upper()
    customer = cust_repo.get_by_id(cust_id)
    if not customer:
        print(f"[FAIL] Khong tim thay khach hang {cust_id}!")
        return

    print(f"[EDIT] Sua doi khach hang: {customer.full_name}")
    try:
        full_name = input(f"Nhap ten moi (Bo trong giu nguyen '{customer.full_name}'): ").strip() or customer.full_name
        email = input(f"Nhap email moi (Bo trong giu nguyen '{customer.email}'): ").strip() or customer.email
        if "@" not in email:
            raise ValueError("Email không hợp lệ!")
            
        phone = input(f"Nhap so dien thoai moi (Bo trong giu nguyen '{customer.phone}'): ").strip() or customer.phone
        address = input(f"Nhap dia chi moi (Bo trong giu nguyen '{customer.address}'): ").strip() or customer.address
        
        pts_in = input(f"Nhap diem tich luy moi (Bo trong giu nguyen '{customer.loyalty_points}'): ").strip()
        loyalty_points = int(pts_in) if pts_in else customer.loyalty_points
        if loyalty_points < 0:
            raise ValueError("Điểm tích lũy không được phép nhỏ hơn 0!")

        cust_repo.update(cust_id, full_name, email, phone, address, loyalty_points)
        print(f"[OK] Cap nhat khach hang {cust_id} thanh cong!")
    except ValueError as e:
        print(f"[FAIL] Loi: {e}")
    except Exception as e:
        print(f"[FAIL] Da xay ra loi: {e}")

def xoa_khach_hang():
    print("\n--- XOA KHACH HANG ---")
    xem_danh_sach_khach_hang()
    cust_id = input("\n-> Nhap ma khach hang can xoa: ").strip().upper()
    customer = cust_repo.get_by_id(cust_id)
    if not customer:
        print(f"[FAIL] Khong tim thay khach hang co ma {cust_id}!")
        return

    confirm = input(f"[WARN] Ban chac chan muon xoa khach hang '{customer.full_name}'? (y/n): ").strip().lower()
    if confirm == 'y':
        try:
            cust_repo.delete(cust_id)
            print(f"[OK] Da xoa thanh cong khach hang {cust_id}!")
        except Exception as e:
            print(f"[FAIL] Loi: {e}")
    else:
        print("[INFO] Da huy thao tac xoa.")

def menu_quan_ly_don_hang():
    while True:
        print("\n--- [CRUD DON HANG] ---")
        print("1. Xem danh sach don hang (Read)")
        print("2. Tao don hang moi (Create)")
        print("3. Cap nhat trang thai don (Update)")
        print("4. Huy/Xoa don hang (Delete)")
        print("0. Quay lai menu chinh")
        
        choice = input("-> Lua chon cua ban: ").strip()
        if choice == "1":
            xem_danh_sach_don_hang()
        elif choice == "2":
            tao_don_hang_moi()
        elif choice == "3":
            cap_nhat_trang_thai_don_hang()
        elif choice == "4":
            xoa_don_hang()
        elif choice == "0":
            break
        else:
            print("[WARN] Lua chon khong hop le, vui long chon lai!")

def xem_danh_sach_don_hang():
    orders = order_repo.get_all()
    if not orders:
        print("[EMPTY] Danh sach don hang trong!")
        return

    print(f"{'MA DON':12} | {'MA KHACH HANG':15} | {'KENH BAN':10} | {'THANH TOAN':10} | {'TONG TIEN (VND)':15} | {'TRANG THAI':10} | {'NGAY TAO'}")
    print("-" * 115)
    for o in orders:
        print(f"{o.order_id:12} | {o.customer_id:15} | {o.channel:10} | {o.payment_method:10} | {o.total_amount:15,.0f} | {o.status:10} | {o.created_at}")

def tao_don_hang_moi():
    print("\n--- TAO DON HANG MOI ---")
    try:
        new_id = f"ORD-{random.randint(10000, 99999)}"
        print(f"-> Ma don hang tu dong sinh: {new_id}")

        xem_danh_sach_khach_hang()
        customer_id = input("\n-> Nhap ma khach hang mua hang: ").strip().upper()
        customer = cust_repo.get_by_id(customer_id)
        if not customer:
            raise ValueError(f"Mã khách hàng {customer_id} không tồn tại trên hệ thống! Vui lòng tạo khách hàng trước.")

        xem_danh_sach_san_pham()
        items = []
        total_amount = 0.0
        
        while True:
            prod_id = input("\n-> Nhap ma san pham muon mua (hoac nhan Enter de hoan tat): ").strip().upper()
            if not prod_id:
                break
                
            product = prod_repo.get_by_id(prod_id)
            if not product:
                print("[FAIL] Khong tim thay san pham!")
                continue

            if product.quantity <= 0:
                print("[FAIL] San pham da het hang!")
                continue

            qty = int(input(f"Nhap so luong mua (Ton kho hien co: {product.quantity}): "))
            if qty <= 0:
                print("[FAIL] So luong mua phai > 0!")
                continue
            if qty > product.quantity:
                print(f"[FAIL] Khong du hang! Chi co the mua toi da {product.quantity} san pham.")
                continue

            product.quantity -= qty
            
            subtotal = product.price * qty
            total_amount += subtotal
            
            items.append({
                "product_id": product.product_id,
                "product_name": product.name,
                "price": product.price,
                "quantity": qty
            })
            print(f"[OK] Da them {qty} san pham '{product.name}' vao gio hang.")

        if not items:
            raise ValueError("Đơn hàng phải có ít nhất 1 sản phẩm!")

        suggested_channel = random.choice(["shopee", "lazada", "tiktok", "facebook", "offline"])
        channel = input(f"Nhap kenh ban (shopee/lazada/tiktok/facebook/offline - Goi y '{suggested_channel}'): ").strip().lower() or suggested_channel
        if channel not in ["shopee", "lazada", "tiktok", "facebook", "offline"]:
            raise ValueError("Kênh bán hàng không hợp lệ!")

        suggested_payment = random.choice(["cash", "card", "momo", "vnpay"])
        payment_method = input(f"Nhap phuong thuc thanh toan (cash/card/momo/vnpay - Goi y '{suggested_payment}'): ").strip().lower() or suggested_payment
        if payment_method not in ["cash", "card", "momo", "vnpay"]:
            raise ValueError("Phương thức thanh toán không hợp lệ!")

        new_order = Order(
            order_id=new_id,
            customer_id=customer_id,
            items=items,
            channel=channel,
            payment_method=payment_method,
            total_amount=total_amount,
            status="pending"
        )
        
        order_repo.create(new_order)
        prod_repo._luu_du_lieu()
        print(f"[OK] Tao don hang thanh cong! Tong gia tri don hang: {total_amount:,.0f} VND.")
        
    except ValueError as e:
        print(f"[FAIL] Loi validate: {e}")
    except Exception as e:
        print(f"[FAIL] Da xay ra loi: {e}")

def cap_nhat_trang_thai_don_hang():
    print("\n--- CAP NHAT TRANG THAI DON HANG ---")
    xem_danh_sach_don_hang()
    order_id = input("\n-> Nhap ma don hang can cap nhat: ").strip().upper()
    order = order_repo.get_by_id(order_id)
    if not order:
        print(f"[FAIL] Khong tim thay don hang {order_id}!")
        return

    print(f"Trang thai hien tai: '{order.status}'")
    status = input("Nhap trang thai moi (pending/completed/cancelled): ").strip().lower()
    if status not in ["pending", "completed", "cancelled"]:
        print("[FAIL] Trang thai khong hop le!")
        return

    try:
        order_repo.update(order_id, status)
        print(f"[OK] Da cap nhat trang thai don hang {order_id} thanh '{status}'!")
    except Exception as e:
        print(f"[FAIL] Loi: {e}")

def xoa_don_hang():
    print("\n--- HUY/XOA DON HANG ---")
    xem_danh_sach_don_hang()
    order_id = input("\n-> Nhap ma don hang can xoa: ").strip().upper()
    order = order_repo.get_by_id(order_id)
    if not order:
        print(f"[FAIL] Khong tim thay don hang {order_id}!")
        return

    confirm = input(f"[WARN] Ban chac chan muon xoa don hang {order_id}? (y/n): ").strip().lower()
    if confirm == 'y':
        try:
            order_repo.delete(order_id)
            print(f"[OK] Da xoa don hang {order_id}!")
        except Exception as e:
            print(f"[FAIL] Loi: {e}")
    else:
        print("[INFO] Da huy thao tac xoa.")

def xuat_du_lieu_ra_csv():
    print("\n--- [Buoi 8] XUAT DU LIEU RA FILE CSV ---")
    print("1. Xuat danh sach San pham ra CSV")
    print("2. Xuat danh sach Khach hang ra CSV")
    choice = input("-> Lua chon cua ban: ").strip()
    
    try:
        if choice == "1":
            products = prod_repo.get_all()
            if not products:
                print("[EMPTY] Khong co san pham nao de xuat!")
                return
            data = [p.to_dict() for p in products]
            handler = CSVFileHandler(get_absolute_path("exports", "products_export.csv"))
            handler.ghi(data)
            print("[OK] Da xuat san pham thanh cong tai 'exports/products_export.csv'!")
        elif choice == "2":
            customers = cust_repo.get_all()
            if not customers:
                print("[EMPTY] Khong co khach hang nao de xuat!")
                return
            data = [c.to_dict() for c in customers]
            handler = CSVFileHandler(get_absolute_path("exports", "customers_export.csv"))
            handler.ghi(data)
            print("[OK] Da xuat khach hang thanh cong tai 'exports/customers_export.csv'!")
        else:
            print("[WARN] Lua chon khong hop le!")
    except Exception as e:
        print(f"[FAIL] Loi xuat file CSV: {e}")

def xuat_du_lieu_ra_txt():
    print("\n--- [Buoi 8] XUAT BAO CAO RA FILE TXT ---")
    try:
        products = prod_repo.get_all()
        customers = cust_repo.get_all()
        orders = order_repo.get_all()
        
        report_lines = []
        report_lines.append("============================================================")
        report_lines.append(f"     BAO CAO DOANH THU & HOAT DONG KINH DOANH - {datetime.date.today().strftime('%Y-%m-%d')}")
        report_lines.append("============================================================")
        report_lines.append(f"Tong so luong san pham: {len(products)}")
        report_lines.append(f"Tong so luong khach hang: {len(customers)}")
        report_lines.append(f"Tong so luong don hang: {len(orders)}")
        
        total_rev = sum(o.total_amount for o in orders if o.status != "cancelled")
        report_lines.append(f"Tong doanh thu du kien (tru don huy): {total_rev:,.0f} VND")
        report_lines.append("-" * 60)
        
        report_lines.append("DANH SACH DON HANG CHI TIET:")
        for o in orders:
            report_lines.append(f" - [{o.order_id}] KH: {o.customer_id} | Tong: {o.total_amount:12,.0f} VND | Trang thai: {o.status}")
            
        report_lines.append("============================================================")
        
        handler = TXTFileHandler(get_absolute_path("exports", "summary_report.txt"))
        handler.ghi_nhiều_dòng(report_lines)
        print("[OK] Da xuat bao cao kinh doanh thanh cong tai 'exports/summary_report.txt'!")
        
        print("\n[INFO] DOC THU LAI FILE TXT VUA GHI BANG PHUONG THUC READLINE()/READLINES():")
        lines = handler.doc_từng_dòng()
        for i, line in enumerate(lines[:5], 1):
            print(f"Dong {i}: {line}")
            
    except Exception as e:
        print(f"[FAIL] Loi xuat/doc file TXT: {e}")

def menu_chuyen_doi_dinh_dang():
    print("\n--- [Buoi 8] CHUYEN DOI DINH DANG FILE (JSON <-> CSV <-> TXT) ---")
    print("1. Chuyen doi Khach hang tu JSON sang CSV")
    print("2. Chuyen doi San pham tu JSON sang TXT")
    print("3. Chuyen doi nguoc Khach hang tu CSV sang JSON")
    
    choice = input("-> Lua chon cua ban: ").strip()
    try:
        if choice == "1":
            chuyen_doi_json_sang_csv(
                get_absolute_path("data", "customers.json"), 
                get_absolute_path("data", "customers_converted.csv")
            )
            print("[OK] Da chuyen doi thanh cong tai 'data/customers_converted.csv'!")
        elif choice == "2":
            chuyen_doi_json_sang_txt(
                get_absolute_path("data", "products.json"), 
                get_absolute_path("data", "products_report.txt")
            )
            print("[OK] Da chuyen doi thanh cong tai 'data/products_report.txt'!")
        elif choice == "3":
            if not os.path.exists(get_absolute_path("data", "customers_converted.csv")):
                print("[WARN] Ban can chon chuc nang 1 truoc de co tep CSV mau!")
                return
            chuyen_doi_csv_sang_json(
                get_absolute_path("data", "customers_converted.csv"), 
                get_absolute_path("data", "customers_back.json")
            )
            print("[OK] Da chuyen doi thanh cong tai 'data/customers_back.json'!")
        else:
            print("[WARN] Lua chon khong hop le!")
    except Exception as e:
        print(f"[FAIL] Loi chuyen doi file: {e}")

def demo_xu_ly_loi_file():
    print("\n--- [Buoi 8] DEMO CAC LOAI LOI FILE & XU LY NGOAI LE ---")
    print("He thong se co tinh kich hoat 3 loi pho bien sau:")
    
    print("\n-> 1. Triggers FileNotFoundError (Doc file khong ton tai):")
    try:
        h = JSONFileHandler(get_absolute_path("data", "file_nay_chac_chan_khong_ton_tai.json"))
        h.doc()
    except FileNotFoundError as e:
        print(f"   [CATCHED - FileNotFoundError] Thanh cong bat loi: {e}")
    except Exception as e:
        print(f"   [CATCHED - Loi khac]: {e}")
    else:
        print("   [ELSE] Khong co loi xay ra (Dieu nay la bat kha thi!)")
    finally:
        print("   [FINALLY] Luon duoc thuc thi ke ca khi co loi xay ra.")

    print("\n-> 2. Triggers JSONDecodeError (Doc file chua JSON sai cu phap):")
    malformed_filepath = get_absolute_path("data", "malformed.json")
    try:
        with open(malformed_filepath, 'w', encoding='utf-8') as f:
            f.write("{ 'this_is_invalid_json': true, lacking_double_quotes }")
            
        h = JSONFileHandler(malformed_filepath)
        h.doc()
    except json.JSONDecodeError as e:
        print(f"   [CATCHED - JSONDecodeError] Thanh cong bat loi cu phap: {e}")
    except IOError as e:
        print(f"   [CATCHED - IOError]: {e}")
    finally:
        if os.path.exists(malformed_filepath):
            os.remove(malformed_filepath)
        print("   [FINALLY] Da xoa file rac thu nghiem.")

    print("\n-> 3. Triggers ValueError/TypeError (Ghi kieu du lieu khong phu hop):")
    try:
        h = JSONFileHandler(get_absolute_path("data", "invalid_type.json"))
        unserializable_data = {1, 2, 3}
        h.ghi(unserializable_data)
    except ValueError as e:
        print(f"   [CATCHED - ValueError] Loi gia tri/kieu du lieu: {e}")
    except TypeError as e:
        print(f"   [CATCHED - TypeError] Loi kieu du lieu he thong: {e}")
    except Exception as e:
        print(f"   [CATCHED - Exception]: {e}")

def demo_random_library():
    print("\n--- [Buoi 9] THUC HANH MODULE RANDOM ---")
    print("Dang chuan bi sinh ngau nhien 5 san pham mo phong:")
    
    cats = ["Dien tu", "Gia dung", "Thoi trang", "Sach", "Lam dep"]
    names = ["Tai nghe", "Ban la", "Ao phong", "But bi", "Son moi", "Chuot khong day", "So da", "Quat ban"]
    channels = ["online", "offline", "both"]
    
    random_products = []
    
    for i in range(1, 6):
        rand_id = f"PRD-{random.randint(100000, 999999)}"
        rand_qty = random.randint(5, 50)
        
        rand_discount = random.random() * 0.2
        rand_price = random.uniform(50000.0, 2000000.0) * (1 - rand_discount)
        
        rand_cat = random.choice(cats)
        rand_name = f"{random.choice(names)} Random #{i}"
        rand_channel = random.choice(channels)
        
        product = Product(
            product_id=rand_id,
            name=rand_name,
            price=rand_price,
            quantity=rand_qty,
            category=rand_cat,
            channel=rand_channel
        )
        random_products.append(product)

    print("[OK] Da sinh thanh cong 5 san pham ngau nhien:")
    for p in random_products:
        print(f" -> [{p.product_id}] {p.name} - Gia: {p.price:,.2f} VND | So luong: {p.quantity} | Kenh: {p.channel}")

    print("\n[SHUFFLE] 2. Demo random.shuffle() (Xao tron danh sach hien thi):")
    ids = [p.product_id for p in random_products]
    print(f"   - Truoc xao tron: {ids}")
    random.shuffle(ids)
    print(f"   - Sau xao tron : {ids}")

    print("\n[SAMPLE] 3. Demo random.sample() (Lay mau ngau nhien khong trung lap):")
    sampled_prods = random.sample(random_products, 2)
    print("   - 2 san pham duoc lay mau ngau nhien:")
    for p in sampled_prods:
        print(f"     + [{p.product_id}] {p.name}")

    save_choice = input("\n[SAVE] Ban co muon luu 5 san pham ngau nhien nay vao database chinh? (y/n): ").strip().lower()
    if save_choice == 'y':
        try:
            for p in random_products:
                prod_repo.create(p)
            print("[OK] Da luu thanh cong 5 san pham ngau nhien vao file 'data/products.json'!")
        except Exception as e:
            print(f"[FAIL] Loi luu du lieu: {e}")
    else:
        print("[INFO] Da bo qua, khong luu du lieu ngau nhien.")

def hien_thi_thong_tin_sys():
    print("\n--- [Buoi 9] THONG TIN HE THONG (sys module & File Size) ---")
    
    v = sys.version_info
    print(f"1. Phien ban Python (sys.version_info): {v.major}.{v.minor}.{v.micro} (Release: {v.releaselevel})")
    
    print(f"2. Nen tang he thong (sys.platform): {sys.platform}")
    
    print(f"3. Tham so dong lenh nhan vao (sys.argv): {sys.argv}")
    
    print(f"4. Thu muc chay ung dung chinh (sys.path[0]): {sys.path[0]}")
    
    print("\n[STAT] KICH THUOC FILE DU LIEU HIEN TAI (bytes):")
    files = {
        "San pham (JSON)": get_absolute_path("data", "products.json"),
        "Khach hang (JSON)": get_absolute_path("data", "customers.json"),
        "Don hang (JSON)": get_absolute_path("data", "orders.json"),
        "Bao cao tom tat (TXT)": get_absolute_path("exports", "summary_report.txt")
    }
    for label, path in files.items():
        if os.path.exists(path):
            sz = os.path.getsize(path)
            print(f"   - Tep {label:25}: {sz:8,} bytes (Duong dan: '{path}')")
        else:
            print(f"   - Tep {label:25}: Chua ton tai")

def run_auto_demo():
    print("\n" + "="*80)
    print("[DEMO] CHE DO TU DONG CHAY THU NGHIEM (sys.argv: '--demo')")
    print("="*80)
    
    print("\n* BUOC 1: Sinh ngau nhien du lieu mau...")
    products_demo = [
        Product(f"PRD-{random.randint(1000, 9999)}", "San pham Demo A", 150000.0, 20, "Dien tu", "both"),
        Product(f"PRD-{random.randint(1000, 9999)}", "Sach Giao Trinh OOP", 95000.0, 100, "Sach", "online")
    ]
    for p in products_demo:
        try:
            prod_repo.create(p)
            print(f"   - Da tao: {p}")
        except Exception:
            pass
            
    print("\n* BUOC 2: Hien thi danh sach san pham xao tron...")
    xem_danh_sach_san_pham(shuffled=True)
    
    print("\n* BUOC 3: Xuat bao cao tom tat ra file TXT...")
    xuat_du_lieu_ra_txt()
    
    print("\n* BUOC 4: Hien thi thong so he thong...")
    hien_thi_thong_tin_sys()
    
    print("\n" + "="*80)
    print("[OK] CHE DO DEMO TU DONG DA THUC THI XONG. CHUONG TRINH THOAT.")
    print("="*80 + "\n")
    sys.exit(0)

def show_main_menu():
    print("+------------------------------------------+")
    print("|   HE THONG QUAN LY BAN HANG DA KENH V2   |")
    print("+------------------------------------------+")
    print("|  [BUOI 8 - File & Xu ly loi]             |")
    print("|  1. Quan ly San pham (CRUD -> JSON)      |")
    print("|  2. Quan ly Khach hang (CRUD -> JSON)    |")
    print("|  3. Quan ly Don hang (CRUD -> JSON)      |")
    print("|  4. Xuat du lieu ra CSV                  |")
    print("|  5. Xuat du lieu ra TXT                  |")
    print("|  6. Chuyen doi dinh dang file            |")
    print("|  7. Demo xu ly loi file                  |")
    print("+------------------------------------------+")
    print("|  [BUOI 9 - Random & Sys]                 |")
    print("|  8. Tao du lieu ngau nhien (random)      |")
    print("|  9. Thong tin he thong (sys)             |")
    print("|  0. Thoat (sys.exit)                     |")
    print("+------------------------------------------+")

def main():
    kiem_tra_he_thong()
    
    if len(sys.argv) > 1 and sys.argv[1].lower() in ["--demo", "-d"]:
        run_auto_demo()
        
    while True:
        show_main_menu()
        try:
            choice = input("-> Nhap lua chon cua ban (0-9): ").strip()
            if choice == "1":
                menu_quan_ly_san_pham()
            elif choice == "2":
                menu_quan_ly_khach_hang()
            elif choice == "3":
                menu_quan_ly_don_hang()
            elif choice == "4":
                xuat_du_lieu_ra_csv()
            elif choice == "5":
                xuat_du_lieu_ra_txt()
            elif choice == "6":
                menu_chuyen_doi_dinh_dang()
            elif choice == "7":
                demo_xu_ly_loi_file()
            elif choice == "8":
                demo_random_library()
            elif choice == "9":
                hien_thi_thong_tin_sys()
            elif choice == "0":
                print("\n[exit] Cam on ban da su dung chuong trinh thuc hanh! Thoat he thong...")
                sys.exit(0)
            else:
                print("[WARN] Lua chon ngoai vung menu! Hay nhap tu 0 den 9.")
        except KeyboardInterrupt:
            print("\n\n[exit] Chuong trinh bi dung khan cap bang to hop phim. Tam biet!")
            sys.exit(0)
        except Exception as e:
            print(f"[FAIL] Da xay ra loi khong xac dinh tai Menu chinh: {e}")
            print("Vui long thu lai thao tac.")

if __name__ == "__main__":
    main()
