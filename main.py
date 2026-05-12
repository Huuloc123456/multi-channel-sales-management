"""
main.py
========
Điểm khởi đầu (entry point) của ứng dụng.

Khởi tạo logging, tạo thư mục dữ liệu nếu chưa có,
sau đó khởi động giao diện Tkinter.
"""

import tkinter as tk
import logging
import sys
from pathlib import Path

# ------------------------------------------------------------------ #
#  CẤU HÌNH LOGGING                                                   #
# ------------------------------------------------------------------ #

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------ #
#  KHỞI TẠO THƯ MỤC DỮ LIỆU                                          #
# ------------------------------------------------------------------ #

def ensure_data_directories():
    """Tạo các thư mục cần thiết nếu chưa tồn tại."""
    for directory in ["data", "logs", "exports", "assets"]:
        Path(directory).mkdir(exist_ok=True)
    logger.info("Các thư mục hệ thống đã sẵn sàng.")


# ------------------------------------------------------------------ #
#  MAIN                                                                #
# ------------------------------------------------------------------ #

def main():
    """Hàm chính khởi động ứng dụng."""
    logger.info("=" * 60)
    logger.info("Khởi động Hệ thống Quản lý Bán hàng Đa kênh")
    logger.info("=" * 60)

    ensure_data_directories()

    # Khởi tạo Tkinter root
    root = tk.Tk()

    try:
        from ui.main_window import MainWindow
        app = MainWindow(root)
        logger.info("Giao diện chính đã sẵn sàng.")
        root.mainloop()
    except Exception as exc:
        logger.critical("Lỗi nghiêm trọng khi khởi động: %s", exc, exc_info=True)
        import tkinter.messagebox as mb
        mb.showerror(
            "Lỗi khởi động",
            f"Không thể khởi động ứng dụng:\n{exc}"
        )
        sys.exit(1)
    finally:
        logger.info("Ứng dụng đã đóng.")


if __name__ == "__main__":
    main()
