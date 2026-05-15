import pytest
from models.product import Product
from models.customer import Customer
from models.order import Order, OrderItem
from datetime import datetime

def test_product_creation():
    p = Product(name="Áo thun", price=150000, quantity=10, category="Thời trang", channel="online", product_id="SP-123")
    assert p.product_id == "SP-123"
    assert p.name == "Áo thun"
    assert p.price == 150000
    assert p.quantity == 10
    
def test_product_to_dict():
    p = Product(name="Áo thun", price=150000, quantity=10, category="Thời trang", channel="online", product_id="SP-123")
    d = p.to_dict()
    assert d["product_id"] == "SP-123"
    assert d["name"] == "Áo thun"
    assert "created_at" in d

def test_product_from_dict():
    d = {
        "product_id": "SP-456",
        "name": "Quần",
        "price": 200000,
        "quantity": 5,
        "category": "Thời trang",
        "channel": "offline"
    }
    p = Product.from_dict(d)
    assert p.product_id == "SP-456"
    assert p.price == 200000

def test_customer_creation():
    c = Customer(full_name="Nguyễn Văn A", email="a@email.com", phone="0901234567", customer_id="KH-111")
    assert c.customer_id == "KH-111"
    assert c.email == "a@email.com"

def test_customer_loyalty_points():
    c = Customer(full_name="Nguyễn Văn A", email="a@email.com", phone="0901234567", customer_id="KH-111")
    c.add_loyalty_points(100)
    assert c.loyalty_points == 100

def test_order_item():
    item = OrderItem("SP-1", "Sản phẩm 1", 100000, 2)
    assert item.subtotal == 200000
    
def test_order_creation():
    order = Order("KH-1", channel="online")
    item1 = OrderItem("SP-1", "Sản phẩm 1", 100000, 2)
    item2 = OrderItem("SP-2", "Sản phẩm 2", 50000, 1)
    
    order.add_item(item1)
    order.add_item(item2)
    
    assert order.item_count == 3
    assert order.subtotal == 250000
    assert order.total_amount == 250000
    
def test_order_discount():
    order = Order("KH-1")
    item = OrderItem("SP-1", "Sản phẩm", 100000, 1)
    order.add_item(item)
    
    order.discount = 0.2
    assert order.total_amount == 80000

def test_order_status_transition():
    order = Order("KH-1")
    assert order.status == "pending"
    order.status = "confirmed"
    assert order.status == "confirmed"

# ---------------- EDGE CASES & EXCEPTIONS ---------------- #

def test_product_invalid_creation():
    p = Product(name="Valid", price=100, quantity=1)
    with pytest.raises(ValueError):
        p.name = "" # Empty name
    with pytest.raises(ValueError):
        p.price = -100 # Negative price
    with pytest.raises(ValueError):
        p.quantity = -1 # Negative qty
    with pytest.raises(ValueError):
        p.channel = "invalid" # Invalid channel

def test_product_update_stock():
    p = Product(name="P", price=100, quantity=10)
    p.update_stock(5)
    assert p.quantity == 15
    p.update_stock(-10)
    assert p.quantity == 5
    with pytest.raises(ValueError):
        p.update_stock(-10) # Not enough stock
    assert p.quantity == 5 # Unchanged

def test_customer_invalid_creation():
    with pytest.raises(ValueError):
        Customer(full_name="", email="test@test.com", phone="0912345678")
    with pytest.raises(ValueError):
        Customer(full_name="A", email="invalid", phone="0912345678")
    with pytest.raises(ValueError):
        Customer(full_name="A", email="test@test.com", phone="123")
    with pytest.raises(ValueError):
        Customer(full_name="A", email="test@test.com", phone="0912345678", loyalty_points=-10)

def test_customer_redeem_points():
    c = Customer(full_name="A", email="a@email.com", phone="0912345678")
    c.add_loyalty_points(100)
    c.redeem_points(40)
    assert c.loyalty_points == 60
    with pytest.raises(ValueError):
        c.redeem_points(100) # Not enough points
    assert c.loyalty_points == 60 # Unchanged

def test_order_item_merge():
    order = Order("KH-1")
    item1 = OrderItem("SP-1", "Sản phẩm 1", 100000, 2)
    item2 = OrderItem("SP-1", "Sản phẩm 1", 100000, 3) # Same ID
    order.add_item(item1)
    order.add_item(item2)
    assert len(order.items) == 1
    assert order.items[0].quantity == 5

def test_order_remove_item():
    order = Order("KH-1")
    item1 = OrderItem("SP-1", "Sản phẩm 1", 100000, 2)
    item2 = OrderItem("SP-2", "Sản phẩm 2", 50000, 1)
    order.add_item(item1)
    order.add_item(item2)
    order.remove_item("SP-1")
    assert len(order.items) == 1
    assert order.items[0].product_id == "SP-2"

def test_order_invalid_modifications():
    order = Order("KH-1")
    with pytest.raises(ValueError):
        order.discount = 1.5 # Invalid discount
    with pytest.raises(ValueError):
        order.status = "invalid_status"

def test_order_completed_frozen():
    order = Order("KH-1")
    item = OrderItem("SP-1", "Sản phẩm 1", 100000, 2)
    order.status = "completed"
    with pytest.raises(RuntimeError):
        order.add_item(item) # Cannot modify completed order
