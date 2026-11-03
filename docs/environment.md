# Development environment used by the current components

| Tool | Version | Role |
|---|---|---|
| Python | 3.14.6 | Project commands and database setup |
| Git | 2.51.0.windows.1 | Version control |
| VS Code | 1.143.0 | Editing with the Python extension |
| PostgreSQL | 18.6 | Portable database server |
| pgAdmin 4 | 9.18 | Local connection and SQL inspection |

The virtual environment is `.venv`, selected in the project VS Code settings.

| Library | Version | First use |
|---|---|---|
| SQLAlchemy | 2.1.5 | Connections and session helpers in app/database.py |
| psycopg | 3.3.6 | PostgreSQL driver selected by the connection URL |
| python-dotenv | 1.2.4 | Read local database settings from .env |

`requirements.txt` declares these database dependencies; `requirements-lock.txt`
pins their installed dependency closure. Versions are recorded in
`docs/evidence/environment.json`. See the [setup instructions](../README.md).

## Schema and ER diagram

SQLAlchemy also defines the five table mappings and constraints in app/models.py.
ReportLab generates the SVG database diagram through scripts/build_design_pack.py.
Install the optional diagram tool with `python -m pip install -r requirements-design.txt`,
then run `python -m scripts.build_design_pack`.

## API checks and tests

requests 2.34.2 retrieves API responses; urllib3 provides retry support.
pytest 9.1.1 runs the source-contract tests, and Ruff 0.17.1 checks the Python code.
These packages and their dependencies are added to requirements.txt and its lock
when the source adapters and tests are introduced. ReportLab now generates both
the database and application architecture diagrams. No connected web interface
or model training is implemented.
