"""
data_processing/product_manager.py
====================================
Manager xử lý nghiệp vụ liên quan đến Sản phẩm.
"""

import logging
from typing import Optional

from .base_manager import BaseManager
from models.product import Product

logger = logging.getLogger(__name__)

DEFAULT_PRODUCT_FILE = "data/products.json"


class ProductManager(BaseManager):
    """
    Quản lý CRUD cho entity Product.

    Kế thừa từ BaseManager và triển khai:
        - _from_dict()      → Product.from_dict()
        - _get_entity_id()  → product.product_id
    """

    def __init__(self, data_file: str = DEFAULT_PRODUCT_FILE):
        super().__init__(data_file)

    # ------------------------------------------------------------------ #
    #  OVERRIDE HOOKS                                                      #
    # ------------------------------------------------------------------ #

    def _from_dict(self, data: dict) -> Product:
        return Product.from_dict(data)

    def _get_entity_id(self, entity: Product) -> str:
        return entity.product_id

    # ------------------------------------------------------------------ #
    #  DOMAIN-SPECIFIC METHODS                                            #
    # ------------------------------------------------------------------ #

    def get_by_category(self, category: str) -> list[Product]:
        """Lọc sản phẩm theo danh mục."""
        return self.search(category=category)

    def get_by_channel(self, channel: str) -> list[Product]:
        """Lọc sản phẩm theo kênh bán hàng."""
        return self.search(channel=channel)

    def get_low_stock(self, threshold: int = 5) -> list[Product]:
        """Lấy danh sách sản phẩm sắp hết hàng (tồn kho <= threshold)."""
        return [p for p in self.get_all() if p.quantity <= threshold]

    def update_stock(self, product_id: str, delta: int) -> bool:
        """
        Điều chỉnh tồn kho theo delta.

        Args:
            product_id (str): Mã sản phẩm.
            delta (int): Thay đổi số lượng (dương: nhập, âm: bán).

        Returns:
            bool: True nếu thành công.
        """
        product = self.get_by_id(product_id)
        if not product:
            logger.warning("Không tìm thấy sản phẩm: %s", product_id)
            return False
        try:
            product.update_stock(delta)
            return self.update(product)
        except ValueError as exc:
            logger.error("Lỗi cập nhật tồn kho: %s", exc)
            return False

    def get_statistics(self) -> dict:
        """
        Thống kê tổng quan danh mục sản phẩm.

        Returns:
            dict: Tổng số SP, tổng giá trị tồn kho, số SP hết hàng.
        """
        products = self.get_all()
        total_value = sum(p.price * p.quantity for p in products)
        out_of_stock = sum(1 for p in products if p.quantity == 0)
        return {
            "total_products": len(products),
            "total_inventory_value": total_value,
            "out_of_stock_count": out_of_stock,
            "low_stock_count": len(self.get_low_stock()),
        }
