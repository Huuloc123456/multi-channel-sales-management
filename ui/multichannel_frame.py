""" ui/multichannel_frame.py  Frame Dữ liệu Đa kênh – Shopee / Facebook / TikTok Shop. Chức năng: • Hiển thị đơn hàng theo từng kênh bán hàng • Thống kê nhanh theo kênh • Nhập đơn từ dữ liệu mô phỏng (demo) hoặc file CSV • Xuất báo cáo theo từng kênh """

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json, csv, logging, threading, random
from pathlib import Path
from datetime import datetime, timedelta

from ui import theme as T
from ui.widgets import IconButton, DataTable, build_page_header
from utils.helpers import format_currency, generate_id, get_timestamp

logger = logging.getLogger(__name__)

ORDER_FILE    = Path("data/orders.json")
CUSTOMER_FILE = Path("data/customers.json")
PRODUCT_FILE  = Path("data/products.json")

# ── Channel metadata ────────────────────────────────────────────────────────
CHANNELS = {
    "shopee":   {"label":"Shopee",   "icon":"🛍", "color":"#ee4d2d", "bg":"#fff4f2"},
    "facebook": {"label":"Facebook", "icon":"📘", "color":"#1877f2", "bg":"#f0f4ff"},
    "tiktok":   {"label":"TikTok",   "icon":"🎵", "color":"#fe2c55", "bg":"#fff0f2"},
    "online":   {"label":"Online",   "icon":"🌐", "color":"#2196f3", "bg":"#f0f7ff"},
    "offline":  {"label":"Tại quầy","icon":"🏪", "color":"#f39c12", "bg":"#fff8f0"},
}

STATUS_VN = {
    "pending":"Chờ xác nhận","confirmed":"Đã xác nhận",
    "shipping":"Đang giao","completed":"Hoàn thành","cancelled":"Đã hủy",
}

