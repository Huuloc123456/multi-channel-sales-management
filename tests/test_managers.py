import pytest
import os
from data_processing.product_manager import ProductManager
from models.product import Product

@pytest.fixture
def product_manager(tmp_path):
    # Set up temporary JSON file for testing
    temp_file = tmp_path / "test_products.json"
    manager = ProductManager(data_file=str(temp_file))
    return manager

def test_manager_add(product_manager):
    p = Product(name="Product 1", price=100, quantity=10, category="Cat", channel="online", product_id="SP-1")
    product_manager.add(p)
    
    all_products = product_manager.get_all()
    assert len(all_products) == 1
    assert all_products[0].product_id == "SP-1"

def test_manager_get_by_id(product_manager):
    p = Product(name="Product 1", price=100, quantity=10, category="Cat", channel="online", product_id="SP-1")
    product_manager.add(p)
    
    found = product_manager.get_by_id("SP-1")
    assert found is not None
    assert found.name == "Product 1"
    
    not_found = product_manager.get_by_id("SP-999")
    assert not_found is None

def test_manager_update(product_manager):
    p = Product(name="Product 1", price=100, quantity=10, category="Cat", channel="online", product_id="SP-1")
    product_manager.add(p)
    
    p.name = "Updated Product"
    p.price = 200
    assert product_manager.update(p) == True
    
    updated = product_manager.get_by_id("SP-1")
    assert updated.name == "Updated Product"
    assert updated.price == 200

def test_manager_delete(product_manager):
    p = Product(name="Product 1", price=100, quantity=10, category="Cat", channel="online", product_id="SP-1")
    product_manager.add(p)
    
    assert product_manager.delete("SP-1") == True
    assert len(product_manager.get_all()) == 0
    
def test_manager_search(product_manager):
    p1 = Product(name="Áo thun đỏ", price=100, quantity=10, category="Áo", channel="online", product_id="SP-1")
    p2 = Product(name="Quần jean xanh", price=200, quantity=5, category="Quần", channel="offline", product_id="SP-2")
    product_manager.add(p1)
    product_manager.add(p2)
    
    results = product_manager.search(name="thun")
    assert len(results) == 1
    assert results[0].product_id == "SP-1"

# ---------------- CUSTOMER MANAGER ---------------- #
from data_processing.customer_manager import CustomerManager
from models.customer import Customer

@pytest.fixture
def customer_manager(tmp_path):
    temp_file = tmp_path / "test_customers.json"
    return CustomerManager(data_file=str(temp_file))

def test_customer_manager_add_and_get(customer_manager):
    c = Customer(full_name="Nguyễn Văn A", email="a@email.com", phone="0901234567", customer_id="KH-1")
    assert customer_manager.add(c) == True
    
    # Try adding same ID
    c2 = Customer(full_name="Nguyễn Văn B", email="b@email.com", phone="0901234567", customer_id="KH-1")
    assert customer_manager.add(c2) == False
    
    found = customer_manager.get_by_id("KH-1")
    assert found.full_name == "Nguyễn Văn A"

def test_customer_manager_loyalty(customer_manager):
    c = Customer(full_name="Nguyễn Văn A", email="a@email.com", phone="0901234567", customer_id="KH-1")
    customer_manager.add(c)
    
    # Update points via object then manager
    c.add_loyalty_points(100)
    customer_manager.update(c)
    
    updated = customer_manager.get_by_id("KH-1")
    assert updated.loyalty_points == 100

# ---------------- ORDER MANAGER ---------------- #
from data_processing.order_manager import OrderManager
from models.order import Order, OrderItem

@pytest.fixture
def order_manager(tmp_path):
    temp_file = tmp_path / "test_orders.json"
    return OrderManager(data_file=str(temp_file))

def test_order_manager_add(order_manager):
    order = Order("KH-1", order_id="ORD-1")
    item = OrderItem("SP-1", "Product", 100, 1)
    order.add_item(item)
    
    assert order_manager.add(order) == True
    assert len(order_manager.get_all()) == 1

def test_order_manager_update_status(order_manager):
    order = Order("KH-1", order_id="ORD-1")
    order_manager.add(order)
    
    order.status = "confirmed"
    assert order_manager.update(order) == True
    
    updated = order_manager.get_by_id("ORD-1")
    assert updated.status == "confirmed"
    
    # Not found
    order_not_found = Order("KH-2", order_id="ORD-999")
    assert order_manager.update(order_not_found) == False

