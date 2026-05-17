from typing import List
from .json_handler import JSONFileHandler
from .csv_handler import CSVFileHandler
from .txt_handler import TXTFileHandler

def chuyen_doi_json_sang_csv(json_path: str, csv_path: str, fieldnames: List[str] = None) -> bool:
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
    try:
        csv_handler = CSVFileHandler(csv_path)
        data = csv_handler.doc()
        
        json_handler = JSONFileHandler(json_path)
        return json_handler.ghi(data)
    except Exception as e:
        raise Exception(f"Lỗi chuyển đổi CSV ↔ JSON: {e}")

def chuyen_doi_json_sang_txt(json_path: str, txt_path: str) -> bool:
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
