""" ui/order_workflow.py  Luồng xử lý đơn hàng – workflow stepper + xuất TXT. Import vào order_frame.py. """

import tkinter as tk
from tkinter import ttk, messagebox
from ui import theme as T
from ui.widgets import IconButton, ModalDialog
from utils.helpers import format_currency

# Định nghĩa luồng trạng thái hợp lệ
WORKFLOW = {
    "pending":   {"next": "confirmed", "label": "✅ Duyệt đơn",  "color": T.STATUS_CONFIRMED},
    "confirmed": {"next": "shipping",  "label": "🚚 Giao hàng",  "color": T.STATUS_SHIPPING},
    "shipping":  {"next": "completed", "label": "✔ Hoàn thành", "color": T.STATUS_COMPLETED},
    "completed": {"next": None,        "label": "Đã hoàn thành","color": T.STATUS_COMPLETED},
    "cancelled": {"next": None,        "label": "Đã hủy",        "color": T.STATUS_CANCELLED},
}

STEPS = ["pending", "confirmed", "shipping", "completed"]
STEP_LABELS = {
    "pending":   "Chờ xác nhận",
    "confirmed": "Đã duyệt",
    "shipping":  "Đang giao",
    "completed": "Hoàn thành",
}
STATUS_VN = {
    "pending":"Chờ xác nhận","confirmed":"Đã xác nhận",
    "shipping":"Đang giao","completed":"Hoàn thành","cancelled":"Đã hủy",
}
CHANNEL_VN = {
    "online":"Online","offline":"Tại quầy",
    "facebook":"Facebook","shopee":"Shopee","tiktok":"TikTok",
}


