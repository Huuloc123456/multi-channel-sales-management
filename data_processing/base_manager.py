""" data_processing/base_manager.py  Lớp cơ sở cho các Manager xử lý nghiệp vụ CRUD. Nguyên lý OOP áp dụng: - Template Method Pattern: Định nghĩa khung (framework) cho CRUD, lớp con chỉ cần implement _from_dict() và _get_entity_id(). - Dependency Injection: Manager nhận FileHandlerFactory thay vì tạo handler trực tiếp → dễ test, linh hoạt. """

import logging
from typing import Optional
from file_handlers.factory import FileHandlerFactory

logger = logging.getLogger(__name__)


class BaseManager:
    """ Manager cơ sở cung cấp CRUD hoàn chỉnh thông qua file. Lớp con cần override: - _from_dict(data: dict) → entity object - _get_entity_id(entity) → str """

    def __init__(self, data_file: str):
        """ Args: data_file (str): Đường dẫn file lưu dữ liệu (json, csv, txt). """
        self._handler = FileHandlerFactory.get_handler(data_file)
        self._data_file = data_file

    # ------------------------------------------------------------------ #
    #  HOOK METHODS – lớp con phải override                               #
    # ------------------------------------------------------------------ #

    def _from_dict(self, data: dict):
        """ Tạo entity từ dictionary. Lớp con phải override. """
        raise NotImplementedError

    def _get_entity_id(self, entity) -> str:
        """ Lấy ID của entity. Lớp con phải override. """
        raise NotImplementedError

    # ------------------------------------------------------------------ #
    #  TEMPLATE METHODS – CRUD chung                                      #
    # ------------------------------------------------------------------ #

    def _load_all(self) -> list:
        """ Đọc toàn bộ dữ liệu từ file, trả về list entity. """
        try:
            raw_list = self._handler.read()
            return [self._from_dict(item) for item in raw_list]
        except FileNotFoundError:
            logger.info("File chưa tồn tại, bắt đầu với danh sách rỗng.")
            return []
        except (ValueError, KeyError) as exc:
            logger.error("Lỗi đọc dữ liệu: %s", exc)
            return []

    def _save_all(self, entities: list) -> bool:
        """ Ghi toàn bộ danh sách entity ra file. """
        raw_list = [e.to_dict() for e in entities]
        return self._handler.write(raw_list)

    def get_all(self) -> list:
        """ Lấy toàn bộ bản ghi. """
        return self._load_all()

    def get_by_id(self, entity_id: str) -> Optional[object]:
        """ Tìm bản ghi theo ID. """
        for entity in self._load_all():
            if self._get_entity_id(entity) == entity_id:
                return entity
        return None

    def add(self, entity) -> bool:
        """ Thêm bản ghi mới. Returns: bool: True nếu thành công, False nếu ID đã tồn tại. """
        entities = self._load_all()
        entity_id = self._get_entity_id(entity)
        if any(self._get_entity_id(e) == entity_id for e in entities):
            logger.warning("ID đã tồn tại: %s", entity_id)
            return False
        entities.append(entity)
        return self._save_all(entities)

    def update(self, updated_entity) -> bool:
        """ Cập nhật bản ghi theo ID. Returns: bool: True nếu tìm thấy và cập nhật thành công. """
        entities = self._load_all()
        entity_id = self._get_entity_id(updated_entity)
        for i, entity in enumerate(entities):
            if self._get_entity_id(entity) == entity_id:
                entities[i] = updated_entity
                return self._save_all(entities)
        logger.warning("Không tìm thấy ID để cập nhật: %s", entity_id)
        return False

    def delete(self, entity_id: str) -> bool:
        """ Xóa bản ghi theo ID. Returns: bool: True nếu tìm thấy và xóa thành công. """
        entities = self._load_all()
        original_count = len(entities)
        entities = [e for e in entities if self._get_entity_id(e) != entity_id]
        if len(entities) == original_count:
            logger.warning("Không tìm thấy ID để xóa: %s", entity_id)
            return False
        return self._save_all(entities)

    def count(self) -> int:
        """ Đếm tổng số bản ghi. """
        return len(self._load_all())

    def search(self, **filters) -> list:
        """ Tìm kiếm theo nhiều điều kiện (AND logic). Args: **filters: Tên thuộc tính và giá trị cần lọc. Hỗ trợ tìm kiếm chuỗi không phân biệt hoa/thường. Example: manager.search(category="Điện tử", channel="online") """
        results = []
        for entity in self._load_all():
            d = entity.to_dict()
            match = all(
                str(filters[k]).lower() in str(d.get(k, "")).lower()
                for k in filters
            )
            if match:
                results.append(entity)
        return results
