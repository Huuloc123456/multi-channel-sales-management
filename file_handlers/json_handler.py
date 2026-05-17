import os
import json
from typing import Any
from .base_handler import FileHandler

class JSONFileHandler(FileHandler):
    def doc(self) -> Any:
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Không tìm thấy tệp JSON tại: {self.filepath}")

        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Lỗi cú pháp JSON trong file {self.filepath}: {e.msg}", e.doc, e.pos)
        except IOError as e:
            raise IOError(f"Lỗi I/O khi đọc tệp JSON: {e}")

    def ghi(self, data: Any) -> bool:
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except TypeError as e:
            raise ValueError(f"Dữ liệu không thể serialize sang JSON: {e}")
        except IOError as e:
            raise IOError(f"Lỗi I/O khi ghi tệp JSON: {e}")

    def chuoi_sang_json(self, json_string: str) -> Any:
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            raise ValueError(f"Chuỗi JSON không hợp lệ: {e}")

    def json_sang_chuoi(self, data: Any) -> str:
        try:
            return json.dumps(data, ensure_ascii=False)
        except TypeError as e:
            raise ValueError(f"Dữ liệu không thể chuyển đổi sang chuỗi: {e}")
