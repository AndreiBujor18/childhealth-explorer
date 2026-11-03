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

## Five-table schema

The tables are `source`, `country`, `indicator`, `observation` and
`import_log`. SQLAlchemy models are in `app/models.py`; the SQL reference
is `db/schema.sql`.

```powershell
.\.venv\Scripts\python.exe -m app.create_tables
.\.venv\Scripts\python.exe -m scripts.verify_database
```

The verification compares columns, keys, constraints and indexes in a
rolled-back temporary schema, then exports `db/schema_dump.sql` using
`pg_dump --schema-only`. All five project tables remain empty.

See [PostgreSQL evidence](docs/postgresql.md) and the
[ER diagram](docs/diagrams/database-erd.svg).

## API feasibility checks

Existing adapters retrieve and normalize UNICEF vaccination data and
World Bank mortality and socioeconomic indicators. They share an
observation contract, raw-response cache and validation rules.

The pilot covers 20 countries, seven indicators and 2000-2023. It contains
3,360 normalized records, including 11 missing values, and 469 complete
country-year combinations. Missing values are preserved.

```powershell
.\.venv\Scripts\python.exe -m etl.verify_sources
.\.venv\Scripts\python.exe -m scripts.check_indicator_urls
.\.venv\Scripts\python.exe -m pytest -q
```

These commands verify source availability and save files. They do not
load observations into PostgreSQL. See [Indicators](docs/indicators.md),
`docs/evidence/api_validation.json`, `coverage.csv` and
`sample_observations.csv` in the same evidence folder.

## Libraries used in this stage

- SQLAlchemy: database connections and session helpers.
- psycopg: PostgreSQL driver.
- python-dotenv: local connection settings from .env.

See [environment details](docs/environment.md) for versions and usage.

SQLAlchemy also defines table mappings and constraints. The optional ReportLab
library generates the ER diagram. Install it with
`python -m pip install -r requirements-design.txt` and run
`python -m scripts.build_design_pack`.

The [database design](docs/architecture.md) explains the keys, metadata and constraints.

The source adapters use requests for HTTP and urllib3 for retries. pytest and Ruff
are used for verification. The topic, source selection and API-specific challenges
are documented with the adapters in [lab notes](docs/lab1.md) and
[challenge notes](docs/challenges.md). The architecture diagram includes clearly
marked planned components; they are not active dependencies.
