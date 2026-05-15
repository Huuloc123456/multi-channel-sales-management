""" ui/login_window.py  Màn hình đăng nhập – Hệ thống Quản lý Bán hàng Đa kênh. Thiết kế: Panel trái (dark navy) + Panel phải (form đăng nhập). """

import tkinter as tk
from tkinter import messagebox
import logging

from ui import theme as T

logger = logging.getLogger(__name__)


# Tài khoản demo (plaintext đơn giản cho mục đích học tập)
DEMO_ACCOUNTS = {
    "admin":  {"password": "admin123", "role": "admin",  "display": "Quản trị viên"},
    "staff":  {"password": "staff123", "role": "staff",  "display": "Nhân viên bán hàng"},
}


class LoginWindow:
    """ Cửa sổ đăng nhập split-panel. Sau khi xác thực thành công, gọi callback on_login_success(username, role). """

    def __init__(self, root: tk.Tk, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self._setup_window()
        self._build_ui()

    # ------------------------------------------------------------------ #
    #  SETUP                                                               #
    # ------------------------------------------------------------------ #

    def _setup_window(self):
        self.root.title("Đăng nhập - Hệ thống Quản lý Bán hàng")
        self.root.geometry("900x580")
        self.root.resizable(False, False)
        self.root.configure(bg=T.SIDEBAR_BG)
        # Center window
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth()  // 2) - (900 // 2)
        y = (self.root.winfo_screenheight() // 2) - (580 // 2)
        self.root.geometry(f"900x580+{x}+{y}")

    # ------------------------------------------------------------------ #
    #  BUILD UI                                                            #
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        # ---- Main container (2 columns) ----
        container = tk.Frame(self.root, bg=T.SIDEBAR_BG)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=0)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)

        self._build_left_panel(container)
        self._build_right_panel(container)

    def _build_left_panel(self, parent):
        """ Panel trái: logo + brand + feature list. """
        left = tk.Frame(parent, bg=T.SIDEBAR_BG, width=420)
        left.grid(row=0, column=0, sticky="nsew")
        left.pack_propagate(False)

        # Spacer top
        tk.Frame(left, bg=T.SIDEBAR_BG, height=60).pack(fill="x")

        # Logo block
        logo_frame = tk.Frame(left, bg="#c0392b", width=90, height=90)
        logo_frame.pack(pady=(20, 0))
        logo_frame.pack_propagate(False)
        tk.Label(
            logo_frame,
            text="🏪",
            font=(T.FONT_APP, 32),
            bg="#c0392b",
            fg=T.TEXT_WHITE,
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Brand name
        tk.Label(
            left,
            text="SALES MANAGER",
            font=(T.FONT_APP, 18, "bold"),
            bg=T.SIDEBAR_BG,
            fg=T.TEXT_WHITE,
        ).pack(pady=(20, 4))

        tk.Label(
            left,
            text="Hệ thống Quản lý Bán hàng Đa kênh",
            font=T.F_LOGIN_BRAND_SUB,
            bg=T.SIDEBAR_BG,
            fg=T.SIDEBAR_SUBTEXT,
        ).pack(pady=(0, 30))

        # Feature list
        features = [
            "Quản lý sản phẩm & kho hàng",
            "Đơn hàng Online & Offline",
            "Phân tích doanh thu",
            "Lưu trữ JSON, CSV, TXT, XML",
            "Tích hợp API bên ngoài",
        ]
        for feat in features:
            row = tk.Frame(left, bg=T.SIDEBAR_BG)
            row.pack(fill="x", padx=40, pady=3)
            tk.Label(
                row, text="✓",
                font=(T.FONT_APP, 10, "bold"),
                bg=T.SIDEBAR_BG, fg=T.ACCENT_GREEN,
            ).pack(side="left")
            tk.Label(
                row, text=f"  {feat}",
                font=T.F_LOGIN_FEATURE,
                bg=T.SIDEBAR_BG, fg="#c5cae9",
            ).pack(side="left")

    def _build_right_panel(self, parent):
        """ Panel phải: form đăng nhập. """
        right = tk.Frame(parent, bg="#f8f9fb")
        right.grid(row=0, column=1, sticky="nsew")

        # Vertical centering via inner frame
        inner = tk.Frame(right, bg="#f8f9fb")
        inner.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.75)

        # Title
        tk.Label(
            inner,
            text="Chào mừng trở lại",
            font=T.F_LOGIN_TITLE,
            bg="#f8f9fb",
            fg=T.TEXT_PRIMARY,
            anchor="w",
        ).pack(fill="x", pady=(0, 4))

        tk.Label(
            inner,
            text="Đăng nhập để tiếp tục",
            font=T.F_LOGIN_SUB,
            bg="#f8f9fb",
            fg=T.TEXT_SECONDARY,
            anchor="w",
        ).pack(fill="x", pady=(0, 28))

        # Username field
        tk.Label(
            inner, text="Tài khoản",
            font=T.F_LOGIN_LABEL,
            bg="#f8f9fb", fg=T.TEXT_PRIMARY, anchor="w",
        ).pack(fill="x", pady=(0, 4))

        self._username_var = tk.StringVar(value="admin")
        username_entry = tk.Entry(
            inner,
            textvariable=self._username_var,
            font=T.F_FORM_INPUT,
            bg="#ffffff",
            fg=T.TEXT_PRIMARY,
            relief="flat",
            bd=0,
        )
        username_entry.pack(fill="x", ipady=10)
        self._add_bottom_border(inner, "#e0e0e0")

        tk.Frame(inner, bg="#f8f9fb", height=16).pack()

        # Password field
        tk.Label(
            inner, text="Mật khẩu",
            font=T.F_LOGIN_LABEL,
            bg="#f8f9fb", fg=T.TEXT_PRIMARY, anchor="w",
        ).pack(fill="x", pady=(0, 4))

        self._password_var = tk.StringVar()
        password_entry = tk.Entry(
            inner,
            textvariable=self._password_var,
            font=T.F_FORM_INPUT,
            bg="#ffffff",
            fg=T.TEXT_PRIMARY,
            show="●",
            relief="flat",
            bd=0,
        )
        password_entry.pack(fill="x", ipady=10)
        self._add_bottom_border(inner, "#e0e0e0")

        tk.Frame(inner, bg="#f8f9fb", height=28).pack()

        # Login button
        login_btn = tk.Button(
            inner,
            text="ĐĂNG NHẬP",
            font=T.F_LOGIN_BTN,
            bg=T.ACCENT_RED,
            fg=T.TEXT_WHITE,
            activebackground="#c0392b",
            activeforeground=T.TEXT_WHITE,
            relief="flat",
            cursor="hand2",
            command=self._do_login,
        )
        login_btn.pack(fill="x", ipady=12)

        tk.Frame(inner, bg="#f8f9fb", height=24).pack()

        
        # Bind Enter key
        self.root.bind("<Return>", lambda e: self._do_login())
        username_entry.focus_set()

    def _add_bottom_border(self, parent, color="#e0e0e0"):
        """ Thêm đường kẻ dưới field. """
        tk.Frame(parent, bg=color, height=1).pack(fill="x")

    # ------------------------------------------------------------------ #
    #  LOGIC                                                               #
    # ------------------------------------------------------------------ #

    def _do_login(self):
        username = self._username_var.get().strip()
        password = self._password_var.get().strip()

        if not username or not password:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập tài khoản và mật khẩu.")
            return
            
        import json
        from pathlib import Path
        import hashlib
        
        users_file = Path("data/users.json")
        users = []
        if users_file.exists():
            try:
                with open(users_file, "r", encoding="utf-8") as f:
                    users = json.load(f)
            except Exception:
                pass
                
        # Find user
        account = next((u for u in users if u.get("username") == username), None)
        
        if not account:
            # Fallback to hardcoded admin if file is completely broken or missing
            if username == "admin" and password == "admin":
                self.on_login_success("admin", "admin", "Quản trị viên")
                return
            messagebox.showerror("Lỗi đăng nhập", "Tài khoản không tồn tại.")
            return
            
        # Check active status
        if not account.get("is_active", True):
            messagebox.showerror("Tài khoản bị khóa", "Tài khoản của bạn đã bị khóa. Vui lòng liên hệ Quản trị viên.")
            return
            
        # Verify password
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        stored_hash = account.get("password_hash")
        
        # Backward compatibility for plaintext or missing password
        is_valid = False
        if stored_hash:
            is_valid = (pwd_hash == stored_hash)
        else:
            # default to 'admin' if no hash exists
            is_valid = (password == "admin")

        if is_valid:
            logger.info("Đăng nhập thành công: %s (%s)", username, account.get("role", "staff"))
            self.on_login_success(username, account.get("role", "staff"), account.get("full_name", username))
        else:
            messagebox.showerror("Lỗi đăng nhập", "Mật khẩu không đúng.")
            logger.warning("Đăng nhập thất bại cho tài khoản: %s", username)
