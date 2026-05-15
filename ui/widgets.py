""" ui/widgets.py  Các widget tái sử dụng dùng chung trong toàn bộ UI. """

import tkinter as tk
from tkinter import ttk
import logging

from ui import theme as T

logger = logging.getLogger(__name__)


# --- STAT CARD ---

class StatCard(tk.Frame):
    """ Card thống kê nhỏ với đường viền màu bên trái. Hiển thị: label + icon (hàng trên) và số liệu lớn (hàng dưới). """

    def __init__(self, parent, label: str, value: str, icon: str = "📊",
                 accent_color: str = T.ACCENT_GREEN, **kwargs):
        super().__init__(parent, bg=T.CARD_BG, **kwargs)
        self._build(label, value, icon, accent_color)

    def _build(self, label, value, icon, color):
        # Left accent bar
        bar = tk.Frame(self, bg=color, width=4)
        bar.pack(side="left", fill="y")

        content = tk.Frame(self, bg=T.CARD_BG)
        content.pack(side="left", fill="both", expand=True, padx=14, pady=12)

        # Top row: label + icon
        top = tk.Frame(content, bg=T.CARD_BG)
        top.pack(fill="x")
        tk.Label(top, text=label, font=T.F_STAT_LABEL,
                 bg=T.CARD_BG, fg=T.TEXT_SECONDARY, anchor="w").pack(side="left")
        tk.Label(top, text=icon, font=(T.FONT_APP, 14),
                 bg=T.CARD_BG, fg=T.TEXT_SECONDARY).pack(side="right")

        # Value
        self._value_label = tk.Label(
            content, text=value, font=T.F_STAT_VALUE,
            bg=T.CARD_BG, fg=T.TEXT_PRIMARY, anchor="w",
        )
        self._value_label.pack(fill="x", pady=(4, 0))

    def set_value(self, value: str):
        self._value_label.config(text=value)


# --- SEARCH BAR ---

class SearchBar(tk.Frame):
    """ Thanh tìm kiếm với icon 🔍. """

    def __init__(self, parent, placeholder: str = "Tìm kiếm...",
                 on_search=None, **kwargs):
        super().__init__(parent, bg=T.CARD_BG, relief="flat",
                         highlightbackground=T.BORDER_COLOR,
                         highlightthickness=1, **kwargs)
        self._on_search = on_search
        self._build(placeholder)

    def _build(self, placeholder):
        tk.Label(self, text="🔍", font=(T.FONT_APP, 10),
                 bg=T.CARD_BG, fg=T.TEXT_SECONDARY).pack(side="left", padx=(8, 2))
        self._var = tk.StringVar()
        self._var.trace_add("write", self._on_change)
        entry = tk.Entry(
            self, textvariable=self._var,
            font=T.F_FORM_INPUT,
            bg=T.CARD_BG, fg=T.TEXT_PRIMARY,
            relief="flat", bd=0,
        )
        entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))
        self._placeholder = placeholder
        self._set_placeholder(entry)

    def _set_placeholder(self, entry):
        if not self._var.get():
            self._var.set(self._placeholder)
            entry.config(fg=T.TEXT_MUTED)
            entry.bind("<FocusIn>", lambda e: self._clear_placeholder(entry))

    def _clear_placeholder(self, entry):
        if self._var.get() == self._placeholder:
            self._var.set("")
            entry.config(fg=T.TEXT_PRIMARY)

    def _on_change(self, *_):
        if self._on_search and self._var.get() != self._placeholder:
            self._on_search(self._var.get())

    def get(self) -> str:
        v = self._var.get()
        return "" if v == self._placeholder else v

    def set(self, value: str):
        self._var.set(value)


# --- ICON BUTTON ---

