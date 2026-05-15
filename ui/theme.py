""" ui/theme.py  Hệ thống màu sắc, font và style dùng chung cho toàn bộ giao diện Tkinter. """

# --- MÀU SẮC CHÍNH ---

# Sidebar (dark navy)
SIDEBAR_BG        = "#1a2035"
SIDEBAR_HOVER     = "#252d45"
SIDEBAR_ACTIVE    = "#e83e5a"
SIDEBAR_TEXT      = "#ffffff"
SIDEBAR_SUBTEXT   = "#8a93b2"
SIDEBAR_LOGO_BG   = "#141929"

# Content area
CONTENT_BG        = "#f5f6fa"
CONTENT_HEADER_BG = "#ffffff"
HEADER_BORDER     = "#e8eaf0"

# Card / Panel
CARD_BG           = "#ffffff"
CARD_BORDER       = "#e8eaf0"
CARD_SHADOW       = "#d0d3de"

# Accent / Brand
ACCENT_RED        = "#e83e5a"
ACCENT_BLUE       = "#1565c0"
ACCENT_DARK_BLUE  = "#1a2442"
ACCENT_GREEN      = "#2ecc71"
ACCENT_ORANGE     = "#f39c12"
ACCENT_PURPLE     = "#8e44ad"

# Status colors
STATUS_PENDING    = "#f39c12"
STATUS_CONFIRMED  = "#3498db"
STATUS_SHIPPING   = "#9b59b6"
STATUS_COMPLETED  = "#2ecc71"
STATUS_CANCELLED  = "#e74c3c"

# Revenue channel colors
ONLINE_COLOR      = "#2196f3"
OFFLINE_COLOR     = "#f39c12"

# Text
TEXT_PRIMARY      = "#1a2035"
TEXT_SECONDARY    = "#6b7280"
TEXT_MUTED        = "#9ca3af"
TEXT_WHITE        = "#ffffff"

# Border
BORDER_COLOR      = "#e5e7eb"
DIVIDER_COLOR     = "#f0f1f5"

# --- BUTTON COLORS ---

BTN_PRIMARY_BG    = "#1565c0"
BTN_PRIMARY_FG    = "#ffffff"
BTN_DANGER_BG     = "#e83e5a"
BTN_DANGER_FG     = "#ffffff"
BTN_WARNING_BG    = "#f39c12"
BTN_WARNING_FG    = "#ffffff"
BTN_SUCCESS_BG    = "#2ecc71"
BTN_SUCCESS_FG    = "#ffffff"
BTN_SECONDARY_BG  = "#6b7280"
BTN_SECONDARY_FG  = "#ffffff"
BTN_EXPORT_BG     = "#1a2442"
BTN_EXPORT_FG     = "#ffffff"

# --- FONTS ---

FONT_APP          = "Segoe UI"

# Sidebar
F_SIDEBAR_LOGO    = (FONT_APP, 13, "bold")
F_SIDEBAR_SUB     = (FONT_APP, 9)
F_SIDEBAR_USER    = (FONT_APP, 11, "bold")
F_SIDEBAR_ROLE    = (FONT_APP, 9)
F_SIDEBAR_NAV     = (FONT_APP, 10)
F_SIDEBAR_LOGOUT  = (FONT_APP, 10)

# Header
F_HEADER_TITLE    = (FONT_APP, 10)
F_HEADER_TIME     = (FONT_APP, 9)

# Page
F_PAGE_TITLE      = (FONT_APP, 18, "bold")
F_PAGE_SUBTITLE   = (FONT_APP, 10)
F_SECTION_TITLE   = (FONT_APP, 12, "bold")

# Stat card
F_STAT_LABEL      = (FONT_APP, 9)
F_STAT_VALUE      = (FONT_APP, 20, "bold")

# Table
F_TABLE_HEADER    = (FONT_APP, 9, "bold")
F_TABLE_ROW       = (FONT_APP, 9)

# Button
F_BTN             = (FONT_APP, 9, "bold")
F_BTN_SM          = (FONT_APP, 9)

# Form
F_FORM_LABEL      = (FONT_APP, 10)
F_FORM_INPUT      = (FONT_APP, 10)

# Login
F_LOGIN_TITLE     = (FONT_APP, 22, "bold")
F_LOGIN_SUB       = (FONT_APP, 11)
F_LOGIN_LABEL     = (FONT_APP, 10, "bold")
F_LOGIN_BTN       = (FONT_APP, 11, "bold")
F_LOGIN_BRAND     = (FONT_APP, 16, "bold")
F_LOGIN_BRAND_SUB = (FONT_APP, 10)
F_LOGIN_FEATURE   = (FONT_APP, 10)

# --- SIZES ---

SIDEBAR_WIDTH     = 200
HEADER_HEIGHT     = 50
BTN_PADX          = 12
BTN_PADY          = 6
CARD_PADX         = 16
CARD_PADY         = 12

# --- STAT CARD COLORS (left-border accent) ---

STAT_COLORS = [
    "#2ecc71",   # Tổng doanh thu – xanh lá
    "#2196f3",   # Online – xanh dương
    "#f39c12",   # Offline – cam
    "#e83e5a",   # Tổng đơn hàng – đỏ
    "#1565c0",   # Sản phẩm – navy
    "#8e44ad",   # Khách hàng – tím
]
