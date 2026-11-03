# Lab 1 - ChildHealth Explorer

## 1.2 Topic proposal

**ChildHealth Explorer** examines the association between vaccination, economic resources, access to basic services and under-five mortality using annual country-level data from 2000 to 2023. The research question is: **how are childhood vaccination, socioeconomic conditions and access to basic services associated with under-five mortality across countries and over time?** The topic relates to SDG 3, particularly child health, and is scoped for an individual semester project. It uses the UNICEF SDMX API for vaccination and the World Bank Indicators API for mortality, GDP, health expenditure, water and sanitation. Intended users are students, public health analysts and NGOs. The proposed ML task compares linear regression and random forest regression to estimate mortality from the available indicators. The interface will combine filters, country comparisons, charts and model results.

**Limitations:** this is an ecological analysis of public aggregates, with no individual records. Estimates based on indicators from the same year will be interpreted as associations; they do not establish causation or constitute forecasts for future years. The project does not provide clinical recommendations.

## 1.3 Development environment

Python 3.14.6, Git, VS Code, portable PostgreSQL 18.6 and pgAdmin 4 from the same official ZIP archive. Measured versions are recorded in `docs/evidence/environment.json`; active database, HTTP and test dependencies are pinned in `requirements-lock.txt`.

The virtual environment is `.venv`. The current code uses SQLAlchemy, psycopg and python-dotenv for PostgreSQL, requests/urllib3 for API downloads and retries, and pytest/Ruff for verification. ReportLab and PDF inspection tools are optional authoring dependencies. The web API, connected UI and ML shown in the architecture are plans; their frameworks are not active runtime dependencies. Docker is optional and was not required.

## 1.4 PostgreSQL and pgAdmin

The official EDB Windows x86-64 PostgreSQL 18.6 ZIP was extracted into `.local/pgsql`. Server data is in `.local/pgdata`, with a separate pgAdmin profile in `.local/pgadmin`. Project-local paths replace the lab's example `C:\pgsql`; paths are quoted explicitly. No Windows service was registered.

The `gh_user` role and `global_health` database use UTF-8 and SCRAM authentication. The server listens only on `127.0.0.1:5432`. Randomly generated local passwords and server files are excluded from Git. `scripts/start-postgres.ps1` and `scripts/stop-postgres.ps1` control the instance. The connection and `SELECT version()` are documented in `docs/evidence/database_verification.json`, actual pgAdmin screenshots and `docs/evidence/recheck-2026-11-04.json`.

## 1.5 Challenges and solutions

| Challenge | Proposed solution |
|---|---|
| Different API codes and response structures | Use ISO3 identifiers, one adapter per source and a verified common contract. |
| Regional aggregates mixed with countries | Use the World Bank country catalog and exclude aggregate rows. |
| Missing values and gaps in annual series | Preserve `NULL`, measure coverage and consider imputation only during ML development. |
| API changes or retirement | Cache raw responses with URL, timestamp and SHA-256; keep modules independent and allow a later CSV adapter. |
| **Different vaccination ages and definitions** | Keep DTP3 and first-dose measles coverage separate; preserve age/definition metadata without assuming a common denominator. |
| **Multiple factors associated with under-five mortality** | Include GDP, health expenditure, water and sanitation; interpret associations and discuss unmeasured factors. |
| **The same estimates redistributed by several APIs** | Attribute sources and select a primary series per concept, without duplicating observations in training. |
| **Information leakage across years in ML** | Planned temporal split: training 2000-2017, validation 2018-2020, testing 2021-2023. Fit transformations on training data only; add separate country-based validation to assess geographic generalization. |

## 1.6 Architecture

See [Architecture and data model](architecture.md): external sources -> adapters and import pipeline -> PostgreSQL -> FastAPI and analysis/ML -> web interface. Separating the database from external sources supports fast browsing, reuse of a consistent data version and independence from API outages. Project folders follow these components.

A new API implements `SourceAdapter.fetch`, is registered in `etl/registry.py` and receives entries in the indicator catalog. Validation and coverage checks are reused. The third-source test exercises this contract with a test adapter; a third live source remains a future extension.

## 1.7 Sources and indicators

| Source | Code | Indicator | Unit | Role |
|---|---|---|---|---|
| UNICEF | IM_DTP3 | DTP3 vaccination coverage | % | Feature |
| UNICEF | IM_MCV1 | First-dose measles vaccination coverage | % | Feature |
| World Bank | SH.DYN.MORT | Under-five mortality | per 1,000 live births | ML target |
| World Bank | NY.GDP.PCAP.PP.KD | GDP per capita, PPP | constant 2021 international $ | Feature |
| World Bank | SH.XPD.CHEX.GD.ZS | Current health expenditure | % of GDP | Feature |
| World Bank | SH.H2O.BASW.ZS | At least basic drinking water services | % of population | Feature |
| World Bank | SH.STA.BASS.ZS | At least basic sanitation services | % of population | Feature |

The pilot covers Romania, Bulgaria, Germany, France, Poland, Spain, the United Kingdom, Sweden, the United States, Canada, Brazil, Mexico, India, Indonesia, South Africa, Kenya, Nigeria, Egypt, Australia and Japan. It uses 2000-2023 and both sexes combined where applicable. The sample establishes feasibility; it is not a statistically representative sample of the world.

The 21 October 2026 check found 480/480 non-null values for the first five indicators, 470/480 for water and 479/480 for sanitation. **469/480 country-year combinations are complete.** Extending to more countries will require the same checks. Each request records its timestamp, URL and response hash. `docs/evidence/api_validation.json` contains the full URLs; `coverage.csv` summarizes coverage and `sample_observations.csv` contains real normalized observations.

The [indicator catalog](indicators.md) lists reproducible Romania URLs. API checks save evidence files and leave PostgreSQL empty.

## 1.8 Database schema

Five tables: `source`, `country`, `indicator`, `observation`, `import_log`. See `db/schema.sql` and the ER diagram in [Architecture](architecture.md). Changes include source-specific code uniqueness, `concept_code`, indicator-level age metadata, longer fields and year/sex/value constraints. Indicators and APIs share the same tables. Missing values remain `NULL`.

## 1.9 Implementation and verification

SQLAlchemy models in `app/models.py` are instantiated by `python -m app.create_tables`. `python -m scripts.verify_database` checks the version and row counts, executes the reference design in a temporary transactional schema, compares columns, keys, constraints and indexes, rolls back the comparison and exports `db/schema_dump.sql` using `pg_dump --schema-only`.

Verified result: all five tables exist and are empty; the SQLAlchemy schema matches the SQL design. API verification has not populated the database. Tests cover SDMX decoding, World Bank pagination, missing values, duplicates, numeric limits and an additional adapter.

## Lab 1 scope

Source adapters, validation and the empty database are implemented. Production
loading, the connected application and trained models remain later work.
