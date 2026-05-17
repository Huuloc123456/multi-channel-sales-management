"""
csv_handler.py

Xử lý đọc/ghi tệp định dạng CSV.
Sử dụng csv.DictReader và csv.DictWriter để xử lý tự động header.
"""

import os
import csv
from typing import List, Dict, Any
from .base_handler import FileHandler

class CSVFileHandler(FileHandler):
    """
    Xử lý đọc/ghi tệp định dạng CSV.
    Sử dụng csv.DictReader và csv.DictWriter để xử lý tự động header.
    """
    def __init__(self, filepath: str, fieldnames: List[str] = None):
        super().__init__(filepath)
        self.fieldnames = fieldnames

    def doc(self) -> List[Dict[str, str]]:
        """Đọc file CSV và trả về danh sách các Dictionary."""
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Không tìm thấy tệp CSV tại: {self.filepath}")

        try:
            rows = []
            with open(self.filepath, mode='r', encoding='utf-8-sig', newline='') as f:
                # Demo sử dụng csv.DictReader
                reader = csv.DictReader(f)
                # Tự động gán fieldnames nếu chưa khai báo trước đó
                if not self.fieldnames and reader.fieldnames:
                    self.fieldnames = reader.fieldnames
                for row in reader:
                    rows.append(dict(row))
            return rows
        except csv.Error as e:
            raise ValueError(f"Lỗi cấu trúc tệp CSV: {e}")
        except IOError as e:
            raise IOError(f"Lỗi hệ thống khi đọc tệp CSV: {e}")

    def ghi(self, data: List[Dict[str, Any]]) -> bool:
        """Ghi danh sách Dictionary ra tệp CSV."""
        if not isinstance(data, list):
            raise ValueError("Dữ liệu ghi vào CSV bắt buộc phải là một danh sách (list).")

        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            
            # Nếu không có fieldnames, lấy keys của dict đầu tiên làm header
            if not self.fieldnames and len(data) > 0:
                self.fieldnames = list(data[0].keys())

            if not self.fieldnames:
                raise ValueError("Không xác định được tiêu đề cột (fieldnames) cho tệp CSV.")

            with open(self.filepath, mode='w', encoding='utf-8-sig', newline='') as f:
                # Demo sử dụng csv.DictWriter
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()
                writer.writerows(data)
            return True
        except csv.Error as e:
            raise ValueError(f"Lỗi định dạng khi ghi CSV: {e}")
        except IOError as e:
            raise IOError(f"Lỗi I/O khi ghi tệp CSV: {e}")
