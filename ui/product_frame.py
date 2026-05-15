""" ui/product_frame.py  Frame Quản lý Sản phẩm. Chức năng: Tìm kiếm, lọc kênh, xem danh sách, thêm/sửa/xóa, xuất CSV/XML. """

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv
import xml.etree.ElementTree as ET
import logging
from pathlib import Path

from ui import theme as T
from ui.widgets import (
    SearchBar, IconButton, DataTable, ModalDialog, build_page_header
)
from models.product import Product
from utils.helpers import format_currency

logger = logging.getLogger(__name__)

DATA_FILE = Path("data/products.json")


def _load_products() -> list[Product]:
    try:
        DATA_FILE.parent.mkdir(exist_ok=True)
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return [Product.from_dict(d) for d in json.load(f)]
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save_products(products: list[Product]):
    DATA_FILE.parent.mkdir(exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([p.to_dict() for p in products], f, ensure_ascii=False, indent=2)


# --- TABLE COLUMNS ---

COLUMNS = [
    {"id": "product_id", "heading": "Mã SP",      "width": 110, "anchor": "w"},
    {"id": "name",       "heading": "Tên sản phẩm","width": 180, "anchor": "w", "stretch": True},
    {"id": "category",   "heading": "Danh mục",   "width": 110, "anchor": "w"},
    {"id": "price",      "heading": "Giá",         "width": 110, "anchor": "e"},
    {"id": "quantity",   "heading": "Tồn kho",     "width": 80,  "anchor": "center"},
    {"id": "unit",       "heading": "ĐVT",         "width": 60,  "anchor": "center"},
    {"id": "channel",    "heading": "Kênh",        "width": 100, "anchor": "w"},
]

CHANNEL_LABELS = {"online": "Online", "offline": "Tại quầy", "both": "Tất cả kênh"}
CHANNEL_KEYS   = {"": None, "Online": "online", "Tại quầy": "offline", "Tất cả kênh": "both"}


class ProductFrame(tk.Frame):
    """ Frame quản lý danh mục sản phẩm. """

    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, bg=T.CONTENT_BG, **kwargs)
        self.controller = controller
        self._products: list[Product] = []
        self._build()
        self.refresh()

    # ------------------------------------------------------------------ #
    #  BUILD                                                               #
    # ------------------------------------------------------------------ #

    def _build(self):
        # Page title
        build_page_header(
            self,
            title="Quản lý sản phẩm",
            subtitle="Quản lý danh mục sản phẩm đa kênh",
            icon="🗃",
        )

        # ---- Toolbar ----
        toolbar = tk.Frame(self, bg=T.CONTENT_BG)
        toolbar.pack(fill="x", padx=24, pady=(0, 8))

        # Search
        self._search = SearchBar(toolbar, placeholder="Tìm sản phẩm...",
                                 on_search=self._apply_filter)
        self._search.pack(side="left", fill="x", expand=True, ipady=2)

        # Channel filter
        tk.Label(toolbar, text="Kênh:", font=T.F_FORM_LABEL,
                 bg=T.CONTENT_BG, fg=T.TEXT_SECONDARY).pack(side="left", padx=(12, 4))
        self._channel_var = tk.StringVar()
        cb = ttk.Combobox(toolbar, textvariable=self._channel_var,
                          values=["", "Online", "Tại quầy", "Tất cả kênh"],
                          width=14, state="readonly", font=T.F_FORM_INPUT)
        cb.pack(side="left", padx=(0, 12))
        cb.bind("<<ComboboxSelected>>", lambda e: self._apply_filter())

        # Buttons
        IconButton(toolbar, "Xuất XML", icon="📄",
                   bg=T.BTN_EXPORT_BG, command=self._export_xml
                   ).pack(side="left", padx=(0, 6))
        IconButton(toolbar, "Xuất CSV", icon="📊",
                   bg=T.BTN_DARK_BLUE if hasattr(T, "BTN_DARK_BLUE") else "#1a2442",
                   command=self._export_csv
                   ).pack(side="left", padx=(0, 6))
        IconButton(toolbar, "+ Thêm", bg=T.ACCENT_RED,
                   command=self._add_product
                   ).pack(side="left")

        # ---- Table ----
        table_frame = tk.Frame(self, bg=T.CARD_BG,
                               highlightbackground=T.CARD_BORDER, highlightthickness=1)
        table_frame.pack(fill="both", expand=True, padx=24, pady=(0, 8))
        self._table = DataTable(table_frame, columns=COLUMNS)
        self._table.pack(fill="both", expand=True, padx=1, pady=1)

        # ---- Bottom buttons ----
        bottom = tk.Frame(self, bg=T.CONTENT_BG)
        bottom.pack(fill="x", padx=24, pady=(0, 16))
        IconButton(bottom, "✏  Sửa", bg=T.BTN_PRIMARY_BG,
                   command=self._edit_product).pack(side="left", padx=(0, 8))
        IconButton(bottom, "🗑  Xóa", bg=T.BTN_DANGER_BG,
                   command=self._delete_product).pack(side="left")

    # ------------------------------------------------------------------ #
    #  DATA                                                                #
    # ------------------------------------------------------------------ #

    def refresh(self):
        self._products = _load_products()
        self._apply_filter()

    def _apply_filter(self, *_):
        keyword = self._search.get().lower()
        channel_label = self._channel_var.get()
        channel_key   = CHANNEL_KEYS.get(channel_label)

        filtered = self._products
        if keyword:
            filtered = [p for p in filtered
                        if keyword in p.name.lower()
                        or keyword in p.product_id.lower()
                        or keyword in p.category.lower()]
        if channel_key:
            filtered = [p for p in filtered if p.channel == channel_key]

        rows = []
        for p in filtered:
            rows.append([
                p.product_id,
                p.name,
                p.category,
                format_currency(p.price),
                str(p.quantity),
                "cái",
                CHANNEL_LABELS.get(p.channel, p.channel),
            ])
        self._table.load_rows(rows)

    # ------------------------------------------------------------------ #
    #  CRUD                                                                #
    # ------------------------------------------------------------------ #

    def _add_product(self):
        dialog = ProductDialog(self, title="Thêm sản phẩm mới")
        self.wait_window(dialog)
        if dialog.result:
            self._products.append(dialog.result)
            _save_products(self._products)
            self._apply_filter()
            messagebox.showinfo("Thành công", "Đã thêm sản phẩm mới.")

    def _edit_product(self):
        sel = self._table.get_selected()
        if not sel:
            messagebox.showwarning("Chọn sản phẩm", "Vui lòng chọn sản phẩm cần sửa.")
            return
        pid = sel[0]
        product = next((p for p in self._products if p.product_id == pid), None)
        if not product:
            return
        dialog = ProductDialog(self, title="Chỉnh sửa sản phẩm", product=product)
        self.wait_window(dialog)
        if dialog.result:
            idx = next(i for i, p in enumerate(self._products) if p.product_id == pid)
            self._products[idx] = dialog.result
            _save_products(self._products)
            self._apply_filter()
            messagebox.showinfo("Thành công", "Đã cập nhật sản phẩm.")

    def _delete_product(self):
        sel = self._table.get_selected()
        if not sel:
            messagebox.showwarning("Chọn sản phẩm", "Vui lòng chọn sản phẩm cần xóa.")
            return
        pid = sel[0]
        name = sel[1]
        if not messagebox.askyesno("Xác nhận xóa",
                                   f"Bạn có chắc muốn xóa sản phẩm:\n{name}?"):
            return
        self._products = [p for p in self._products if p.product_id != pid]
        _save_products(self._products)
        self._apply_filter()
        messagebox.showinfo("Thành công", "Đã xóa sản phẩm.")

    # ------------------------------------------------------------------ #
    #  EXPORT                                                              #
    # ------------------------------------------------------------------ #

    def _export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile="products.csv",
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["Mã SP", "Tên", "Danh mục", "Giá", "Tồn kho", "Kênh"])
                for p in self._products:
                    writer.writerow([p.product_id, p.name, p.category,
                                     p.price, p.quantity, p.channel])
            messagebox.showinfo("Xuất CSV", f"Đã xuất thành công:\n{path}")
        except Exception as e:
            messagebox.showerror("Lỗi xuất CSV", str(e))

    def _export_xml(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".xml",
            filetypes=[("XML Files", "*.xml")],
            initialfile="products.xml",
        )
        if not path:
            return
        try:
            root = ET.Element("products")
            for p in self._products:
                elem = ET.SubElement(root, "product")
                for key, val in p.to_dict().items():
                    child = ET.SubElement(elem, key)
                    child.text = str(val)
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ")
            tree.write(path, encoding="utf-8", xml_declaration=True)
            messagebox.showinfo("Xuất XML", f"Đã xuất thành công:\n{path}")
        except Exception as e:
            messagebox.showerror("Lỗi xuất XML", str(e))


