""" models/order.py  Mô hình đối tượng Order (Đơn hàng) và OrderItem (Chi tiết đơn hàng). Nguyên lý OOP áp dụng: - Composition (Hợp thành): Order chứa danh sách các OrderItem. - Encapsulation: Tất cả thuộc tính là private, truy cập qua property. - Business Logic được đóng gói bên trong class (tính tổng tiền, trạng thái). """

from utils.helpers import generate_id, get_timestamp
from utils.validators import validate_price


class OrderItem:
    """ Đại diện cho một dòng sản phẩm trong đơn hàng. Attributes (private): __product_id (str): Mã sản phẩm tham chiếu. __product_name (str): Tên sản phẩm tại thời điểm đặt hàng. __unit_price (float): Đơn giá tại thời điểm đặt hàng. __quantity (int): Số lượng đặt. """

    def __init__(
        self,
        product_id: str,
        product_name: str,
        unit_price: float,
        quantity: int,
    ):
        if not product_id:
            raise ValueError("Mã sản phẩm không được để trống.")
        if not validate_price(unit_price):
            raise ValueError(f"Đơn giá không hợp lệ: {unit_price}")
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError(f"Số lượng phải là số nguyên > 0, nhận: {quantity}")

        self.__product_id: str = product_id
        self.__product_name: str = product_name.strip()
        self.__unit_price: float = float(unit_price)
        self.__quantity: int = quantity

    # ------------------------------------------------------------------ #
    #  GETTERS                                                             #
    # ------------------------------------------------------------------ #

    @property
    def product_id(self) -> str:
        return self.__product_id

    @property
    def product_name(self) -> str:
        return self.__product_name

    @property
    def unit_price(self) -> float:
        return self.__unit_price

    @property
    def quantity(self) -> int:
        return self.__quantity

    @property
    def subtotal(self) -> float:
        """ Thành tiền = đơn giá × số lượng. """
        return self.__unit_price * self.__quantity

    # ------------------------------------------------------------------ #
    #  METHODS                                                             #
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict:
        return {
            "product_id": self.__product_id,
            "product_name": self.__product_name,
            "unit_price": self.__unit_price,
            "quantity": self.__quantity,
            "subtotal": self.subtotal,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OrderItem":
        return cls(
            product_id=data["product_id"],
            product_name=data["product_name"],
            unit_price=float(data["unit_price"]),
            quantity=int(data["quantity"]),
        )

    def __repr__(self) -> str:
        return (
            f"OrderItem(product_id={self.__product_id!r}, "
            f"qty={self.__quantity}, subtotal={self.subtotal:,.0f}₫)"
        )


class Order:
    """ Đại diện cho một đơn hàng trong hệ thống. Attributes (private): __order_id (str): Mã định danh đơn hàng. __customer_id (str): Mã khách hàng tham chiếu. __items (list[OrderItem]): Danh sách sản phẩm trong đơn. __channel (str): Kênh bán hàng phát sinh đơn. __status (str): Trạng thái đơn hàng. __discount (float): Tỷ lệ giảm giá (0.0 – 1.0). __notes (str): Ghi chú đơn hàng. __created_at (str): Thời điểm tạo đơn. __updated_at (str): Thời điểm cập nhật gần nhất. """

    VALID_STATUSES = ("pending", "confirmed", "shipping", "completed", "cancelled")
    VALID_CHANNELS = ("online", "offline", "facebook", "shopee", "tiktok")

    def __init__(
        self,
        customer_id: str,
        channel: str = "offline",
        discount: float = 0.0,
        notes: str = "",
        order_id: str = None,
        status: str = "pending",
        created_at: str = None,
        updated_at: str = None,
        items: list = None,
    ):
        if not customer_id:
            raise ValueError("Mã khách hàng không được để trống.")

        self.__order_id: str = order_id or generate_id("ORD")
        self.__customer_id: str = customer_id
        self.__notes: str = notes.strip()
        self.__created_at: str = created_at or get_timestamp()
        self.__updated_at: str = updated_at or get_timestamp()
        self.__items: list[OrderItem] = []

        # Dùng setter để validate
        self.channel = channel
        self.status = status
        self.discount = discount

        # Khôi phục items từ dict (khi đọc file)
        if items:
            for item in items:
                if isinstance(item, dict):
                    self.__items.append(OrderItem.from_dict(item))
                elif isinstance(item, OrderItem):
                    self.__items.append(item)

    # ------------------------------------------------------------------ #
    #  GETTERS                                                             #
    # ------------------------------------------------------------------ #

    @property
    def order_id(self) -> str:
        return self.__order_id

    @property
    def customer_id(self) -> str:
        return self.__customer_id

    @property
    def items(self) -> list:
        """ Trả về bản sao để tránh chỉnh sửa trực tiếp từ bên ngoài. """
        return list(self.__items)

    @property
    def channel(self) -> str:
        return self.__channel

    @property
    def status(self) -> str:
        return self.__status

    @property
    def discount(self) -> float:
        return self.__discount

    @property
    def notes(self) -> str:
        return self.__notes

    @property
    def created_at(self) -> str:
        return self.__created_at

    @property
    def updated_at(self) -> str:
        return self.__updated_at

    @property
    def subtotal(self) -> float:
        """ Tổng tiền trước giảm giá. """
        return sum(item.subtotal for item in self.__items)

    @property
    def total_amount(self) -> float:
        """ Tổng tiền sau giảm giá. """
        return self.subtotal * (1 - self.__discount)

    @property
    def item_count(self) -> int:
        """ Tổng số lượng sản phẩm. """
        return sum(item.quantity for item in self.__items)

    # ------------------------------------------------------------------ #
    #  SETTERS                                                             #
    # ------------------------------------------------------------------ #

    @channel.setter
    def channel(self, value: str):
        if value not in self.VALID_CHANNELS:
            raise ValueError(
                f"Kênh bán hàng không hợp lệ: {value!r}. "
                f"Chọn: {self.VALID_CHANNELS}"
            )
        self.__channel = value
        self.__updated_at = get_timestamp()

    @status.setter
    def status(self, value: str):
        if value not in self.VALID_STATUSES:
            raise ValueError(
                f"Trạng thái không hợp lệ: {value!r}. "
                f"Chọn: {self.VALID_STATUSES}"
            )
        self.__status = value
        self.__updated_at = get_timestamp()

    @discount.setter
    def discount(self, value: float):
        if not isinstance(value, (int, float)) or not (0.0 <= value <= 1.0):
            raise ValueError(
                f"Tỷ lệ giảm giá phải trong khoảng [0.0, 1.0], nhận: {value}"
            )
        self.__discount = float(value)
        self.__updated_at = get_timestamp()

    @notes.setter
    def notes(self, value: str):
        self.__notes = value.strip() if value else ""
        self.__updated_at = get_timestamp()

    # ------------------------------------------------------------------ #
    #  ITEM MANAGEMENT                                                     #
    # ------------------------------------------------------------------ #

    def add_item(self, item: OrderItem):
        """ Thêm một OrderItem vào đơn hàng. Nếu sản phẩm đã tồn tại, cộng thêm số lượng. """
        if self.__status in ("completed", "cancelled"):
            raise RuntimeError(
                f"Không thể sửa đơn hàng ở trạng thái: {self.__status!r}"
            )
        for existing in self.__items:
            if existing.product_id == item.product_id:
                # Tạo item mới với số lượng cộng dồn
                merged = OrderItem(
                    product_id=existing.product_id,
                    product_name=existing.product_name,
                    unit_price=existing.unit_price,
                    quantity=existing.quantity + item.quantity,
                )
                self.__items.remove(existing)
                self.__items.append(merged)
                self.__updated_at = get_timestamp()
                return
        self.__items.append(item)
        self.__updated_at = get_timestamp()

    def remove_item(self, product_id: str):
        """ Xóa sản phẩm khỏi đơn hàng theo mã sản phẩm. """
        self.__items = [i for i in self.__items if i.product_id != product_id]
        self.__updated_at = get_timestamp()

    # ------------------------------------------------------------------ #
    #  SERIALIZATION                                                       #
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict:
        """ Chuyển đổi object thành dictionary để lưu file. """
        return {
            "order_id": self.__order_id,
            "customer_id": self.__customer_id,
            "channel": self.__channel,
            "status": self.__status,
            "discount": self.__discount,
            "notes": self.__notes,
            "items": [item.to_dict() for item in self.__items],
            "subtotal": self.subtotal,
            "total_amount": self.total_amount,
            "item_count": self.item_count,
            "created_at": self.__created_at,
            "updated_at": self.__updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Order":
        """ Tạo object Order từ dictionary (đọc từ file). """
        return cls(
            customer_id=data["customer_id"],
            channel=data.get("channel", "offline"),
            discount=float(data.get("discount", 0.0)),
            notes=data.get("notes", ""),
            order_id=data.get("order_id"),
            status=data.get("status", "pending"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            items=data.get("items", []),
        )

    def __repr__(self) -> str:
        return (
            f"Order(id={self.__order_id!r}, customer={self.__customer_id!r}, "
            f"status={self.__status!r}, total={self.total_amount:,.0f}₫)"
        )

    def __str__(self) -> str:
        return (
            f"[{self.__order_id}] KH: {self.__customer_id} | "
            f"Kênh: {self.__channel} | "
            f"TT: {self.__status} | "
            f"Tổng: {self.total_amount:,.0f}₫"
        )
