import pytest
import os
import json
from pathlib import Path
from file_handlers.json_handler import JsonHandler

@pytest.fixture
def temp_json_file(tmp_path):
    # Trả về đường dẫn của file tạm
    return str(tmp_path / "test_data.json")

def test_json_write_and_read(temp_json_file):
    handler = JsonHandler(temp_json_file)
    data = [{"id": 1, "name": "Test 1"}, {"id": 2, "name": "Test 2"}]
    
    # Test write
    assert handler.write(data) == True
    assert os.path.exists(temp_json_file)
    
    # Test read
    read_data = handler.read()
    assert len(read_data) == 2
    assert read_data[0]["name"] == "Test 1"

def test_json_read_non_existent(temp_json_file):
    handler = JsonHandler(temp_json_file)
    with pytest.raises(FileNotFoundError):
        handler.read()

def test_json_read_invalid_json(temp_json_file):
    with open(temp_json_file, "w") as f:
        f.write("Invalid JSON String")
        
    handler = JsonHandler(temp_json_file)
    with pytest.raises(ValueError):
        handler.read()

def test_json_append(temp_json_file):
    handler = JsonHandler(temp_json_file)
    handler.write([{"id": 1}])
    
    handler.append({"id": 2})
    
    data = handler.read()
    assert len(data) == 2
    assert data[1]["id"] == 2

# ---------------- CSV HANDLER ---------------- #
from file_handlers.csv_handler import CsvHandler

@pytest.fixture
def temp_csv_file(tmp_path):
    return str(tmp_path / "test_data.csv")

def test_csv_write_and_read(temp_csv_file):
    handler = CsvHandler(temp_csv_file)
    data = [
        {"id": "1", "name": "Test 1", "price": "100"}, 
        {"id": "2", "name": "Test 2", "price": "200"}
    ]
    
    # Test write
    assert handler.write(data) == True
    assert os.path.exists(temp_csv_file)
    
    # Test read
    read_data = handler.read()
    assert len(read_data) == 2
    assert read_data[0]["name"] == "Test 1"
    assert read_data[1]["price"] == "200"

def test_csv_write_empty(temp_csv_file):
    handler = CsvHandler(temp_csv_file)
    handler.write([])
    # Sẽ tạo file rỗng mà không báo lỗi
    assert os.path.exists(temp_csv_file)
    assert len(handler.read()) == 0

def test_csv_append(temp_csv_file):
    handler = CsvHandler(temp_csv_file)
    data = [{"id": "1", "name": "Test 1"}]
    handler.write(data)
    
    handler.append_row({"id": "2", "name": "Test 2"})
    
    read_data = handler.read()
    assert len(read_data) == 2
    assert read_data[1]["name"] == "Test 2"

