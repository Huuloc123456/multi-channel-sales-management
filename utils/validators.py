"""
utils/validators.py
====================
Các hàm kiểm tra tính hợp lệ của dữ liệu đầu vào.
"""

import re


# ------------------------------------------------------------------ #
#  EMAIL                                                               #
# ------------------------------------------------------------------ #

_EMAIL_PATTERN = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
)


def validate_email(email: str) -> bool:
    """
    Kiểm tra địa chỉ email có hợp lệ không.

    Args:
        email (str): Địa chỉ email cần kiểm tra.

    Returns:
        bool: True nếu hợp lệ.

    Example:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid-email")
        False
    """
    if not email or not isinstance(email, str):
        return False
    return bool(_EMAIL_PATTERN.match(email.strip()))


# ------------------------------------------------------------------ #
#  PHONE                                                               #
# ------------------------------------------------------------------ #

_PHONE_PATTERN = re.compile(
    r"^(\+84|84|0)(3[2-9]|5[6-9]|7[06-9]|8[0-689]|9[0-9])\d{7}$"
)


def validate_phone(phone: str) -> bool:
    """
    Kiểm tra số điện thoại Việt Nam có hợp lệ không.
    Hỗ trợ các đầu số: 03x, 05x, 07x, 08x, 09x và dạng +84.

    Args:
        phone (str): Số điện thoại cần kiểm tra.

    Returns:
        bool: True nếu hợp lệ.

    Example:
        >>> validate_phone("0912345678")
        True
        >>> validate_phone("12345")
        False
    """
    if not phone or not isinstance(phone, str):
        return False
    cleaned = re.sub(r"[\s\-\.]", "", phone.strip())
    return bool(_PHONE_PATTERN.match(cleaned))


# ------------------------------------------------------------------ #
#  PRICE / QUANTITY                                                    #
# ------------------------------------------------------------------ #

def validate_price(price) -> bool:
    """
    Kiểm tra giá trị giá/tiền có hợp lệ không (>= 0).

    Args:
        price: Giá trị cần kiểm tra.

    Returns:
        bool: True nếu là số hợp lệ và >= 0.
    """
    try:
        return float(price) >= 0
    except (TypeError, ValueError):
        return False


def validate_quantity(qty) -> bool:
    """
    Kiểm tra số lượng có hợp lệ không (số nguyên >= 0).

    Args:
        qty: Giá trị cần kiểm tra.

    Returns:
        bool: True nếu hợp lệ.
    """
    try:
        return isinstance(qty, int) and qty >= 0
    except (TypeError, ValueError):
        return False


# ------------------------------------------------------------------ #
#  GENERAL                                                             #
# ------------------------------------------------------------------ #

def validate_non_empty(value: str, field_name: str = "Trường") -> str:
    """
    Kiểm tra chuỗi không được để trống.

    Args:
        value (str): Chuỗi cần kiểm tra.
        field_name (str): Tên trường để hiển thị trong thông báo lỗi.

    Returns:
        str: Chuỗi đã strip nếu hợp lệ.

    Raises:
        ValueError: Nếu chuỗi rỗng hoặc chỉ chứa khoảng trắng.
    """
    if not value or not value.strip():
        raise ValueError(f"{field_name} không được để trống.")
    return value.strip()
