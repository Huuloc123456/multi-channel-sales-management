""" ui/order_frame.py  Frame Quản lý Đơn hàng. Chức năng: Tìm kiếm, lọc trạng thái/kênh, xem chi tiết, tạo đơn, cập nhật TT, xóa, xuất. """

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
from ui.order_workflow import WorkflowDialog
from models.order import Order, OrderItem
from models.customer import Customer
from models.product import Product
from utils.helpers import format_currency

logger = logging.getLogger(__name__)

ORDER_FILE    = Path("data/orders.json")
CUSTOMER_FILE = Path("data/customers.json")
PRODUCT_FILE  = Path("data/products.json")


def _load_json(path: Path) -> list:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save_orders(orders: list[Order]):
    ORDER_FILE.parent.mkdir(exist_ok=True)
    with open(ORDER_FILE, "w", encoding="utf-8") as f:
        json.dump([o.to_dict() for o in orders], f, ensure_ascii=False, indent=2)


STATUS_VN = {
    "pending":   "Chờ xác nhận",
    "confirmed": "Đã xác nhận",
    "shipping":  "Đang giao",
    "completed": "Hoàn thành",
    "cancelled": "Đã hủy",
}
STATUS_EN = {v: k for k, v in STATUS_VN.items()}

CHANNEL_VN = {
    "online":   "Online",
    "offline":  "Tại quầy",
    "facebook": "Facebook",
    "shopee":   "Shopee",
    "tiktok":   "TikTok",
}

PAYMENT_LABELS = ["cash", "transfer", "momo", "vnpay", "card"]

COLUMNS = [
    {"id": "order_id",   "heading": "Mã đơn",      "width": 110, "anchor": "w"},
    {"id": "customer",   "heading": "Khách hàng",   "width": 150, "anchor": "w"},
    {"id": "channel",    "heading": "Kênh",          "width": 90,  "anchor": "w"},
    {"id": "total",      "heading": "Tổng tiền",     "width": 120, "anchor": "e"},
    {"id": "status",     "heading": "Trạng thái",   "width": 110, "anchor": "w"},
    {"id": "payment",    "heading": "Thanh toán",   "width": 90,  "anchor": "w"},
    {"id": "created_at", "heading": "Thời gian",    "width": 155, "anchor": "w", "stretch": True},
]


