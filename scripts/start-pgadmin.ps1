param([switch]$Wait)
$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PgAdminRoot = Join-Path $ProjectRoot '.local\pgsql\pgAdmin 4'
$PgAdminPython = Join-Path $PgAdminRoot 'python\python.exe'
$PgAdminApp = Join-Path $PgAdminRoot 'web\pgAdmin4.py'
$env:PGADMIN_SERVER_MODE = 'OFF'
$env:PATH = (Join-Path $ProjectRoot '.local\pgsql\bin') + ';' + $env:PATH
$PgAdminProcess = Start-Process -FilePath $PgAdminPython -ArgumentList @('-s', ('"' + $PgAdminApp + '"')) -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $ProjectRoot '.local\pgadmin-stdout.log') -RedirectStandardError (Join-Path $ProjectRoot '.local\pgadmin-stderr.log')
$PgAdminProcess.Id | Set-Content -LiteralPath (Join-Path $ProjectRoot '.local\pgadmin-process.txt')
Write-Output 'pgAdmin starts at http://127.0.0.1:5051/; first startup may take a minute.'
if ($Wait) { Wait-Process -Id $PgAdminProcess.Id }
