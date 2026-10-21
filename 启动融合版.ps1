$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
$nodePath = (Get-Command node -ErrorAction Stop).Source
if (!(Test-Path -LiteralPath $pythonPath)) {
    throw '请先按 六题画像接入说明.md 创建虚拟环境并安装依赖。'
}
if (!(Test-Path -LiteralPath (Join-Path $projectRoot 'frontend\node_modules\vite\bin\vite.js'))) {
    throw '请先在 frontend 运行 npm ci。'
}
if (!(Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue)) {
    Start-Process -FilePath $pythonPath -ArgumentList '-u','run_local.py' -WorkingDirectory (Join-Path $projectRoot 'backend') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $projectRoot 'backend.local.stdout.log') -RedirectStandardError (Join-Path $projectRoot 'backend.local.stderr.log')
}
if (!(Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue)) {
    Start-Process -FilePath $nodePath -ArgumentList 'node_modules/vite/bin/vite.js','--strictPort' -WorkingDirectory (Join-Path $projectRoot 'frontend') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $projectRoot 'frontend.local.stdout.log') -RedirectStandardError (Join-Path $projectRoot 'frontend.local.stderr.log')
}
Write-Host '六题画像入口：http://127.0.0.1:3000/#/accessibility'
Write-Host '后端日志：backend.local.stdout.log / backend.local.stderr.log'
Start-Process 'http://127.0.0.1:3000/#/accessibility'
