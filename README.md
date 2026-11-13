# ChildHealth Explorer

**Childhood Vaccination, Socioeconomic Conditions, and Under-Five Mortality**

An individual global health project studying associations between vaccination coverage, economic resources, basic services and under-five mortality. It uses public country-level aggregates, with no patient records. The approved pilot covers **20 countries, 2000-2023, both sexes**. Associations are not interpreted as causal effects.

**Lab 3 is a working server-rendered application:** browse the PostgreSQL data at **http://127.0.0.1:8000/**, filter observations and run the pipeline from HTML forms. All pages are built on the server, with no browser JavaScript. The direction is **presentation -> service -> data access**: only repositories query/write data; controllers only parse HTTP input, call services and render templates.

The approved 20-country, 2000-2023 dataset contains **4,309 observations and 335 retained IQR outlier flags**. The Lab 2 verification snapshot contains 18 import logs; two additional browser imports in Lab 3 increased the current log count to 36 without adding duplicate observations.

## Run the application

After the database setup below, start PostgreSQL and the application from the repository root:

```powershell
.\scripts\start-postgres.ps1
.\scripts\start-web.ps1
```

Or run `.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload`. Open **http://127.0.0.1:8000/**. Keep the server terminal running.

| Layer / responsibility | Implementation |
|---|---|
| Presentation: parse requests and render HTML | `app/controllers/`, `app/templates/`, `app/views.py` |
| Services: pagination, validation and job orchestration | `app/services/` |
| DAL: parameterized reads and writes, injected sessions | `app/repositories/` |
| Shared immutable values | `app/domain.py`, `etl/step_result.py` |
| Dependency wiring / application entry | `app/dependencies.py`, `app/main.py` |
| Pipeline transaction owner | `etl/import_runner.py`; repositories never commit |

[Lab 3 results](docs/lab3_results.md) contain the three required screenshots, the request call chain, the region demonstration, sex-filter tests and the architecture-test failure demonstration. See the [checklist](docs/lab3-checklist.md), [layer guide](docs/lab3_layers.md) and [prompts](docs/prompts/lab3.md).

