"""
order_repository.py

Lớp quản lý lưu trữ và thực hiện CRUD dữ liệu Đơn hàng.
"""

import os
from typing import List, Optional
from file_handlers import JSONFileHandler
from models import Order
from utils import get_absolute_path

class OrderRepository:
    """Lớp quản lý lưu trữ và thực hiện CRUD dữ liệu Đơn hàng."""
    def __init__(self, filepath: str = None):
        # Đảm bảo đường dẫn tuyệt đối riêng biệt cho Project 2
        self.filepath = filepath or get_absolute_path("data", "orders.json")
        self.handler = JSONFileHandler(self.filepath)
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
