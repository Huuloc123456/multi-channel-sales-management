from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Product:
    product_id: str
    name: str
    price: float
    quantity: int
    category: str = "Chưa phân loại"
    channel: str = "both"

    def to_dict(self) -> Dict[str, Any]:
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
        return cls(
            product_id=data["product_id"],
            name=data["name"],
            price=float(data["price"]),
            quantity=int(data["quantity"]),
            category=data.get("category", "Chưa phân loại"),
            channel=data.get("channel", "both")
        )