class OrderFrame(tk.Frame):
    """ Frame quản lý đơn hàng. """

    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, bg=T.CONTENT_BG, **kwargs)
        self.controller = controller
        self._orders: list[Order] = []
        self._cust_map: dict = {}
        self._build()
        self.refresh()

    def _build(self):
        build_page_header(
            self,
            title="Quản lý đơn hàng",
            subtitle="Theo dõi đơn hàng đa kênh",
            icon="📦",
        )

        # Toolbar
        toolbar = tk.Frame(self, bg=T.CONTENT_BG)
        toolbar.pack(fill="x", padx=24, pady=(0, 8))

        self._search = SearchBar(toolbar, placeholder="Tìm đơn hàng...",
                                 on_search=self._apply_filter)
        self._search.pack(side="left", fill="x", expand=True, ipady=2)

        # Channel filter
        self._channel_var = tk.StringVar()
        ch_cb = ttk.Combobox(toolbar, textvariable=self._channel_var,
                              values=[""] + list(CHANNEL_VN.values()),
                              width=12, state="readonly", font=T.F_FORM_INPUT)
        ch_cb.pack(side="left", padx=(8, 4))
        ch_cb.bind("<<ComboboxSelected>>", lambda e: self._apply_filter())

        # Status filter
        self._status_var = tk.StringVar()
        st_cb = ttk.Combobox(toolbar, textvariable=self._status_var,
                              values=[""] + list(STATUS_VN.values()),
                              width=14, state="readonly", font=T.F_FORM_INPUT)
        st_cb.pack(side="left", padx=(0, 8))
        st_cb.bind("<<ComboboxSelected>>", lambda e: self._apply_filter())

        IconButton(toolbar, "📤 CSV", bg=T.BTN_EXPORT_BG,
                   command=self._export_csv).pack(side="left", padx=(0, 4))
        IconButton(toolbar, "📄 TXT", bg=T.BTN_EXPORT_BG,
                   command=self._export_txt_report).pack(side="left", padx=(0, 6))
        IconButton(toolbar, "+ Tạo đơn", bg=T.ACCENT_RED,
                   command=self._create_order).pack(side="left")

        # Table
        frame = tk.Frame(self, bg=T.CARD_BG,
                         highlightbackground=T.CARD_BORDER, highlightthickness=1)
        frame.pack(fill="both", expand=True, padx=24, pady=(0, 8))
        self._table = DataTable(frame, columns=COLUMNS)
        self._table.pack(fill="both", expand=True, padx=1, pady=1)
        self._table.bind_double_click(lambda e: self._view_order())

        # Bottom
        bottom = tk.Frame(self, bg=T.CONTENT_BG)
        bottom.pack(fill="x", padx=24, pady=(0, 16))
        IconButton(bottom, "⚡ Xử lý đơn", bg=T.ACCENT_RED,
                   command=self._handle_order).pack(side="left", padx=(0, 8))
        IconButton(bottom, "👁 Xem", bg=T.BTN_PRIMARY_BG,
                   command=self._view_order).pack(side="left", padx=(0, 8))
        IconButton(bottom, "✏ Cập nhật TT", bg=T.BTN_WARNING_BG,
                   command=self._update_status).pack(side="left", padx=(0, 8))
        IconButton(bottom, "🗑 Xóa", bg=T.BTN_DANGER_BG,
                   command=self._delete_order).pack(side="left")

    def refresh(self):
        raw_orders    = _load_json(ORDER_FILE)
        raw_customers = _load_json(CUSTOMER_FILE)
        self._cust_map = {c["customer_id"]: c.get("full_name", "?") for c in raw_customers}
        self._orders = [Order.from_dict(o) for o in raw_orders]
        self._apply_filter()

    def _apply_filter(self, *_):
        keyword = self._search.get().lower()
        ch_vn   = self._channel_var.get()
        st_vn   = self._status_var.get()

        filtered = self._orders
        if keyword:
            filtered = [o for o in filtered
                        if keyword in o.order_id.lower()
                        or keyword in self._cust_map.get(o.customer_id, "").lower()]
        if ch_vn:
            ch_key = {v: k for k, v in CHANNEL_VN.items()}.get(ch_vn)
            if ch_key:
                filtered = [o for o in filtered if o.channel == ch_key]
        if st_vn:
            st_key = STATUS_EN.get(st_vn)
            if st_key:
                filtered = [o for o in filtered if o.status == st_key]

        rows = []
        for o in filtered:
            rows.append([
                o.order_id,
                self._cust_map.get(o.customer_id, o.customer_id),
                CHANNEL_VN.get(o.channel, o.channel),
                format_currency(o.total_amount),
                STATUS_VN.get(o.status, o.status),
                o.notes or "cash",
                o.created_at,
            ])
        self._table.load_rows(rows)

    # ---- CRUD ----

    def _create_order(self):
        raw_customers = _load_json(CUSTOMER_FILE)
        raw_products  = _load_json(PRODUCT_FILE)
        customers = [Customer.from_dict(c) for c in raw_customers]
        products  = [Product.from_dict(p) for p in raw_products]
        if not customers:
            messagebox.showwarning("Thiếu dữ liệu", "Chưa có khách hàng. Vui lòng thêm khách hàng trước.")
            return
        if not products:
            messagebox.showwarning("Thiếu dữ liệu", "Chưa có sản phẩm. Vui lòng thêm sản phẩm trước.")
            return
        dialog = OrderCreateDialog(self, customers=customers, products=products)
        self.wait_window(dialog)
        if dialog.result:
            self._orders.append(dialog.result)
            _save_orders(self._orders)
            self._apply_filter()
            messagebox.showinfo("Thành công", f"Đã tạo đơn hàng: {dialog.result.order_id}")

    def _handle_order(self):
        """ Mở WorkflowDialog để xử lý đơn theo luồng nghiệp vụ. """
        sel = self._table.get_selected()
        if not sel:
            messagebox.showwarning("Chọn đơn", "Vui lòng chọn đơn hàng.")
            return
        oid   = sel[0]
        order = next((o for o in self._orders if o.order_id == oid), None)
        if not order:
            return
        def _on_changed(updated_order):
            _save_orders(self._orders)
            self._apply_filter()
        WorkflowDialog(
            self, order=order,
            cust_name=self._cust_map.get(order.customer_id, order.customer_id),
            on_status_changed=_on_changed,
        )

    def _view_order(self):
        sel = self._table.get_selected()
        if not sel:
            messagebox.showwarning("Chọn đơn", "Vui lòng chọn đơn hàng.")
            return
        oid = sel[0]
        order = next((o for o in self._orders if o.order_id == oid), None)
        if not order:
            return
        OrderDetailDialog(self, order=order,
                          cust_name=self._cust_map.get(order.customer_id, order.customer_id))

    def _update_status(self):
        sel = self._table.get_selected()
        if not sel:
            messagebox.showwarning("Chọn đơn", "Vui lòng chọn đơn hàng.")
            return
        oid = sel[0]
        order = next((o for o in self._orders if o.order_id == oid), None)
        if not order:
            return
        dialog = StatusUpdateDialog(self, current=order.status)
        self.wait_window(dialog)
        if dialog.result:
            try:
                order.status = dialog.result
                _save_orders(self._orders)
                self._apply_filter()
                messagebox.showinfo("Thành công",
                                    f"Đã cập nhật trạng thái: {STATUS_VN[dialog.result]}")
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))

    def _delete_order(self):
        sel = self._table.get_selected()
        if not sel:
            messagebox.showwarning("Chọn đơn", "Vui lòng chọn đơn hàng.")
            return
        oid = sel[0]
        if not messagebox.askyesno("Xác nhận xóa",
                                   f"Bạn có chắc muốn xóa đơn hàng:\n{oid}?"):
            return
        self._orders = [o for o in self._orders if o.order_id != oid]
        _save_orders(self._orders)
        self._apply_filter()
        messagebox.showinfo("Thành công", "Đã xóa đơn hàng.")

    def _export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile="orders.csv",
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["Mã đơn", "Khách hàng", "Kênh",
                                 "Tổng tiền", "Trạng thái", "Thời gian"])
                for o in self._orders:
                    writer.writerow([
                        o.order_id,
                        self._cust_map.get(o.customer_id, o.customer_id),
                        CHANNEL_VN.get(o.channel, o.channel),
                        o.total_amount,
                        STATUS_VN.get(o.status, o.status),
                        o.created_at,
                    ])
            messagebox.showinfo("Xuất CSV", f"Đã xuất:\n{path}")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def _export_txt_report(self):
        """ Xuất danh sách đơn hàng đang lọc ra file TXT. """
        import csv as _csv
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text","*.txt")],
            initialfile="orders_report.txt",
        )
        if not path:
            return
        try:
            SEP = "-" * 72
            lines = [
                "=" * 72,
                "  DANH SÁCH ĐƠN HÀNG – HỆ THỐNG QUẢN LÝ BÁN HÀNG",
                "=" * 72,
                f"{'Mã đơn':<14}{'Khách hàng':<22}{'Kênh':<12}"
                f"{'Tổng tiền':>16}{'Trạng thái':<16}",
                SEP,
            ]
            for o in self._orders:
                lines.append(
                    f"{o.order_id:<14}"
                    f"{self._cust_map.get(o.customer_id, o.customer_id)[:20]:<22}"
                    f"{CHANNEL_VN.get(o.channel, o.channel):<12}"
                    f"{format_currency(o.total_amount):>16}"
                    f"{STATUS_VN.get(o.status, o.status):<16}"
                )
            lines += [SEP, f"Tổng cộng: {len(self._orders)} đơn hàng", "=" * 72]
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            messagebox.showinfo("Xuất TXT", f"Đã xuất:\n{path}")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))


