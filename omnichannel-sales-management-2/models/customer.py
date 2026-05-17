""" models/customer.py  Mô hình đối tượng Customer (Khách hàng). Nguyên lý OOP áp dụng: - Encapsulation (Bao đóng): Thuộc tính private, truy cập qua property. - Validation trong setter đảm bảo tính toàn vẹn dữ liệu. """

from utils.helpers import generate_id, get_timestamp
from utils.validators import validate_email, validate_phone


class Customer:
    """ Đại diện cho một khách hàng trong hệ thống. Attributes (private): __customer_id (str): Mã định danh duy nhất. __full_name (str): Họ và tên khách hàng. __email (str): Địa chỉ email (dùng làm định danh đăng nhập). __phone (str): Số điện thoại liên hệ. __address (str): Địa chỉ giao hàng. __loyalty_points (int): Điểm tích lũy thành viên. __created_at (str): Thời điểm đăng ký. __updated_at (str): Thời điểm cập nhật gần nhất. """

    def __init__(
        self,
        full_name: str,
        email: str,
        phone: str,
        address: str = "",
        loyalty_points: int = 0,
        customer_id: str = None,
        created_at: str = None,
        updated_at: str = None,
    ):
        self.__customer_id: str = customer_id or generate_id("CUS")
        self.__address: str = address.strip()
        self.__created_at: str = created_at or get_timestamp()
        self.__updated_at: str = updated_at or get_timestamp()

        # Dùng setter để validate ngay khi khởi tạo
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.loyalty_points = loyalty_points

    # ------------------------------------------------------------------ #
    #  GETTERS                                                             #
    # ------------------------------------------------------------------ #

    @property
    def customer_id(self) -> str:
        return self.__customer_id

    @property
    def full_name(self) -> str:
        return self.__full_name

    @property
    def email(self) -> str:
        return self.__email

    @property
    def phone(self) -> str:
        return self.__phone

    @property
    def address(self) -> str:
        return self.__address

    @property
    def loyalty_points(self) -> int:
        return self.__loyalty_points

    @property
    def created_at(self) -> str:
        return self.__created_at

    @property
    def updated_at(self) -> str:
        return self.__updated_at

    # ------------------------------------------------------------------ #
    #  SETTERS                                                             #
    # ------------------------------------------------------------------ #

    @full_name.setter
    def full_name(self, value: str):
        if not value or not value.strip():
            raise ValueError("Họ tên khách hàng không được để trống.")
        self.__full_name = value.strip()
        self.__updated_at = get_timestamp()

    @email.setter
    def email(self, value: str):
        if not validate_email(value):
            raise ValueError(f"Địa chỉ email không hợp lệ: {value!r}")
        self.__email = value.strip().lower()
        self.__updated_at = get_timestamp()

    @phone.setter
    def phone(self, value: str):
        if not validate_phone(value):
            raise ValueError(f"Số điện thoại không hợp lệ: {value!r}")
        self.__phone = value.strip()
        self.__updated_at = get_timestamp()

    @address.setter
    def address(self, value: str):
        self.__address = value.strip() if value else ""
        self.__updated_at = get_timestamp()

    @loyalty_points.setter
    def loyalty_points(self, value: int):
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"Điểm tích lũy không hợp lệ: {value}. Phải >= 0.")
        self.__loyalty_points = value
        self.__updated_at = get_timestamp()

    # ------------------------------------------------------------------ #
    #  METHODS                                                             #
    # ------------------------------------------------------------------ #

    def add_loyalty_points(self, points: int):
        """ Cộng điểm tích lũy sau mỗi giao dịch mua hàng. Args: points (int): Số điểm cộng thêm (phải > 0). """
        if points <= 0:
            raise ValueError("Số điểm cộng phải > 0.")
        self.__loyalty_points += points
        self.__updated_at = get_timestamp()

    def redeem_points(self, points: int):
        """ Trừ điểm khi khách hàng đổi ưu đãi. Args: points (int): Số điểm cần trừ. Raises: ValueError: Nếu điểm hiện tại không đủ. """
        if points <= 0:
            raise ValueError("Số điểm đổi phải > 0.")
        if self.__loyalty_points < points:
            raise ValueError(
                f"Điểm không đủ. Hiện có: {self.__loyalty_points}, cần: {points}."
            )
        self.__loyalty_points -= points
        self.__updated_at = get_timestamp()

    def to_dict(self) -> dict:
        """ Chuyển đổi object thành dictionary để lưu file. """
        return {
            "customer_id": self.__customer_id,
            "full_name": self.__full_name,
            "email": self.__email,
            "phone": self.__phone,
            "address": self.__address,
            "loyalty_points": self.__loyalty_points,
            "created_at": self.__created_at,
            "updated_at": self.__updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Customer":
        """ Tạo object Customer từ dictionary (đọc từ file). """
        return cls(
            full_name=data["full_name"],
            email=data["email"],
            phone=data["phone"],
            address=data.get("address", ""),
            loyalty_points=int(data.get("loyalty_points", 0)),
            customer_id=data.get("customer_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def __repr__(self) -> str:
        return (
            f"Customer(id={self.__customer_id!r}, name={self.__full_name!r}, "
            f"email={self.__email!r})"
        )

    def __str__(self) -> str:
        return f"[{self.__customer_id}] {self.__full_name} <{self.__email}>"
