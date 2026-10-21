@echo off
chcp 65001 >nul
cd /d "%~dp0"
start "Learning Backend" "%ComSpec%" /k call "%~dp0启动后端.cmd"
start "Learning Frontend" "%ComSpec%" /k call "%~dp0启动前端.cmd"
echo 等待两个窗口启动成功，再打开浏览器中的页面。
start "" "http://127.0.0.1:3000/#/accessibility"
echo 如果浏览器首次显示无法访问，等待启动完成后刷新即可。
echo 结束演示时，在两个运行窗口分别按 Ctrl+C。
pause