# --- ORDER DETAIL DIALOG ---

class OrderDetailDialog(ModalDialog):
    def __init__(self, parent, order: Order, cust_name: str):
        super().__init__(parent, title=f"Chi tiết đơn hàng – {order.order_id}",
                         width=560, height=500)
        self._order = order
        self._cust_name = cust_name
        self._build()

    def _build(self):
        o = self._order
        tk.Label(self, text=f"Chi tiết đơn hàng",
                 font=T.F_SECTION_TITLE, bg=T.CONTENT_BG,
                 fg=T.TEXT_PRIMARY).pack(fill="x", padx=20, pady=(16, 8))

        # Info grid
        info = tk.Frame(self, bg=T.CONTENT_BG)
        info.pack(fill="x", padx=20, pady=(0, 12))
        info.columnconfigure(1, weight=1)
        info.columnconfigure(3, weight=1)

        pairs = [
            ("Mã đơn:",    o.order_id,      "Khách hàng:", self._cust_name),
            ("Kênh:",      CHANNEL_VN.get(o.channel, o.channel),
             "Trạng thái:", STATUS_VN.get(o.status, o.status)),
            ("Tổng tiền:", format_currency(o.total_amount),
             "Ngày tạo:",  o.created_at),
        ]
        for row_i, (l1, v1, l2, v2) in enumerate(pairs):
            tk.Label(info, text=l1, font=T.F_FORM_LABEL,
                     bg=T.CONTENT_BG, fg=T.TEXT_SECONDARY).grid(
                row=row_i, column=0, sticky="w", pady=3)
            tk.Label(info, text=v1, font=(T.FONT_APP, 10, "bold"),
                     bg=T.CONTENT_BG, fg=T.TEXT_PRIMARY).grid(
                row=row_i, column=1, sticky="w", padx=(4, 20))
            tk.Label(info, text=l2, font=T.F_FORM_LABEL,
                     bg=T.CONTENT_BG, fg=T.TEXT_SECONDARY).grid(
                row=row_i, column=2, sticky="w")
            tk.Label(info, text=v2, font=(T.FONT_APP, 10, "bold"),
                     bg=T.CONTENT_BG, fg=T.TEXT_PRIMARY).grid(
                row=row_i, column=3, sticky="w", padx=4)

        # Items table
        tk.Label(self, text="Sản phẩm trong đơn:",
                 font=T.F_FORM_LABEL, bg=T.CONTENT_BG,
                 fg=T.TEXT_SECONDARY).pack(fill="x", padx=20, pady=(4, 4))

        item_cols = [
            {"id": "name",  "heading": "Sản phẩm", "width": 200, "anchor": "w", "stretch": True},
            {"id": "price", "heading": "Đơn giá",   "width": 110, "anchor": "e"},
            {"id": "qty",   "heading": "SL",        "width": 60,  "anchor": "center"},
            {"id": "sub",   "heading": "Thành tiền","width": 120, "anchor": "e"},
        ]
        frame = tk.Frame(self, bg=T.CARD_BG,
                         highlightbackground=T.CARD_BORDER, highlightthickness=1)
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 12))
        tbl = DataTable(frame, columns=item_cols)
        tbl.pack(fill="both", expand=True, padx=1, pady=1)
        rows = [[
            item.product_name,
            format_currency(item.unit_price),
            str(item.quantity),
            format_currency(item.subtotal),
        ] for item in o.items]
        tbl.load_rows(rows)

        tk.Button(self, text="Đóng", font=T.F_BTN,
                  bg=T.BTN_SECONDARY_BG, fg=T.TEXT_WHITE,
                  relief="flat", cursor="hand2",
                  command=self.destroy,
                  ).pack(pady=(0, 12))


