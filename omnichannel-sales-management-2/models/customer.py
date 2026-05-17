"""
customer.py

Định nghĩa mô hình dữ liệu Khách hàng (Customer) bằng dataclass.
"""

from dataclasses import dataclass
from typing import Dict, Any

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
