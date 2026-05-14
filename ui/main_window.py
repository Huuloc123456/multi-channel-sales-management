import customtkinter as ctk # Sửa lỗi "ctk is not defined"
from tkinter import ttk
from managers.product_manager import ProductManager # Sửa lỗi "ProductManager is not defined"
from models.product import Product # Sửa lỗi "Product is not defined" trong hàm add_product
from utils.validators import validate_product_data # Để dùng ở Bước 1 (Validate) [cite: 20]

class ProductManagerFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="white")
        self.manager = ProductManager() # Khởi tạo Manager theo quy tắc [cite: 16]

        # Tiêu đề
        ctk.CTkLabel(self, text="Quản lý Sản phẩm", font=("Arial", 20, "bold")).pack(anchor="w", padx=20, pady=20)

        # --- KHU VỰC NHẬP LIỆU (Form Thêm/Sửa) ---
        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.form_frame.pack(fill="x", padx=20)

        self.name_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Tên sản phẩm") # [cite: 17]
        self.name_entry.pack(side="left", padx=5)
        
        self.price_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Giá") # [cite: 17]
        self.price_entry.pack(side="left", padx=5)

        self.btn_add = ctk.CTkButton(self.form_frame, text="Thêm mới", command=self.add_product) # [cite: 17]
        self.btn_add.pack(side="left", padx=5)

        # --- BẢNG HIỂN THỊ (Treeview) ---
        style = ttk.Style()
        style.configure("Treeview", rowheight=30, font=("Arial", 10))
        
        self.tree = ttk.Treeview(self, columns=("ID", "Name", "Price"), show="headings") # [cite: 18]
        self.tree.heading("ID", text="Mã SP")
        self.tree.heading("Name", text="Tên Sản Phẩm")
        self.tree.heading("Price", text="Đơn Giá")
        self.tree.pack(fill="both", expand=True, padx=20, pady=20)

        self.refresh_table()

    def refresh_table(self):
        # Xóa trắng bảng [cite: 19]
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Lấy data từ Manager (KHÔNG đọc file trực tiếp ở đây) [cite: 19]
        for p in self.manager.get_all():
            self.tree.insert("", "end", values=(p.id, p.name, f"{p.price:,} đ"))

    def add_product(self):
        # BƯỚC 1: Sử dụng hàm validate từ utils/validators.py
        name = self.name_entry.get()
        price = self.price_entry.get()
        
        # Giả sử mặc định stock là 10 cho sản phẩm mới
        is_valid, message = validate_product_data(name, price, 10)
        
        if not is_valid:
            # Bạn có thể dùng messagebox để hiện lỗi cho người dùng
            print(f"Lỗi nhập liệu: {message}") 
            return

        # BƯỚC 2: Tạo Object Product sau khi đã import thành công [cite: 20]
        new_p = Product(id="P01", name=name, price=int(price), stock=10)
        
        # BƯỚC 3: Lưu qua Manager [cite: 20]
        self.manager.add(new_p)
        self.refresh_table()
        
        # Xóa trống ô nhập sau khi thêm thành công
        self.name_entry.delete(0, 'end')
        self.price_entry.delete(0, 'end')