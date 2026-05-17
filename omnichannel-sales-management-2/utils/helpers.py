""" utils/helpers.py  Các hàm tiện ích dùng chung trong toàn bộ hệ thống. """

import uuid
import datetime


def generate_id(prefix: str = "") -> str:
    """ Tạo mã định danh duy nhất dạng PREFIX-XXXXXXXX (8 ký tự hex). Args: prefix (str): Tiền tố phân biệt loại entity (PRD, CUS, ORD...). Returns: str: Mã định danh duy nhất, ví dụ 'PRD-A1B2C3D4'. Example: >>> generate_id("PRD") 'PRD-A1B2C3D4' """
    short_id = uuid.uuid4().hex[:8].upper()
    return f"{prefix}-{short_id}" if prefix else short_id


def get_timestamp(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """ Lấy thời điểm hiện tại theo định dạng chỉ định. Args: fmt (str): Định dạng strftime (mặc định 'YYYY-MM-DD HH:MM:SS'). Returns: str: Chuỗi thời gian hiện tại. """
    return datetime.datetime.now().strftime(fmt)


def format_currency(amount: float, symbol: str = "₫") -> str:
    """ Định dạng số tiền theo chuẩn Việt Nam. Args: amount (float): Số tiền cần định dạng. symbol (str): Ký hiệu tiền tệ (mặc định '₫'). Returns: str: Chuỗi tiền đã định dạng, ví dụ '1.500.000₫'. Example: >>> format_currency(1500000) '1.500.000₫' """
    try:
        # Định dạng theo kiểu Việt Nam: dấu chấm phân cách hàng nghìn
        formatted = f"{int(amount):,}".replace(",", ".")
        return f"{formatted}{symbol}"
    except (TypeError, ValueError):
        return f"0{symbol}"


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """ Cắt ngắn chuỗi nếu quá dài. Args: text (str): Chuỗi gốc. max_length (int): Độ dài tối đa. suffix (str): Hậu tố chỉ báo cắt ngắn. Returns: str: Chuỗi đã cắt ngắn hoặc nguyên vẹn. """
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def calculate_loyalty_points(total_amount: float, rate: float = 0.01) -> int:
    """ Tính số điểm tích lũy từ giá trị đơn hàng. Args: total_amount (float): Tổng giá trị đơn hàng (VND). rate (float): Tỷ lệ điểm/VND (mặc định 1% → 1₫ = 0.01 điểm). Returns: int: Số điểm tích lũy (làm tròn xuống). """
    if total_amount <= 0:
        return 0
    return int(total_amount * rate)
