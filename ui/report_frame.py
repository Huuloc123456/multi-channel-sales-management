""" ui/report_frame.py – Báo cáo & Thống kê (phiên bản nâng cấp)  • KPI cards • Biểu đồ doanh thu theo kênh (HBar + Pie) • Biểu đồ trạng thái đơn hàng (Bar) • Bảng top sản phẩm bán chạy • Xuất báo cáo CSV / TXT """

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json, csv, logging
from pathlib import Path
from datetime import datetime, timedelta

from ui import theme as T
from ui.widgets import IconButton, DataTable, build_page_header
from ui.charts import BarChart, HBarChart, PieChart, LineChart
from utils.helpers import format_currency

logger = logging.getLogger(__name__)

# ── constants ──────────────────────────────────────────────────────────────
STATUS_VN = {"pending":"Chờ xác nhận","confirmed":"Đã xác nhận",
             "shipping":"Đang giao","completed":"Hoàn thành","cancelled":"Đã hủy"}
STATUS_COLORS = {"pending":T.STATUS_PENDING,"confirmed":T.STATUS_CONFIRMED,
                 "shipping":T.STATUS_SHIPPING,"completed":T.STATUS_COMPLETED,
                 "cancelled":T.STATUS_CANCELLED}
CHANNEL_VN = {"online":"Online","offline":"Tại quầy","facebook":"Facebook",
              "shopee":"Shopee","tiktok":"TikTok"}
CHANNEL_COLORS = {"online":"#2196f3","offline":"#f39c12","facebook":"#1877f2",
                  "shopee":"#ee4d2d","tiktok":"#fe2c55"}

def _load(path: str) -> list:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


