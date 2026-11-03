# ChildHealth Explorer - PostgreSQL setup

This stage configures the local PostgreSQL database and pgAdmin connection.

Verified tools: Python 3.14.6, PostgreSQL 18.6 and pgAdmin 4 version 9.18.
The database is `global_health`, owned by `gh_user`, with UTF8 encoding.

## Setup (Windows / PowerShell)

Download the official Windows x86-64 PostgreSQL ZIP from EDB and extract
its `pgsql` folder into `.local/pgsql`. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m scripts.setup_postgres
.\.venv\Scripts\python.exe -m scripts.setup_pgadmin
.\scripts\start-pgadmin.ps1
```

Open `http://127.0.0.1:5051/` and connect to `global_health` as `gh_user`.
Run `SELECT version();` in pgAdmin Query Tool to check the server version.

The PostgreSQL distribution is in `.local/pgsql`, server data in
`.local/pgdata`, and the separate pgAdmin profile in `.local/pgadmin`.
Passwords are generated locally and excluded from Git. Do not commit
`.env` or `.local/`.

For later sessions, run `.\scripts\start-postgres.ps1` and
`.\scripts\start-pgadmin.ps1`. Stop PostgreSQL afterwards with
`.\scripts\stop-postgres.ps1`.

## Libraries used in this stage

- SQLAlchemy: database connections and session helpers.
- psycopg: PostgreSQL driver.
- python-dotenv: local connection settings from .env.

See [environment details](docs/environment.md) for versions and usage.
