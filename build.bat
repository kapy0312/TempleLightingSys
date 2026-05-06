@echo off
chcp 65001 >nul
title 正坤點燈管理系統 - 打包工具

echo.
echo ╔══════════════════════════════════════════╗
echo ║     正坤點燈管理系統  PyInstaller 打包     ║
echo ╚══════════════════════════════════════════╝
echo.

:: 確認虛擬環境是否已啟動
if not defined VIRTUAL_ENV (
    echo [警告] 未偵測到虛擬環境，嘗試自動啟動 venv...
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat
        echo [OK] 虛擬環境已啟動。
    ) else (
        echo [錯誤] 找不到 venv 資料夾，請先執行：
        echo         python -m venv venv
        echo         .\venv\Scripts\activate
        echo         pip install -r requirements.txt
        pause
        exit /b 1
    )
)

echo [1/3] 清除舊的打包快取與 dist 資料夾...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
if exist "*.spec" del /q *.spec
echo [OK] 清除完成。
echo.

echo [2/3] 開始執行 PyInstaller 打包...
echo.

pyinstaller -F -w --clean ^
  --name "正坤點燈管理系統" ^
  --icon="favicon.ico" ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  main.py

echo.

:: 確認打包是否成功
if exist "dist\正坤點燈管理系統.exe" (
    echo ╔══════════════════════════════════════════╗
    echo ║           ✅ 打包成功！                   ║
    echo ╚══════════════════════════════════════════╝
    echo.
    echo 執行檔位置：dist\正坤點燈管理系統.exe
    echo.
    echo [3/3] 提示：若需保留舊有資料，請將 temple_data.db
    echo       複製到與 .exe 相同的資料夾中。
    echo.
) else (
    echo ╔══════════════════════════════════════════╗
    echo ║           ❌ 打包失敗！                   ║
    echo ╚══════════════════════════════════════════╝
    echo.
    echo 請檢查上方錯誤訊息，常見原因：
    echo  - requirements.txt 套件未安裝完整
    echo  - favicon.ico 檔案不存在
    echo  - templates 或 static 資料夾路徑錯誤
)

echo.
pause