@echo off
chcp 65001 >nul
cd /d "%~dp0frontend"
if not exist "node_modules\vite\bin\vite.js" (
echo 请先运行 01_首次安装.cmd。
pause
exit /b 1
)
node node_modules/vite/bin/vite.js --host 127.0.0.1 --strictPort
if errorlevel 1 (
echo 若提示 3000 端口占用，请先打开 http://127.0.0.1:3000/#/accessibility 检查旧服务。
pause
)
