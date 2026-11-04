# ChildHealth Explorer

**Childhood Vaccination, Socioeconomic Conditions, and Under-Five Mortality** is an individual global health project. This repository contains the deliverables for **Lab 1 - Topic, Environment and Architecture**.

## Research question

How are vaccination coverage, economic resources and access to basic services associated with under-five mortality across countries from 2000 to 2023?

The planned application will help students, public health analysts and NGOs compare countries, explore trends and estimate under-five mortality. It uses public country-level aggregates, with no individual medical records. Results will describe associations rather than causal effects.

## Completed in Lab 1

- Topic proposal, intended users and a machine learning plan.
- A local Python environment and portable PostgreSQL from the official EDB ZIP archive.
- A five-layer architecture and a database schema with five tables.
- Working API adapters for UNICEF and the World Bank.
- Validation of seven indicators across 20 countries, 2000-2023.
- Complete data for 469 of 480 country-year combinations; raw responses cached locally.
- Five empty PostgreSQL tables, a schema export and an automated comparison with the SQL design.
- Browser verification of all seven indicator URLs on 4 November 2026.

Production data loading, application endpoints, a connected interface and model training are planned for later stages. API verification saves evidence files without populating the database.

## Deliverables

| Requirement | Files / evidence |
|---|---|
| 1.2 Topic proposal | [Lab notes](docs/lab1.md), section 1.2 |
| 1.3 Environment and versions | [Environment](docs/environment.md), `requirements-lock.txt` |
| 1.4 PostgreSQL and pgAdmin | [Database setup](docs/postgresql.md), `docs/evidence/screenshots/` |
| 1.5 Challenges and solutions | [Topic-specific challenges](docs/challenges.md) |
| 1.6 Architecture and project structure | [Architecture](docs/architecture.md), `docs/diagrams/` |
| 1.7 Indicators and API verification | [Indicator catalog](docs/indicators.md), `config/indicators.json`, `docs/evidence/` |
| 1.8 Database design | `db/schema.sql`, `app/models.py`, [schema explanation](docs/architecture.md) |
| 1.9 Tables and schema export | `db/schema_dump.sql`, `docs/evidence/database_verification.json` |
| Short report | [Lab-1-Report-ChildHealth-Explorer.pdf](output/pdf/Lab-1-Report-ChildHealth-Explorer.pdf), 4 pages |

All eight Lab 1 checklist items are complete. The author submitted the PDF and repository link in Google Classroom on **4 November 2026**. See the [checklist](docs/lab1-checklist.md) and [submission record](docs/submission-lab1.md).

