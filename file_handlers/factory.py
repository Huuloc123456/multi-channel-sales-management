""" file_handlers/factory.py  FileHandlerFactory – Áp dụng Factory Pattern để tạo đúng handler. Nguyên lý OOP áp dụng: - Factory Pattern: Ẩn logic tạo object, người dùng chỉ cần biết đường dẫn file và Factory tự chọn đúng Handler. - Polymorphism (Đa hình): Tất cả handler trả về đều có chung giao diện BaseFileHandler, nên code gọi không cần quan tâm loại cụ thể. - Open/Closed Principle: Thêm handler mới chỉ cần đăng ký vào _REGISTRY, không sửa logic core. """

import logging
from pathlib import Path

from .base_handler import BaseFileHandler
from .json_handler import JsonHandler
from .csv_handler import CsvHandler
from .txt_handler import TxtHandler

logger = logging.getLogger(__name__)


class FileHandlerFactory:
    """ Factory tạo đúng FileHandler dựa trên phần mở rộng của file. Usage: handler = FileHandlerFactory.get_handler("data/products.json") data = handler.read() handler.write(data) Supported extensions: .json → JsonHandler .csv → CsvHandler .txt → TxtHandler """

    # Registry ánh xạ extension → Handler class
    # Dễ dàng mở rộng mà không cần sửa get_handler()
    _REGISTRY: dict[str, type] = {
        ".json": JsonHandler,
        ".csv": CsvHandler,
        ".txt": TxtHandler,
    }

    @classmethod
    def get_handler(cls, file_path: str, **kwargs) -> BaseFileHandler:
        """ Trả về đúng FileHandler tương ứng với đuôi file. Args: file_path (str): Đường dẫn tới file dữ liệu. **kwargs: Tham số bổ sung được chuyển tiếp đến constructor của Handler tương ứng (ví dụ: indent=2 cho JSON). Returns: BaseFileHandler: Instance của JsonHandler, CsvHandler, hoặc TxtHandler. Raises: ValueError: Nếu phần mở rộng không được hỗ trợ. Example: >>> handler = FileHandlerFactory.get_handler("reports/log.txt") >>> isinstance(handler, TxtHandler) True """
        extension = Path(file_path).suffix.lower()

        handler_class = cls._REGISTRY.get(extension)

        if handler_class is None:
            supported = ", ".join(cls._REGISTRY.keys())
            logger.error(
                "Định dạng file không được hỗ trợ: %s. Hỗ trợ: %s",
                extension,
                supported,
            )
            raise ValueError(
                f"Định dạng file không được hỗ trợ: {extension!r}.\n"
                f"Các định dạng hỗ trợ: {supported}"
            )

        handler = handler_class(file_path, **kwargs)
        logger.debug(
            "Factory tạo %s cho file: %s",
            handler_class.__name__,
            file_path,
        )
        return handler

    @classmethod
    def register_handler(cls, extension: str, handler_class: type):
        """ Đăng ký một Handler mới vào Factory (Open/Closed Principle). Args: extension (str): Phần mở rộng file (ví dụ: '.xml'). handler_class (type): Lớp Handler kế thừa BaseFileHandler. Raises: TypeError: Nếu handler_class không kế thừa BaseFileHandler. """
        if not issubclass(handler_class, BaseFileHandler):
            raise TypeError(
                f"{handler_class.__name__} phải kế thừa BaseFileHandler."
            )
        ext = extension if extension.startswith(".") else f".{extension}"
        cls._REGISTRY[ext.lower()] = handler_class
        logger.info("Đã đăng ký handler mới: %s → %s", ext, handler_class.__name__)

    @classmethod
    def supported_extensions(cls) -> list[str]:
        """ Trả về danh sách các định dạng file được hỗ trợ. """
        return list(cls._REGISTRY.keys())
