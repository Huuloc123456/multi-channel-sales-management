import json

class ProductManager:
    def __init__(self):
        self.file_path = "data/products.json"

    def get_all(self):
        # Đọc file và chuyển thành danh sách đối tượng Product
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [Product(**item) for item in data]
        except FileNotFoundError:
            return []

    def add(self, product_obj):
        # Logic lưu đối tượng vào file
        products = self.get_all()
        products.append(product_obj)
        # Ghi lại vào file JSON (Hàm write_data an toàn)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump([p.__dict__ for p in products], f, ensure_ascii=False, indent=4)