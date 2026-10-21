@echo off
chcp 65001 >nul
cd /d "%~dp0backend"
if not exist "..\.venv\Scripts\python.exe" (
echo 请先运行 01_首次安装.cmd。
pause
exit /b 1
)
"..\.venv\Scripts\python.exe" run_local.py
if errorlevel 1 pause
