from abc import ABC, abstractmethod
from typing import Any

class FileHandler(ABC):
    def __init__(self, filepath: str):
        self.filepath = filepath

    @abstractmethod
    def doc(self) -> Any:
        pass

    @abstractmethod
    def ghi(self, data: Any) -> bool:
        pass
