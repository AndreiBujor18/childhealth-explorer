# Lab 1 compliance checklist

Initial audit: 3 November 2026; completed with browser confirmation on 4 November. All 15 lab pages, local code and evidence, report pages and quality checks were reviewed. **All eight items in section 1.10 are complete. The author submitted the report and repository link on 4 November.**

Requirements source: `Lab 1 - CSP in Global Health (1).pdf`, Tasks 1.2-1.9 and section 1.10 on page 15. Official project title: **Childhood Vaccination, Socioeconomic Conditions, and Under-Five Mortality**.

## Required lab tasks

- [x] **1.2 - Topic proposal** (lab pp. 1-2): research question, relevance, at least two public sources, intended users and an ML idea, scoped for an individual semester project. Evidence: `docs/lab1.md`, section 1.2; report p. 1. Sources: UNICEF and World Bank; planned ML: linear regression compared with random forest regression for under-five mortality.
- [x] **1.3 - Development environment and versions** (lab pp. 2-3): Python, VS Code and extensions, Git/GitHub account, PostgreSQL, pgAdmin, virtual environment and Task 1.9 dependencies. Verified: Python 3.14.6, Git 2.51.0.windows.1, psql 18.6; `pip check` found no conflicts. Evidence: `docs/environment.md`, `docs/evidence/environment.json`, `requirements.txt`, `requirements-lock.txt`, `.vscode/settings.json`. Docker and Postman/Bruno are optional.
- [x] **1.4 - Portable PostgreSQL and pgAdmin** (lab pp. 3-6): official EDB ZIP, configured instance, `gh_user`, `global_health` and a working pgAdmin connection. Required screenshots: `docs/evidence/screenshots/pgadmin-select-version.jpg` and `pgadmin-global-health.jpg`. Documentation: `docs/postgresql.md`. On 4 November, the connection and five empty tables were rechecked and `SELECT version()` was run in pgAdmin. Evidence: `docs/evidence/recheck-2026-11-04.json` and its screenshot. Keep the server running for a live demonstration.
- [x] **1.5 - At least two topic-specific challenges with solutions** (lab pp. 6-7): different definitions/reference populations and confounding in the vaccination-mortality relationship. Evidence: `docs/challenges.md`, the extended table in `docs/lab1.md`, report p. 2.
- [x] **1.6 - Adapted architecture and project structure** (lab pp. 7-8): UNICEF/World Bank -> Python import -> PostgreSQL -> FastAPI and analysis/ML -> interface. The database separation and import pipeline's exclusive responsibility for external requests and observation writes are explained. Evidence: `docs/architecture.md`, `docs/diagrams/application-architecture.svg`, project folders and report p. 2. Future components are identified.
- [x] **1.7 - Indicators, codes, sources, units and browser checks** (lab pp. 8-10): catalog, live validation and browser confirmation complete. All seven Romania URLs returned HTTP 200 and 24 annual records each on 3 November. JSON structures, country, years, codes, missing values and numeric limits were validated. The author opened all seven in Chrome on 4 November and supplied seven screenshots, each showing the corresponding JSON response. Evidence: `docs/evidence/url-check-2026-11-03.json`, `browser-url-check-2026-11-04.json`, `docs/evidence/screenshots/api-browser-2026-11-04/`. The 21 October pilot snapshot is preserved; the earlier integrated-browser block is historical evidence.
- [x] **1.8 - Project schema and justified changes** (lab pp. 10-12): five tables, relationships, keys, index and documented changes: source-specific code uniqueness, `concept_code`, `age_group`, field lengths and constraints. Evidence: `db/schema.sql`, `docs/architecture.md`, `docs/diagrams/database-erd.svg`, report p. 4.
- [x] **1.9 - Table implementation and schema export** (lab pp. 12-15): SQLAlchemy models, table creation, `pg_dump --schema-only` export and comparison with the design. Evidence: `app/database.py`, `app/models.py`, `app/create_tables.py`, `db/schema_dump.sql`, `docs/evidence/database_verification.json`. The five empty tables were reconfirmed in a read-only check on 4 November: `docs/evidence/recheck-2026-11-04.json`.

## Deliverables - section 1.10, page 15

- [x] **Short report:** `output/pdf/Lab-1-Report-ChildHealth-Explorer.pdf`, exactly 4 pages, with English text and diagrams. Covers the topic, environment, PostgreSQL, challenges, architecture, indicators and database implementation; includes an actual pgAdmin screenshot. UI implementation is reserved for Lab 3.
- [x] **Final report reviewed:** GitHub link, live checks and 4 November browser confirmation included. All four pages were visually reviewed and English wording checked.
- [x] **Public repository:** [AndreiBujor18/childhealth-explorer](https://github.com/AndreiBujor18/childhealth-explorer), branch `main`, local remote `origin`. Unauthenticated access was verified. Evidence: `docs/evidence/screenshots/github-publication.jpg`. Local passwords are excluded from commits.
- [x] **Submitted:** the author supplied a Google Classroom screenshot showing **Project Phase 1** as submitted, with the final PDF and GitHub link attached, on 4 November 2026. See `docs/submission-lab1.md`.

## Additional checks

- [x] Nine Python tests passed at the pre-submission audit.
- [x] Ruff reported no issues in `app`, `etl`, `scripts` and `tests`.
- [x] `pip check` reported no dependency conflicts.
- [x] `.env`, `.venv/`, `.local/` and `data/raw/` are ignored by Git.
- [x] Common adapter contract and registry support a third source; a test adapter demonstrates the extension point. Lab 1 requires at least two sources, not a third live integration.

## Presentation and later stages

For a live demonstration, start PostgreSQL and pgAdmin. The connection and five empty tables were rechecked on 4 November. The portable server does not need to run continuously.

Full PostgreSQL loading, FastAPI endpoints, connected Jinja2 pages, Plotly charts and evaluated ML models belong to later stages. The lab explicitly requires the five tables to remain empty at the end of Lab 1. The earlier UI prototype is preserved on `codex/lab3-ui-prototype`; UI implementation is reserved for Lab 3. Online application hosting is not a Lab 1 deliverable.

Adaptations to the examples are documented: UNICEF and World Bank are the selected sources; PostgreSQL uses quoted project-local paths; adapters share a Python observation contract; the planned final UI will use Jinja2/Plotly.
