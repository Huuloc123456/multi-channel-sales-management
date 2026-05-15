import pytest
from utils.validators import validate_email, validate_phone, validate_price, validate_quantity, validate_non_empty
from utils.helpers import generate_id, get_timestamp, format_currency, truncate_string, calculate_loyalty_points

# ----------------- VALIDATORS TESTS ----------------- #

def test_validate_email():
    assert validate_email("test@example.com") == True
    assert validate_email("invalid-email") == False
    assert validate_email("") == False
    assert validate_email(None) == False

def test_validate_phone():
    assert validate_phone("0912345678") == True
    assert validate_phone("+84912345678") == True
    assert validate_phone("1234567") == False
    assert validate_phone("0212345678") == False # not starting with 3, 5, 7, 8, 9
    assert validate_phone("") == False

def test_validate_price():
    assert validate_price(100) == True
    assert validate_price(0) == True
    assert validate_price(15.5) == True
    assert validate_price(-10) == False
    assert validate_price("100") == True
    assert validate_price("abc") == False

def test_validate_quantity():
    assert validate_quantity(10) == True
    assert validate_quantity(0) == True
    assert validate_quantity(-1) == False
    assert validate_quantity(1.5) == False
    assert validate_quantity("10") == False

def test_validate_non_empty():
    assert validate_non_empty(" test ") == "test"
    with pytest.raises(ValueError):
        validate_non_empty("")
    with pytest.raises(ValueError):
        validate_non_empty("   ")


# ----------------- HELPERS TESTS ----------------- #

def test_generate_id():
    id1 = generate_id("TEST")
    assert id1.startswith("TEST-")
    assert len(id1) == 13 # 4 prefix + 1 dash + 8 hex
    
    id2 = generate_id()
    assert len(id2) == 8

def test_format_currency():
    assert format_currency(1500000) == "1.500.000₫"
    assert format_currency(0) == "0₫"
    assert format_currency(1500000.5) == "1.500.000₫"
    assert format_currency("invalid") == "0₫"

def test_truncate_string():
    assert truncate_string("Hello World", 5) == "He..."
    assert truncate_string("Hello", 10) == "Hello"
    assert truncate_string("", 5) == ""

def test_calculate_loyalty_points():
    assert calculate_loyalty_points(150000) == 1500
    assert calculate_loyalty_points(0) == 0
    assert calculate_loyalty_points(-100) == 0