# --- STATUS UPDATE DIALOG ---

class StatusUpdateDialog(ModalDialog):
    def __init__(self, parent, current: str):
        super().__init__(parent, title="Cập nhật trạng thái", width=360, height=220)
        self._build(current)

    def _build(self, current: str):
        tk.Label(self, text="Chọn trạng thái mới:",
                 font=T.F_FORM_LABEL, bg=T.CONTENT_BG,
                 fg=T.TEXT_PRIMARY).pack(padx=20, pady=(20, 8), anchor="w")

        self._var = tk.StringVar(value=STATUS_VN.get(current, current))
        cb = ttk.Combobox(self, textvariable=self._var,
                          values=list(STATUS_VN.values()),
                          state="readonly", font=T.F_FORM_INPUT, width=24)
        cb.pack(padx=20, fill="x")

        btn_row = tk.Frame(self, bg=T.CONTENT_BG)
        btn_row.pack(fill="x", padx=20, pady=20)
        IconButton(btn_row, "Hủy",
                   bg=T.BTN_SECONDARY_BG, command=self.destroy).pack(side="right", padx=(6, 0))
        IconButton(btn_row, "✔ Cập nhật",
                   bg=T.BTN_PRIMARY_BG, command=self._save).pack(side="right")

    def _save(self):
        vn = self._var.get()
        self.result = STATUS_EN.get(vn)
        self.destroy()


