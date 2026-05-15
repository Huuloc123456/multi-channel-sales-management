""" file_handlers/json_handler.py  Triển khai cụ thể của BaseFileHandler cho định dạng JSON. Nguyên lý OOP áp dụng: - Inheritance (Kế thừa): JsonHandler kế thừa BaseFileHandler. - Override (Ghi đè): Triển khai cụ thể read() và write() cho JSON. - Exception Handling: Xử lý đầy đủ các trường hợp lỗi. """

import json
import logging
from typing import Any

from .base_handler import BaseFileHandler

logger = logging.getLogger(__name__)


class JsonHandler(BaseFileHandler):
    """ Handler để đọc/ghi dữ liệu dạng JSON. Kế thừa từ BaseFileHandler và ghi đè read() + write(). Hỗ trợ đọc/ghi list và dict với encoding UTF-8. """

    def __init__(self, file_path: str, indent: int = 4, encoding: str = "utf-8"):
        """ Args: file_path (str): Đường dẫn tới file .json. indent (int): Số khoảng trắng thụt đầu dòng khi ghi (mặc định 4). encoding (str): Encoding khi đọc/ghi (mặc định utf-8). """
        super().__init__(file_path)
        self.__indent = indent
        self.__encoding = encoding

    # ------------------------------------------------------------------ #
    #  OVERRIDE: read()                                                    #
    # ------------------------------------------------------------------ #

    def read(self) -> Any:
        """ Đọc và parse nội dung file JSON. Returns: Any: list hoặc dict được parse từ JSON. Trả về list rỗng nếu file rỗng. Raises: FileNotFoundError: Nếu file không tồn tại. ValueError: Nếu nội dung không phải JSON hợp lệ. IOError: Nếu có lỗi hệ thống khi đọc file. """
        if not self.exists():
            logger.warning("File không tồn tại: %s", self._file_path)
            raise FileNotFoundError(f"Không tìm thấy file: {self._file_path}")

        try:
            with open(self._file_path, "r", encoding=self.__encoding) as f:
                content = f.read().strip()
                if not content:
                    logger.info("File JSON rỗng: %s. Trả về [].", self._file_path)
                    return []
                data = json.loads(content)
                logger.debug("Đọc thành công %s", self._file_path)
                return data
        except json.JSONDecodeError as exc:
            logger.error("Sai định dạng JSON tại %s: %s", self._file_path, exc)
            raise ValueError(
                f"Nội dung file không phải JSON hợp lệ: {self._file_path}\n"
                f"Chi tiết: {exc}"
            ) from exc
        except OSError as exc:
            logger.error("Lỗi I/O khi đọc %s: %s", self._file_path, exc)
            raise IOError(f"Không thể đọc file: {self._file_path}") from exc

    # ------------------------------------------------------------------ #
    #  OVERRIDE: write()                                                   #
    # ------------------------------------------------------------------ #

    def write(self, data: Any) -> bool:
        """ Ghi dữ liệu ra file JSON với định dạng đẹp (pretty-print). Args: data (Any): list hoặc dict cần ghi. Returns: bool: True nếu ghi thành công. Raises: TypeError: Nếu data không thể serialize sang JSON. IOError: Nếu có lỗi hệ thống khi ghi file. """
        self.ensure_directory()

        try:
            json_str = json.dumps(data, ensure_ascii=False, indent=self.__indent)
        except (TypeError, ValueError) as exc:
            logger.error("Không thể serialize dữ liệu sang JSON: %s", exc)
            raise TypeError(
                f"Dữ liệu không thể chuyển đổi sang JSON: {exc}"
            ) from exc

        try:
            with open(self._file_path, "w", encoding=self.__encoding) as f:
                f.write(json_str)
            logger.debug("Ghi thành công %d bản ghi vào %s", len(data) if isinstance(data, list) else 1, self._file_path)
            return True
        except OSError as exc:
            logger.error("Lỗi I/O khi ghi %s: %s", self._file_path, exc)
            raise IOError(f"Không thể ghi file: {self._file_path}") from exc

    # ------------------------------------------------------------------ #
    #  ADDITIONAL METHODS                                                  #
    # ------------------------------------------------------------------ #

    def append(self, record: dict) -> bool:
        """ Thêm một bản ghi vào cuối danh sách JSON. Tiện lợi hơn read() → append → write() thủ công. Args: record (dict): Bản ghi cần thêm. Returns: bool: True nếu thành công. """
        try:
            data = self.read() if self.exists() else []
        except (FileNotFoundError, ValueError):
            data = []

        if not isinstance(data, list):
            raise TypeError("File JSON phải chứa một mảng (list) ở gốc.")

        data.append(record)
        return self.write(data)
