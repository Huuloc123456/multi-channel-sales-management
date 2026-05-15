""" ui/customer_frame.py  Frame Quản lý Khách hàng. Chức năng: Tìm kiếm, lọc kênh, thêm/sửa/xóa, xuất CSV. """

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv
import logging
from pathlib import Path

from ui import theme as T
from ui.widgets import (
    SearchBar, IconButton, DataTable, ModalDialog, build_page_header
)
from models.customer import Customer

logger = logging.getLogger(__name__)

DATA_FILE = Path("data/customers.json")


def _load_customers() -> list[Customer]:
    try:
        DATA_FILE.parent.mkdir(exist_ok=True)
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return [Customer.from_dict(d) for d in json.load(f)]
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save_customers(customers: list[Customer]):
    DATA_FILE.parent.mkdir(exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([c.to_dict() for c in customers], f, ensure_ascii=False, indent=2)


COLUMNS = [
    {"id": "customer_id", "heading": "Mã KH",       "width": 110, "anchor": "w"},
    {"id": "full_name",   "heading": "Họ và tên",    "width": 160, "anchor": "w", "stretch": True},
    {"id": "phone",       "heading": "Điện thoại",   "width": 120, "anchor": "w"},
    {"id": "email",       "heading": "Email",         "width": 180, "anchor": "w"},
    {"id": "address",     "heading": "Địa chỉ",       "width": 180, "anchor": "w"},
    {"id": "channel",     "heading": "Kênh",          "width": 90,  "anchor": "w"},
    {"id": "points",      "heading": "Điểm TL",       "width": 70,  "anchor": "center"},
]

CHANNELS = ["", "Tại quầy", "Online", "Facebook", "Shopee"]


class CustomerFrame(tk.Frame):
    """ Frame quản lý khách hàng. """

    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, bg=T.CONTENT_BG, **kwargs)
        self.controller = controller
        self._customers: list[Customer] = []
        self._build()
        self.refresh()

    def _build(self):
        build_page_header(
            self,
            title="Quản lý khách hàng",
            subtitle="Danh sách khách hàng đa kênh",
            icon="👥",
        )

        # Toolbar
        toolbar = tk.Frame(self, bg=T.CONTENT_BG)
        toolbar.pack(fill="x", padx=24, pady=(0, 8))

        self._search = SearchBar(toolbar, placeholder="Tìm khách hàng...",
                                 on_search=self._apply_filter)
        self._search.pack(side="left", fill="x", expand=True, ipady=2)

        self._channel_var = tk.StringVar()
        cb = ttk.Combobox(toolbar, textvariable=self._channel_var,
                          values=CHANNELS, width=14,
                          state="readonly", font=T.F_FORM_INPUT)
        cb.pack(side="left", padx=(12, 6))
        cb.bind("<<ComboboxSelected>>", lambda e: self._apply_filter())

        IconButton(toolbar, "📊 CSV", bg=T.BTN_EXPORT_BG,
                   command=self._export_csv).pack(side="left", padx=(0, 6))
        IconButton(toolbar, "+ Thêm", bg=T.ACCENT_RED,
                   command=self._add_customer).pack(side="left")

        # Table
        frame = tk.Frame(self, bg=T.CARD_BG,
                         highlightbackground=T.CARD_BORDER, highlightthickness=1)
        frame.pack(fill="both", expand=True, padx=24, pady=(0, 8))
        self._table = DataTable(frame, columns=COLUMNS)
        self._table.pack(fill="both", expand=True, padx=1, pady=1)

        # Bottom buttons
        bottom = tk.Frame(self, bg=T.CONTENT_BG)
        bottom.pack(fill="x", padx=24, pady=(0, 16))
        IconButton(bottom, "✏  Sửa", bg=T.BTN_PRIMARY_BG,
                   command=self._edit_customer).pack(side="left", padx=(0, 8))
        IconButton(bottom, "🗑  Xóa", bg=T.BTN_DANGER_BG,
                   command=self._delete_customer).pack(side="left")

    def refresh(self):
        self._customers = _load_customers()
        self._apply_filter()

    def _apply_filter(self, *_):
        keyword = self._search.get().lower()
        ch = self._channel_var.get()

        filtered = self._customers
        if keyword:
            filtered = [c for c in filtered
                        if keyword in c.full_name.lower()
                        or keyword in c.email.lower()
                        or keyword in c.phone]

        rows = []
        for c in filtered:
            rows.append([
                c.customer_id, c.full_name, c.phone,
                c.email, c.address,
                "Tại quầy",  # default – thực tế nên lưu channel trong Customer
                str(c.loyalty_points),
            ])
        self._table.load_rows(rows)

    # ---- CRUD ----

    def _add_customer(self):
        dialog = CustomerDialog(self, title="Thêm khách hàng mới")
        self.wait_window(dialog)
        if dialog.result:
            self._customers.append(dialog.result)
            _save_customers(self._customers)
            self._apply_filter()
            messagebox.showinfo("Thành công", "Đã thêm khách hàng mới.")

    def _edit_customer(self):
        sel = self._table.get_selected()
        if not sel:
            messagebox.showwarning("Chọn khách hàng", "Vui lòng chọn khách hàng cần sửa.")
            return
        cid = sel[0]
        customer = next((c for c in self._customers if c.customer_id == cid), None)
        if not customer:
            return
        dialog = CustomerDialog(self, title="Chỉnh sửa khách hàng", customer=customer)
        self.wait_window(dialog)
        if dialog.result:
            idx = next(i for i, c in enumerate(self._customers) if c.customer_id == cid)
            self._customers[idx] = dialog.result
            _save_customers(self._customers)
            self._apply_filter()
            messagebox.showinfo("Thành công", "Đã cập nhật khách hàng.")

    def _delete_customer(self):
        sel = self._table.get_selected()
        if not sel:
            messagebox.showwarning("Chọn khách hàng", "Vui lòng chọn khách hàng cần xóa.")
            return
        cid, name = sel[0], sel[1]
        if not messagebox.askyesno("Xác nhận xóa",
                                   f"Bạn có chắc muốn xóa khách hàng:\n{name}?"):
            return
        self._customers = [c for c in self._customers if c.customer_id != cid]
        _save_customers(self._customers)
        self._apply_filter()
        messagebox.showinfo("Thành công", "Đã xóa khách hàng.")

    def _export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile="customers.csv",
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["Mã KH", "Họ tên", "Điện thoại", "Email", "Địa chỉ", "Điểm TL"])
                for c in self._customers:
                    writer.writerow([c.customer_id, c.full_name, c.phone,
                                     c.email, c.address, c.loyalty_points])
            messagebox.showinfo("Xuất CSV", f"Đã xuất:\n{path}")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))


