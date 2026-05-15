""" ui/api_frame.py  Frame Dữ liệu bên ngoài – Thu thập từ API và website. 3 tab: Tỷ giá hối đoái | KH từ API | SP từ API """

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import threading
import json
from pathlib import Path

from ui import theme as T
from ui.widgets import IconButton, DataTable, build_page_header

logger = logging.getLogger(__name__)

# Data paths
CUSTOMER_FILE = Path("data/customers.json")
PRODUCT_FILE  = Path("data/products.json")


class ApiFrame(tk.Frame):
    """ Frame thu thập dữ liệu từ API bên ngoài. """

    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, bg=T.CONTENT_BG, **kwargs)
        self.controller = controller
        self._build()

    def _build(self):
        build_page_header(
            self,
            title="Dữ liệu bên ngoài",
            subtitle="Thu thập dữ liệu từ API và website",
            icon="🌐",
        )

        # Notebook tabs
        style = ttk.Style()
        style.configure("Api.TNotebook", background=T.CONTENT_BG, borderwidth=0)
        style.configure("Api.TNotebook.Tab", font=T.F_FORM_LABEL,
                        padding=(12, 6), background=T.CONTENT_BG)
        style.map("Api.TNotebook.Tab",
                  background=[("selected", T.CARD_BG)],
                  foreground=[("selected", T.ACCENT_RED)])

        nb = ttk.Notebook(self, style="Api.TNotebook")
        nb.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        # Tab 1: Tỷ giá
        self._tab_exchange = ExchangeTab(nb, controller=self.controller)
        nb.add(self._tab_exchange, text="🔄 Tỷ giá hối đoái")

        # Tab 2: KH từ API
        self._tab_customers = CustomerApiTab(nb, controller=self.controller)
        nb.add(self._tab_customers, text="👥 KH từ API")

        # Tab 3: SP từ API
        self._tab_products = ProductApiTab(nb, controller=self.controller)
        nb.add(self._tab_products, text="📦 SP từ API")

    def refresh(self):
        pass  # Tabs load on demand


# --- TAB 1: TỶ GIÁ HỐI ĐOÁI ---

class ExchangeTab(tk.Frame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, bg=T.CONTENT_BG, **kwargs)
        self._build()

    def _build(self):
        # Source info
        info = tk.Frame(self, bg="#e8f4fd")
        info.pack(fill="x", padx=0, pady=(8, 12))
        tk.Label(info, text="🔗 Nguồn: exchangerate-api.com (API miễn phí)",
                 font=T.F_FORM_LABEL, bg="#e8f4fd", fg="#1565c0",
                 anchor="w").pack(fill="x", padx=14, pady=8)

        # Table
        cols = [
            {"id": "currency", "heading": "Tiền tệ",   "width": 120, "anchor": "w"},
            {"id": "code",     "heading": "Mã",         "width": 80,  "anchor": "center"},
            {"id": "rate",     "heading": "Tỷ giá (VND)","width": 160, "anchor": "e"},
            {"id": "change",   "heading": "Thay đổi",   "width": 100, "anchor": "center"},
        ]
        frame = tk.Frame(self, bg=T.CARD_BG,
                         highlightbackground=T.CARD_BORDER, highlightthickness=1)
        frame.pack(fill="both", expand=True, padx=0, pady=(0, 8))
        self._table = DataTable(frame, columns=cols)
        self._table.pack(fill="both", expand=True, padx=1, pady=1)

        # Button
        btn_row = tk.Frame(self, bg=T.CONTENT_BG)
        btn_row.pack(fill="x", pady=(0, 8))
        IconButton(btn_row, "🔄 Tải tỷ giá",
                   bg=T.ACCENT_RED, command=self._fetch
                   ).pack(side="right")

    def _fetch(self):
        self._table.clear()
        threading.Thread(target=self._do_fetch, daemon=True).start()

    def _do_fetch(self):
        try:
            import urllib.request
            url = "https://open.er-api.com/v6/latest/USD"
            with urllib.request.urlopen(url, timeout=10) as r:
                data = json.loads(r.read())
            rates = data.get("rates", {})
            vnd = rates.get("VND", 1)

            CURRENCIES = {
                "USD": "Đô la Mỹ", "EUR": "Euro", "JPY": "Yên Nhật",
                "GBP": "Bảng Anh", "CNY": "Nhân dân tệ", "KRW": "Won Hàn Quốc",
                "THB": "Baht Thái", "SGD": "Đô la Singapore",
            }
            rows = []
            for code, name in CURRENCIES.items():
                rate = rates.get(code, 0)
                if rate:
                    vnd_per = vnd / rate
                    rows.append([name, code, f"{vnd_per:,.0f}₫", "—"])

            self.after(0, lambda: self._table.load_rows(rows))
        except Exception as exc:
            logger.warning("Exchange API error: %s", exc)
            self.after(0, lambda: messagebox.showwarning(
                "Kết nối", f"Không thể lấy dữ liệu tỷ giá.\n{exc}"))


