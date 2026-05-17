"""
json_handler.py

Xử lý đọc/ghi tệp định dạng JSON.
Sử dụng đầy đủ các hàm: json.load(), json.dump(), json.loads(), json.dumps().
"""

import os
import json
from typing import Any
from .base_handler import FileHandler

class JSONFileHandler(FileHandler):
    """
    Xử lý đọc/ghi tệp định dạng JSON.
    Sử dụng đầy đủ các hàm: json.load(), json.dump(), json.loads(), json.dumps().
    """
    def doc(self) -> Any:
        """Đọc và chuyển đổi tệp JSON thành cấu trúc dữ liệu Python."""
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Không tìm thấy tệp JSON tại: {self.filepath}")

        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                # Demo sử dụng json.load()
                data = json.load(f)
                return data
        except json.JSONDecodeError as e:
            # Xử lý lỗi định dạng JSON
            raise json.JSONDecodeError(f"Lỗi cú pháp JSON trong file {self.filepath}: {e.msg}", e.doc, e.pos)
        except IOError as e:
            raise IOError(f"Lỗi I/O khi đọc tệp JSON: {e}")

    def ghi(self, data: Any) -> bool:
        """Ghi cấu trúc dữ liệu Python vào tệp JSON."""
        try:
            # Tạo thư mục cha nếu chưa tồn tại
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, 'w', encoding='utf-8') as f:
                # Demo sử dụng json.dump()
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except TypeError as e:
            raise ValueError(f"Dữ liệu không thể serialize sang JSON: {e}")
        except IOError as e:
            raise IOError(f"Lỗi I/O khi ghi tệp JSON: {e}")

    # --- DEMO JSON.LOADS() & JSON.DUMPS() ---
    def chuoi_sang_json(self, json_string: str) -> Any:
        """Demo sử dụng json.loads() để chuyển chuỗi JSON thành Dict/List."""
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            raise ValueError(f"Chuỗi JSON không hợp lệ: {e}")

    def json_sang_chuoi(self, data: Any) -> str:
        """Demo sử dụng json.dumps() để chuyển đổi Dict/List thành chuỗi JSON."""
        try:
            return json.dumps(data, ensure_ascii=False)
        except TypeError as e:
            raise ValueError(f"Dữ liệu không thể chuyển đổi sang chuỗi: {e}")
