"""
file_handlers/base_handler.py
==============================
Lớp cơ sở trừu tượng (Abstract Base Class) cho tất cả file handlers.

Nguyên lý OOP áp dụng:
- Abstraction (Trừu tượng hóa): Định nghĩa "hợp đồng" (contract) gồm
  các phương thức read() và write() mà mọi lớp con PHẢI triển khai.
- Sử dụng abc.ABC và @abstractmethod để bắt buộc ghi đè tại lớp con.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseFileHandler(ABC):
    """
    Lớp cơ sở trừu tượng định nghĩa giao diện chung cho mọi file handler.

    Mọi lớp con (JsonHandler, CsvHandler, TxtHandler) PHẢI ghi đè:
        - read()  : Đọc dữ liệu từ file và trả về cấu trúc Python.
        - write() : Ghi dữ liệu Python ra file.

    Lớp này cũng cung cấp các helper method dùng chung (non-abstract).
    """

    def __init__(self, file_path: str):
        """
        Args:
            file_path (str): Đường dẫn tuyệt đối hoặc tương đối tới file.
        """
        self._file_path = Path(file_path)

    # ------------------------------------------------------------------ #
    #  ABSTRACT METHODS – bắt buộc lớp con phải ghi đè                   #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def read(self) -> Any:
        """
        Đọc dữ liệu từ file.

        Returns:
            Any: Dữ liệu đã được parse (list, dict, str tùy handler).

        Raises:
            FileNotFoundError: Nếu file không tồn tại.
            ValueError: Nếu nội dung file không đúng định dạng.
            IOError: Nếu có lỗi I/O khi đọc.
        """

    @abstractmethod
    def write(self, data: Any) -> bool:
        """
        Ghi dữ liệu ra file.

        Args:
            data (Any): Dữ liệu cần ghi.

        Returns:
            bool: True nếu ghi thành công, False nếu thất bại.

        Raises:
            IOError: Nếu có lỗi khi ghi file.
            TypeError: Nếu kiểu dữ liệu không tương thích.
        """

    # ------------------------------------------------------------------ #
    #  CONCRETE HELPER METHODS – dùng chung cho mọi lớp con              #
    # ------------------------------------------------------------------ #

    def exists(self) -> bool:
        """Kiểm tra file có tồn tại không."""
        return self._file_path.exists()

    def ensure_directory(self):
        """Tạo thư mục cha nếu chưa tồn tại."""
        self._file_path.parent.mkdir(parents=True, exist_ok=True)

    def get_file_size(self) -> int:
        """Lấy kích thước file (bytes). Trả về 0 nếu file không tồn tại."""
        return self._file_path.stat().st_size if self.exists() else 0

    def delete(self) -> bool:
        """
        Xóa file.

        Returns:
            bool: True nếu xóa thành công, False nếu file không tồn tại.
        """
        try:
            self._file_path.unlink()
            return True
        except FileNotFoundError:
            return False

    @property
    def file_path(self) -> Path:
        """Trả về đường dẫn file dạng Path object."""
        return self._file_path

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={str(self._file_path)!r})"
