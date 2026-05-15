""" file_handlers/csv_handler.py  Triển khai cụ thể của BaseFileHandler cho định dạng CSV. Nguyên lý OOP áp dụng: - Inheritance (Kế thừa): CsvHandler kế thừa BaseFileHandler. - Override (Ghi đè): Triển khai read() và write() cho CSV. - Sử dụng csv.DictReader/DictWriter để xử lý header tự động. """

import csv
import logging
from typing import Any

from .base_handler import BaseFileHandler

logger = logging.getLogger(__name__)


class CsvHandler(BaseFileHandler):
    """ Handler để đọc/ghi dữ liệu dạng CSV. Đọc file CSV về dạng list[dict] với header làm key. Ghi list[dict] ra file CSV, tự động lấy fieldnames từ dict đầu tiên. """

    def __init__(
        self,
        file_path: str,
        delimiter: str = ",",
        encoding: str = "utf-8-sig",
    ):
        """ Args: file_path (str): Đường dẫn tới file .csv. delimiter (str): Ký tự phân tách cột (mặc định ','). encoding (str): Encoding (mặc định 'utf-8-sig' để tương thích Excel). """
        super().__init__(file_path)
        self.__delimiter = delimiter
        self.__encoding = encoding

    # ------------------------------------------------------------------ #
    #  OVERRIDE: read()                                                    #
    # ------------------------------------------------------------------ #

    def read(self) -> list[dict]:
        """ Đọc file CSV và trả về danh sách dictionary. Returns: list[dict]: Mỗi phần tử là một hàng, key là tên cột. Trả về list rỗng nếu file rỗng. Raises: FileNotFoundError: Nếu file không tồn tại. ValueError: Nếu file CSV có cấu trúc không hợp lệ. IOError: Nếu có lỗi hệ thống. """
        if not self.exists():
            logger.warning("File không tồn tại: %s", self._file_path)
            raise FileNotFoundError(f"Không tìm thấy file: {self._file_path}")

        try:
            rows = []
            with open(self._file_path, "r", encoding=self.__encoding, newline="") as f:
                reader = csv.DictReader(f, delimiter=self.__delimiter)
                for row in reader:
                    rows.append(dict(row))
            logger.debug("Đọc %d dòng từ %s", len(rows), self._file_path)
            return rows
        except csv.Error as exc:
            logger.error("Lỗi định dạng CSV tại %s: %s", self._file_path, exc)
            raise ValueError(
                f"File CSV không hợp lệ: {self._file_path}\nChi tiết: {exc}"
            ) from exc
        except OSError as exc:
            logger.error("Lỗi I/O khi đọc %s: %s", self._file_path, exc)
            raise IOError(f"Không thể đọc file: {self._file_path}") from exc

    # ------------------------------------------------------------------ #
    #  OVERRIDE: write()                                                   #
    # ------------------------------------------------------------------ #

    def write(self, data: list[dict]) -> bool:
        """ Ghi danh sách dictionary ra file CSV. Args: data (list[dict]): Dữ liệu cần ghi. Mỗi dict là một hàng. Các key của dict[0] sẽ làm header. Returns: bool: True nếu ghi thành công. Raises: TypeError: Nếu data không phải list[dict]. IOError: Nếu có lỗi hệ thống khi ghi. """
        if not isinstance(data, list):
            raise TypeError(f"Dữ liệu phải là list[dict], nhận: {type(data).__name__}")

        self.ensure_directory()

        try:
            if not data:
                # Ghi file rỗng (chỉ header nếu biết, hoặc trống hoàn toàn)
                open(self._file_path, "w", encoding=self.__encoding).close()
                return True

            fieldnames = list(data[0].keys())
            with open(
                self._file_path, "w", encoding=self.__encoding, newline=""
            ) as f:
                writer = csv.DictWriter(
                    f, fieldnames=fieldnames, delimiter=self.__delimiter,
                    extrasaction="ignore"
                )
                writer.writeheader()
                writer.writerows(data)

            logger.debug("Ghi %d dòng vào %s", len(data), self._file_path)
            return True
        except csv.Error as exc:
            logger.error("Lỗi khi ghi CSV %s: %s", self._file_path, exc)
            raise IOError(
                f"Không thể ghi file CSV: {self._file_path}\nChi tiết: {exc}"
            ) from exc
        except OSError as exc:
            logger.error("Lỗi I/O khi ghi %s: %s", self._file_path, exc)
            raise IOError(f"Không thể ghi file: {self._file_path}") from exc

    # ------------------------------------------------------------------ #
    #  ADDITIONAL METHODS                                                  #
    # ------------------------------------------------------------------ #

    def append_row(self, record: dict) -> bool:
        """ Thêm một hàng vào cuối file CSV mà không cần load toàn bộ. Args: record (dict): Bản ghi cần thêm. Returns: bool: True nếu thành công. """
        self.ensure_directory()
        file_exists = self.exists() and self.get_file_size() > 0

        try:
            with open(
                self._file_path, "a", encoding=self.__encoding, newline=""
            ) as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=list(record.keys()),
                    delimiter=self.__delimiter,
                    extrasaction="ignore",
                )
                if not file_exists:
                    writer.writeheader()
                writer.writerow(record)
            return True
        except OSError as exc:
            logger.error("Lỗi khi append CSV %s: %s", self._file_path, exc)
            raise IOError(f"Không thể ghi thêm vào file: {self._file_path}") from exc