# --- CUSTOMER DIALOG ---

class CustomerDialog(ModalDialog):
    """ Dialog thêm / sửa khách hàng. """

    def __init__(self, parent, title: str, customer: Customer = None):
        super().__init__(parent, title=title, width=480, height=420)
        self._customer = customer
        self._build_form()
        if customer:
            self._populate(customer)

    def _build_form(self):
        tk.Label(self, text=self.title(),
                 font=T.F_SECTION_TITLE,
                 bg=T.CONTENT_BG, fg=T.TEXT_PRIMARY,
                 ).pack(fill="x", padx=20, pady=(16, 8))

        form = tk.Frame(self, bg=T.CONTENT_BG)
        form.pack(fill="both", expand=True)
        form.columnconfigure(1, weight=1)

        self._name_var    = tk.StringVar()
        self._email_var   = tk.StringVar()
        self._phone_var   = tk.StringVar()
        self._address_var = tk.StringVar()
        self._points_var  = tk.StringVar(value="0")

        self._make_field(form, "Họ và tên *",   self._name_var,    row=0)
        self._make_field(form, "Email *",        self._email_var,   row=1)
        self._make_field(form, "Điện thoại *",  self._phone_var,   row=2)
        self._make_field(form, "Địa chỉ",        self._address_var, row=3)
        self._make_field(form, "Điểm tích lũy", self._points_var,  row=4)

        self._footer_buttons(self, self._save, self.destroy)

    def _populate(self, c: Customer):
        self._name_var.set(c.full_name)
        self._email_var.set(c.email)
        self._phone_var.set(c.phone)
        self._address_var.set(c.address)
        self._points_var.set(str(c.loyalty_points))

    def _save(self):
        try:
            c = Customer(
                full_name=self._name_var.get(),
                email=self._email_var.get(),
                phone=self._phone_var.get(),
                address=self._address_var.get(),
                loyalty_points=int(self._points_var.get() or 0),
                customer_id=self._customer.customer_id if self._customer else None,
                created_at=self._customer.created_at if self._customer else None,
            )
            self.result = c
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Dữ liệu không hợp lệ", str(e), parent=self)
