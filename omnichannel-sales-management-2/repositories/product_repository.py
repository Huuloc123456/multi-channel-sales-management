import os
from typing import List, Optional
from file_handlers import JSONFileHandler
from models import Product
from utils import get_absolute_path

class ProductRepository:
    def __init__(self, filepath: str = None):
        self.filepath = filepath or get_absolute_path("data", "products.json")
        self.handler = JSONFileHandler(self.filepath)
        self.products: List[Product] = []
        self._nap_du_lieu()

    def _nap_du_lieu(self):
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
            self.products = []

    def _luu_du_lieu(self) -> bool:
        data = [p.to_dict() for p in self.products]
        return self.handler.ghi(data)

    def create(self, product: Product) -> bool:
        if self.get_by_id(product.product_id):
            raise ValueError(f"Mã sản phẩm {product.product_id} đã tồn tại trong hệ thống!")
        
        self.products.append(product)
        return self._luu_du_lieu()

    def get_all(self) -> List[Product]:
        self._nap_du_lieu()
        return self.products

    def get_by_id(self, product_id: str) -> Optional[Product]:
        self._nap_du_lieu()
        for p in self.products:
            if p.product_id.strip().upper() == product_id.strip().upper():
                return p
        return None

    def update(self, product_id: str, name: str, price: float, quantity: int, category: str, channel: str) -> bool:
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
        product = self.get_by_id(product_id)
        if not product:
            raise ValueError(f"Không tìm thấy sản phẩm có mã {product_id} để xóa!")
        
        self.products.remove(product)
        return self._luu_du_lieu()