# --- TAB 2: KHÁCH HÀNG TỪ API ---

class CustomerApiTab(tk.Frame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, bg=T.CONTENT_BG, **kwargs)
        self._data = []
        self._build()

    def _build(self):
        info = tk.Frame(self, bg="#e8f4fd")
        info.pack(fill="x", padx=0, pady=(8, 12))
        tk.Label(info, text="🔗 Nguồn: randomuser.me API – Dữ liệu khách hàng ngẫu nhiên",
                 font=T.F_FORM_LABEL, bg="#e8f4fd", fg="#1565c0",
                 anchor="w").pack(fill="x", padx=14, pady=8)

        cols = [
            {"id": "name",    "heading": "Họ và tên",   "width": 180, "anchor": "w", "stretch": True},
            {"id": "email",   "heading": "Email",         "width": 200, "anchor": "w"},
            {"id": "phone",   "heading": "Điện thoại",   "width": 140, "anchor": "w"},
        ]
        frame = tk.Frame(self, bg=T.CARD_BG,
                         highlightbackground=T.CARD_BORDER, highlightthickness=1)
        frame.pack(fill="both", expand=True, padx=0, pady=(0, 8))
        self._table = DataTable(frame, columns=cols)
        self._table.pack(fill="both", expand=True, padx=1, pady=1)

        btn_row = tk.Frame(self, bg=T.CONTENT_BG)
        btn_row.pack(fill="x", pady=(0, 8))
        IconButton(btn_row, "💾 Nhập vào hệ thống",
                   bg=T.BTN_SUCCESS_BG, command=self._import
                   ).pack(side="right", padx=(6, 0))
        IconButton(btn_row, "🔄 Tải dữ liệu",
                   bg=T.ACCENT_RED, command=self._fetch
                   ).pack(side="right")

    def _fetch(self):
        self._table.clear()
        self._data = []
        threading.Thread(target=self._do_fetch, daemon=True).start()

    def _do_fetch(self):
        try:
            import urllib.request
            url = "https://randomuser.me/api/?results=10&nat=vn&noinfo"
            with urllib.request.urlopen(url, timeout=10) as r:
                data = json.loads(r.read())
            results = data.get("results", [])
            self._data = results
            rows = []
            for u in results:
                name  = u["name"]["first"] + " " + u["name"]["last"]
                email = u.get("email", "")
                phone = u.get("phone", "")
                rows.append([name, email, phone])
            self.after(0, lambda: self._table.load_rows(rows))
        except Exception as exc:
            logger.warning("RandomUser API error: %s", exc)
            self.after(0, lambda: messagebox.showwarning(
                "Kết nối", f"Không thể lấy dữ liệu.\n{exc}"))

    def _import(self):
        if not self._data:
            messagebox.showwarning("Chưa có dữ liệu", "Hãy tải dữ liệu trước.")
            return
        try:
            from models.customer import Customer
            try:
                with open(CUSTOMER_FILE, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            except Exception:
                existing = []
            for u in self._data:
                name  = u["name"]["first"] + " " + u["name"]["last"]
                email = u.get("email", f"user{len(existing)}@api.com")
                phone = "0" + u.get("phone", "912345678").replace(" ", "")[-9:]
                try:
                    c = Customer(full_name=name, email=email, phone=phone)
                    existing.append(c.to_dict())
                except Exception:
                    pass
            CUSTOMER_FILE.parent.mkdir(exist_ok=True)
            with open(CUSTOMER_FILE, "w", encoding="utf-8") as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Thành công",
                                f"Đã nhập {len(self._data)} khách hàng vào hệ thống.")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))


