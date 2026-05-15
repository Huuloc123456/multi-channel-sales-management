""" ui/dashboard_frame.py  Frame Dashboard – Tổng quan hệ thống bán hàng. Hiển thị: stat cards + biểu đồ doanh thu theo kênh + tồn kho thấp + đơn gần đây. """

import tkinter as tk
from tkinter import ttk
import json
import logging
from pathlib import Path
from datetime import datetime

from ui import theme as T
from ui.widgets import StatCard, DataTable, ProgressBar, build_page_header

logger = logging.getLogger(__name__)


class DashboardFrame(tk.Frame):
    """ Frame tổng quan – hiển thị các KPI và danh sách nhanh. """

    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, bg=T.CONTENT_BG, **kwargs)
        self.controller = controller
        self._build()
        self.refresh()

    # ------------------------------------------------------------------ #
    #  BUILD UI                                                            #
    # ------------------------------------------------------------------ #

    def _build(self):
        # Scrollable canvas
        canvas = tk.Canvas(self, bg=T.CONTENT_BG, highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._inner = tk.Frame(canvas, bg=T.CONTENT_BG)
        self._win_id = canvas.create_window((0, 0), window=self._inner, anchor="nw")

        self._inner.bind("<Configure>",
                         lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(self._win_id, width=e.width))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        self._canvas = canvas
        self._build_inner()

    def _build_inner(self):
        pad = {"padx": 24, "pady": 0}

        # Page title
        build_page_header(
            self._inner,
            title="Dashboard",
            subtitle="Tổng quan hệ thống bán hàng",
            icon="📊",
        )

        # ---- STAT CARDS ----
        self._stat_frame = tk.Frame(self._inner, bg=T.CONTENT_BG)
        self._stat_frame.pack(fill="x", padx=24, pady=(0, 16))

        configs = [
            ("Tổng doanh thu",    "0₫",  "💰", T.STAT_COLORS[0]),
            ("Đơn hàng Online",   "0₫",  "🌐", T.STAT_COLORS[1]),
            ("Đơn hàng Offline",  "0₫",  "🏪", T.STAT_COLORS[2]),
            ("Tổng đơn hàng",     "0",   "📦", T.STAT_COLORS[3]),
            ("Sản phẩm",          "0",   "🗃", T.STAT_COLORS[4]),
            ("Khách hàng",        "0",   "👥", T.STAT_COLORS[5]),
        ]
        self._stat_cards = []
        for i, (label, val, icon, color) in enumerate(configs):
            card = StatCard(
                self._stat_frame,
                label=label, value=val,
                icon=icon, accent_color=color,
            )
            card.grid(row=0, column=i, sticky="nsew", padx=(0, 8), pady=0)
            self._stat_frame.columnconfigure(i, weight=1)
            self._stat_cards.append(card)

        # ---- MIDDLE ROW: Doanh thu + Tồn kho ----
        mid = tk.Frame(self._inner, bg=T.CONTENT_BG)
        mid.pack(fill="x", padx=24, pady=(0, 16))
        mid.columnconfigure(0, weight=3)
        mid.columnconfigure(1, weight=2)

        self._build_revenue_panel(mid)
        self._build_low_stock_panel(mid)

        # ---- RECENT ORDERS ----
        self._build_recent_orders(self._inner)

    def _build_revenue_panel(self, parent):
        """ Bảng doanh thu theo kênh với progress bars. """
        panel = tk.Frame(parent, bg=T.CARD_BG, relief="flat",
                         highlightbackground=T.CARD_BORDER, highlightthickness=1)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=0)

        tk.Label(panel, text="Doanh thu theo kênh",
                 font=T.F_SECTION_TITLE, bg=T.CARD_BG,
                 fg=T.TEXT_PRIMARY, anchor="w",
                 ).pack(fill="x", padx=16, pady=(14, 12))

        self._rev_rows: dict[str, dict] = {}
        for channel, color in [("Online", T.ONLINE_COLOR), ("Offline", T.OFFLINE_COLOR)]:
            row = tk.Frame(panel, bg=T.CARD_BG)
            row.pack(fill="x", padx=16, pady=(0, 12))

            top = tk.Frame(row, bg=T.CARD_BG)
            top.pack(fill="x")
            icon = "🌐" if channel == "Online" else "🏪"
            tk.Label(top, text=f"{icon}  {channel}",
                     font=T.F_FORM_LABEL, bg=T.CARD_BG,
                     fg=T.TEXT_PRIMARY).pack(side="left")
            val_lbl = tk.Label(top, text="0₫",
                               font=(T.FONT_APP, 10, "bold"),
                               bg=T.CARD_BG, fg=color)
            val_lbl.pack(side="right")

            bar = ProgressBar(row, value=0.0, color=color)
            bar.pack(fill="x", pady=(4, 0))

            self._rev_rows[channel] = {"label": val_lbl, "bar": bar, "color": color}

    def _build_low_stock_panel(self, parent):
        """ Danh sách sản phẩm tồn kho thấp. """
        panel = tk.Frame(parent, bg=T.CARD_BG, relief="flat",
                         highlightbackground=T.CARD_BORDER, highlightthickness=1)
        panel.grid(row=0, column=1, sticky="nsew", pady=0)

        tk.Label(panel, text="Tồn kho thấp",
                 font=T.F_SECTION_TITLE, bg=T.CARD_BG,
                 fg=T.TEXT_PRIMARY, anchor="w",
                 ).pack(fill="x", padx=16, pady=(14, 8))

        self._low_stock_frame = tk.Frame(panel, bg=T.CARD_BG)
        self._low_stock_frame.pack(fill="both", expand=True, padx=16, pady=(0, 12))

    def _build_recent_orders(self, parent):
        """ Bảng đơn hàng gần đây. """
        section = tk.Frame(parent, bg=T.CONTENT_BG)
        section.pack(fill="x", padx=24, pady=(0, 24))

        tk.Label(section, text="Đơn hàng gần đây",
                 font=T.F_SECTION_TITLE, bg=T.CONTENT_BG,
                 fg=T.TEXT_PRIMARY, anchor="w",
                 ).pack(fill="x", pady=(0, 8))

        cols = [
            {"id": "order_id",    "heading": "Mã đơn",       "width": 120, "anchor": "w"},
            {"id": "customer",    "heading": "Khách hàng",    "width": 160, "anchor": "w"},
            {"id": "channel",     "heading": "Kênh",          "width": 90,  "anchor": "w"},
            {"id": "total",       "heading": "Tổng tiền",     "width": 120, "anchor": "e"},
            {"id": "status",      "heading": "Trạng thái",    "width": 110, "anchor": "w"},
            {"id": "created_at",  "heading": "Thời gian",     "width": 160, "anchor": "w", "stretch": True},
        ]
        frame = tk.Frame(section, bg=T.CARD_BG, relief="flat",
                         highlightbackground=T.CARD_BORDER, highlightthickness=1)
        frame.pack(fill="x")
        self._recent_table = DataTable(frame, columns=cols)
        self._recent_table.pack(fill="both", expand=True, padx=1, pady=1)
        self._recent_table.tree.config(height=6)

    # ------------------------------------------------------------------ #
    #  DATA LOADING                                                        #
    # ------------------------------------------------------------------ #

    def refresh(self):
        """ Tải lại dữ liệu từ file và cập nhật UI. """
        try:
            products  = self._load_json("data/products.json")
            customers = self._load_json("data/customers.json")
            orders    = self._load_json("data/orders.json")
            self._update_stats(products, customers, orders)
            self._update_revenue(orders)
            self._update_low_stock(products)
            self._update_recent_orders(orders, customers)
        except Exception as exc:
            logger.error("Dashboard refresh error: %s", exc, exc_info=True)

    @staticmethod
    def _load_json(path: str) -> list:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _update_stats(self, products, customers, orders):
        online_rev  = sum(o.get("total_amount", 0) for o in orders if o.get("channel") == "online")
        offline_rev = sum(o.get("total_amount", 0) for o in orders if o.get("channel") in ("offline", "tại quầy"))
        total_rev   = sum(o.get("total_amount", 0) for o in orders)

        def fmt(n): return f"{int(n):,}".replace(",", ".") + "₫"

        vals = [
            fmt(total_rev),
            fmt(online_rev),
            fmt(offline_rev),
            str(len(orders)),
            str(len(products)),
            str(len(customers)),
        ]
        for card, v in zip(self._stat_cards, vals):
            card.set_value(v)

    def _update_revenue(self, orders):
        online  = sum(o.get("total_amount", 0) for o in orders if o.get("channel") == "online")
        offline = sum(o.get("total_amount", 0) for o in orders if o.get("channel") != "online")
        total   = online + offline or 1

        def fmt(n): return f"{int(n):,}".replace(",", ".") + "₫"

        for channel, val in [("Online", online), ("Offline", offline)]:
            info = self._rev_rows.get(channel)
            if info:
                info["label"].config(text=fmt(val))
                self.after(100, lambda b=info["bar"], v=val/total: b.set_value(v))

    def _update_low_stock(self, products):
        for w in self._low_stock_frame.winfo_children():
            w.destroy()

        # Lấy 8 sản phẩm có tồn kho thấp nhất
        sorted_p = sorted(products, key=lambda p: p.get("quantity", 0))[:8]
        for p in sorted_p:
            row = tk.Frame(self._low_stock_frame, bg=T.CARD_BG)
            row.pack(fill="x", pady=2)
            qty = p.get("quantity", 0)
            color = T.ACCENT_RED if qty < 20 else (T.ACCENT_ORANGE if qty < 50 else T.ACCENT_GREEN)
            tk.Label(row, text=p.get("name", "?"),
                     font=T.F_TABLE_ROW, bg=T.CARD_BG,
                     fg=T.TEXT_PRIMARY, anchor="w").pack(side="left")
            tk.Label(row, text=f"{qty} cái",
                     font=(T.FONT_APP, 9, "bold"),
                     bg=T.CARD_BG, fg=color).pack(side="right")

    def _update_recent_orders(self, orders, customers):
        # Map customer_id -> full_name
        cust_map = {c["customer_id"]: c.get("full_name", "?") for c in customers}

        STATUS_VN = {
            "pending":   "Chờ xác nhận",
            "confirmed": "Đã xác nhận",
            "shipping":  "Đang giao",
            "completed": "Hoàn thành",
            "cancelled": "Đã hủy",
        }
        CHANNEL_VN = {
            "online":  "Online",
            "offline": "Tại quầy",
            "facebook":"Facebook",
            "shopee":  "Shopee",
            "tiktok":  "TikTok",
        }

        # 10 đơn mới nhất
        recent = sorted(orders, key=lambda o: o.get("created_at", ""), reverse=True)[:10]

        rows = []
        for o in recent:
            total = o.get("total_amount", 0)
            fmt_total = f"{int(total):,}".replace(",", ".") + "₫"
            channel = CHANNEL_VN.get(o.get("channel", ""), o.get("channel", ""))
            status  = STATUS_VN.get(o.get("status", ""), o.get("status", ""))
            rows.append([
                o.get("order_id", ""),
                cust_map.get(o.get("customer_id", ""), o.get("customer_id", "")),
                channel,
                fmt_total,
                status,
                o.get("created_at", ""),
            ])
        self._recent_table.load_rows(rows)
