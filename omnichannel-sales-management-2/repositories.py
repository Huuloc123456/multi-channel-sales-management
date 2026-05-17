"""
repositories.py

Các lớp kho lưu trữ dữ liệu (Repositories) cho Hệ thống Quản lý Bán hàng Đa kênh.
Sử dụng JSONFileHandler để thực hiện các thao tác CRUD dữ liệu được lưu trữ trong thư mục /data/.

Các Repository chính:
- ProductRepository (Quản lý sản phẩm)
- CustomerRepository (Quản lý khách hàng)
- OrderRepository (Quản lý đơn hàng)
"""

import os
from typing import List, Optional, Dict, Any
from file_handlers import JSONFileHandler
from models import Product, Customer, Order

class ProductRepository:
    """Lớp quản lý lưu trữ và thực hiện CRUD dữ liệu Sản phẩm."""
    def __init__(self, filepath: str = "data/products.json"):
        self.filepath = filepath
        self.handler = JSONFileHandler(filepath)
        self.products: List[Product] = []
        self._nap_du_lieu()

    def _nap_du_lieu(self):
        """Đọc dữ liệu từ file JSON vào bộ nhớ RAM khi khởi tạo."""
        if not os.path.exists(self.filepath):
            self.products = []
            return
        
        try:
            data = self.handler.doc()
            if isinstance(data, list):
                self.products = [Product.from_dict(d) for d in data]
            else:
                self.products = []
        except Exception:
            # Nếu file rỗng hoặc lỗi cấu trúc khi khởi tạo, cho mảng rỗng
            self.products = []

    def _luu_du_lieu(self) -> bool:
        """Ghi đè danh sách sản phẩm hiện tại vào file JSON thông qua Handler."""
        data = [p.to_dict() for p in self.products]
        return self.handler.ghi(data)

    # --- CÁC PHƯƠNG THỨC CRUD ---

    def create(self, product: Product) -> bool:
        """(C) - Thêm mới một sản phẩm."""
        # Kiểm tra trùng ID sản phẩm
        if self.get_by_id(product.product_id):
            raise ValueError(f"Mã sản phẩm {product.product_id} đã tồn tại trong hệ thống!")
        
        self.products.append(product)
        return self._luu_du_lieu()

    def get_all(self) -> List[Product]:
        """(R) - Xem danh sách tất cả sản phẩm."""
        self._nap_du_lieu() # Nạp lại dữ liệu mới nhất từ file
        return self.products

    def get_by_id(self, product_id: str) -> Optional[Product]:
        """(R) - Tìm kiếm sản phẩm theo ID."""
        self._nap_du_lieu()
        for p in self.products:
            if p.product_id.strip().upper() == product_id.strip().upper():
                return p
        return None

    def update(self, product_id: str, name: str, price: float, quantity: int, category: str, channel: str) -> bool:
        """(U) - Sửa thông tin sản phẩm."""
        product = self.get_by_id(product_id)
        if not product:
            raise ValueError(f"Không tìm thấy sản phẩm có mã {product_id} để sửa đổi!")

        product.name = name.strip()
        product.price = price
        product.quantity = quantity
        product.category = category.strip()
        product.channel = channel.strip()
        
        return self._luu_du_lieu()

    def delete(self, product_id: str) -> bool:
        """(D) - Xóa sản phẩm khỏi danh sách."""
        product = self.get_by_id(product_id)
        if not product:
            raise ValueError(f"Không tìm thấy sản phẩm có mã {product_id} để xóa!")
        
        self.products.remove(product)
        return self._luu_du_lieu()