UI implementation is reserved for Lab 3. The earlier design prototype is preserved separately on [`codex/lab3-ui-prototype`](https://github.com/AndreiBujor18/childhealth-explorer/tree/codex/lab3-ui-prototype). The `main` branch contains the Lab 1 database, API feasibility checks and required design documentation. Lab 2 implementation has not started.

## Local setup (Windows / PowerShell)

Run these commands from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Use `requirements-lock.txt` to reproduce the active database, source-check and test dependencies verified with Python 3.14.6. `requirements.txt` provides version ranges for Python 3.12+. Optional diagram/report tools are listed separately in `requirements-design.txt`. Planned web and ML frameworks are not runtime dependencies at this stage.

Download the **Windows x86-64 ZIP** from the [official EDB page](https://www.enterprisedb.com/download-postgresql-binaries) and extract the `pgsql` folder into `.local/pgsql`. Then run:

```powershell
.\.venv\Scripts\python.exe -m scripts.setup_postgres
.\.venv\Scripts\python.exe -m app.create_tables
.\.venv\Scripts\python.exe -m scripts.verify_database
.\.venv\Scripts\python.exe -m scripts.setup_pgadmin
.\scripts\start-pgadmin.ps1
```

Open `http://127.0.0.1:5051/` for pgAdmin. It uses a separate local profile with the project server already registered. The database is `global_health` and the user is `gh_user`. Randomly generated credentials are stored only in `.env`; the administrator password is in `.local/postgres-admin-password.txt`. These files are excluded from Git.

For later sessions:

```powershell
.\scripts\start-postgres.ps1
.\scripts\start-pgadmin.ps1
```

Keep pgAdmin running during the session. To stop PostgreSQL afterwards, run `.\scripts\stop-postgres.ps1`. Server data is in `.local/pgdata`, separate from the binaries. The server listens only on `127.0.0.1`, using port 5432, or 5433 if 5432 was already occupied during setup. Paths containing spaces are handled explicitly.

If PostgreSQL is already installed, create the project user and database, copy `.env.example` to `.env` and fill in the connection settings. A second server installation is unnecessary.

## Libraries used in the current code

| Component | Libraries and purpose |
|---|---|
| PostgreSQL connection and models | SQLAlchemy for connections/models, psycopg for the PostgreSQL driver, python-dotenv for local connection settings |
| API extraction and validation | requests for HTTP; urllib3 retry support; Python standard-library JSON, CSV and decimal handling |
| Verification | pytest for the source-contract tests; Ruff for static checks |
| Diagram/report authoring | Optional ReportLab for SVG/PDF generation; pypdf and pypdfium2 for PDF inspection |

## Source verification and checks

```powershell
.\.venv\Scripts\python.exe -m etl.verify_sources
.\.venv\Scripts\python.exe -m scripts.check_indicator_urls
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check app etl scripts tests
```

`etl.verify_sources` reuses `data/raw/` after the first download; use `--refresh` to download new responses. `scripts.check_indicator_urls` always checks the seven Romania URLs live while preserving the pilot snapshot. The checks record full URLs, retrieval times and SHA-256 hashes. Pilot verification also saves coverage and normalized observations. Original responses and metadata stay in `data/raw/`, excluded from Git; a small public sample is in `docs/evidence/sample_observations.csv`.

All seven Romania URLs returned HTTP 200 with 24 annual records each on 3 November. Their JSON responses were also opened in Chrome on 4 November. The [indicator catalog](docs/indicators.md) links to the checks and screenshots.

## Adding a third API

1. Implement `fetch(indicator, countries, start, end)` in a new adapter returning `ObservationRecord` objects.
2. Register the adapter in `etl/registry.py`.
3. Add the source, indicators, units and limits to `config/indicators.json`.
4. Verify the contract, original source, dimensions and compatibility of the series.

Validation and coverage checks remain shared. Indicators that fit the existing dimensions do not require a schema change. New dimensions, such as subnational observations or multiple age groups within one series, require a justified model extension. `test_third_source_needs_only_registration_and_contract` demonstrates this extension point with a test adapter; it does not claim a third live integration.

## Sources

- [UNICEF - SDMX API documentation](https://data.unicef.org/sdmx-api-documentation/)
- [UNICEF - immunization and WUENIC metadata](https://data.unicef.org/topic/child-health/immunization/)
- [World Bank - Indicators API documentation](https://datahelpdesk.worldbank.org/knowledgebase/articles/898581-api-basic-call-structures)
- [World Bank - under-five mortality](https://data.worldbank.org/indicator/SH.DYN.MORT)
- [Our World in Data - API for a possible extension](https://docs.owid.io/projects/etl/api/chart-api/)

UNICEF and the World Bank may redistribute the same international estimates. The project uses complementary indicators; republished values are not treated as independent observations. Attribution and reuse conditions must be checked in each indicator's metadata.

## Commit organization

The four Lab 1 commits cover PostgreSQL configuration, schema implementation, API feasibility checks and final verification/submission. Each component introduces its own setup instructions, libraries and design explanation. Report generation and its optional dependencies are documented with the final deliverables. Future bug-fix messages will identify the actual defect and the correction. Verify each task before committing and publishing it.
