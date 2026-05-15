""" ui/user_frame.py  Frame Quản lý Người dùng – chỉ dành cho Quản trị viên (admin). Chức năng: Xem danh sách, thêm người dùng, khóa/mở, xóa, sửa. """

import tkinter as tk
from tkinter import ttk, messagebox
import json
import logging
from pathlib import Path
from datetime import datetime
import re

from ui import theme as T
from ui.widgets import (
    IconButton, DataTable, ModalDialog, build_page_header
)

logger = logging.getLogger(__name__)

USER_FILE = Path("data/users.json")

# Dữ liệu mặc định nếu file chưa tồn tại
DEFAULT_USERS = [
    {
        "username":   "admin",
        "full_name":  "Quản trị viên",
        "role":       "admin",
        "email":      "admin@sales.com",
        "is_active":  True,
        "created_at": "2026-04-20 02:39:02",
    },
    {
        "username":   "staff",
        "full_name":  "Nhân viên bán hàng",
        "role":       "staff",
        "email":      "staff@sales.com",
        "is_active":  True,
        "created_at": "2026-04-20 02:39:02",
    },
]

ROLE_VN   = {"admin": "Quản trị viên", "staff": "Nhân viên"}
ROLE_ICON = {"admin": "🔑 Admin",      "staff": "👤 Nhân viên"}

COLUMNS = [
    {"id": "username",   "heading": "Tài khoản",   "width": 130, "anchor": "w"},
    {"id": "full_name",  "heading": "Họ và tên",   "width": 180, "anchor": "w"},
    {"id": "role_icon",  "heading": "Vai trò",      "width": 120, "anchor": "w"},
    {"id": "email",      "heading": "Email",         "width": 200, "anchor": "w", "stretch": True},
    {"id": "is_active",  "heading": "Trạng thái",  "width": 100, "anchor": "center"},
    {"id": "created_at", "heading": "Ngày tạo",     "width": 140, "anchor": "w"},
]


def _load_users() -> list[dict]:
    try:
        USER_FILE.parent.mkdir(exist_ok=True)
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        _save_users(DEFAULT_USERS)
        return list(DEFAULT_USERS)


def _save_users(users: list[dict]):
    USER_FILE.parent.mkdir(exist_ok=True)
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


class UserFrame(tk.Frame):
    """ Frame quản lý người dùng (admin only). """

    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, bg=T.CONTENT_BG, **kwargs)
        self.controller = controller
        self._users: list[dict] = []
        self._build()
        self.refresh()

    def _build(self):
        build_page_header(
            self,
            title="Quản lý người dùng",
            subtitle="Phân quyền và tài khoản hệ thống",
            icon="👤",
        )

        # Toolbar
        toolbar = tk.Frame(self, bg=T.CONTENT_BG)
        toolbar.pack(fill="x", padx=24, pady=(0, 8))
        IconButton(toolbar, "+ Thêm người dùng",
                   bg=T.ACCENT_RED, command=self._add_user
                   ).pack(side="left")

        # Table
        frame = tk.Frame(self, bg=T.CARD_BG,
                         highlightbackground=T.CARD_BORDER, highlightthickness=1)
        frame.pack(fill="both", expand=True, padx=24, pady=(0, 8))
        self._table = DataTable(frame, columns=COLUMNS)
        self._table.pack(fill="both", expand=True, padx=1, pady=1)

        # Bottom
        bottom = tk.Frame(self, bg=T.CONTENT_BG)
        bottom.pack(fill="x", padx=24, pady=(0, 16))
        IconButton(bottom, "✏ Sửa",   bg=T.BTN_PRIMARY_BG,
                   command=self._edit_user  ).pack(side="left", padx=(0, 8))
        IconButton(bottom, "🔒 Khóa/Mở", bg=T.BTN_WARNING_BG,
                   command=self._toggle_active).pack(side="left", padx=(0, 8))
        IconButton(bottom, "🗑 Xóa",  bg=T.BTN_DANGER_BG,
                   command=self._delete_user ).pack(side="left")

    def refresh(self):
        self._users = _load_users()
        self._reload_table()

    def _reload_table(self):
        rows = []
        for u in self._users:
            active_text = "✅ Hoạt động" if u.get("is_active", True) else "🔒 Bị khóa"
            rows.append([
                u.get("username", ""),
                u.get("full_name", ""),
                ROLE_ICON.get(u.get("role", ""), u.get("role", "")),
                u.get("email", ""),
                active_text,
                u.get("created_at", ""),
            ])
        self._table.load_rows(rows)

    # ---- CRUD ----

    def _add_user(self):
        existing_usernames = [u["username"] for u in self._users]
        dialog = UserDialog(self, title="Thêm người dùng mới",
                            existing_usernames=existing_usernames)
        self.wait_window(dialog)
        if dialog.result:
            self._users.append(dialog.result)
            _save_users(self._users)
            self._reload_table()
            messagebox.showinfo("Thành công", "Đã thêm người dùng mới.")

    def _edit_user(self):
        sel = self._table.get_selected()
        if not sel:
            messagebox.showwarning("Chọn người dùng", "Vui lòng chọn người dùng cần sửa.")
            return
        uname = sel[0]
        user = next((u for u in self._users if u["username"] == uname), None)
        if not user:
            return
        existing = [u["username"] for u in self._users if u["username"] != uname]
        dialog = UserDialog(self, title="Chỉnh sửa người dùng",
                            user=user, existing_usernames=existing)
        self.wait_window(dialog)
        if dialog.result:
            idx = next(i for i, u in enumerate(self._users) if u["username"] == uname)
            self._users[idx] = dialog.result
            _save_users(self._users)
            self._reload_table()
            messagebox.showinfo("Thành công", "Đã cập nhật người dùng.")

    def _toggle_active(self):
        sel = self._table.get_selected()
        if not sel:
            messagebox.showwarning("Chọn người dùng", "Vui lòng chọn người dùng.")
            return
        uname = sel[0]
        if uname == "admin":
            messagebox.showwarning("Không thể", "Không thể khóa tài khoản admin chính.")
            return
        for u in self._users:
            if u["username"] == uname:
                u["is_active"] = not u.get("is_active", True)
                action = "mở khóa" if u["is_active"] else "khóa"
                _save_users(self._users)
                self._reload_table()
                messagebox.showinfo("Thành công", f"Đã {action} tài khoản: {uname}")
                return

    def _delete_user(self):
        sel = self._table.get_selected()
        if not sel:
            messagebox.showwarning("Chọn người dùng", "Vui lòng chọn người dùng.")
            return
        uname = sel[0]
        if uname == "admin":
            messagebox.showwarning("Không thể", "Không thể xóa tài khoản admin chính.")
            return
        if not messagebox.askyesno("Xác nhận xóa",
                                   f"Xóa tài khoản '{uname}'?"):
            return
        self._users = [u for u in self._users if u["username"] != uname]
        _save_users(self._users)
        self._reload_table()
        messagebox.showinfo("Thành công", f"Đã xóa tài khoản: {uname}")


