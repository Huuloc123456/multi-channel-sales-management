import pytest
import tkinter as tk
from ui import theme as T
from ui.widgets import SearchBar, StatCard, IconButton, DataTable

@pytest.fixture(scope="module")
def tk_root():
    """ Tạo một instance Tkinter root dùng chung cho các test UI, nhưng không gọi mainloop() để test chạy ngầm. """
    root = tk.Tk()
    root.withdraw() # Ẩn cửa sổ đi
    yield root
    root.destroy()

def test_theme_constants():
    # Kiểm tra một số biến theme được nạp đúng
    assert hasattr(T, "CONTENT_BG")
    assert hasattr(T, "TEXT_PRIMARY")
    assert isinstance(T.FONT_APP, str)

def test_searchbar_creation(tk_root):
    # Đảm bảo widget không văng lỗi khi khởi tạo
    try:
        sb = SearchBar(tk_root, placeholder="Tìm kiếm...")
        assert sb is not None
        assert sb.get() == ""
    except Exception as e:
        pytest.fail(f"Khởi tạo SearchBar thất bại: {e}")

def test_iconbutton_creation(tk_root):
    try:
        btn = IconButton(tk_root, text="Test Btn", bg="#ff0000", command=lambda: None)
        assert btn is not None
    except Exception as e:
        pytest.fail(f"Khởi tạo IconButton thất bại: {e}")

def test_datatable_creation(tk_root):
    try:
        cols = [
            {"id": "id", "heading": "ID", "width": 50},
            {"id": "name", "heading": "Name", "width": 100}
        ]
        table = DataTable(tk_root, columns=cols)
        assert table is not None
        
        # Test load rows
        rows = [["1", "Item A"], ["2", "Item B"]]
        table.load_rows(rows)
        assert len(table.tree.get_children()) == 2
        
    except Exception as e:
        pytest.fail(f"Khởi tạo DataTable thất bại: {e}")
