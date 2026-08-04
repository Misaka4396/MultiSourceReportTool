@echo off
REM ============================================
REM  多源报告汇总推送工具 — PyInstaller 打包脚本
REM ============================================
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Building executable...
pyinstaller --onefile --windowed --name "MultiSourceReportTool" --add-data "resources;resources" main.py

echo.
echo Build complete! Check the .\dist\ folder.
pause
