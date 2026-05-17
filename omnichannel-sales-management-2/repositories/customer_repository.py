import os
from typing import List, Optional
from file_handlers import JSONFileHandler
from models import Customer
from utils import get_absolute_path

class CustomerRepository:
    def __init__(self, filepath: str = None):
        self.filepath = filepath or get_absolute_path("data", "customers.json")
        self.handler = JSONFileHandler(self.filepath)
        self.customers: List[Customer] = []
        self._nap_du_lieu()

    def _nap_du_lieu(self):
        if not os.path.exists(self.filepath):
            self.customers = []
            return
        
        try:
            data = self.handler.doc()
            if isinstance(data, list):
                self.customers = [Customer.from_dict(d) for d in data]
            else:
                self.customers = []
        except Exception:
            self.customers = []

    def _luu_du_lieu(self) -> bool:
        data = [c.to_dict() for c in self.customers]
        return self.handler.ghi(data)

    def create(self, customer: Customer) -> bool:
        if self.get_by_id(customer.customer_id):
            raise ValueError(f"Mã khách hàng {customer.customer_id} đã tồn tại!")
        
        self.customers.append(customer)
        return self._luu_du_lieu()

    def get_all(self) -> List[Customer]:
        self._nap_du_lieu()
        return self.customers

    def get_by_id(self, customer_id: str) -> Optional[Customer]:
        self._nap_du_lieu()
        for c in self.customers:
            if c.customer_id.strip().upper() == customer_id.strip().upper():
                return c
        return None

    def update(self, customer_id: str, full_name: str, email: str, phone: str, address: str, loyalty_points: int) -> bool:
        customer = self.get_by_id(customer_id)
        if not customer:
            raise ValueError(f"Không tìm thấy khách hàng có mã {customer_id}!")

        customer.full_name = full_name.strip()
        customer.email = email.strip()
        customer.phone = phone.strip()
        customer.address = address.strip()
        customer.loyalty_points = loyalty_points
        
        return self._luu_du_lieu()

    def delete(self, customer_id: str) -> bool:
        customer = self.get_by_id(customer_id)
        if not customer:
            raise ValueError(f"Không tìm thấy khách hàng có mã {customer_id}!")
        
        self.customers.remove(customer)
        return self._luu_du_lieu()
