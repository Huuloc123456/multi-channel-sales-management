#!/bin/bash
# ================================================================
#  build.sh - Đóng gói ứng dụng thành file .exe (cross-platform)
#  Hệ thống Quản lý Bán hàng Đa kênh
#  Chạy: bash build.sh
# ================================================================

set -e  # Dừng nếu có lỗi

echo "============================================================"
echo "  BUILD: He thong Quan ly Ban hang Da kenh"
echo "============================================================"

# --- Kiểm tra PyInstaller ---
if ! pip show pyinstaller &>/dev/null; then
    echo "[INFO] Cai dat PyInstaller..."
    pip install pyinstaller
fi

# --- Dọn dẹp build cũ ---
echo "[INFO] Don dep build cu..."
rm -rf build dist *.spec

# --- Tạo thư mục cần thiết ---
mkdir -p data logs exports assets

# --- Chạy PyInstaller ---
echo "[INFO] Dang dong goi..."

pyinstaller \
    --noconfirm \
    --onefile \
    --windowed \
    --name "OmnichannelSales" \
    --add-data "data:data" \
    --add-data "assets:assets" \
    --hidden-import "tkinter" \
    --hidden-import "tkinter.ttk" \
    --hidden-import "json" \
    --hidden-import "csv" \
    --clean \
    main.py

# --- Tạo thư mục hỗ trợ trong dist ---
mkdir -p dist/data dist/logs dist/exports dist/assets

echo ""
echo "============================================================"
echo "  BUILD THANH CONG!"
echo "  File: dist/OmnichannelSales"
echo "============================================================"
