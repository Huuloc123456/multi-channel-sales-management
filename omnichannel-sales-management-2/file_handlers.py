"""
file_handlers.py

Module xử lý file đa cấu trúc và định dạng cho Hệ thống Quản lý Bán hàng Đa kênh.
Buổi thực hành 8: File & Xử lý lỗi hệ thống.

Các tính năng nổi bật:
- Lớp trừu tượng FileHandler kế thừa từ abc.ABC.
- Lớp con JSONFileHandler, CSVFileHandler, TXTFileHandler thực thi đầy đủ các chức năng đọc/ghi.
- Xử lý các lỗi phổ biến (FileNotFoundError, JSONDecodeError, ValueError, IOError).
- Tính năng chuyển đổi định dạng tệp linh hoạt giữa JSON, CSV, và TXT.
"""

import os
import json
import csv
from abc import ABC, abstractmethod
from typing import Any, List, Dict

# =====================================================================
# [BUỔI 8 - LỚP TRỪU TƯỢNG]
# =====================================================================
class FileHandler(ABC):
    """
    Lớp trừu tượng cơ sở định nghĩa giao diện chung cho mọi trình xử lý tệp tin.
    Sử dụng các phương thức trừu tượng bằng tiếng Việt theo yêu cầu.
    """
    def __init__(self, filepath: str):
        self.filepath = filepath

    @abstractmethod
    def doc(self) -> Any:
        """Phương thức trừu tượng đọc dữ liệu từ tệp tin."""
        pass

    @abstractmethod
    def ghi(self, data: Any) -> bool:
        """Phương thức trừu tượng ghi dữ liệu vào tệp tin."""
        pass


# =====================================================================
# [BUỔI 8 - LỚP CON JSON]
# =====================================================================
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


# =====================================================================
# [BUỔI 8 - LỚP CON CSV]
# =====================================================================
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


# =====================================================================
# [BUỔI 8 - LỚP CON TXT]
# =====================================================================
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


# =====================================================================
# [BUỔI 8 - CHUYỂN ĐỔI ĐỊNH DẠNG FILE]
# =====================================================================
def chuyen_doi_json_sang_csv(json_path: str, csv_path: str, fieldnames: List[str] = None) -> bool:
    """Chuyển đổi dữ liệu từ tệp JSON sang CSV."""
    try:
        json_handler = JSONFileHandler(json_path)
        data = json_handler.doc()
        
        if not isinstance(data, list):
            raise ValueError("Dữ liệu JSON gốc phải là danh sách các đối tượng để chuyển đổi sang CSV.")

        csv_handler = CSVFileHandler(csv_path, fieldnames)
        return csv_handler.ghi(data)
    except Exception as e:
        raise Exception(f"Lỗi chuyển đổi JSON ↔ CSV: {e}")

def chuyen_doi_csv_sang_json(csv_path: str, json_path: str) -> bool:
    """Chuyển đổi dữ liệu từ tệp CSV sang JSON."""
    try:
        csv_handler = CSVFileHandler(csv_path)
        data = csv_handler.doc()
        
        json_handler = JSONFileHandler(json_path)
        return json_handler.ghi(data)
    except Exception as e:
        raise Exception(f"Lỗi chuyển đổi CSV ↔ JSON: {e}")

def chuyen_doi_json_sang_txt(json_path: str, txt_path: str) -> bool:
    """Chuyển đổi dữ liệu từ JSON sang cấu trúc bảng ASCII/Văn bản trong tệp TXT."""
    try:
        json_handler = JSONFileHandler(json_path)
        data = json_handler.doc()
        
        txt_content = ""
        if isinstance(data, list):
            if len(data) > 0:
                headers = list(data[0].keys())
                txt_content += " | ".join(headers).upper() + "\n"
                txt_content += "=" * 60 + "\n"
                for item in data:
                    txt_content += " | ".join(str(item.get(h, "")) for h in headers) + "\n"
        elif isinstance(data, dict):
            for k, v in data.items():
                txt_content += f"{k}: {v}\n"
        else:
            txt_content = str(data)

        txt_handler = TXTFileHandler(txt_path)
        return txt_handler.ghi(txt_content)
    except Exception as e:
        raise Exception(f"Lỗi chuyển đổi JSON ↔ TXT: {e}")