class IconButton(tk.Button):
    """ Button với icon + text, styling nhất quán. """

    def __init__(self, parent, text: str, icon: str = "",
                 bg: str = T.BTN_PRIMARY_BG, fg: str = T.TEXT_WHITE,
                 command=None, **kwargs):
        label = f"{icon}  {text}" if icon else text
        super().__init__(
            parent,
            text=label,
            font=T.F_BTN,
            bg=bg, fg=fg,
            activebackground=bg, activeforeground=fg,
            relief="flat",
            cursor="hand2",
            padx=T.BTN_PADX, pady=T.BTN_PADY,
            command=command,
            **kwargs,
        )
        self.bind("<Enter>", lambda e: self.config(bg=self._darken(bg)))
        self.bind("<Leave>", lambda e: self.config(bg=bg))

    @staticmethod
    def _darken(hex_color: str) -> str:
        """ Làm tối màu hex 15%. """
        try:
            h = hex_color.lstrip("#")
            r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
            r = max(0, int(r * 0.85))
            g = max(0, int(g * 0.85))
            b = max(0, int(b * 0.85))
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return hex_color


# --- DATA TABLE (Treeview wrapper) ---

class DataTable(tk.Frame):
    """ Bảng dữ liệu dựa trên ttk.Treeview với scrollbar. Hỗ trợ: striped rows, column resize, row selection. """

    ROW_COLORS = ("#ffffff", "#f9fafb")

    def __init__(self, parent, columns: list[dict], **kwargs):
        """ columns: list of dict với keys: - id (str): column id - heading (str): tiêu đề cột - width (int): độ rộng (px) - anchor (str): "w" | "center" | "e" - stretch (bool): có co giãn không """
        super().__init__(parent, bg=T.CARD_BG, **kwargs)
        self._columns = columns
        self._build()

    def _build(self):
        self._style = ttk.Style()
        self._configure_style()

        col_ids = [c["id"] for c in self._columns]
        self.tree = ttk.Treeview(
            self,
            columns=col_ids,
            show="headings",
            selectmode="browse",
            style="Custom.Treeview",
        )

        for col in self._columns:
            self.tree.heading(
                col["id"],
                text=col.get("heading", col["id"]),
                anchor=col.get("anchor", "w"),
            )
            self.tree.column(
                col["id"],
                width=col.get("width", 120),
                anchor=col.get("anchor", "w"),
                stretch=col.get("stretch", False),
                minwidth=col.get("minwidth", 60),
            )

        # Scrollbars
        vsb = ttk.Scrollbar(self, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def _configure_style(self):
        self._style.configure(
            "Custom.Treeview",
            background=T.CARD_BG,
            foreground=T.TEXT_PRIMARY,
            fieldbackground=T.CARD_BG,
            rowheight=32,
            font=T.F_TABLE_ROW,
            borderwidth=0,
        )
        self._style.configure(
            "Custom.Treeview.Heading",
            background=T.CONTENT_BG,
            foreground=T.TEXT_SECONDARY,
            font=T.F_TABLE_HEADER,
            borderwidth=0,
            relief="flat",
            padding=(8, 6),
        )
        self._style.map(
            "Custom.Treeview",
            background=[("selected", "#dbeafe")],
            foreground=[("selected", T.TEXT_PRIMARY)],
        )
        self._style.layout("Custom.Treeview", [
            ("Custom.Treeview.treearea", {"sticky": "nswe"}),
        ])

    def load_rows(self, rows: list[list]):
        """ Xóa dữ liệu cũ và nạp danh sách rows mới. """
        self.clear()
        for i, row in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", "end", values=row, tags=(tag,))
        self.tree.tag_configure("even", background="#ffffff")
        self.tree.tag_configure("odd",  background="#f9fafb")

    def clear(self):
        """ Xóa toàn bộ dữ liệu. """
        self.tree.delete(*self.tree.get_children())

    def get_selected(self):
        """ Trả về tuple values của dòng đang chọn hoặc None. """
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0], "values")

    def get_selected_iid(self):
        sel = self.tree.selection()
        return sel[0] if sel else None

    def bind_double_click(self, callback):
        self.tree.bind("<Double-1>", callback)

    def bind_select(self, callback):
        self.tree.bind("<<TreeviewSelect>>", callback)


# --- MODAL DIALOG BASE ---