# --- ORDER CREATE DIALOG ---

class OrderCreateDialog(ModalDialog):
    """ Dialog tạo đơn hàng mới, chọn khách + thêm sản phẩm. """

    def __init__(self, parent, customers: list, products: list):
        super().__init__(parent, title="Tạo đơn hàng mới", width=600, height=560)
        self._customers = customers
        self._products  = products
        self._cart: list[OrderItem] = []
        self._build()

    def _build(self):
        tk.Label(self, text="Tạo đơn hàng mới",
                 font=T.F_SECTION_TITLE, bg=T.CONTENT_BG,
                 fg=T.TEXT_PRIMARY).pack(fill="x", padx=20, pady=(16, 8))

        form = tk.Frame(self, bg=T.CONTENT_BG)
        form.pack(fill="x", padx=20)
        form.columnconfigure(1, weight=1)

        # Customer
        tk.Label(form, text="Khách hàng *", font=T.F_FORM_LABEL,
                 bg=T.CONTENT_BG, fg=T.TEXT_PRIMARY, anchor="w"
                 ).grid(row=0, column=0, sticky="w", padx=(0, 8), pady=6)
        cust_names = [f"{c.customer_id} – {c.full_name}" for c in self._customers]
        self._cust_var = tk.StringVar()
        ttk.Combobox(form, textvariable=self._cust_var, values=cust_names,
                     state="readonly", font=T.F_FORM_INPUT
                     ).grid(row=0, column=1, sticky="ew", pady=6, ipady=4)

        # Channel
        tk.Label(form, text="Kênh bán *", font=T.F_FORM_LABEL,
                 bg=T.CONTENT_BG, fg=T.TEXT_PRIMARY, anchor="w"
                 ).grid(row=1, column=0, sticky="w", padx=(0, 8), pady=6)
        self._channel_var = tk.StringVar(value="offline")
        ttk.Combobox(form, textvariable=self._channel_var,
                     values=list(CHANNEL_VN.keys()),
                     state="readonly", font=T.F_FORM_INPUT
                     ).grid(row=1, column=1, sticky="ew", pady=6, ipady=4)

        # Add product to cart
        tk.Label(form, text="Thêm sản phẩm:", font=T.F_FORM_LABEL,
                 bg=T.CONTENT_BG, fg=T.TEXT_PRIMARY, anchor="w"
                 ).grid(row=2, column=0, sticky="w", padx=(0, 8), pady=6)

        prod_row = tk.Frame(form, bg=T.CONTENT_BG)
        prod_row.grid(row=2, column=1, sticky="ew", pady=6)
        prod_names = [f"{p.product_id} – {p.name}" for p in self._products]
        self._prod_var = tk.StringVar()
        ttk.Combobox(prod_row, textvariable=self._prod_var, values=prod_names,
                     state="readonly", font=T.F_FORM_INPUT, width=28
                     ).pack(side="left", ipady=4)
        self._qty_var = tk.StringVar(value="1")
        tk.Entry(prod_row, textvariable=self._qty_var,
                 font=T.F_FORM_INPUT, width=6, relief="solid", bd=1
                 ).pack(side="left", padx=(6, 6), ipady=4)
        tk.Button(prod_row, text="Thêm", font=T.F_BTN_SM,
                  bg=T.BTN_SUCCESS_BG, fg=T.TEXT_WHITE,
                  relief="flat", cursor="hand2",
                  command=self._add_item).pack(side="left")

        # Cart table
        cart_cols = [
            {"id": "name",  "heading": "Sản phẩm", "width": 200, "anchor": "w", "stretch": True},
            {"id": "price", "heading": "Đơn giá",   "width": 110, "anchor": "e"},
            {"id": "qty",   "heading": "SL",        "width": 50,  "anchor": "center"},
            {"id": "sub",   "heading": "Thành tiền","width": 120, "anchor": "e"},
        ]
        frame = tk.Frame(self, bg=T.CARD_BG,
                         highlightbackground=T.CARD_BORDER, highlightthickness=1)
        frame.pack(fill="both", expand=True, padx=20, pady=(8, 0))
        self._cart_table = DataTable(frame, columns=cart_cols)
        self._cart_table.pack(fill="both", expand=True, padx=1, pady=1)
        self._cart_table.tree.config(height=5)

        # Total
        self._total_label = tk.Label(self, text="Tổng tiền: 0₫",
                                     font=(T.FONT_APP, 11, "bold"),
                                     bg=T.CONTENT_BG, fg=T.ACCENT_RED, anchor="e")
        self._total_label.pack(fill="x", padx=22, pady=(4, 0))

        self._footer_buttons(self, self._save, self.destroy)

    def _add_item(self):
        prod_str = self._prod_var.get()
        if not prod_str:
            messagebox.showwarning("Thiếu thông tin", "Chọn sản phẩm.", parent=self)
            return
        try:
            qty = int(self._qty_var.get())
            assert qty > 0
        except Exception:
            messagebox.showwarning("Số lượng", "Số lượng phải là số nguyên > 0.", parent=self)
            return
        pid = prod_str.split(" – ")[0]
        product = next((p for p in self._products if p.product_id == pid), None)
        if not product:
            return
        item = OrderItem(product_id=product.product_id,
                         product_name=product.name,
                         unit_price=product.price,
                         quantity=qty)
        self._cart.append(item)
        self._refresh_cart()

    def _refresh_cart(self):
        rows = [[
            item.product_name,
            format_currency(item.unit_price),
            str(item.quantity),
            format_currency(item.subtotal),
        ] for item in self._cart]
        self._cart_table.load_rows(rows)
        total = sum(i.subtotal for i in self._cart)
        self._total_label.config(text=f"Tổng tiền: {format_currency(total)}")

    def _save(self):
        cust_str = self._cust_var.get()
        if not cust_str:
            messagebox.showwarning("Thiếu thông tin", "Chọn khách hàng.", parent=self)
            return
        if not self._cart:
            messagebox.showwarning("Giỏ trống", "Thêm ít nhất 1 sản phẩm.", parent=self)
            return
        cid = cust_str.split(" – ")[0]
        channel = self._channel_var.get()
        order = Order(customer_id=cid, channel=channel)
        for item in self._cart:
            order.add_item(item)
        self.result = order
        self.destroy()
