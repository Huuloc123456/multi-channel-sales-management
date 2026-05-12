"""
data_processing/customer_manager.py
=====================================
Manager xử lý nghiệp vụ liên quan đến Khách hàng.
"""

import logging
from typing import Optional

from .base_manager import BaseManager
from models.customer import Customer

logger = logging.getLogger(__name__)

DEFAULT_CUSTOMER_FILE = "data/customers.json"


class CustomerManager(BaseManager):
    """
    Quản lý CRUD cho entity Customer.
    """

    def __init__(self, data_file: str = DEFAULT_CUSTOMER_FILE):
        super().__init__(data_file)

    # ------------------------------------------------------------------ #
    #  OVERRIDE HOOKS                                                      #
    # ------------------------------------------------------------------ #

    def _from_dict(self, data: dict) -> Customer:
        return Customer.from_dict(data)

    def _get_entity_id(self, entity: Customer) -> str:
        return entity.customer_id

    # ------------------------------------------------------------------ #
    #  DOMAIN-SPECIFIC METHODS                                            #
    # ------------------------------------------------------------------ #

    def get_by_email(self, email: str) -> Optional[Customer]:
        """Tìm khách hàng theo email (định danh duy nhất)."""
        email_lower = email.strip().lower()
        for customer in self.get_all():
            if customer.email == email_lower:
                return customer
        return None

    def get_by_phone(self, phone: str) -> Optional[Customer]:
        """Tìm khách hàng theo số điện thoại."""
        results = self.search(phone=phone)
        return results[0] if results else None

    def add_points(self, customer_id: str, points: int) -> bool:
        """
        Cộng điểm tích lũy cho khách hàng.

        Returns:
            bool: True nếu thành công.
        """
        customer = self.get_by_id(customer_id)
        if not customer:
            return False
        try:
            customer.add_loyalty_points(points)
            return self.update(customer)
        except ValueError as exc:
            logger.error("Lỗi cộng điểm: %s", exc)
            return False

    def redeem_points(self, customer_id: str, points: int) -> bool:
        """
        Trừ điểm khi khách hàng đổi ưu đãi.

        Returns:
            bool: True nếu thành công, False nếu không đủ điểm.
        """
        customer = self.get_by_id(customer_id)
        if not customer:
            return False
        try:
            customer.redeem_points(points)
            return self.update(customer)
        except ValueError as exc:
            logger.error("Lỗi đổi điểm: %s", exc)
            return False

    def is_email_taken(self, email: str) -> bool:
        """Kiểm tra email đã được đăng ký chưa."""
        return self.get_by_email(email) is not None

    def get_top_customers(self, n: int = 10) -> list[Customer]:
        """Lấy n khách hàng có điểm tích lũy cao nhất."""
        customers = self.get_all()
        return sorted(customers, key=lambda c: c.loyalty_points, reverse=True)[:n]