Useful URLs: [Romania 2023](http://127.0.0.1:8000/?country=ROU&year_from=2023&year_to=2023), [Sub-Saharan Africa](http://127.0.0.1:8000/?region=Sub-Saharan+Africa). `GET /actions/extract` and `GET /actions/load` return 405: only the explicit POST buttons run these actions. The sex filter supports BTSX/MLE/FMLE; live male/female filters are empty because the pilot uses BTSX totals. The required one-male-row test runs against an isolated synthetic fixture, never fabricated production data.

## Lab 2 deliverables



| Requirement | Deliverable |
|---|---|
| Extraction and saved-file transformation | `etl/extract_*.py`, `etl/transform_*.py`, `config/lab2_indicators.json` |
| Task 2.1: exploration and missingness | [Executed notebook](notebooks/lab2_exploration.ipynb), [evidence](docs/evidence/lab2-exploration.json) |
| Task 2.2: cleaning, retained IQR flags and migration | `etl/clean.py`, `migrations/`, [counts and explanations](docs/lab2_results.md) |
| Task 2.3: two idempotent imports | `etl/load.py`, `etl/import_*.py`, [two-run evidence](docs/evidence/lab2-imports.json) |
| Task 2.4: seven SQL checks and three source comparisons | [Queries](db/lab2_checks.sql), [results](docs/lab2_results.md) |
| Reproduction | This README and the [detailed guide](docs/lab2_setup.md) |
| AI assistance and delivery review | [Prompts and commit trace](docs/prompts/lab2.md), [checklist](docs/lab2-checklist.md) |

Lab 2 is preserved on [`master`](https://github.com/AndreiBujor18/childhealth-explorer/tree/master) at its submitted version. **Lab 3 is delivered on `main`**, as its PDF requires. The earlier [`codex/lab3-ui-prototype`](https://github.com/AndreiBujor18/childhealth-explorer/tree/codex/lab3-ui-prototype) branch is a historical design reference; the connected application is now on `main`. Neither lab needs a separate PDF report. ML training is a later stage.

## Setup from scratch (Windows / PowerShell)

Install Python 3.12+ and Git, then run:

```powershell
git clone https://github.com/AndreiBujor18/childhealth-explorer.git
cd childhealth-explorer
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`requirements.txt` gives dependency ranges; `requirements-lock.txt` pins the active ETL/database/test environment verified with Python 3.14.6 on Windows. Notebook tools are optional in `requirements-notebook.txt`; historical diagram/report tools are in `requirements-design.txt`.

For a new local PostgreSQL installation, download the **Windows x86-64 ZIP** from the [official EDB page](https://www.enterprisedb.com/download-postgresql-binaries), extract `pgsql` into `.local/pgsql`, then run:

```powershell
.\.venv\Scripts\python.exe -m scripts.setup_postgres
.\.venv\Scripts\python.exe -m scripts.migrate_database
.\.venv\Scripts\python.exe -m alembic check
```

If PostgreSQL is already installed, create a project user/database, copy `.env.example` to `.env`, set `DATABASE_URL`, and run the migration instead. Existing Lab 1 databases are verified before stamping the baseline and adding `is_outlier`; existing observations are preserved.

The portable setup uses `global_health`, user `gh_user`, localhost port 5432 (or 5433 if 5432 was occupied during setup). Random credentials are kept in `.env`; the administrator password is in `.local/postgres-admin-password.txt`. Both are ignored. Data is in `.local/pgdata`, separate from the binaries. For later sessions, start PostgreSQL with `.\scripts\start-postgres.ps1`.

To use pgAdmin with the portable installation:

```powershell
.\.venv\Scripts\python.exe -m scripts.setup_pgadmin
.\scripts\start-pgadmin.ps1
```

Open `http://127.0.0.1:5051/`; the server is registered in a separate local profile. Keep pgAdmin running during the session. See [database setup](docs/postgresql.md) for details. Stop PostgreSQL afterwards with `.\scripts\stop-postgres.ps1`.

## Extract and explore

```powershell
.\.venv\Scripts\python.exe -m etl.extract
```

Validated snapshots and URL/hash metadata are saved under `data/raw/<source>/`, outside Git. Existing snapshots are reused; add `--refresh` to deliberately replace them. Transformations read local files without API calls. Downloads validate response shapes, follow pagination and fail on HTTP errors. The [guide](docs/lab2_setup.md) explains provider-specific filters and units.

The committed notebook includes real outputs. To rerun it interactively:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-notebook.txt
.\.venv\Scripts\python.exe -m ipykernel install --prefix .venv --name childhealth --display-name "Python (ChildHealth Explorer)"
.\.venv\Scripts\python.exe -m jupyter lab
```

Open `notebooks/lab2_exploration.ipynb` and select the ChildHealth kernel. It displays head/info/missingness for all nine series, distinguishing missing measurements from absent country-year combinations.

## Clean, import and verify

With PostgreSQL running and migrations applied:

```powershell
.\.venv\Scripts\python.exe -m scripts.profile_cleaning
.\.venv\Scripts\python.exe -m scripts.verify_imports
.\.venv\Scripts\python.exe -m scripts.check_lab2_data
.\.venv\Scripts\python.exe -m scripts.compare_lab2_sources
```

`verify_imports` intentionally loads the snapshots twice and records the result in `docs/evidence/lab2-imports.json`. For a normal single import, use `python -m etl.import_all` in the project environment. Individual commands are `etl.import_worldbank`, `etl.import_who`, `etl.import_owid` and `etl.import_unicef`; World Bank must run first to populate the country catalog.

Each indicator reports normalized input, clean, rejected, loaded, new and updated rows. Rule logs explain exclusions. Most exclusions select the study's countries/years; IQR outliers are retained. `rows_loaded` counts processed upserts, so a repeated import reports updates and zero new rows. An indicator's data and success log commit together or both roll back. Further runs add logs while preserving observations for unchanged snapshots.

The historical Lab 2 SQL checker is read-only and executes [lab2_checks.sql](db/lab2_checks.sql), which can also be opened in pgAdmin. Re-running verification updates its evidence files and import logs. The source comparison needs internet access and retrieves fresh official API/CSV exports for Romania, 2023. [Results](docs/lab2_results.md) explain every check, coverage gap, outlier count and source comparison.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp=tmp/pytest
.\.venv\Scripts\python.exe -m ruff check app etl scripts tests migrations
```

To include the two PostgreSQL integration tests (isolated schemas, test changes rolled back):

```powershell
$env:LAB2_TEST_DATABASE='1'
.\.venv\Scripts\python.exe -m pytest -q --basetemp=tmp/pytest-integration
Remove-Item Env:LAB2_TEST_DATABASE
```

## Sources and interpretation

The mandatory providers are **WHO, World Bank and Our World in Data**. UNICEF is retained for vaccination coverage. WHO/OWID mortality series supplement the World Bank target for comparison; providers can redistribute the same UN IGME estimates, so these are not independent extra training observations.

- [WHO GHO OData](https://www.who.int/data/gho/info/gho-odata-api): under-five mortality, with age/wealth dimensions checked explicitly.
- [World Bank API](https://datahelpdesk.worldbank.org/knowledgebase/articles/898581-api-basic-call-structures): mortality, GDP PPP, health expenditure, water, sanitation and non-aggregate country metadata.
- [OWID chart API](https://docs.owid.io/projects/etl/api/chart-api/): mortality CSV and unit metadata; deaths per 100 births are multiplied by 10 to match per 1,000 births.
- [UNICEF SDMX](https://data.unicef.org/sdmx-api-documentation/): DTP3 and first-dose measles coverage.

Definitions, attribution, provider terms, processing and retrieval dates are recorded in the guide/snapshots. Missing values are not converted to zero. Pilot IQR flags do not establish clinical abnormality or causality.

## Libraries and commits

FastAPI handles routes and dependency injection, Uvicorn serves the app, Jinja2 renders HTML, and httpx2 supports presentation tests. SQLAlchemy defines models and upserts; psycopg connects to PostgreSQL; python-dotenv loads local settings. Requests/urllib3 handle HTTP and retries. Pandas/NumPy transform and clean tables; Alembic manages migrations. Pytest/Ruff verify the implementation. Jupyter is optional for exploration; ReportLab/PDF tools remain optional Lab 1 authoring dependencies.

The four Lab 1 and five Lab 2 commits are preserved. Lab 3 uses separate commits for DAL, service, presentation, pipeline actions, sex filtering and verification. Two specific fixes identify their actual defects: trailing spaces in region metadata and unreadable import counts on narrow screens. Each implementation step includes its documentation and prompt trace. `.env`, `.local/` and `data/raw/` remain outside Git.

## Historical Lab 1

The [checklist](docs/lab1-checklist.md), [report](output/pdf/Lab-1-Report-ChildHealth-Explorer.pdf), [architecture](docs/architecture.md), [indicator catalog](docs/indicators.md) and [submission record](docs/submission-lab1.md) document the original stage. Its five tables were empty at submission; that schema dump and evidence remain historical snapshots. Current schema changes are in the migration chain; current data checks are the Lab 2 commands above.
