"""
data_processing/order_manager.py
==================================
Manager xử lý nghiệp vụ liên quan đến Đơn hàng.
"""

import logging
from typing import Optional

from .base_manager import BaseManager
from models.order import Order
from utils.helpers import get_timestamp

logger = logging.getLogger(__name__)

DEFAULT_ORDER_FILE = "data/orders.json"


class OrderManager(BaseManager):
    """
    Quản lý CRUD cho entity Order.

    Bổ sung các nghiệp vụ:
        - Thay đổi trạng thái đơn hàng theo luồng hợp lệ.
        - Thống kê doanh thu theo kênh, thời gian.
    """

    # Luồng chuyển trạng thái hợp lệ
    _STATUS_TRANSITIONS = {
        "pending":   ["confirmed", "cancelled"],
        "confirmed": ["shipping", "cancelled"],
        "shipping":  ["completed", "cancelled"],
        "completed": [],   # Trạng thái cuối
        "cancelled": [],   # Trạng thái cuối
    }

    def __init__(self, data_file: str = DEFAULT_ORDER_FILE):
        super().__init__(data_file)

    # ------------------------------------------------------------------ #
    #  OVERRIDE HOOKS                                                      #
    # ------------------------------------------------------------------ #

    def _from_dict(self, data: dict) -> Order:
        return Order.from_dict(data)

    def _get_entity_id(self, entity: Order) -> str:
        return entity.order_id

    # ------------------------------------------------------------------ #
    #  DOMAIN-SPECIFIC METHODS                                            #
    # ------------------------------------------------------------------ #

    def get_by_customer(self, customer_id: str) -> list[Order]:
        """Lấy tất cả đơn hàng của một khách hàng."""
        return self.search(customer_id=customer_id)

    def get_by_channel(self, channel: str) -> list[Order]:
        """Lấy đơn hàng theo kênh bán."""
        return self.search(channel=channel)

    def get_by_status(self, status: str) -> list[Order]:
        """Lấy đơn hàng theo trạng thái."""
        return self.search(status=status)

    def change_status(self, order_id: str, new_status: str) -> bool:
        """
        Thay đổi trạng thái đơn hàng theo luồng hợp lệ.

        Args:
            order_id (str): Mã đơn hàng.
            new_status (str): Trạng thái mới.

        Returns:
            bool: True nếu chuyển trạng thái thành công.
        """
        order = self.get_by_id(order_id)
        if not order:
            logger.warning("Không tìm thấy đơn hàng: %s", order_id)
            return False

        allowed = self._STATUS_TRANSITIONS.get(order.status, [])
        if new_status not in allowed:
            logger.warning(
                "Không thể chuyển đơn %s từ '%s' sang '%s'. Cho phép: %s",
                order_id, order.status, new_status, allowed
            )
            return False

        try:
            order.status = new_status
            return self.update(order)
        except ValueError as exc:
            logger.error("Lỗi chuyển trạng thái: %s", exc)
            return False

    def get_revenue_by_channel(self) -> dict:
        """
        Tổng hợp doanh thu theo kênh bán hàng.

        Returns:
            dict: {channel: total_revenue}
        """
        orders = [o for o in self.get_all() if o.status == "completed"]
        revenue = {}
        for order in orders:
            revenue[order.channel] = revenue.get(order.channel, 0) + order.total_amount
        return revenue

    def get_statistics(self) -> dict:
        """
        Thống kê tổng quan đơn hàng.

        Returns:
            dict: Tổng đơn, doanh thu, đơn hủy, đơn hoàn thành.
        """
        orders = self.get_all()
        completed = [o for o in orders if o.status == "completed"]
        cancelled = [o for o in orders if o.status == "cancelled"]
        total_revenue = sum(o.total_amount for o in completed)
        return {
            "total_orders": len(orders),
            "completed_orders": len(completed),
            "cancelled_orders": len(cancelled),
            "pending_orders": len([o for o in orders if o.status == "pending"]),
            "total_revenue": total_revenue,
            "avg_order_value": total_revenue / len(completed) if completed else 0,
            "revenue_by_channel": self.get_revenue_by_channel(),
        }
