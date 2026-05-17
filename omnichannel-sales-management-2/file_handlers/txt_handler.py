import os
from typing import List
from .base_handler import FileHandler

class TXTFileHandler(FileHandler):
    def doc(self) -> str:
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Không tìm thấy tệp TXT tại: {self.filepath}")

        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except IOError as e:
            raise IOError(f"Lỗi đọc file TXT: {e}")

    def doc_từng_dòng(self) -> List[str]:
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Không tìm thấy tệp TXT tại: {self.filepath}")

        try:
            lines = []
            with open(self.filepath, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                if first_line:
                    lines.append(first_line.strip())
                
                remaining_lines = f.readlines()
                for line in remaining_lines:
                    lines.append(line.strip())
            return [line for line in lines if line]
        except IOError as e:
            raise IOError(f"Lỗi I/O khi đọc từng dòng: {e}")

    def ghi(self, data: str) -> bool:
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write(data)
            return True
        except IOError as e:
            raise IOError(f"Lỗi ghi tệp văn bản: {e}")

    def ghi_nối_tiếp(self, data: str) -> bool:
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, 'a', encoding='utf-8') as f:
                f.write(data + "\n")
            return True
        except IOError as e:
            raise IOError(f"Lỗi ghi nối tiếp tệp văn bản: {e}")

    def ghi_nhiều_dòng(self, lines: List[str]) -> bool:
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, 'w', encoding='utf-8') as f:
                formatted_lines = [line if line.endswith('\n') else line + '\n' for line in lines]
                f.writelines(formatted_lines)
            return True
        except IOError as e:
            raise IOError(f"Lỗi ghi nhiều dòng tệp văn bản: {e}")