# --- PRODUCT DIALOG ---

class ProductDialog(ModalDialog):
    """ Dialog thêm / sửa sản phẩm. """

    def __init__(self, parent, title: str, product: Product = None):
        super().__init__(parent, title=title, width=480, height=440)
        self._product = product
        self._build_form()
        if product:
            self._populate(product)

    def _build_form(self):
        tk.Label(self, text=self.title(),
                 font=T.F_SECTION_TITLE,
                 bg=T.CONTENT_BG, fg=T.TEXT_PRIMARY,
                 ).pack(fill="x", padx=20, pady=(16, 8))

        form = tk.Frame(self, bg=T.CONTENT_BG)
        form.pack(fill="both", expand=True)
        form.columnconfigure(1, weight=1)

        self._name_var     = tk.StringVar()
        self._price_var    = tk.StringVar()
        self._qty_var      = tk.StringVar()
        self._cat_var      = tk.StringVar()
        self._channel_var  = tk.StringVar(value="both")

        self._make_field(form, "Tên sản phẩm *", self._name_var,  row=0)
        self._make_field(form, "Giá (VND) *",    self._price_var, row=1)
        self._make_field(form, "Tồn kho *",      self._qty_var,   row=2)
        self._make_field(form, "Danh mục",        self._cat_var,   row=3)
        self._make_combobox(form, "Kênh bán hàng", self._channel_var,
                            ["both", "online", "offline"], row=4)

        self._footer_buttons(self, self._save, self.destroy)

    def _populate(self, p: Product):
        self._name_var.set(p.name)
        self._price_var.set(str(int(p.price)))
        self._qty_var.set(str(p.quantity))
        self._cat_var.set(p.category)
        self._channel_var.set(p.channel)

    def _save(self):
        try:
            name    = self._name_var.get().strip()
            price   = float(self._price_var.get())
            qty     = int(self._qty_var.get())
            cat     = self._cat_var.get().strip() or "Chưa phân loại"
            channel = self._channel_var.get()

            if not name:
                raise ValueError("Tên sản phẩm không được để trống.")

            if self._product:
                # Edit existing – preserve ID
                import copy
                p = Product(
                    name=name, price=price, quantity=qty,
                    category=cat, channel=channel,
                    product_id=self._product.product_id,
                    created_at=self._product.created_at,
                )
            else:
                p = Product(name=name, price=price, quantity=qty,
                            category=cat, channel=channel)
            self.result = p
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Dữ liệu không hợp lệ", str(e), parent=self)