class ModalDialog(tk.Toplevel):
    """ Base class cho các dialog modal (thêm / sửa). """

    def __init__(self, parent, title: str, width: int = 480, height: int = 400):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.configure(bg=T.CONTENT_BG)
        self.grab_set()  # Modal
        self.transient(parent)
        self._center(width, height)
        self.result = None

    def _center(self, w, h):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _make_field(self, parent, label: str, var: tk.StringVar,
                    row: int, placeholder: str = ""):
        """ Helper tạo label + entry theo dạng form. """
        tk.Label(parent, text=label, font=T.F_FORM_LABEL,
                 bg=T.CONTENT_BG, fg=T.TEXT_PRIMARY, anchor="w"
                 ).grid(row=row, column=0, sticky="w", padx=(20, 8), pady=(10, 2))
        entry = tk.Entry(parent, textvariable=var, font=T.F_FORM_INPUT,
                         bg=T.CARD_BG, fg=T.TEXT_PRIMARY,
                         relief="solid", bd=1)
        entry.grid(row=row, column=1, sticky="ew", padx=(0, 20), pady=(10, 2), ipady=6)
        return entry

    def _make_combobox(self, parent, label: str, var: tk.StringVar,
                       values: list, row: int):
        tk.Label(parent, text=label, font=T.F_FORM_LABEL,
                 bg=T.CONTENT_BG, fg=T.TEXT_PRIMARY, anchor="w"
                 ).grid(row=row, column=0, sticky="w", padx=(20, 8), pady=(10, 2))
        cb = ttk.Combobox(parent, textvariable=var, values=values,
                          font=T.F_FORM_INPUT, state="readonly")
        cb.grid(row=row, column=1, sticky="ew", padx=(0, 20), pady=(10, 2), ipady=4)
        return cb

    def _footer_buttons(self, parent, on_save, on_cancel):
        """ Hàng nút Lưu / Hủy ở cuối dialog. """
        footer = tk.Frame(parent, bg=T.CONTENT_BG)
        footer.pack(fill="x", padx=20, pady=(12, 16))
        IconButton(footer, "Hủy", bg=T.BTN_SECONDARY_BG, command=on_cancel
                   ).pack(side="right", padx=(6, 0))
        IconButton(footer, "💾  Lưu", bg=T.BTN_PRIMARY_BG, command=on_save
                   ).pack(side="right")


# --- PAGE HEADER ---

def build_page_header(parent, title: str, subtitle: str,
                      icon: str = "📋", bg: str = T.CONTENT_BG):
    """ Tạo block tiêu đề trang chuẩn. """
    frame = tk.Frame(parent, bg=bg)
    frame.pack(fill="x", padx=0, pady=(0, 16))
    row = tk.Frame(frame, bg=bg)
    row.pack(fill="x")
    tk.Label(row, text=icon, font=(T.FONT_APP, 22),
             bg=bg, fg=T.TEXT_PRIMARY).pack(side="left", padx=(0, 10))
    text_col = tk.Frame(row, bg=bg)
    text_col.pack(side="left")
    tk.Label(text_col, text=title, font=T.F_PAGE_TITLE,
             bg=bg, fg=T.TEXT_PRIMARY, anchor="w").pack(fill="x")
    tk.Label(text_col, text=subtitle, font=T.F_PAGE_SUBTITLE,
             bg=bg, fg=T.TEXT_SECONDARY, anchor="w").pack(fill="x")
    # Divider
    tk.Frame(frame, bg=T.BORDER_COLOR, height=1).pack(fill="x", pady=(12, 0))
    return frame


# --- PROGRESS BAR (Canvas based) ---

class ProgressBar(tk.Canvas):
    """ Thanh tiến trình ngang đơn giản. """

    def __init__(self, parent, value: float = 0.0,
                 color: str = T.ONLINE_COLOR, height: int = 8, **kwargs):
        kwargs.setdefault("bg", T.CARD_BG)
        kwargs.setdefault("highlightthickness", 0)
        super().__init__(parent, height=height, **kwargs)
        self._color = color
        self._value = max(0.0, min(1.0, value))
        self.bind("<Configure>", self._on_resize)
        self._drawn = False

    def _on_resize(self, event=None):
        self._draw()

    def _draw(self):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 2:
            return
        # Background track
        self.create_rectangle(0, 2, w, h - 2, fill="#e0e0e0", outline="", width=0)
        # Fill
        fill_w = int(w * self._value)
        if fill_w > 0:
            self.create_rectangle(0, 2, fill_w, h - 2,
                                  fill=self._color, outline="", width=0)

    def set_value(self, value: float):
        self._value = max(0.0, min(1.0, value))
        self._draw()