class CustomerRepository:
    """Lớp quản lý lưu trữ và thực hiện CRUD dữ liệu Khách hàng."""
    def __init__(self, filepath: str = "data/customers.json"):
        self.filepath = filepath
        self.handler = JSONFileHandler(filepath)
        self.customers: List[Customer] = []
        self._nap_du_lieu()

    def _nap_du_lieu(self):
        """Đọc dữ liệu từ file JSON vào bộ nhớ RAM khi khởi tạo."""
        if not os.path.exists(self.filepath):
            self.customers = []
            return
        
        try:
            data = self.handler.doc()
            if isinstance(data, list):
                self.customers = [Customer.from_dict(d) for d in data]
            else:
                self.customers = []
        except Exception:
            self.customers = []

    def _luu_du_lieu(self) -> bool:
        """Ghi danh sách khách hàng vào file JSON."""
        data = [c.to_dict() for c in self.customers]
        return self.handler.ghi(data)

    # --- CÁC PHƯƠNG THỨC CRUD ---

    def create(self, customer: Customer) -> bool:
        """(C) - Thêm mới khách hàng."""
        if self.get_by_id(customer.customer_id):
            raise ValueError(f"Mã khách hàng {customer.customer_id} đã tồn tại!")
        
        self.customers.append(customer)
        return self._luu_du_lieu()

    def get_all(self) -> List[Customer]:
        """(R) - Xem danh sách khách hàng."""
        self._nap_du_lieu()
        return self.customers

    def get_by_id(self, customer_id: str) -> Optional[Customer]:
        """(R) - Tìm khách hàng theo ID."""
        self._nap_du_lieu()
        for c in self.customers:
            if c.customer_id.strip().upper() == customer_id.strip().upper():
                return c
        return None

    def update(self, customer_id: str, full_name: str, email: str, phone: str, address: str, loyalty_points: int) -> bool:
        """(U) - Cập nhật thông tin khách hàng."""
        customer = self.get_by_id(customer_id)
        if not customer:
            raise ValueError(f"Không tìm thấy khách hàng có mã {customer_id}!")

        customer.full_name = full_name.strip()
        customer.email = email.strip()
        customer.phone = phone.strip()
        customer.address = address.strip()
        customer.loyalty_points = loyalty_points
        
        return self._luu_du_lieu()

    def delete(self, customer_id: str) -> bool:
        """(D) - Xóa khách hàng."""
        customer = self.get_by_id(customer_id)
        if not customer:
            raise ValueError(f"Không tìm thấy khách hàng có mã {customer_id}!")
        
        self.customers.remove(customer)
        return self._luu_du_lieu()


class OrderRepository:
    """Lớp quản lý lưu trữ và thực hiện CRUD dữ liệu Đơn hàng."""
    def __init__(self, filepath: str = "data/orders.json"):
        self.filepath = filepath
        self.handler = JSONFileHandler(filepath)
        self.orders: List[Order] = []
        self._nap_du_lieu()

    def _nap_du_lieu(self):
        """Đọc dữ liệu từ file JSON khi khởi tạo."""
        if not os.path.exists(self.filepath):
            self.orders = []
            return
        
        try:
            data = self.handler.doc()
            if isinstance(data, list):
                self.orders = [Order.from_dict(d) for d in data]
            else:
                self.orders = []
        except Exception:
            self.orders = []

    def _luu_du_lieu(self) -> bool:
        """Ghi danh sách đơn hàng vào file JSON."""
        data = [o.to_dict() for o in self.orders]
        return self.handler.ghi(data)

    # --- CÁC PHƯƠNG THỨC CRUD ---

    def create(self, order: Order) -> bool:
        """(C) - Thêm mới đơn hàng."""
        if self.get_by_id(order.order_id):
            raise ValueError(f"Mã đơn hàng {order.order_id} đã tồn tại!")
        
        self.orders.append(order)
        return self._luu_du_lieu()

    def get_all(self) -> List[Order]:
        """(R) - Xem toàn bộ đơn hàng."""
        self._nap_du_lieu()
        return self.orders

    def get_by_id(self, order_id: str) -> Optional[Order]:
        """(R) - Tìm đơn hàng theo ID."""
        self._nap_du_lieu()
        for o in self.orders:
            if o.order_id.strip().upper() == order_id.strip().upper():
                return o
        return None

    def update(self, order_id: str, status: str) -> bool:
        """(U) - Cập nhật trạng thái đơn hàng (đơn giản hóa)."""
        order = self.get_by_id(order_id)
        if not order:
            raise ValueError(f"Không tìm thấy đơn hàng có mã {order_id}!")

        order.status = status.strip()
        return self._luu_du_lieu()

    def delete(self, order_id: str) -> bool:
        """(D) - Xóa đơn hàng."""
        order = self.get_by_id(order_id)
        if not order:
            raise ValueError(f"Không tìm thấy đơn hàng có mã {order_id}!")
        
        self.orders.remove(order)
        return self._luu_du_lieu()
