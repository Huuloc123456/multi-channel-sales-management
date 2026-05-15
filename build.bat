@echo off
REM ================================================================
REM  build.bat - Đóng gói ứng dụng thành file .exe bằng PyInstaller
REM  Hệ thống Quản lý Bán hàng Đa kênh
REM  Chạy: build.bat
REM ================================================================

echo ============================================================
echo   BUILD: He thong Quan ly Ban hang Da kenh
echo ============================================================

REM --- Kiểm tra PyInstaller ---
pip show pyinstaller >nul 2>&1
IF ERRORLEVEL 1 (
    echo [INFO] PyInstaller chua duoc cai dat. Dang cai dat...
    pip install pyinstaller
)

REM --- Dọn dẹp build cũ ---
echo [INFO] Don dep build cu...
IF EXIST "build" rmdir /S /Q "build"
IF EXIST "dist"  rmdir /S /Q "dist"
IF EXIST "*.spec" del /Q "*.spec"

REM --- Tạo các thư mục cần thiết ---
IF NOT EXIST "data"    mkdir data
IF NOT EXIST "logs"    mkdir logs
IF NOT EXIST "exports" mkdir exports
IF NOT EXIST "assets"  mkdir assets

REM --- Chạy PyInstaller ---
echo [INFO] Dang dong goi ung dung...

pyinstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name "OmnichannelSales" ^
    --add-data "data;data" ^
    --add-data "assets;assets" ^
    --hidden-import "tkinter" ^
    --hidden-import "tkinter.ttk" ^
    --hidden-import "json" ^
    --hidden-import "csv" ^
    --clean ^
    main.py

REM --- Kiểm tra kết quả ---
IF EXIST "dist\OmnichannelSales.exe" (
    echo.
    echo ============================================================
    echo   BUILD THANH CONG!
    echo   File EXE: dist\OmnichannelSales.exe
    echo ============================================================

    REM Sao chép thư mục data mẫu vào dist
    IF NOT EXIST "dist\data"    mkdir "dist\data"
    IF NOT EXIST "dist\logs"    mkdir "dist\logs"
    IF NOT EXIST "dist\exports" mkdir "dist\exports"
    IF NOT EXIST "dist\assets"  mkdir "dist\assets"

    echo [INFO] Da sao chep thu muc du lieu vao dist\
) ELSE (
    echo.
    echo [LOI] Build that bai! Kiem tra output phia tren.
    exit /b 1
)

echo.
echo Ban co the chay thu: dist\OmnichannelSales.exe
