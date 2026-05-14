import customtkinter as ctk
from tkinter import messagebox, ttk
from PIL import Image

class Validators:
    @staticmethod
    def validate_product(data):
        """Kiểm tra tính hợp lệ của dữ liệu sản phẩm"""
        # data = [ID, Name, Category, Price, Stock]
        if not all(str(item).strip() for item in data):
            return False, "Không được để trống thông tin!"
        if not str(data[3]).replace('M', '').isdigit(): # Giả định giá có chữ M hoặc số
            return False, "Giá sản phẩm phải là số!"
        if not str(data[4]).isdigit():
            return False, "Số lượng tồn kho phải là số nguyên!"
        return True, ""

    @staticmethod
    def validate_customer(data):
        """Kiểm tra tính hợp lệ của dữ liệu khách hàng"""
        # data = [ID, Name, Phone, Type]
        if not all(str(item).strip() for item in data):
            return False, "Không được để trống thông tin khách hàng!"
        if len(str(data[2])) < 10:
            return False, "Số điện thoại không hợp lệ!"
        return True, ""

# 2. PHẦN MANAGERS (Quy tắc tích hợp: Xử lý dữ liệu gián tiếp)
class ProductManager:
    def __init__(self, storage):
        self.storage = storage
    def get_all(self): return self.storage
    def add(self, p_obj): self.storage.append(p_obj)
    def update(self, p_id, new_p_obj):
        for i, p in enumerate(self.storage):
            if p[0] == p_id:
                self.storage[i] = new_p_obj
                break
    def delete(self, p_id):
        self.storage[:] = [p for p in self.storage if p[0] != p_id]

class CustomerManager:
    def __init__(self, storage):
        self.storage = storage
    def get_all(self): return self.storage
    def add(self, c_obj): self.storage.append(c_obj)
    def update(self, c_id, new_c_obj):
        for i, c in enumerate(self.storage):
            if c[0] == c_id:
                self.storage[i] = new_c_obj
                break
    def delete(self, c_id):
        self.storage[:] = [c for c in self.storage if c[0] != c_id]

ctk.set_appearance_mode("light")


