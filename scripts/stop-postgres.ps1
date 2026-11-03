$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PgCtl = Join-Path $ProjectRoot '.local\pgsql\bin\pg_ctl.exe'
$PgData = Join-Path $ProjectRoot '.local\pgdata'
& $PgCtl -D $PgData -m fast -w stop
if ($LASTEXITCODE -ne 0) { throw 'PostgreSQL could not stop; check .local/postgres.log.' }