# ══════════════════════════════════════════════════════════════════════════ #
class ReportFrame(tk.Frame):
    """ Frame Báo cáo & Thống kê nâng cao. """

    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, bg=T.CONTENT_BG, **kwargs)
        self.controller = controller
        self._build()
        self.refresh()

    # ── layout ─────────────────────────────────────────────────────────────
    def _build(self):
        # Outer scrollable container
        canvas = tk.Canvas(self, bg=T.CONTENT_BG, highlightthickness=0)
        vsb    = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._inner = tk.Frame(canvas, bg=T.CONTENT_BG)
        wid = canvas.create_window((0,0), window=self._inner, anchor="nw")
        self._inner.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(wid, width=e.width))
        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        self._build_inner()

    def _build_inner(self):
        pad = {"padx": 24}

        # ── header ──────────────────────────────────────────────────────
        build_page_header(self._inner,
            title="Báo cáo & Thống kê",
            subtitle="Phân tích doanh thu và hiệu quả bán hàng đa kênh",
            icon="📈")

        # ── filter bar ──────────────────────────────────────────────────
        fbar = tk.Frame(self._inner, bg=T.CARD_BG,
                        highlightbackground=T.CARD_BORDER, highlightthickness=1)
        fbar.pack(fill="x", **pad, pady=(0,14))
        finner = tk.Frame(fbar, bg=T.CARD_BG)
        finner.pack(fill="x", padx=14, pady=10)

        tk.Label(finner, text="Lọc khoảng thời gian:", font=T.F_FORM_LABEL,
                 bg=T.CARD_BG, fg=T.TEXT_SECONDARY).pack(side="left")

        self._range_var = tk.StringVar(value="Tất cả")
        ranges = ["Tất cả","Hôm nay","7 ngày qua","30 ngày qua","Tháng này"]
        rb_cb = ttk.Combobox(finner, textvariable=self._range_var, values=ranges,
                             state="readonly", font=T.F_FORM_INPUT, width=14)
        rb_cb.pack(side="left", padx=(8,16))
        rb_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        tk.Label(finner, text="Kênh:", font=T.F_FORM_LABEL,
                 bg=T.CARD_BG, fg=T.TEXT_SECONDARY).pack(side="left")
        self._ch_var = tk.StringVar(value="Tất cả")
        ch_cb = ttk.Combobox(finner, textvariable=self._ch_var,
                             values=["Tất cả"]+list(CHANNEL_VN.values()),
                             state="readonly", font=T.F_FORM_INPUT, width=12)
        ch_cb.pack(side="left", padx=(6,16))
        ch_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        IconButton(finner, "🔄 Làm mới", bg=T.BTN_PRIMARY_BG,
                   command=self.refresh).pack(side="left", padx=(0,8))
        IconButton(finner, "📊 Xuất CSV", bg=T.BTN_EXPORT_BG,
                   command=self._export_csv).pack(side="left", padx=(0,6))
        IconButton(finner, "📄 Xuất TXT", bg=T.BTN_EXPORT_BG,
                   command=self._export_txt).pack(side="left")

        # ── KPI cards ───────────────────────────────────────────────────
        kpi = tk.Frame(self._inner, bg=T.CONTENT_BG)
        kpi.pack(fill="x", **pad, pady=(0,14))
        kpi_defs = [
            ("Tổng doanh thu", "💰", T.STAT_COLORS[0]),
            ("Đơn hoàn thành", "✅", T.STAT_COLORS[3]),
            ("Đơn đang giao",  "🚚", T.STAT_COLORS[2]),
            ("Tỷ lệ HT",       "📊", T.STAT_COLORS[4]),
        ]
        self._kpi_cards = []
        for i,(lbl,icon,col) in enumerate(kpi_defs):
            card = _make_kpi(kpi, lbl, "–", icon, col)
            card.grid(row=0, column=i, sticky="nsew", padx=(0,10 if i<3 else 0))
            kpi.columnconfigure(i, weight=1)
            self._kpi_cards.append(card)

        # ── row 1: HBar + Pie ────────────────────────────────────────────
        row1 = tk.Frame(self._inner, bg=T.CONTENT_BG)
        row1.pack(fill="x", **pad, pady=(0,14))
        row1.columnconfigure(0, weight=3)
        row1.columnconfigure(1, weight=2)

        hbar_card = _card(row1, "Doanh thu theo kênh bán hàng")
        hbar_card.grid(row=0, column=0, sticky="nsew", padx=(0,12))
        self._hbar = HBarChart(hbar_card, data=[], bg=T.CARD_BG)
        self._hbar.pack(fill="both", expand=True, padx=12, pady=(0,12))

        pie_card = _card(row1, "Tỷ trọng doanh thu")
        pie_card.grid(row=0, column=1, sticky="nsew")
        self._pie = PieChart(pie_card, data=[], bg=T.CARD_BG, height=200)
        self._pie.pack(fill="both", expand=True, padx=12, pady=(0,12))

        # ── row 2: Line chart (trend) ────────────────────────────────────
        line_card = _card(self._inner, "Xu hướng doanh thu (7 ngày gần nhất)")
        line_card.pack(fill="x", **pad, pady=(0,14))
        self._line = LineChart(line_card, series=[], bg=T.CARD_BG, height=200)
        self._line.pack(fill="x", expand=False, padx=12, pady=(0,12))

        # ── row 3: Status bar + Top products ────────────────────────────
        row3 = tk.Frame(self._inner, bg=T.CONTENT_BG)
        row3.pack(fill="x", **pad, pady=(0,14))
        row3.columnconfigure(0, weight=2)
        row3.columnconfigure(1, weight=3)

        st_card = _card(row3, "Trạng thái đơn hàng")
        st_card.grid(row=0, column=0, sticky="nsew", padx=(0,12))
        self._status_inner = tk.Frame(st_card, bg=T.CARD_BG)
        self._status_inner.pack(fill="x", padx=16, pady=(0,14))

        top_card = _card(row3, "Top 5 sản phẩm bán chạy")
        top_card.grid(row=0, column=1, sticky="nsew")
        top_cols = [
            {"id":"rank", "heading":"#",        "width":36,  "anchor":"center"},
            {"id":"name", "heading":"Sản phẩm", "width":200, "anchor":"w","stretch":True},
            {"id":"qty",  "heading":"Đã bán",   "width":80,  "anchor":"center"},
            {"id":"rev",  "heading":"Doanh thu","width":120, "anchor":"e"},
        ]
        self._top_tbl = DataTable(top_card, columns=top_cols)
        self._top_tbl.pack(fill="both", expand=True, padx=8, pady=(0,10))
        self._top_tbl.tree.config(height=6)

    # ── data loading ────────────────────────────────────────────────────────
    def refresh(self):
        try:
            orders    = _load("data/orders.json")
            products  = _load("data/products.json")
            customers = _load("data/customers.json")

            orders = self._apply_filters(orders)

            self._update_kpis(orders)
            self._update_channel_charts(orders)
            self._update_line_chart(orders)
            self._update_statuses(orders)
            self._update_top_products(orders, products)
        except Exception as exc:
            logger.error("Report refresh: %s", exc, exc_info=True)

    def _apply_filters(self, orders: list) -> list:
        # Date range filter
        rng = self._range_var.get()
        now = datetime.now()
        if rng == "Hôm nay":
            cutoff = now.replace(hour=0, minute=0, second=0)
        elif rng == "7 ngày qua":
            cutoff = now - timedelta(days=7)
        elif rng == "30 ngày qua":
            cutoff = now - timedelta(days=30)
        elif rng == "Tháng này":
            cutoff = now.replace(day=1, hour=0, minute=0, second=0)
        else:
            cutoff = None

        if cutoff:
            def _in_range(o):
                try:
                    t = datetime.strptime(o.get("created_at",""), "%Y-%m-%d %H:%M:%S")
                    return t >= cutoff
                except Exception:
                    return True
            orders = [o for o in orders if _in_range(o)]

        # Channel filter
        ch_vn = self._ch_var.get()
        if ch_vn != "Tất cả":
            ch_key = {v:k for k,v in CHANNEL_VN.items()}.get(ch_vn)
            if ch_key:
                orders = [o for o in orders if o.get("channel") == ch_key]
        return orders

    def _update_kpis(self, orders):
        total    = sum(o.get("total_amount",0) for o in orders)
        done     = sum(1 for o in orders if o.get("status")=="completed")
        shipping = sum(1 for o in orders if o.get("status")=="shipping")
        rate     = f"{done/len(orders)*100:.1f}%" if orders else "0%"
        vals = [format_currency(total), str(done), str(shipping), rate]
        for card, v in zip(self._kpi_cards, vals):
            card._val.config(text=v)

    def _update_channel_charts(self, orders):
        ch_rev = {}
        for o in orders:
            ch = o.get("channel","?")
            ch_rev[ch] = ch_rev.get(ch,0) + o.get("total_amount",0)

        data = [(CHANNEL_VN.get(k,k), v) for k,v in
                sorted(ch_rev.items(), key=lambda x:-x[1])]

        # Update HBar
        self._hbar.update_data(data)
        # Update Pie
        self._pie.update_data(data)

    def _update_line_chart(self, orders):
        """ Doanh thu 7 ngày gần nhất – mỗi ngày một điểm, theo kênh online vs offline. """
        today = datetime.now().date()
        days  = [(today - timedelta(days=6-i)) for i in range(7)]
        day_labels = [d.strftime("%d/%m") for d in days]

        online_pts  = []
        offline_pts = []
        for d in days:
            lbl   = d.strftime("%d/%m")
            ds    = d.strftime("%Y-%m-%d")
            on_r  = sum(o.get("total_amount",0) for o in orders
                        if o.get("created_at","").startswith(ds)
                        and o.get("channel") == "online")
            off_r = sum(o.get("total_amount",0) for o in orders
                        if o.get("created_at","").startswith(ds)
                        and o.get("channel") != "online")
            online_pts.append((lbl, on_r))
            offline_pts.append((lbl, off_r))

        self._line.update_series([
            ("Online",  online_pts),
            ("Offline", offline_pts),
        ])

    def _update_statuses(self, orders):
        for w in self._status_inner.winfo_children():
            w.destroy()
        counts = {k:0 for k in STATUS_VN}
        for o in orders:
            s = o.get("status","?")
            if s in counts:
                counts[s] += 1
        total = len(orders) or 1

        for st, lbl in STATUS_VN.items():
            cnt   = counts[st]
            color = STATUS_COLORS.get(st, T.TEXT_MUTED)
            pct   = cnt / total

            row = tk.Frame(self._status_inner, bg=T.CARD_BG)
            row.pack(fill="x", pady=3)

            top = tk.Frame(row, bg=T.CARD_BG)
            top.pack(fill="x")
            tk.Label(top, text=lbl, font=T.F_FORM_LABEL,
                     bg=T.CARD_BG, fg=T.TEXT_PRIMARY).pack(side="left")
            tk.Label(top, text=f"{cnt}  ({pct*100:.0f}%)",
                     font=(T.FONT_APP,9,"bold"), bg=T.CARD_BG, fg=color
                     ).pack(side="right")

            track = tk.Canvas(row, height=7, bg="#f0f1f5",
                              highlightthickness=0)
            track.pack(fill="x", pady=(2,0))
            track.update_idletasks()
            w = track.winfo_width() or 300
            fw = max(4, int(w*pct))
            track.create_rectangle(0,0,w,7, fill="#f0f1f5", outline="")
            track.create_rectangle(0,0,fw,7, fill=color, outline="")

    def _update_top_products(self, orders, products):
        prod_map = {p["product_id"]: p.get("name","?") for p in products}
        sold: dict[str, dict] = {}
        for o in orders:
            for item in o.get("items", []):
                pid  = item.get("product_id","?")
                qty  = item.get("quantity", 0)
                rev  = item.get("subtotal",  0)
                if pid not in sold:
                    sold[pid] = {"name": prod_map.get(pid, item.get("product_name","?")),
                                 "qty": 0, "rev": 0}
                sold[pid]["qty"] += qty
                sold[pid]["rev"] += rev

        top5 = sorted(sold.values(), key=lambda x: -x["rev"])[:5]
        rows = [[str(i+1), p["name"], str(p["qty"]), format_currency(p["rev"])]
                for i,p in enumerate(top5)]
        self._top_tbl.load_rows(rows)

    # ── exports ─────────────────────────────────────────────────────────────
    def _export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV","*.csv")],
            initialfile=f"baocao_{datetime.now():%Y%m%d}.csv")
        if not path:
            return
        try:
            orders = self._apply_filters(_load("data/orders.json"))
            customers = {c["customer_id"]: c.get("full_name","?")
                         for c in _load("data/customers.json")}
            with open(path,"w",newline="",encoding="utf-8-sig") as f:
                w = csv.writer(f)
                w.writerow(["Mã đơn","Khách hàng","Kênh",
                             "Tổng tiền","Trạng thái","Ngày tạo"])
                for o in orders:
                    w.writerow([
                        o.get("order_id",""),
                        customers.get(o.get("customer_id",""), o.get("customer_id","")),
                        CHANNEL_VN.get(o.get("channel",""), o.get("channel","")),
                        o.get("total_amount",0),
                        STATUS_VN.get(o.get("status",""), o.get("status","")),
                        o.get("created_at",""),
                    ])
            messagebox.showinfo("Xuất CSV", f"Đã xuất {len(orders)} đơn hàng:\n{path}")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def _export_txt(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text","*.txt")],
            initialfile=f"baocao_{datetime.now():%Y%m%d}.txt")
        if not path:
            return
        try:
            orders    = self._apply_filters(_load("data/orders.json"))
            products  = _load("data/products.json")
            customers = {c["customer_id"]: c.get("full_name","?")
                         for c in _load("data/customers.json")}

            total_rev = sum(o.get("total_amount",0) for o in orders)
            done_cnt  = sum(1 for o in orders if o.get("status")=="completed")

            ch_rev: dict[str,float] = {}
            for o in orders:
                ch = o.get("channel","?")
                ch_rev[ch] = ch_rev.get(ch,0) + o.get("total_amount",0)

            lines = []
            SEP = "=" * 60
            lines += [SEP,
                      "  BÁO CÁO DOANH THU – HỆ THỐNG QUẢN LÝ BÁN HÀNG",
                      f"  Ngày xuất: {datetime.now():%d/%m/%Y %H:%M:%S}",
                      f"  Bộ lọc: {self._range_var.get()} | Kênh: {self._ch_var.get()}",
                      SEP, ""]

            lines += ["TỔNG QUAN",
                      f"  Tổng doanh thu : {format_currency(total_rev)}",
                      f"  Tổng đơn hàng  : {len(orders)}",
                      f"  Đơn hoàn thành : {done_cnt}",
                      f"  Tỷ lệ HT       : {done_cnt/len(orders)*100:.1f}%" if orders else "  Tỷ lệ HT: 0%",
                      ""]

            lines += ["DOANH THU THEO KÊNH"]
            for ch, rev in sorted(ch_rev.items(), key=lambda x:-x[1]):
                pct = rev/total_rev*100 if total_rev else 0
                lines.append(f"  {CHANNEL_VN.get(ch,ch):<14}: {format_currency(rev):>18} ({pct:.1f}%)")
            lines.append("")

            lines += ["TRẠNG THÁI ĐƠN HÀNG"]
            for st, lbl in STATUS_VN.items():
                cnt = sum(1 for o in orders if o.get("status")==st)
                lines.append(f"  {lbl:<16}: {cnt}")
            lines += ["", SEP]

            with open(path,"w",encoding="utf-8") as f:
                f.write("\n".join(lines))
            messagebox.showinfo("Xuất TXT", f"Đã xuất báo cáo:\n{path}")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))


