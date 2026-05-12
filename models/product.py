"""
models/product.py
=================
Mô hình đối tượng Product (Sản phẩm).

Nguyên lý OOP áp dụng:
- Encapsulation (Bao đóng): Tất cả thuộc tính được khai báo là private
  (tiền tố __) và chỉ được truy cập qua getter/setter.
- Abstraction (Trừu tượng hóa): Ẩn đi chi tiết triển khai bên trong,
  chỉ công khai giao diện cần thiết.
"""

from datetime import datetime
from utils.helpers import generate_id, get_timestamp
from utils.validators import validate_price


class Product:
    """
    Đại diện cho một sản phẩm trong hệ thống bán hàng.

    Attributes (private):
        __product_id (str): Mã định danh duy nhất của sản phẩm.
        __name (str): Tên sản phẩm.
        __price (float): Giá bán sản phẩm (VND).
        __quantity (int): Số lượng tồn kho.
        __category (str): Danh mục sản phẩm.
        __channel (str): Kênh bán hàng (online/offline/both).
        __created_at (str): Thời điểm tạo bản ghi.
        __updated_at (str): Thời điểm cập nhật gần nhất.
    """

    VALID_CHANNELS = ("online", "offline", "both")

    def __init__(
        self,
        name: str,
        price: float,
        quantity: int,
        category: str = "Chưa phân loại",
        channel: str = "both",
        product_id: str = None,
        created_at: str = None,
        updated_at: str = None,
    ):
        self.__product_id: str = product_id or generate_id("PRD")
        self.__name: str = name.strip()
        self.__category: str = category.strip()
        self.__channel: str = channel if channel in self.VALID_CHANNELS else "both"
        self.__created_at: str = created_at or get_timestamp()
        self.__updated_at: str = updated_at or get_timestamp()

        # Dùng setter để tận dụng validation
        self.price = price
        self.quantity = quantity

    # ------------------------------------------------------------------ #
    #  GETTERS                                                             #
    # ------------------------------------------------------------------ #

    @property
    def product_id(self) -> str:
        return self.__product_id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def price(self) -> float:
        return self.__price

    @property
    def quantity(self) -> int:
        return self.__quantity

    @property
    def category(self) -> str:
        return self.__category

    @property
    def channel(self) -> str:
        return self.__channel

    @property
    def created_at(self) -> str:
        return self.__created_at

    @property
    def updated_at(self) -> str:
        return self.__updated_at

    # ------------------------------------------------------------------ #
    #  SETTERS  (có validation)                                           #
    # ------------------------------------------------------------------ #

    @name.setter
    def name(self, value: str):
        if not value or not value.strip():
            raise ValueError("Tên sản phẩm không được để trống.")
        self.__name = value.strip()
        self.__updated_at = get_timestamp()

    @price.setter
    def price(self, value: float):
        if not validate_price(value):
            raise ValueError(f"Giá sản phẩm không hợp lệ: {value}. Phải >= 0.")
        self.__price = float(value)
        self.__updated_at = get_timestamp()

    @quantity.setter
    def quantity(self, value: int):
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"Số lượng không hợp lệ: {value}. Phải là số nguyên >= 0.")
        self.__quantity = value
        self.__updated_at = get_timestamp()

    @category.setter
    def category(self, value: str):
        self.__category = value.strip() if value else "Chưa phân loại"
        self.__updated_at = get_timestamp()

    @channel.setter
    def channel(self, value: str):
        if value not in self.VALID_CHANNELS:
            raise ValueError(
                f"Kênh bán hàng không hợp lệ: {value}. "
                f"Chọn một trong: {self.VALID_CHANNELS}"
            )
        self.__channel = value
        self.__updated_at = get_timestamp()

    # ------------------------------------------------------------------ #
    #  METHODS                                                             #
    # ------------------------------------------------------------------ #

    def update_stock(self, delta: int):
        """
        Cộng/trừ số lượng tồn kho.

        Args:
            delta (int): Giá trị thay đổi (dương: nhập hàng, âm: bán hàng).

        Raises:
            ValueError: Nếu số lượng sau khi thay đổi < 0.
        """
        new_qty = self.__quantity + delta
        if new_qty < 0:
            raise ValueError(
                f"Không đủ tồn kho. Hiện có: {self.__quantity}, cần giảm: {abs(delta)}."
            )
        self.__quantity = new_qty
        self.__updated_at = get_timestamp()

    def to_dict(self) -> dict:
        """Chuyển đổi object thành dictionary để lưu file."""
        return {
            "product_id": self.__product_id,
            "name": self.__name,
            "price": self.__price,
            "quantity": self.__quantity,
            "category": self.__category,
            "channel": self.__channel,
            "created_at": self.__created_at,
            "updated_at": self.__updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        """Tạo object Product từ dictionary (đọc từ file)."""
        return cls(
            name=data["name"],
            price=float(data["price"]),
            quantity=int(data["quantity"]),
            category=data.get("category", "Chưa phân loại"),
            channel=data.get("channel", "both"),
            product_id=data.get("product_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def __repr__(self) -> str:
        return (
            f"Product(id={self.__product_id!r}, name={self.__name!r}, "
            f"price={self.__price:,.0f}₫, qty={self.__quantity})"
        )

    def __str__(self) -> str:
        return f"[{self.__product_id}] {self.__name} - {self.__price:,.0f}₫ (SL: {self.__quantity})"