class MainWindow(ctk.CTkFrame):
    def __init__(self, master, role, app_data):
        super().__init__(master, fg_color="#f8f9fc")
        self.role = role
        self.master = master
        
        # Khởi tạo Managers từ app_data
        self.prod_manager = ProductManager(app_data['products'])
        self.cust_manager = CustomerManager(app_data['customers'])

        # Cấu hình Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=220, fg_color="#1e1e2d", corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="SALES SYSTEM", font=("Arial Bold", 22), text_color="white").pack(pady=(30, 10))
        ctk.CTkLabel(self.sidebar, text=f"● {role}", font=("Arial", 13), text_color="#2ecc71").pack(pady=(0, 30))
        
        menu = [("Tổng quan", "📊", self.show_overview), ("Sản phẩm", "📦", self.show_products), ("Khách hàng", "👥", self.show_customers)]
        for t, i, c in menu:
            ctk.CTkButton(self.sidebar, text=f"{i}  {t}", fg_color="transparent", text_color="white", anchor="w", 
                          hover_color="#2b2d3e", height=45, command=c).pack(fill="x", padx=10, pady=2)

        ctk.CTkButton(self.sidebar, text="🚪 Đăng xuất", fg_color="#e64a60", command=lambda: master.show_login_screen()).pack(side="bottom", fill="x", padx=20, pady=20)

        # --- NỘI DUNG CHÍNH ---
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # --- THANH TRẠNG THÁI (STATUS BAR) ---
        self.status_bar = ctk.CTkFrame(self, height=25, fg_color="#eeeeee", corner_radius=0)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.status_label = ctk.CTkLabel(self.status_bar, text="Hệ thống sẵn sàng", font=("Arial", 11), text_color="gray")
        self.status_label.pack(side="left", padx=20)

        self.show_overview()

    def update_status(self, msg):
        self.status_label.configure(text=msg)

    def clear_content(self):
        for widget in self.main_content.winfo_children(): widget.destroy()

    def show_overview(self):
        self.clear_content()
        self.update_status("Đang xem bảng điều khiển tổng quan")
        ctk.CTkLabel(self.main_content, text="BẢNG ĐIỀU KHIỂN CHUNG", font=("Arial Bold", 28)).pack(anchor="w", pady=(0, 20))
        
        stock = sum(int(str(p[4])) for p in self.prod_manager.get_all() if str(p[4]).isdigit())
        cust_count = len(self.cust_manager.get_all())

        container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        container.pack(fill="x", pady=10)
        
        cards = [("Khách hàng", str(cust_count), "#3498db"), ("Tồn kho", str(stock), "#f1c40f")]
        for t, v, c in cards:
            f = ctk.CTkFrame(container, fg_color="white", width=200, height=100, corner_radius=10)
            f.pack(side="left", padx=(0, 20))
            f.pack_propagate(False)
            ctk.CTkLabel(f, text=t, text_color="gray").pack(pady=(15, 0))
            ctk.CTkLabel(f, text=v, font=("Arial Bold", 24), text_color=c).pack()

    def show_products(self):
        self.clear_content()
        self.update_status("Quản lý danh mục sản phẩm")
        
        header = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(header, text="DANH SÁCH SẢN PHẨM", font=("Arial Bold", 20)).pack(side="left")
        
        if self.role == "ADMIN":
            btn_f = ctk.CTkFrame(header, fg_color="transparent")
            btn_f.pack(side="right")
            ctk.CTkButton(btn_f, text="+ Thêm", width=80, fg_color="#2ecc71", command=lambda: self.product_form()).pack(side="left", padx=5)
            ctk.CTkButton(btn_f, text="✎ Sửa", width=80, fg_color="#3498db", command=self.edit_product).pack(side="left", padx=5)
            ctk.CTkButton(btn_f, text="🗑 Xóa", width=80, fg_color="#e64a60", command=self.delete_product).pack(side="left", padx=5)

        self.p_tree = self.create_tree(("id", "name", "cat", "price", "stock"), ["MÃ SP", "TÊN SP", "DANH MỤC", "GIÁ", "TỒN KHO"])
        self.load_p_data()

    def load_p_data(self):
        for i in self.p_tree.get_children(): self.p_tree.delete(i)
        for p in self.prod_manager.get_all(): self.p_tree.insert("", "end", values=p)

    def product_form(self, existing=None):
        win = ctk.CTkToplevel(self)
        win.title("Thông tin sản phẩm")
        win.geometry("400x500")
        win.attributes("-topmost", True)
        
        labels = ["Mã SP", "Tên SP", "Danh mục", "Giá", "Số lượng"]
        ents = {}
        for i, l in enumerate(labels):
            ctk.CTkLabel(win, text=l).pack(padx=20, anchor="w", pady=(10, 0))
            e = ctk.CTkEntry(win, width=300)
            if existing:
                e.insert(0, existing[i])
                if i == 0: e.configure(state="disabled")
            e.pack(padx=20)
            ents[l] = e

        def handle_save():
            data = [ents[l].get() for l in labels]
            is_val, msg = Validators.validate_product(data)
            if not is_val:
                messagebox.showerror("Lỗi dữ liệu", msg)
                return
            
            if existing: self.prod_manager.update(existing[0], data)
            else: self.prod_manager.add(data)
            
            self.load_p_data()
            win.destroy()
            self.update_status(f"Đã {'cập nhật' if existing else 'thêm'} sản phẩm {data[0]}")

        ctk.CTkButton(win, text="LƯU DỮ LIỆU", fg_color="#2ecc71", command=handle_save).pack(pady=30)

    def edit_product(self):
        sel = self.p_tree.selection()
        if sel: self.product_form(self.p_tree.item(sel[0])['values'])
        else: messagebox.showwarning("Chú ý", "Chọn sản phẩm để sửa")

    def delete_product(self):
        sel = self.p_tree.selection()
        if sel and messagebox.askyesno("Xác nhận", "Xóa sản phẩm này?"):
            self.prod_manager.delete(self.p_tree.item(sel[0])['values'][0])
            self.load_p_data()

    def show_customers(self):
        self.clear_content()
        self.update_status("Quản lý danh sách khách hàng")
        
        header = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(header, text="DANH SÁCH KHÁCH HÀNG", font=("Arial Bold", 20)).pack(side="left")
        
        if self.role == "ADMIN":
            btn_f = ctk.CTkFrame(header, fg_color="transparent")
            btn_f.pack(side="right")
            ctk.CTkButton(btn_f, text="+ Thêm", width=80, fg_color="#2ecc71", command=lambda: self.customer_form()).pack(side="left", padx=5)
            ctk.CTkButton(btn_f, text="✎ Sửa", width=80, fg_color="#3498db", command=self.edit_customer).pack(side="left", padx=5)
            ctk.CTkButton(btn_f, text="🗑 Xóa", width=80, fg_color="#e64a60", command=self.delete_customer).pack(side="left", padx=5)

        self.c_tree = self.create_tree(("id", "name", "phone", "type"), ["MÃ KH", "HỌ TÊN", "SỐ ĐIỆN THOẠI", "LOẠI"])
        self.load_c_data()

    def load_c_data(self):
        for i in self.c_tree.get_children(): self.c_tree.delete(i)
        for c in self.cust_manager.get_all(): self.c_tree.insert("", "end", values=c)

    def customer_form(self, existing=None):
        win = ctk.CTkToplevel(self)
        win.title("Thông tin khách hàng")
        win.geometry("400x450")
        win.attributes("-topmost", True)
        
        labels = ["Mã KH", "Họ Tên", "Số điện thoại", "Loại khách"]
        ents = {}
        for i, l in enumerate(labels):
            ctk.CTkLabel(win, text=l).pack(padx=20, anchor="w", pady=(10, 0))
            e = ctk.CTkEntry(win, width=300)
            if existing:
                e.insert(0, existing[i])
                if i == 0: e.configure(state="disabled")
            e.pack(padx=20)
            ents[l] = e

        def handle_save():
            data = [ents[l].get() for l in labels]
            is_val, msg = Validators.validate_customer(data)
            if not is_val:
                messagebox.showerror("Lỗi", msg)
                return
            
            if existing: self.cust_manager.update(existing[0], data)
            else: self.cust_manager.add(data)
            
            self.load_c_data()
            win.destroy()

        ctk.CTkButton(win, text="LƯU KHÁCH HÀNG", fg_color="#2ecc71", command=handle_save).pack(pady=30)

    def edit_customer(self):
        sel = self.c_tree.selection()
        if sel: self.customer_form(self.c_tree.item(sel[0])['values'])
        else: messagebox.showwarning("Chú ý", "Chọn khách hàng để sửa")

    def delete_customer(self):
        sel = self.c_tree.selection()
        if sel and messagebox.askyesno("Xác nhận", "Xóa khách hàng này?"):
            self.cust_manager.delete(self.c_tree.item(sel[0])['values'][0])
            self.load_c_data()

    def create_tree(self, cols, heads):
        f = ctk.CTkFrame(self.main_content, fg_color="white", corner_radius=10)
        f.pack(fill="both", expand=True, pady=10)
        t = ttk.Treeview(f, columns=cols, show="headings")
        for i, c in enumerate(cols):
            t.heading(c, text=heads[i], anchor="w")
            t.column(c, anchor="w", width=120)
        t.pack(fill="both", expand=True, padx=10, pady=10)
        return t


