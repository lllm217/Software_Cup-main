@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 请先安装 Python 3.11 和 Node.js 20 或以上版本，并保持联网。
if exist ".venv\Scripts\python.exe" goto python_ready
py -3.11 -c "import sys; assert sys.version_info[:2] == (3,11)" >nul 2>&1
if errorlevel 1 goto python_fallback
py -3.11 -m venv .venv
if errorlevel 1 goto failed
goto python_ready
:python_fallback
python -c "import sys; assert sys.version_info[:2] == (3,11)" >nul 2>&1
if errorlevel 1 goto python_missing
python -m venv .venv
if errorlevel 1 goto failed
:python_ready
".venv\Scripts\python.exe" -m pip install -r backend\requirements-local.lock.txt
if errorlevel 1 goto failed
call npm.cmd ci --prefix "%~dp0frontend"
if errorlevel 1 goto failed
echo 安装完成！现在运行 02_启动演示.cmd。
pause
exit /b 0
:python_missing
echo 未找到 Python 3.11。请安装并勾选 Add Python to PATH，再重新打开 CMD。
pause
exit /b 1
:failed
echo 安装失败，请保留本窗口中的报错并检查网络和环境。
pause
exit /b 1
