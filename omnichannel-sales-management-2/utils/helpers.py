"""
helpers.py

Các hàm trợ giúp tiện ích và xử lý đường dẫn tuyệt đối cho Project 2.
Đảm bảo hai project chạy hoàn toàn độc lập, sử dụng dữ liệu riêng biệt không trùng lẫn.
"""

import os

# Đường dẫn gốc của project omnichannel-sales-management-2
# Trỏ từ thư mục utils/ lùi lại một cấp
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_absolute_path(*paths) -> str:
    """
    Trả về đường dẫn tuyệt đối bắt đầu từ thư mục gốc của Project 2.
    Giúp chương trình luôn ghi dữ liệu chính xác vào thư mục data/ của Project 2 
    dù chạy ở bất kỳ thư mục làm việc (Cwd) nào.
    """
    return os.path.abspath(os.path.join(BASE_DIR, *paths))