# --- TAB 3: SẢN PHẨM TỪ API ---

class ProductApiTab(tk.Frame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, bg=T.CONTENT_BG, **kwargs)
        self._data = []
        self._build()

    def _build(self):
        info = tk.Frame(self, bg="#e8f4fd")
        info.pack(fill="x", padx=0, pady=(8, 12))
        tk.Label(info, text="🔗 Nguồn: fakestoreapi.com – Sản phẩm demo (quy đổi sang VND)",
                 font=T.F_FORM_LABEL, bg="#e8f4fd", fg="#1565c0",
                 anchor="w").pack(fill="x", padx=14, pady=8)

        cols = [
            {"id": "name",     "heading": "Tên sản phẩm", "width": 240, "anchor": "w", "stretch": True},
            {"id": "category", "heading": "Danh mục",     "width": 140, "anchor": "w"},
            {"id": "price",    "heading": "Giá (VND)",    "width": 130, "anchor": "e"},
        ]
        frame = tk.Frame(self, bg=T.CARD_BG,
                         highlightbackground=T.CARD_BORDER, highlightthickness=1)
        frame.pack(fill="both", expand=True, padx=0, pady=(0, 8))
        self._table = DataTable(frame, columns=cols)
        self._table.pack(fill="both", expand=True, padx=1, pady=1)

        btn_row = tk.Frame(self, bg=T.CONTENT_BG)
        btn_row.pack(fill="x", pady=(0, 8))
        IconButton(btn_row, "📦 Nhập sản phẩm",
                   bg=T.BTN_SUCCESS_BG, command=self._import
                   ).pack(side="right", padx=(6, 0))
        IconButton(btn_row, "🔄 Tải dữ liệu",
                   bg=T.ACCENT_RED, command=self._fetch
                   ).pack(side="right")

    def _fetch(self):
        self._table.clear()
        self._data = []
        threading.Thread(target=self._do_fetch, daemon=True).start()

    def _do_fetch(self):
        try:
            import urllib.request
            # Get exchange rate first
            try:
                with urllib.request.urlopen(
                        "https://open.er-api.com/v6/latest/USD", timeout=5) as r:
                    rates = json.loads(r.read()).get("rates", {})
                    vnd_rate = rates.get("VND", 24000)
            except Exception:
                vnd_rate = 24000

            url = "https://fakestoreapi.com/products?limit=15"
            with urllib.request.urlopen(url, timeout=10) as r:
                products = json.loads(r.read())
            self._data = products
            rows = []
            for p in products:
                price_vnd = int(p.get("price", 0) * vnd_rate)
                rows.append([
                    p.get("title", "")[:60],
                    p.get("category", ""),
                    f"{price_vnd:,}₫".replace(",", "."),
                ])
            self.after(0, lambda: self._table.load_rows(rows))
        except Exception as exc:
            logger.warning("FakeStore API error: %s", exc)
            self.after(0, lambda: messagebox.showwarning(
                "Kết nối", f"Không thể lấy dữ liệu.\n{exc}"))

    def _import(self):
        if not self._data:
            messagebox.showwarning("Chưa có dữ liệu", "Hãy tải dữ liệu trước.")
            return
        try:
            from models.product import Product
            import urllib.request
            try:
                with urllib.request.urlopen(
                        "https://open.er-api.com/v6/latest/USD", timeout=5) as r:
                    rates = json.loads(r.read()).get("rates", {})
                    vnd_rate = rates.get("VND", 24000)
            except Exception:
                vnd_rate = 24000

            try:
                with open(PRODUCT_FILE, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            except Exception:
                existing = []

            count = 0
            for p in self._data:
                try:
                    price_vnd = max(1000, int(p.get("price", 0) * vnd_rate))
                    prod = Product(
                        name=p.get("title", "Sản phẩm")[:80],
                        price=price_vnd,
                        quantity=50,
                        category=p.get("category", "Chưa phân loại"),
                        channel="both",
                    )
                    existing.append(prod.to_dict())
                    count += 1
                except Exception:
                    pass

            PRODUCT_FILE.parent.mkdir(exist_ok=True)
            with open(PRODUCT_FILE, "w", encoding="utf-8") as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Thành công", f"Đã nhập {count} sản phẩm vào hệ thống.")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