class WorkflowDialog(ModalDialog):
    """ Dialog hiển thị chi tiết đơn hàng với stepper workflow. Cho phép: Duyệt → Giao → Hoàn thành | Hủy đơn | Xuất TXT. """

    def __init__(self, parent, order, cust_name: str, on_status_changed=None):
        super().__init__(parent,
                         title=f"Xử lý đơn – {order.order_id}",
                         width=620, height=600)
        self._order    = order
        self._cust     = cust_name
        self._callback = on_status_changed
        self._build()

    # ── build ──────────────────────────────────────────────────────────────
    def _build(self):
        o = self._order

        # Title row
        hdr = tk.Frame(self, bg=T.CONTENT_BG)
        hdr.pack(fill="x", padx=20, pady=(14, 0))
        tk.Label(hdr, text=f"Đơn hàng {o.order_id}",
                 font=T.F_SECTION_TITLE, bg=T.CONTENT_BG,
                 fg=T.TEXT_PRIMARY).pack(side="left")
        ch_label = CHANNEL_VN.get(o.channel, o.channel)
        ch_color = {"Online":"#2196f3","Tại quầy":"#f39c12",
                    "Facebook":"#1877f2","Shopee":"#ee4d2d","TikTok":"#fe2c55"
                    }.get(ch_label, T.ACCENT_BLUE)
        tk.Label(hdr, text=f"  {ch_label}",
                 font=(T.FONT_APP, 9, "bold"),
                 bg=ch_color, fg="#fff", padx=8, pady=2
                 ).pack(side="left", padx=(10, 0))

        # ── Stepper ────────────────────────────────────────────────────────
        self._stepper_frame = tk.Frame(self, bg=T.CONTENT_BG)
        self._stepper_frame.pack(fill="x", padx=20, pady=(12, 4))
        self._draw_stepper()

        # Divider
        tk.Frame(self, bg=T.BORDER_COLOR, height=1).pack(fill="x", padx=20, pady=6)

        # ── Info grid ──────────────────────────────────────────────────────
        info = tk.Frame(self, bg=T.CONTENT_BG)
        info.pack(fill="x", padx=20)
        info.columnconfigure(1, weight=1)
        info.columnconfigure(3, weight=1)
        pairs = [
            ("Khách hàng:", self._cust,
             "Tổng tiền:", format_currency(o.total_amount)),
            ("Kênh:", ch_label,
             "Ngày tạo:", o.created_at),
        ]
        for r, (l1,v1,l2,v2) in enumerate(pairs):
            tk.Label(info, text=l1, font=T.F_FORM_LABEL,
                     bg=T.CONTENT_BG, fg=T.TEXT_SECONDARY
                     ).grid(row=r, column=0, sticky="w", pady=3)
            tk.Label(info, text=v1, font=(T.FONT_APP,10,"bold"),
                     bg=T.CONTENT_BG, fg=T.TEXT_PRIMARY
                     ).grid(row=r, column=1, sticky="w", padx=(4,16))
            tk.Label(info, text=l2, font=T.F_FORM_LABEL,
                     bg=T.CONTENT_BG, fg=T.TEXT_SECONDARY
                     ).grid(row=r, column=2, sticky="w")
            tk.Label(info, text=v2, font=(T.FONT_APP,10,"bold"),
                     bg=T.CONTENT_BG, fg=T.TEXT_PRIMARY
                     ).grid(row=r, column=3, sticky="w", padx=4)

        # ── Items table ────────────────────────────────────────────────────
        from ui.widgets import DataTable
        tk.Label(self, text="Sản phẩm:", font=T.F_FORM_LABEL,
                 bg=T.CONTENT_BG, fg=T.TEXT_SECONDARY
                 ).pack(fill="x", padx=20, pady=(10,2))

        cols = [
            {"id":"name","heading":"Sản phẩm","width":210,"anchor":"w","stretch":True},
            {"id":"price","heading":"Đơn giá","width":110,"anchor":"e"},
            {"id":"qty","heading":"SL","width":50,"anchor":"center"},
            {"id":"sub","heading":"Thành tiền","width":120,"anchor":"e"},
        ]
        tbl_frame = tk.Frame(self, bg=T.CARD_BG,
                             highlightbackground=T.CARD_BORDER, highlightthickness=1)
        tbl_frame.pack(fill="both", expand=True, padx=20, pady=(0,8))
        tbl = DataTable(tbl_frame, columns=cols)
        tbl.pack(fill="both", expand=True, padx=1, pady=1)
        tbl.tree.config(height=5)
        rows = [[i.product_name, format_currency(i.unit_price),
                 str(i.quantity), format_currency(i.subtotal)]
                for i in o.items]
        tbl.load_rows(rows)

        # Total row
        tot = tk.Frame(self, bg=T.CONTENT_BG)
        tot.pack(fill="x", padx=20)
        tk.Label(tot, text=f"Tổng cộng: {format_currency(o.total_amount)}",
                 font=(T.FONT_APP,11,"bold"), bg=T.CONTENT_BG,
                 fg=T.ACCENT_RED, anchor="e").pack(fill="x")

        # ── Action buttons ─────────────────────────────────────────────────
        self._build_actions()

    def _draw_stepper(self):
        for w in self._stepper_frame.winfo_children():
            w.destroy()

        cur_status = self._order.status
        cur_idx    = STEPS.index(cur_status) if cur_status in STEPS else -1

        for i, step in enumerate(STEPS):
            col = tk.Frame(self._stepper_frame, bg=T.CONTENT_BG)
            col.pack(side="left", expand=True, fill="x")

            if i < cur_idx:
                color, fg = T.STATUS_COMPLETED, "#fff"
            elif i == cur_idx:
                color, fg = T.ACCENT_RED, "#fff"
            else:
                color, fg = "#e0e0e0", T.TEXT_MUTED

            circle = tk.Frame(col, bg=color, width=28, height=28)
            circle.pack(anchor="center")
            circle.pack_propagate(False)
            tk.Label(circle, text=str(i+1), font=(T.FONT_APP,9,"bold"),
                     bg=color, fg=fg).place(relx=0.5, rely=0.5, anchor="center")

            tk.Label(col, text=STEP_LABELS[step], font=(T.FONT_APP,8),
                     bg=T.CONTENT_BG,
                     fg=T.TEXT_PRIMARY if i <= cur_idx else T.TEXT_MUTED
                     ).pack(anchor="center", pady=(2,0))

            # Connector line
            if i < len(STEPS) - 1:
                line_color = T.STATUS_COMPLETED if i < cur_idx else "#e0e0e0"
                tk.Frame(self._stepper_frame, bg=line_color,
                         height=2, width=30).pack(side="left", anchor="center")

    def _build_actions(self):
        act = tk.Frame(self, bg=T.CONTENT_BG)
        act.pack(fill="x", padx=20, pady=(4, 14))

        status = self._order.status
        wf     = WORKFLOW.get(status, {})
        next_s = wf.get("next")

        # Next step button
        if next_s:
            IconButton(act, wf["label"], bg=wf["color"],
                       command=lambda: self._advance(next_s)
                       ).pack(side="left", padx=(0,8))

        # Cancel button (only if not done/cancelled)
        if status not in ("completed", "cancelled"):
            IconButton(act, "❌ Hủy đơn", bg=T.BTN_DANGER_BG,
                       command=self._cancel).pack(side="left", padx=(0,8))

        # Export TXT
        IconButton(act, "📄 Xuất TXT", bg=T.BTN_EXPORT_BG,
                   command=self._export_txt).pack(side="left")

        # Close
        IconButton(act, "Đóng", bg=T.BTN_SECONDARY_BG,
                   command=self.destroy).pack(side="right")

    def _advance(self, next_status: str):
        label = STATUS_VN.get(next_status, next_status)
        if not messagebox.askyesno("Xác nhận",
                f"Chuyển đơn hàng sang:\n'{label}'?", parent=self):
            return
        try:
            self._order.status = next_status
            self._draw_stepper()
            # Rebuild action buttons
            for w in self.winfo_children():
                if isinstance(w, tk.Frame) and w != self._stepper_frame:
                    pass  # keep other widgets
            # Refresh action area by rebuilding (simpler: call callback + close)
            if self._callback:
                self._callback(self._order)
            messagebox.showinfo("Thành công",
                                f"Đã cập nhật: {label}", parent=self)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e), parent=self)

    def _cancel(self):
        if not messagebox.askyesno("Xác nhận hủy",
                "Bạn có chắc muốn HỦY đơn hàng này?", parent=self):
            return
        try:
            self._order.status = "cancelled"
            if self._callback:
                self._callback(self._order)
            messagebox.showinfo("Đã hủy", "Đơn hàng đã được hủy.", parent=self)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e), parent=self)

    def _export_txt(self):
        from tkinter import filedialog
        import os
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text","*.txt")],
            initialfile=f"don_{self._order.order_id}.txt",
            parent=self)
        if not path:
            return
        o = self._order
        SEP = "-" * 46
        lines = [
            "=" * 46,
            "       HÓA ĐƠN BÁN HÀNG",
            "=" * 46,
            f"Mã đơn    : {o.order_id}",
            f"Khách hàng: {self._cust}",
            f"Kênh      : {CHANNEL_VN.get(o.channel, o.channel)}",
            f"Trạng thái: {STATUS_VN.get(o.status, o.status)}",
            f"Ngày tạo  : {o.created_at}",
            SEP,
            f"{'Sản phẩm':<28} {'SL':>4} {'Thành tiền':>12}",
            SEP,
        ]
        for item in o.items:
            name = item.product_name[:26]
            lines.append(f"{name:<28} {item.quantity:>4} "
                         f"{format_currency(item.subtotal):>12}")
        lines += [SEP,
                  f"{'TỔNG TIỀN':>32}: {format_currency(o.total_amount):>12}",
                  "=" * 46]
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            messagebox.showinfo("Xuất TXT",
                                f"Đã xuất hóa đơn:\n{path}", parent=self)
        except Exception as e:
            messagebox.showerror("Lỗi", str(e), parent=self)
