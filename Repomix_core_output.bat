@echo off
title 正坤點燈系統 - 核心程式打包工具
echo ==================================================
echo   正在執行 Repomix 打包核心程式碼...
echo   包含檔案：main.py, app.py, index.html, app.js
echo ==================================================
echo.

npx repomix --include "main.py,app.py,templates/index.html,static/js/app.js,requirements.txt,README.md" --output repomix-core.xml

echo.
echo ==================================================
echo   ✅ 打包完成！
echo   請查看專案目錄下的：repomix-core.xml
echo ==================================================
echo.
pause