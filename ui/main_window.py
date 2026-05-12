"""
ui/main_window.py
==================
Cửa sổ chính của ứng dụng (placeholder cho Thành viên 2).

Thành viên 2 sẽ triển khai toàn bộ giao diện Tkinter tại đây.
Hiện tại chỉ khởi tạo cấu trúc cơ bản để chương trình có thể chạy.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging

logger = logging.getLogger(__name__)


class MainWindow:
    """
    Cửa sổ chính của ứng dụng Hệ thống Quản lý Bán hàng Đa kênh.

    Trách nhiệm:
        - Khởi tạo cửa sổ Tkinter.
        - Điều hướng giữa các màn hình (sản phẩm, khách hàng, đơn hàng).
        - Cung cấp thanh menu và status bar.

    NOTE: Thành viên 2 sẽ implement chi tiết các tab/frame.
    """

    APP_TITLE = "Hệ thống Quản lý Bán hàng Đa kênh"
    WINDOW_SIZE = "1200x700"
    MIN_SIZE = (900, 600)

    def __init__(self, root: tk.Tk):
        self._root = root
        self._setup_window()
        self._build_menu()
        self._build_layout()
        logger.info("MainWindow khởi tạo thành công.")

    def _setup_window(self):
        """Cấu hình cửa sổ chính."""
        self._root.title(self.APP_TITLE)
        self._root.geometry(self.WINDOW_SIZE)
        self._root.minsize(*self.MIN_SIZE)
        # Đặt icon nếu có
        try:
            self._root.iconbitmap("assets/icon.ico")
        except tk.TclError:
            pass

    def _build_menu(self):
        """Xây dựng thanh Menu."""
        menubar = tk.Menu(self._root)

        # Menu File
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Xuất báo cáo", command=self._export_report)
        file_menu.add_separator()
        file_menu.add_command(label="Thoát", command=self._root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Menu Trợ giúp
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Về chúng tôi", command=self._show_about)
        menubar.add_cascade(label="Trợ giúp", menu=help_menu)

        self._root.config(menu=menubar)

    def _build_layout(self):
        """Xây dựng layout chính với Notebook (tab)."""
        # Status bar
        self._status_var = tk.StringVar(value="Sẵn sàng")
        status_bar = tk.Label(
            self._root,
            textvariable=self._status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padx=5,
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Notebook Tabs – Thành viên 2 sẽ thêm nội dung
        self._notebook = ttk.Notebook(self._root)
        self._notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Placeholder tabs
        for tab_name in ["📦 Sản phẩm", "👥 Khách hàng", "🧾 Đơn hàng", "📊 Báo cáo"]:
            frame = ttk.Frame(self._notebook)
            ttk.Label(frame, text=f"[{tab_name}] — Thành viên 2 implement tại đây").pack(
                expand=True
            )
            self._notebook.add(frame, text=tab_name)

    def set_status(self, message: str):
        """Cập nhật thanh trạng thái."""
        self._status_var.set(message)

    def _export_report(self):
        messagebox.showinfo("Xuất báo cáo", "Tính năng đang phát triển.")

    def _show_about(self):
        messagebox.showinfo(
            "Về chúng tôi",
            f"{self.APP_TITLE}\nPhiên bản 1.0\nNhóm 1 – Môn Lập trình Python",
        )