# ── helpers ──────────────────────────────────────────────────────────────────
def _make_kpi(parent, label, value, icon, color):
    card = tk.Frame(parent, bg=T.CARD_BG,
                    highlightbackground=T.CARD_BORDER, highlightthickness=1)
    tk.Frame(card, bg=color, width=4).pack(side="left", fill="y")
    inner = tk.Frame(card, bg=T.CARD_BG)
    inner.pack(side="left", fill="both", expand=True, padx=12, pady=12)
    top = tk.Frame(inner, bg=T.CARD_BG)
    top.pack(fill="x")
    tk.Label(top, text=label, font=T.F_STAT_LABEL,
             bg=T.CARD_BG, fg=T.TEXT_SECONDARY, anchor="w").pack(side="left")
    tk.Label(top, text=icon, font=(T.FONT_APP,14),
             bg=T.CARD_BG, fg=T.TEXT_SECONDARY).pack(side="right")
    val_lbl = tk.Label(inner, text=value, font=T.F_STAT_VALUE,
                       bg=T.CARD_BG, fg=T.TEXT_PRIMARY, anchor="w")
    val_lbl.pack(fill="x", pady=(4,0))
    card._val = val_lbl
    return card

def _card(parent, title):
    frame = tk.Frame(parent, bg=T.CARD_BG,
                     highlightbackground=T.CARD_BORDER, highlightthickness=1)
    tk.Label(frame, text=title, font=T.F_SECTION_TITLE,
             bg=T.CARD_BG, fg=T.TEXT_PRIMARY, anchor="w"
             ).pack(fill="x", padx=16, pady=(14,8))
    return frame
