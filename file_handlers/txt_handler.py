"""
txt_handler.py

Xử lý tệp tin văn bản thuần (.txt).
Demo đầy đủ: open() với 'r', 'w', 'a' và read(), readline(), readlines(), write(), writelines().
"""

import os
from typing import List
from .base_handler import FileHandler

class TXTFileHandler(FileHandler):
    """
    Xử lý tệp tin văn bản thuần (.txt).
    Demo đầy đủ: open() với 'r', 'w', 'a' và read(), readline(), readlines(), write(), writelines().
    """
    def doc(self) -> str:
        """Đọc toàn bộ nội dung tệp bằng phương thức read()."""
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Không tìm thấy tệp TXT tại: {self.filepath}")

        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                # Sử dụng read()
                return f.read()
        except IOError as e:
            raise IOError(f"Lỗi đọc file TXT: {e}")

    def doc_từng_dòng(self) -> List[str]:
        """Đọc tệp tin sử dụng readline() và readlines()."""
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Không tìm thấy tệp TXT tại: {self.filepath}")

        try:
            lines = []
            with open(self.filepath, 'r', encoding='utf-8') as f:
                # Demo readline() đọc dòng đầu tiên làm ví dụ
                first_line = f.readline()
                if first_line:
                    lines.append(first_line.strip())
                
                # Demo readlines() đọc các dòng còn lại
                remaining_lines = f.readlines()
                for line in remaining_lines:
                    lines.append(line.strip())
            return [line for line in lines if line] # Chỉ lấy các dòng không rỗng
        except IOError as e:
            raise IOError(f"Lỗi I/O khi đọc từng dòng: {e}")

    def ghi(self, data: str) -> bool:
        """Ghi chuỗi văn bản vào file bằng mode 'w' và phương thức write()."""
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, 'w', encoding='utf-8') as f:
                # Sử dụng write() với mode 'w' (ghi đè)
                f.write(data)
            return True
        except IOError as e:
            raise IOError(f"Lỗi ghi tệp văn bản: {e}")

    def ghi_nối_tiếp(self, data: str) -> bool:
        """Ghi tiếp vào cuối file bằng mode 'a' và phương thức write()."""
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, 'a', encoding='utf-8') as f:
                # Sử dụng write() với mode 'a' (ghi nối tiếp)
                f.write(data + "\n")
            return True
        except IOError as e:
            raise IOError(f"Lỗi ghi nối tiếp tệp văn bản: {e}")

    def ghi_nhiều_dòng(self, lines: List[str]) -> bool:
        """Ghi danh sách chuỗi bằng phương thức writelines()."""
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, 'w', encoding='utf-8') as f:
                # Sử dụng writelines()
                # Tự thêm xuống dòng cho từng dòng văn bản
                formatted_lines = [line if line.endswith('\n') else line + '\n' for line in lines]
                f.writelines(formatted_lines)
            return True
        except IOError as e:
            raise IOError(f"Lỗi ghi nhiều dòng tệp văn bản: {e}")
