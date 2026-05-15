""" ui/main_window.py  Cửa sổ chính của ứng dụng. Bao gồm: Sidebar điều hướng (bên trái) + Content area (bên phải). Hỗ trợ 2 role: admin (đầy đủ menu) và staff (menu hạn chế). """

import tkinter as tk
from tkinter import messagebox
import logging
from datetime import datetime

from ui import theme as T
from ui.login_window import LoginWindow

logger = logging.getLogger(__name__)


class MainWindow:
    """ Cửa sổ chính – quản lý màn hình đăng nhập và màn hình chính. """

    def __init__(self, root: tk.Tk):
        self.root = root
        self._current_user   = None
        self._current_role   = None
        self._current_display= None
        self._show_login()

    # ------------------------------------------------------------------ #
    #  LOGIN → MAIN                                                        #
    # ------------------------------------------------------------------ #

    def _show_login(self):
        """ Hiển thị màn hình đăng nhập. """
        for widget in self.root.winfo_children():
            widget.destroy()
        LoginWindow(self.root, on_login_success=self._on_login)

    def _on_login(self, username: str, role: str, display: str):
        """ Callback sau khi đăng nhập thành công. """
        self._current_user    = username
        self._current_role    = role
        self._current_display = display
        logger.info("Người dùng đăng nhập: %s (%s)", username, role)
        self._show_main()

    def _show_main(self):
        """ Hiển thị giao diện chính. """
        for widget in self.root.winfo_children():
            widget.destroy()
        # Resize to full app
        self.root.geometry("1280x750")
        self.root.resizable(True, True)
        title = f"Sales Manager - {self._current_display} ({self._current_user.upper()})"
        self.root.title(title)

        # Center
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth()  // 2) - (1280 // 2)
        y = (self.root.winfo_screenheight() // 2) - (750 // 2)
        self.root.geometry(f"1280x750+{x}+{y}")

        AppShell(self.root,
                 username=self._current_user,
                 role=self._current_role,
                 display=self._current_display,
                 on_logout=self._show_login)


# --- APP SHELL  (Sidebar + Content) ---

class AppShell(tk.Frame):
    """ Shell chính: sidebar cố định bên trái, content area thay đổi bên phải. """

    # Định nghĩa menu (id, label, icon, role_required)
    NAV_ITEMS = [
        ("dashboard",     "Dashboard",      "📊", None),
        ("products",      "Sản phẩm",       "🗃", None),
        ("customers",     "Khách hàng",     "👥", None),
        ("orders",        "Đơn hàng",       "📦", None),
        ("multichannel",  "Đa kênh",        "📡", None),
        ("reports",       "Báo cáo",        "📈", None),
        ("api",           "Dữ liệu API",    "🌐", None),
        ("files",         "Quản lý File",   "📁", None),
        ("users",         "Người dùng",     "👤", "admin"),
    ]

    def __init__(self, parent, username, role, display, on_logout, **kwargs):
        super().__init__(parent, bg=T.CONTENT_BG, **kwargs)
        self.pack(fill="both", expand=True)

        self._username  = username
        self._role      = role
        self._display   = display
        self._on_logout = on_logout
        self._active    = None
        self._frames    = {}
        self._nav_btns  = {}

        self._build()
        self._navigate("dashboard")
        self._update_clock()

    # ------------------------------------------------------------------ #
    #  BUILD LAYOUT                                                        #
    # ------------------------------------------------------------------ #

    def _build(self):
        # Left sidebar
        self._sidebar = tk.Frame(self, bg=T.SIDEBAR_BG,
                                 width=T.SIDEBAR_WIDTH)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        # Right main area
        right = tk.Frame(self, bg=T.CONTENT_BG)
        right.pack(side="left", fill="both", expand=True)

        self._build_sidebar()
        self._build_header(right)
        self._build_content(right)

    # ------------------------------------------------------------------ #
    #  SIDEBAR                                                             #
    # ------------------------------------------------------------------ #

    def _build_sidebar(self):
        sb = self._sidebar

        # Logo block
        logo_frame = tk.Frame(sb, bg=T.SIDEBAR_LOGO_BG)
        logo_frame.pack(fill="x")
        logo_inner = tk.Frame(logo_frame, bg=T.SIDEBAR_LOGO_BG)
        logo_inner.pack(fill="x", padx=16, pady=14)

        tk.Label(logo_inner, text="🏪",
                 font=(T.FONT_APP, 18),
                 bg=T.SIDEBAR_LOGO_BG, fg=T.TEXT_WHITE
                 ).pack(side="left")
        text_col = tk.Frame(logo_inner, bg=T.SIDEBAR_LOGO_BG)
        text_col.pack(side="left", padx=(8, 0))
        tk.Label(text_col, text="SALES MGR",
                 font=T.F_SIDEBAR_LOGO,
                 bg=T.SIDEBAR_LOGO_BG, fg=T.TEXT_WHITE,
                 anchor="w").pack(fill="x")
        tk.Label(text_col, text="Quản lý đa kênh",
                 font=T.F_SIDEBAR_SUB,
                 bg=T.SIDEBAR_LOGO_BG, fg=T.SIDEBAR_SUBTEXT,
                 anchor="w").pack(fill="x")

        # User block
        user_frame = tk.Frame(sb, bg=T.ACCENT_DARK_BLUE)
        user_frame.pack(fill="x")
        user_inner = tk.Frame(user_frame, bg=T.ACCENT_DARK_BLUE)
        user_inner.pack(fill="x", padx=16, pady=12)
        tk.Label(user_inner, text=self._display,
                 font=T.F_SIDEBAR_USER,
                 bg=T.ACCENT_DARK_BLUE, fg=T.TEXT_WHITE,
                 anchor="w").pack(fill="x")
        role_icon = "🔑" if self._role == "admin" else "👤"
        role_text = "Quản trị viên" if self._role == "admin" else "Nhân viên"
        tk.Label(user_inner, text=f"{role_icon} {role_text}",
                 font=T.F_SIDEBAR_ROLE,
                 bg=T.ACCENT_DARK_BLUE, fg=T.SIDEBAR_SUBTEXT,
                 anchor="w").pack(fill="x")

        # Divider
        tk.Frame(sb, bg=T.SIDEBAR_HOVER, height=1).pack(fill="x")

        # Navigation items
        for item_id, label, icon, required_role in self.NAV_ITEMS:
            if required_role and self._role != required_role:
                continue  # Skip menu items restricted by role
            self._add_nav_button(sb, item_id, label, icon)

        # Spacer
        tk.Frame(sb, bg=T.SIDEBAR_BG).pack(fill="both", expand=True)

        # Divider
        tk.Frame(sb, bg=T.SIDEBAR_HOVER, height=1).pack(fill="x")

        # Logout button
        logout_btn = tk.Frame(sb, bg=T.SIDEBAR_BG, cursor="hand2")
        logout_btn.pack(fill="x")
        logout_inner = tk.Frame(logout_btn, bg=T.SIDEBAR_BG)
        logout_inner.pack(fill="x", padx=16, pady=12)
        lbl = tk.Label(logout_inner,
                       text="🚪  Đăng xuất",
                       font=T.F_SIDEBAR_NAV,
                       bg=T.SIDEBAR_BG,
                       fg=T.ACCENT_RED,
                       anchor="w", cursor="hand2")
        lbl.pack(fill="x")
        for w in [logout_btn, logout_inner, lbl]:
            w.bind("<Button-1>", lambda e: self._logout())
            w.bind("<Enter>", lambda e: [
                logout_btn.config(bg=T.SIDEBAR_HOVER),
                logout_inner.config(bg=T.SIDEBAR_HOVER),
                lbl.config(bg=T.SIDEBAR_HOVER),
            ])
            w.bind("<Leave>", lambda e: [
                logout_btn.config(bg=T.SIDEBAR_BG),
                logout_inner.config(bg=T.SIDEBAR_BG),
                lbl.config(bg=T.SIDEBAR_BG),
            ])

    def _add_nav_button(self, parent, item_id, label, icon):
        btn_frame = tk.Frame(parent, bg=T.SIDEBAR_BG, cursor="hand2")
        btn_frame.pack(fill="x")

        inner = tk.Frame(btn_frame, bg=T.SIDEBAR_BG)
        inner.pack(fill="x", padx=0, pady=0)

        # Active indicator bar
        indicator = tk.Frame(inner, bg=T.SIDEBAR_BG, width=4)
        indicator.pack(side="left", fill="y")

        content = tk.Frame(inner, bg=T.SIDEBAR_BG)
        content.pack(side="left", fill="x", expand=True, padx=(8, 12), pady=10)

        icon_lbl = tk.Label(content, text=icon,
                            font=(T.FONT_APP, 12),
                            bg=T.SIDEBAR_BG, fg=T.SIDEBAR_SUBTEXT)
        icon_lbl.pack(side="left")
        text_lbl = tk.Label(content, text=f"  {label}",
                            font=T.F_SIDEBAR_NAV,
                            bg=T.SIDEBAR_BG, fg=T.SIDEBAR_SUBTEXT,
                            anchor="w")
        text_lbl.pack(side="left", fill="x", expand=True)

        widgets = [btn_frame, inner, content, indicator, icon_lbl, text_lbl]

        def on_click(e, _id=item_id):
            self._navigate(_id)

        def on_enter(e, _id=item_id):
            if _id != self._active:
                for w in [btn_frame, inner, content, indicator, icon_lbl, text_lbl]:
                    try:
                        w.config(bg=T.SIDEBAR_HOVER)
                    except Exception:
                        pass

        def on_leave(e, _id=item_id):
            if _id != self._active:
                for w in [btn_frame, inner, content, indicator, icon_lbl, text_lbl]:
                    try:
                        w.config(bg=T.SIDEBAR_BG)
                    except Exception:
                        pass

        for w in widgets:
            w.bind("<Button-1>", on_click)
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

        self._nav_btns[item_id] = {
            "frame": btn_frame,
            "inner": inner,
            "content": content,
            "indicator": indicator,
            "icon": icon_lbl,
            "text": text_lbl,
        }

    def _set_active_nav(self, item_id: str):
        """ Cập nhật style của nav item đang active. """
        # Reset all
        for _id, widgets in self._nav_btns.items():
            bg = T.SIDEBAR_BG
            for w in [widgets["frame"], widgets["inner"],
                      widgets["content"], widgets["indicator"]]:
                try:
                    w.config(bg=bg)
                except Exception:
                    pass
            try:
                widgets["indicator"].config(bg=T.SIDEBAR_BG)
            except Exception:
                pass
            try:
                widgets["icon"].config(bg=bg, fg=T.SIDEBAR_SUBTEXT)
                widgets["text"].config(bg=bg, fg=T.SIDEBAR_SUBTEXT)
            except Exception:
                pass

        # Set active
        if item_id in self._nav_btns:
            w = self._nav_btns[item_id]
            for key in ["frame", "inner", "content"]:
                try:
                    w[key].config(bg=T.SIDEBAR_ACTIVE)
                except Exception:
                    pass
            try:
                w["indicator"].config(bg=T.SIDEBAR_ACTIVE, width=4)
            except Exception:
                pass
            try:
                w["icon"].config(bg=T.SIDEBAR_ACTIVE, fg=T.TEXT_WHITE)
                w["text"].config(bg=T.SIDEBAR_ACTIVE, fg=T.TEXT_WHITE)
            except Exception:
                pass

    # ------------------------------------------------------------------ #
    #  HEADER                                                              #
    # ------------------------------------------------------------------ #

    def _build_header(self, parent):
        self._header = tk.Frame(parent, bg=T.CONTENT_HEADER_BG,
                                height=T.HEADER_HEIGHT)
        self._header.pack(fill="x")
        self._header.pack_propagate(False)

        inner = tk.Frame(self._header, bg=T.CONTENT_HEADER_BG)
        inner.pack(fill="both", expand=True, padx=24)

        # Page name label (left)
        self._page_label = tk.Label(
            inner, text="Dashboard",
            font=T.F_HEADER_TITLE,
            bg=T.CONTENT_HEADER_BG, fg=T.TEXT_SECONDARY,
            anchor="w",
        )
        self._page_label.pack(side="left", fill="y")

        # Clock (right)
        self._clock_label = tk.Label(
            inner, text="",
            font=T.F_HEADER_TIME,
            bg=T.CONTENT_HEADER_BG, fg=T.TEXT_SECONDARY,
        )
        self._clock_label.pack(side="right", fill="y")

        # Bottom border
        tk.Frame(parent, bg=T.HEADER_BORDER, height=1).pack(fill="x")

    # ------------------------------------------------------------------ #
    #  CONTENT                                                             #
    # ------------------------------------------------------------------ #

    def _build_content(self, parent):
        self._content_area = tk.Frame(parent, bg=T.CONTENT_BG)
        self._content_area.pack(fill="both", expand=True)

    def _get_frame(self, item_id: str) -> tk.Frame:
        """ Lazy-load frame khi cần thiết. """
        if item_id not in self._frames:
            self._frames[item_id] = self._create_frame(item_id)
        return self._frames[item_id]

    def _create_frame(self, item_id: str) -> tk.Frame:
        """ Tạo frame theo item_id. """
        if item_id == "dashboard":
            from ui.dashboard_frame import DashboardFrame
            return DashboardFrame(self._content_area, controller=self)
        elif item_id == "products":
            from ui.product_frame import ProductFrame
            return ProductFrame(self._content_area, controller=self)
        elif item_id == "customers":
            from ui.customer_frame import CustomerFrame
            return CustomerFrame(self._content_area, controller=self)
        elif item_id == "multichannel":
            from ui.multichannel_frame import MultichannelFrame
            return MultichannelFrame(self._content_area, controller=self)
        elif item_id == "orders":
            from ui.order_frame import OrderFrame
            return OrderFrame(self._content_area, controller=self)
        elif item_id == "reports":
            from ui.report_frame import ReportFrame
            return ReportFrame(self._content_area, controller=self)
        elif item_id == "api":
            from ui.api_frame import ApiFrame
            return ApiFrame(self._content_area, controller=self)
        elif item_id == "files":
            from ui.file_frame import FileFrame
            return FileFrame(self._content_area, controller=self)
        elif item_id == "users":
            from ui.user_frame import UserFrame
            return UserFrame(self._content_area, controller=self)
        else:
            return tk.Frame(self._content_area, bg=T.CONTENT_BG)

    # ------------------------------------------------------------------ #
    #  NAVIGATION                                                          #
    # ------------------------------------------------------------------ #

    def _navigate(self, item_id: str):
        if self._active == item_id:
            return
        # Hide current
        if self._active and self._active in self._frames:
            self._frames[self._active].pack_forget()

        self._active = item_id

        # Update header
        label_map = {
            "dashboard": "Dashboard",
            "products":  "Quản lý Sản phẩm",
            "customers": "Quản lý Khách hàng",
            "orders":    "Quản lý Đơn hàng",
            "multichannel": "Quản lý Đa kênh",
            "reports":      "Báo cáo & Thống kê",
            "api":       "Dữ liệu Bên ngoài",
            "files":     "Quản lý File",
            "users":     "Quản lý Người dùng",
        }
        self._page_label.config(text=label_map.get(item_id, item_id))

        # Show frame (lazy create)
        frame = self._get_frame(item_id)
        frame.pack(fill="both", expand=True, padx=24, pady=16)

        # Refresh data
        if hasattr(frame, "refresh"):
            try:
                frame.refresh()
            except Exception as exc:
                logger.error("Error refreshing %s: %s", item_id, exc, exc_info=True)

        # Update nav
        self._set_active_nav(item_id)

    # ------------------------------------------------------------------ #
    #  CLOCK                                                               #
    # ------------------------------------------------------------------ #

    def _update_clock(self):
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self._clock_label.config(text=now)
        self._content_area.after(1000, self._update_clock)

    # ------------------------------------------------------------------ #
    #  LOGOUT                                                              #
    # ------------------------------------------------------------------ #

    def _logout(self):
        if messagebox.askyesno("Đăng xuất", "Bạn có chắc muốn đăng xuất không?"):
            logger.info("Đăng xuất: %s", self._username)
            self._on_logout()

    # ------------------------------------------------------------------ #
    #  PUBLIC API (for child frames)                                       #
    # ------------------------------------------------------------------ #

    @property
    def current_user(self) -> str:
        return self._username

    @property
    def current_role(self) -> str:
        return self._role

    def navigate_to(self, item_id: str):
        """ Cho phép các frame con điều hướng sang tab khác. """
        self._navigate(item_id)
