"""
models.py

Định nghĩa các mô hình dữ liệu (Models) cho Hệ thống Quản lý Bán hàng Đa kênh.
Sử dụng thư viện chuẩn dataclass để cấu trúc các mô hình đơn giản hóa, tinh giản cho bài thực hành.

Mô hình bao gồm:
- Product (Sản phẩm)
- Customer (Khách hàng)
- Order (Đơn hàng)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import datetime

@dataclass
class Product:
    """Mô hình dữ liệu Sản phẩm."""
    product_id: str
    name: str
    price: float
    quantity: int
    category: str = "Chưa phân loại"
    channel: str = "both"  # online, offline, both

    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi đối tượng sản phẩm thành Dictionary để lưu file JSON/CSV."""
        return {
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "category": self.category,
            "channel": self.channel
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Product':
        """Khởi tạo đối tượng Product từ dữ liệu Dictionary (đọc từ file)."""
        return cls(
            product_id=data["product_id"],
            name=data["name"],
            price=float(data["price"]),
            quantity=int(data["quantity"]),
            category=data.get("category", "Chưa phân loại"),
            channel=data.get("channel", "both")
        )


@dataclass
class Customer:
    """Mô hình dữ liệu Khách hàng."""
    customer_id: str
    full_name: str
    email: str
    phone: str
    address: str = ""
    loyalty_points: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi đối tượng khách hàng thành Dictionary."""
        return {
            "customer_id": self.customer_id,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "loyalty_points": self.loyalty_points
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Customer':
        """Khởi tạo đối tượng Customer từ dữ liệu Dictionary."""
        return cls(
            customer_id=data["customer_id"],
            full_name=data["full_name"],
            email=data["email"],
            phone=data["phone"],
            address=data.get("address", ""),
            loyalty_points=int(data.get("loyalty_points", 0))
        )


@dataclass
class Order:
    """Mô hình dữ liệu Đơn hàng."""
    order_id: str
    customer_id: str
    items: List[Dict[str, Any]] = field(default_factory=list)  # Cấu trúc: [{"product_id": ..., "quantity": ..., "price": ...}]
    channel: str = "offline"  # shopee, lazada, tiktok, facebook, offline
    payment_method: str = "cash"  # cash, card, momo, vnpay
    total_amount: float = 0.0
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi đối tượng đơn hàng thành Dictionary."""
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "items": self.items,
            "channel": self.channel,
            "payment_method": self.payment_method,
            "total_amount": self.total_amount,
            "status": self.status,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Order':
        """Khởi tạo đối tượng Order từ dữ liệu Dictionary."""
        return cls(
            order_id=data["order_id"],
            customer_id=data["customer_id"],
            items=data.get("items", []),
            channel=data.get("channel", "offline"),
            payment_method=data.get("payment_method", "cash"),
            total_amount=float(data.get("total_amount", 0.0)),
            status=data.get("status", "pending"),
            created_at=data.get("created_at", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
