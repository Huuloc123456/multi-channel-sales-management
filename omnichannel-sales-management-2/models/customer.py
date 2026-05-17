from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Customer:
    customer_id: str
    full_name: str
    email: str
    phone: str
    address: str = ""
    loyalty_points: int = 0

    def to_dict(self) -> Dict[str, Any]:
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
        return cls(
            customer_id=data["customer_id"],
            full_name=data["full_name"],
            email=data["email"],
            phone=data["phone"],
            address=data.get("address", ""),
            loyalty_points=int(data.get("loyalty_points", 0))
        )