def _load(path: Path) -> list:
    try:
        with open(path,"r",encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _save(path: Path, data: list):
    path.parent.mkdir(exist_ok=True)
    with open(path,"w",encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ══════════════════════════════════════════════════════════════════════════ #
class MultichannelFrame(tk.Frame):
    """ Frame tổng hợp và phân tích dữ liệu theo từng kênh bán hàng. """

    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, bg=T.CONTENT_BG, **kwargs)
        self.controller = controller
        self._build()
        self.refresh()

    # ── layout ─────────────────────────────────────────────────────────────
    def _build(self):
        build_page_header(self,
            title="Quản lý Đa kênh",
            subtitle="Shopee | Facebook | TikTok | Online | Tại quầy",
            icon="📡")

        # Notebook tabs – one per channel
        style = ttk.Style()
        style.configure("MCh.TNotebook", background=T.CONTENT_BG, borderwidth=0)
        style.configure("MCh.TNotebook.Tab", font=T.F_FORM_LABEL, padding=(14,7))
        style.map("MCh.TNotebook.Tab",
                  background=[("selected", T.CARD_BG)],
                  foreground=[("selected", T.ACCENT_RED)])

        self._nb = ttk.Notebook(self, style="MCh.TNotebook")
        self._nb.pack(fill="both", expand=True, padx=24, pady=(0,16))

        self._tabs: dict[str, ChannelTab] = {}
        for key, meta in CHANNELS.items():
            tab = ChannelTab(self._nb, channel_key=key, meta=meta,
                             controller=self.controller)
            self._tabs[key] = tab
            self._nb.add(tab, text=f"{meta['icon']}  {meta['label']}")

    def refresh(self):
        orders    = _load(ORDER_FILE)
        customers = {c["customer_id"]: c.get("full_name","?")
                     for c in _load(CUSTOMER_FILE)}
        products  = {p["product_id"]: p for p in _load(PRODUCT_FILE)}

        for key, tab in self._tabs.items():
            ch_orders = [o for o in orders if o.get("channel") == key]
            tab.load_data(ch_orders, customers, products)


# ══════════════════════════════════════════════════════════════════════════ #
class ChannelTab(tk.Frame):
    """ Tab cho một kênh cụ thể. """

    def __init__(self, parent, channel_key: str, meta: dict, controller, **kwargs):
        super().__init__(parent, bg=T.CONTENT_BG, **kwargs)
        self._key        = channel_key
        self._meta       = meta
        self.controller  = controller
        self._orders     = []
        self._customers  = {}
        self._products   = {}
        self._build()

    # ── layout ─────────────────────────────────────────────────────────────
    def _build(self):
        # KPI strip
        kpi = tk.Frame(self, bg=T.CONTENT_BG)
        kpi.pack(fill="x", padx=0, pady=(8,12))

        color = self._meta["color"]
        kpi_defs = [
            ("Tổng đơn",    "📦"),
            ("Doanh thu",   "💰"),
            ("Đơn HT",      "✅"),
            ("Tỷ lệ HT",    "📊"),
        ]
        self._kpi_labels = []
        for i, (lbl, icon) in enumerate(kpi_defs):
            card = tk.Frame(kpi, bg=T.CARD_BG,
                            highlightbackground=color, highlightthickness=2)
            card.grid(row=0, column=i, sticky="nsew", padx=(0,10 if i<3 else 0))
            kpi.columnconfigure(i, weight=1)

            tk.Frame(card, bg=color, height=4).pack(fill="x")
            inner = tk.Frame(card, bg=T.CARD_BG)
            inner.pack(fill="both", expand=True, padx=12, pady=10)
            tk.Label(inner, text=lbl, font=T.F_STAT_LABEL,
                     bg=T.CARD_BG, fg=T.TEXT_SECONDARY, anchor="w").pack(fill="x")
            val_lbl = tk.Label(inner, text="–", font=T.F_STAT_VALUE,
                               bg=T.CARD_BG, fg=color, anchor="w")
            val_lbl.pack(fill="x", pady=(2,0))
            self._kpi_labels.append(val_lbl)

        # Toolbar
        tb = tk.Frame(self, bg=T.CONTENT_BG)
        tb.pack(fill="x", pady=(0,8))

        IconButton(tb, f"🔄 Tải demo {self._meta['label']}",
                   bg=self._meta["color"],
                   command=self._import_demo).pack(side="left", padx=(0,8))
        IconButton(tb, "📂 Nhập CSV", bg=T.BTN_PRIMARY_BG,
                   command=self._import_csv).pack(side="left", padx=(0,8))
        IconButton(tb, "📊 Xuất CSV", bg=T.BTN_EXPORT_BG,
                   command=self._export_csv).pack(side="left", padx=(0,8))
        IconButton(tb, "📄 Báo cáo TXT", bg=T.BTN_EXPORT_BG,
                   command=self._export_txt).pack(side="left")

        # Status filter
        self._status_var = tk.StringVar()
        st_cb = ttk.Combobox(tb, textvariable=self._status_var,
                             values=[""] + list(STATUS_VN.values()),
                             width=14, state="readonly", font=T.F_FORM_INPUT)
        st_cb.pack(side="right")
        st_cb.bind("<<ComboboxSelected>>", lambda e: self._refresh_table())

        # Orders table
        cols = [
            {"id":"order_id", "heading":"Mã đơn",    "width":120,"anchor":"w"},
            {"id":"customer", "heading":"Khách hàng","width":160,"anchor":"w","stretch":True},
            {"id":"total",    "heading":"Tổng tiền", "width":130,"anchor":"e"},
            {"id":"status",   "heading":"Trạng thái","width":120,"anchor":"w"},
            {"id":"items",    "heading":"SP",         "width":50, "anchor":"center"},
            {"id":"date",     "heading":"Ngày tạo",  "width":150,"anchor":"w"},
        ]
        frame = tk.Frame(self, bg=T.CARD_BG,
                         highlightbackground=T.CARD_BORDER, highlightthickness=1)
        frame.pack(fill="both", expand=True, pady=(0,8))
        self._table = DataTable(frame, columns=cols)
        self._table.pack(fill="both", expand=True, padx=1, pady=1)

    # ── data ───────────────────────────────────────────────────────────────
    def load_data(self, orders, customers, products):
        self._orders    = orders
        self._customers = customers
        self._products  = products
        self._update_kpis()
        self._refresh_table()

    def _update_kpis(self):
        orders = self._orders
        total_rev = sum(o.get("total_amount",0) for o in orders)
        done_cnt  = sum(1 for o in orders if o.get("status")=="completed")
        rate      = f"{done_cnt/len(orders)*100:.0f}%" if orders else "0%"
        vals = [str(len(orders)), format_currency(total_rev), str(done_cnt), rate]
        for lbl, v in zip(self._kpi_labels, vals):
            lbl.config(text=v)

    def _refresh_table(self):
        st_vn = self._status_var.get()
        orders = self._orders
        if st_vn:
            st_key = {v:k for k,v in STATUS_VN.items()}.get(st_vn)
            if st_key:
                orders = [o for o in orders if o.get("status")==st_key]
        rows = [[
            o.get("order_id",""),
            self._customers.get(o.get("customer_id",""), o.get("customer_id","")),
            format_currency(o.get("total_amount",0)),
            STATUS_VN.get(o.get("status",""), o.get("status","")),
            str(sum(i.get("quantity",1) for i in o.get("items",[]))),
            o.get("created_at",""),
        ] for o in orders]
        self._table.load_rows(rows)

    # ── import demo ────────────────────────────────────────────────────────
    def _import_demo(self):
        """ Tạo đơn hàng demo cho kênh này. """
        customers = _load(CUSTOMER_FILE)
        products  = _load(PRODUCT_FILE)
        if not customers or not products:
            messagebox.showwarning("Thiếu dữ liệu",
                "Cần có ít nhất 1 khách hàng và 1 sản phẩm trong hệ thống.")
            return

        n = random.randint(5, 10)
        statuses = ["pending","confirmed","shipping","completed","cancelled"]
        new_orders = []

        for _ in range(n):
            cust = random.choice(customers)
            num_items = random.randint(1, 3)
            items = []
            total = 0.0
            for _ in range(num_items):
                prod = random.choice(products)
                qty  = random.randint(1, 5)
                sub  = prod["price"] * qty
                items.append({
                    "product_id":   prod["product_id"],
                    "product_name": prod["name"],
                    "unit_price":   prod["price"],
                    "quantity":     qty,
                    "subtotal":     sub,
                })
                total += sub

            days_ago = random.randint(0, 30)
            created  = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")

            new_orders.append({
                "order_id":    generate_id("DH"),
                "customer_id": cust["customer_id"],
                "channel":     self._key,
                "status":      random.choice(statuses),
                "discount":    0.0,
                "notes":       random.choice(["cash","transfer","momo","vnpay"]),
                "items":       items,
                "subtotal":    total,
                "total_amount":total,
                "item_count":  sum(i["quantity"] for i in items),
                "created_at":  created,
                "updated_at":  created,
            })

        existing = _load(ORDER_FILE)
        existing.extend(new_orders)
        _save(ORDER_FILE, existing)

        # Reload
        all_orders = _load(ORDER_FILE)
        all_customers = {c["customer_id"]:c.get("full_name","?")
                         for c in _load(CUSTOMER_FILE)}
        self.load_data(
            [o for o in all_orders if o.get("channel")==self._key],
            all_customers, {p["product_id"]:p for p in _load(PRODUCT_FILE)}
        )
        messagebox.showinfo("Thành công",
            f"Đã tạo {n} đơn hàng demo cho kênh {self._meta['label']}.")

    # ── import CSV ─────────────────────────────────────────────────────────
    def _import_csv(self):
        path = filedialog.askopenfilename(
            title=f"Nhập đơn hàng {self._meta['label']} từ CSV",
            filetypes=[("CSV","*.csv"),("All","*.*")])
        if not path:
            return
        try:
            with open(path,"r",encoding="utf-8-sig") as f:
                rows = list(csv.DictReader(f))
            if not rows:
                messagebox.showwarning("Rỗng","File CSV không có dữ liệu.")
                return

            customers = _load(CUSTOMER_FILE)
            cust_map  = {c.get("full_name","").lower(): c["customer_id"]
                         for c in customers}
            products  = _load(PRODUCT_FILE)
            prod_map  = {p.get("name","").lower(): p for p in products}

            new_orders = []
            for row in rows:
                cust_name = row.get("Khách hàng","").strip()
                cid = cust_map.get(cust_name.lower(), generate_id("KH"))
                total = float(str(row.get("Tổng tiền","0")).replace(",","").replace("₫","") or 0)
                new_orders.append({
                    "order_id":    row.get("Mã đơn", generate_id("DH")),
                    "customer_id": cid,
                    "channel":     self._key,
                    "status":      row.get("Trạng thái","pending"),
                    "discount":    0.0,
                    "notes":       row.get("Thanh toán","cash"),
                    "items":       [],
                    "subtotal":    total,
                    "total_amount":total,
                    "item_count":  0,
                    "created_at":  row.get("Ngày tạo", get_timestamp()),
                    "updated_at":  get_timestamp(),
                })
            existing = _load(ORDER_FILE)
            existing.extend(new_orders)
            _save(ORDER_FILE, existing)
            messagebox.showinfo("Nhập CSV",
                f"Đã nhập {len(new_orders)} đơn hàng từ {path}")
            # Reload tab
            all_orders = _load(ORDER_FILE)
            all_customers = {c["customer_id"]:c.get("full_name","?")
                             for c in _load(CUSTOMER_FILE)}
            self.load_data(
                [o for o in all_orders if o.get("channel")==self._key],
                all_customers, {})
        except Exception as e:
            messagebox.showerror("Lỗi nhập CSV", str(e))

    # ── exports ────────────────────────────────────────────────────────────
    def _export_csv(self):
        label = self._meta["label"]
        path  = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV","*.csv")],
            initialfile=f"orders_{self._key}.csv")
        if not path:
            return
        try:
            with open(path,"w",newline="",encoding="utf-8-sig") as f:
                w = csv.writer(f)
                w.writerow(["Mã đơn","Khách hàng","Tổng tiền","Trạng thái","Ngày tạo"])
                for o in self._orders:
                    w.writerow([
                        o.get("order_id",""),
                        self._customers.get(o.get("customer_id",""), "?"),
                        o.get("total_amount",0),
                        STATUS_VN.get(o.get("status",""), o.get("status","")),
                        o.get("created_at",""),
                    ])
            messagebox.showinfo("Xuất CSV",
                f"Đã xuất {len(self._orders)} đơn {label}:\n{path}")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def _export_txt(self):
        label = self._meta["label"]
        path  = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text","*.txt")],
            initialfile=f"report_{self._key}.txt")
        if not path:
            return
        try:
            orders    = self._orders
            total_rev = sum(o.get("total_amount",0) for o in orders)
            done      = sum(1 for o in orders if o.get("status")=="completed")
            SEP = "─" * 60
            lines = [
                "=" * 60,
                f"  BÁO CÁO KÊNH {label.upper()}",
                f"  Ngày xuất: {datetime.now():%d/%m/%Y %H:%M}",
                "=" * 60, "",
                f"  Tổng đơn hàng  : {len(orders)}",
                f"  Tổng doanh thu : {format_currency(total_rev)}",
                f"  Đơn hoàn thành : {done}",
                f"  Tỷ lệ HT       : {done/len(orders)*100:.1f}%" if orders else "  Tỷ lệ HT: 0%",
                "",
                "TRẠNG THÁI:",
            ]
            for st, lbl in STATUS_VN.items():
                cnt = sum(1 for o in orders if o.get("status")==st)
                lines.append(f"  {lbl:<16}: {cnt}")
            lines += ["", SEP, "CHI TIẾT ĐƠN HÀNG:", SEP,
                      f"{'Mã đơn':<14}{'Khách hàng':<22}{'Tổng tiền':>16}{'Trạng thái':<14}",
                      SEP]
            for o in orders[:50]:  # max 50 rows
                cust = self._customers.get(o.get("customer_id",""), "?")[:18]
                lines.append(
                    f"{o.get('order_id',''):<14}{cust:<22}"
                    f"{format_currency(o.get('total_amount',0)):>16}"
                    f"{STATUS_VN.get(o.get('status',''), '?'):<14}")
            lines += [SEP, "=" * 60]
            with open(path,"w",encoding="utf-8") as f:
                f.write("\n".join(lines))
            messagebox.showinfo("Xuất TXT", f"Đã xuất báo cáo {label}:\n{path}")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
