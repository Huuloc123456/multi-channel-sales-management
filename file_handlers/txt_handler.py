"""
file_handlers/txt_handler.py
=============================
Triển khai cụ thể của BaseFileHandler cho định dạng TXT (plain text).

Dùng để ghi log, báo cáo văn bản thuần, hoặc xuất dữ liệu dạng bảng.

Nguyên lý OOP áp dụng:
- Inheritance (Kế thừa): TxtHandler kế thừa BaseFileHandler.
- Override (Ghi đè): read() và write() phù hợp với plain text.
"""

import logging
from typing import Any

from .base_handler import BaseFileHandler

logger = logging.getLogger(__name__)

# Ký tự phân tách trường mặc định trong file TXT có cấu trúc
DEFAULT_SEPARATOR = " | "


class TxtHandler(BaseFileHandler):
    """
    Handler để đọc/ghi dữ liệu dạng plain text.

    Hỗ trợ hai chế độ:
      - raw  : Đọc/ghi toàn bộ nội dung là chuỗi văn bản.
      - lines: Đọc trả về list[str], ghi nhận list[str] hoặc list[dict].
    """

    def __init__(
        self,
        file_path: str,
        mode: str = "lines",
        separator: str = DEFAULT_SEPARATOR,
        encoding: str = "utf-8",
    ):
        """
        Args:
            file_path (str): Đường dẫn tới file .txt.
            mode (str): 'raw' hoặc 'lines' (mặc định 'lines').
            separator (str): Ký tự dùng để nối các field khi ghi dict.
            encoding (str): Encoding (mặc định 'utf-8').
        """
        super().__init__(file_path)
        if mode not in ("raw", "lines"):
            raise ValueError(f"mode phải là 'raw' hoặc 'lines', nhận: {mode!r}")
        self.__mode = mode
        self.__separator = separator
        self.__encoding = encoding

    # ------------------------------------------------------------------ #
    #  OVERRIDE: read()                                                    #
    # ------------------------------------------------------------------ #

    def read(self) -> Any:
        """
        Đọc file TXT.

        Returns:
            - str  : Nếu mode='raw', trả về toàn bộ nội dung.
            - list[str]: Nếu mode='lines', trả về danh sách từng dòng
                         (đã strip, bỏ dòng trống).

        Raises:
            FileNotFoundError: Nếu file không tồn tại.
            IOError: Nếu có lỗi hệ thống khi đọc.
        """
        if not self.exists():
            logger.warning("File không tồn tại: %s", self._file_path)
            raise FileNotFoundError(f"Không tìm thấy file: {self._file_path}")

        try:
            with open(self._file_path, "r", encoding=self.__encoding) as f:
                content = f.read()

            if self.__mode == "raw":
                return content

            # mode == "lines"
            lines = [line.rstrip("\n") for line in content.splitlines() if line.strip()]
            logger.debug("Đọc %d dòng từ %s", len(lines), self._file_path)
            return lines
        except OSError as exc:
            logger.error("Lỗi I/O khi đọc %s: %s", self._file_path, exc)
            raise IOError(f"Không thể đọc file: {self._file_path}") from exc

    # ------------------------------------------------------------------ #
    #  OVERRIDE: write()                                                   #
    # ------------------------------------------------------------------ #

    def write(self, data: Any) -> bool:
        """
        Ghi dữ liệu ra file TXT.

        Args:
            data: - str       → ghi trực tiếp (cả hai mode).
                  - list[str] → mỗi phần tử một dòng.
                  - list[dict]→ mỗi dict được nối bằng separator thành một dòng.

        Returns:
            bool: True nếu ghi thành công.

        Raises:
            TypeError: Nếu kiểu dữ liệu không được hỗ trợ.
            IOError: Nếu có lỗi hệ thống khi ghi.
        """
        self.ensure_directory()

        try:
            content = self._convert_to_text(data)
        except TypeError:
            raise

        try:
            with open(self._file_path, "w", encoding=self.__encoding) as f:
                f.write(content)
            logger.debug("Ghi thành công vào %s", self._file_path)
            return True
        except OSError as exc:
            logger.error("Lỗi I/O khi ghi %s: %s", self._file_path, exc)
            raise IOError(f"Không thể ghi file: {self._file_path}") from exc

    # ------------------------------------------------------------------ #
    #  ADDITIONAL METHODS                                                  #
    # ------------------------------------------------------------------ #

    def append_line(self, line: str) -> bool:
        """
        Thêm một dòng vào cuối file TXT.

        Args:
            line (str): Dòng văn bản cần thêm.

        Returns:
            bool: True nếu thành công.
        """
        self.ensure_directory()
        try:
            with open(self._file_path, "a", encoding=self.__encoding) as f:
                f.write(line.rstrip("\n") + "\n")
            return True
        except OSError as exc:
            logger.error("Lỗi khi append TXT %s: %s", self._file_path, exc)
            raise IOError(f"Không thể ghi thêm vào file: {self._file_path}") from exc

    def write_report(self, title: str, rows: list[dict], col_width: int = 20) -> bool:
        """
        Ghi báo cáo dạng bảng ASCII vào file TXT.

        Args:
            title (str): Tiêu đề báo cáo.
            rows (list[dict]): Dữ liệu báo cáo.
            col_width (int): Độ rộng mỗi cột.

        Returns:
            bool: True nếu thành công.
        """
        if not rows:
            return self.write(f"{title}\n(Không có dữ liệu)\n")

        headers = list(rows[0].keys())
        separator = "-" * (col_width * len(headers) + 3 * (len(headers) - 1))

        lines = [
            title,
            separator,
            self.__separator.join(h.upper().ljust(col_width) for h in headers),
            separator,
        ]
        for row in rows:
            lines.append(
                self.__separator.join(
                    str(row.get(h, "")).ljust(col_width) for h in headers
                )
            )
        lines.append(separator)
        return self.write("\n".join(lines) + "\n")

    # ------------------------------------------------------------------ #
    #  PRIVATE HELPERS                                                     #
    # ------------------------------------------------------------------ #

    def _convert_to_text(self, data: Any) -> str:
        """Chuyển đổi data sang chuỗi văn bản để ghi file."""
        if isinstance(data, str):
            return data
        if isinstance(data, list):
            if not data:
                return ""
            if all(isinstance(item, str) for item in data):
                return "\n".join(data) + "\n"
            if all(isinstance(item, dict) for item in data):
                return "\n".join(
                    self.__separator.join(str(v) for v in item.values())
                    for item in data
                ) + "\n"
        raise TypeError(
            f"TxtHandler.write() không hỗ trợ kiểu: {type(data).__name__}. "
            "Chấp nhận: str, list[str], list[dict]."
        )