# --- USER DIALOG ---

class UserDialog(ModalDialog):
    def __init__(self, parent, title: str, user: dict = None,
                 existing_usernames: list = None):
        super().__init__(parent, title=title, width=440, height=400)
        self._user = user
        self._existing = existing_usernames or []
        self._build_form()
        if user:
            self._populate(user)

    def _build_form(self):
        tk.Label(self, text=self.title(),
                 font=T.F_SECTION_TITLE, bg=T.CONTENT_BG,
                 fg=T.TEXT_PRIMARY).pack(fill="x", padx=20, pady=(16, 8))

        form = tk.Frame(self, bg=T.CONTENT_BG)
        form.pack(fill="both", expand=True)
        form.columnconfigure(1, weight=1)

        self._uname_var  = tk.StringVar()
        self._name_var   = tk.StringVar()
        self._email_var  = tk.StringVar()
        self._role_var   = tk.StringVar(value="staff")

        self._make_field(form, "Tài khoản *",  self._uname_var, row=0)
        self._make_field(form, "Họ và tên *",  self._name_var,  row=1)
        self._make_field(form, "Email",         self._email_var, row=2)
        self._make_combobox(form, "Vai trò *",   self._role_var,
                            ["admin", "staff"], row=3)

        if self._user:
            # disable username change when editing
            pass

        self._footer_buttons(self, self._save, self.destroy)

    def _populate(self, u: dict):
        self._uname_var.set(u.get("username", ""))
        self._name_var.set(u.get("full_name", ""))
        self._email_var.set(u.get("email", ""))
        self._role_var.set(u.get("role", "staff"))

    def _save(self):
        uname = self._uname_var.get().strip()
        name  = self._name_var.get().strip()
        email = self._email_var.get().strip()
        role  = self._role_var.get()

        if not uname:
            messagebox.showerror("Lỗi", "Tên tài khoản không được để trống.", parent=self)
            return
        if not name:
            messagebox.showerror("Lỗi", "Họ và tên không được để trống.", parent=self)
            return
        if uname in self._existing:
            messagebox.showerror("Lỗi", f"Tài khoản '{uname}' đã tồn tại.", parent=self)
            return
        if email and not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            messagebox.showerror("Lỗi", "Định dạng email không hợp lệ.", parent=self)
            return

        self.result = {
            "username":   uname,
            "full_name":  name,
            "role":       role,
            "email":      email,
            "is_active":  self._user.get("is_active", True) if self._user else True,
            "password_hash": self._user.get("password_hash", "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918") if self._user else "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918",
            "created_at": self._user.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                          if self._user else datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.destroy()
