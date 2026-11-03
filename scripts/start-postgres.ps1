$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PgConfig = Get-Content -LiteralPath (Join-Path $ProjectRoot '.local\postgres.json') | ConvertFrom-Json
$PgCtl = Join-Path $ProjectRoot '.local\pgsql\bin\pg_ctl.exe'
$PgData = Join-Path $ProjectRoot '.local\pgdata'
$PgLog = Join-Path $ProjectRoot '.local\postgres.log'
& $PgCtl -D $PgData status
if ($LASTEXITCODE -ne 0) {
    & $PgCtl -D $PgData -l $PgLog -o "-h 127.0.0.1 -p $($PgConfig.port)" -w start
    if ($LASTEXITCODE -ne 0) { throw 'PostgreSQL could not start; check .local/postgres.log.' }
}