class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Hệ thống Quản lý Bán hàng")
        self.geometry("1000x700") # Tăng kích thước để xem bảng dễ hơn
        self.resizable(False, False)
        
        self.shared_data = {
            "products": [["SP01", "iPhone 15", "Phone", "25M", "10"], ["SP02", "iPad Air", "Tablet", "18M", "5"]],
            "customers": [["KH01", "Nguyễn Văn A", "0901234567", "VIP"], ["KH02", "Lê Thị B", "0988776655", "Thường"]]
        }
        self.show_login_screen()

    def show_login_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar trái trang đăng nhập
        self.sidebar_frame = ctk.CTkFrame(self, fg_color="#1e1e2d", corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        # CHÈN ẢNH LOGO GIỐNG IMAGE_9552F3.PNG
        try:
            img_data = Image.open("img.png")
            my_image = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(120, 120))
            self.logo_label = ctk.CTkLabel(self.sidebar_frame, image=my_image, text="")
        except Exception:
            # Nếu lỗi, tạo Label với icon text thay thế ngay lập tức
            self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="🏪", font=("Arial", 80), text_color="white")
        
        self.logo_label.pack(pady=(60, 20))

        self.brand_label = ctk.CTkLabel(self.sidebar_frame, text="SALES MANAGER", 
                                        font=("Arial Bold", 28), text_color="white")
        self.brand_label.pack()

        self.slogan_label = ctk.CTkLabel(self.sidebar_frame, text="Hệ thống Quản lý Bán hàng Đa kênh", 
                                         font=("Arial", 15), text_color="#a0a0a0")
        self.slogan_label.pack(pady=(0, 40))

        # Bullet points
        features = ["✓  Quản lý sản phẩm & kho hàng", "✓  Đơn hàng Online & Offline", 
                    "✓  Phân tích doanh thu", "✓  Lưu trữ JSON, CSV, TXT, XML", "✓  Tích hợp API bên ngoài"]
        for feat in features:
            f_label = ctk.CTkLabel(self.sidebar_frame, text=feat, font=("Arial", 14), 
                                   text_color="white", anchor="w")
            f_label.pack(fill="x", padx=50, pady=8)

        # --- PHẦN BÊN PHẢI (LOGIN FORM) ---
        self.login_frame = ctk.CTkFrame(self, fg_color="#f8f9fc", corner_radius=0)
        self.login_frame.grid(row=0, column=1, sticky="nsew")

        self.welcome_label = ctk.CTkLabel(self.login_frame, text="Chào mừng trở lại", 
                                          font=("Arial Bold", 35), text_color="#1e1e2d")
        self.welcome_label.pack(pady=(80, 5))
        
        self.sub_label = ctk.CTkLabel(self.login_frame, text="Đăng nhập để tiếp tục", 
                                      font=("Arial", 15), text_color="#a0a0a0")
        self.sub_label.pack(pady=(0, 40))

        # Ô nhập liệu Tài khoản
        self.user_entry = ctk.CTkEntry(self.login_frame, width=350, height=45, placeholder_text="Tài khoản")
        self.user_entry.pack(pady=10)

        # Ô nhập liệu Mật khẩu
        self.pass_entry = ctk.CTkEntry(self.login_frame, width=350, height=45, show="*", placeholder_text="Mật khẩu")
        self.pass_entry.pack(pady=10)
        
        self.user_entry.bind("<Return>", lambda event: self.login_event())
        self.pass_entry.bind("<Return>", lambda event: self.login_event())

        # Nút Đăng nhập
        self.login_button = ctk.CTkButton(self.login_frame, text="ĐĂNG NHẬP", 
                                          fg_color="#e64a60", hover_color="#c23b4e",
                                          width=350, height=50, font=("Arial Bold", 16),
                                          command=self.login_event)
        self.login_button.pack(pady=30)

        # PHẦN TÀI KHOẢN DEMO (Đã được mở rộng)
        # Tăng padx lên để khung trải rộng sang hai bên
        self.demo_frame = ctk.CTkFrame(self.login_frame, fg_color="#eef5ff", corner_radius=8)
        self.demo_frame.pack(pady=20, padx=40, fill="x") # fill="x" giúp nó rộng hết cỡ theo chiều ngang
        
        demo_text = "💡 Tài khoản demo:\n      admin / admin123  (Quản trị viên)\n      staff / staff123  (Nhân viên)"
        self.demo_info = ctk.CTkLabel(self.demo_frame, text=demo_text, 
                                      font=("Arial", 14), # Tăng cỡ chữ cho dễ đọc
                                      text_color="#2c5f9e", 
                                      justify="left",
                                      anchor="w") # Căn lề trái
        self.demo_info.pack(pady=15, padx=20)

        

    def login_event(self):
        u, p = self.user_entry.get(), self.pass_entry.get()
        if u == "admin" and p == "admin123": self.show_main_window("ADMIN")
        elif u == "staff" and p == "staff123": self.show_main_window("STAFF")
        else: messagebox.showerror("Lỗi", "Sai tài khoản!")

    def show_main_window(self, role):
        for widget in self.winfo_children(): widget.destroy()
        # Truyền shared_data vào MainWindow
        self.main_view = MainWindow(self, role, self.shared_data)
        self.main_view.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()