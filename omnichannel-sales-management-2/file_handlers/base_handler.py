"""
base_handler.py

Định nghĩa lớp trừu tượng cơ sở cho mọi trình xử lý tệp tin.
"""

from abc import ABC, abstractmethod
from typing import Any

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
