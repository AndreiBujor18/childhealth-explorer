param([int]$Port = 8000)
$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $ProjectRoot
& (Join-Path $ProjectRoot '.venv\Scripts\python.exe') -m uvicorn app.main:app --host 127.0.0.1 --port $Port --reload --reload-dir app --reload-dir etl
