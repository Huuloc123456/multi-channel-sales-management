"""
order.py

Định nghĩa mô hình dữ liệu Đơn hàng (Order) bằng dataclass.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
import datetime

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
