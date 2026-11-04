# Task 1.3 - Development environment

Tool versions were verified on 21 October 2026. Dependency scope was reviewed on 5 November.

| Tool | Version | Use |
|---|---|---|
| Python | 3.14.6 | Project code and verification commands |
| Git | 2.51.0.windows.1 | Version control |
| Visual Studio Code | 1.143.0 | Editing, with the Python extension |
| PostgreSQL | 18.6 | Portable local database |
| pgAdmin 4 | 9.18 | Database connection and SQL inspection |

The virtual environment is `.venv`; project-level VS Code settings select `.venv/Scripts/python.exe`.

## Libraries used by each component

| First use | Libraries | Purpose |
|---|---|---|
| Database configuration | SQLAlchemy 2.1.5, psycopg 3.3.6, python-dotenv 1.2.4 | Connection/session helpers, PostgreSQL driver and local connection settings |
| Schema implementation | SQLAlchemy; optional ReportLab | Table mappings, constraints and the SVG entity-relationship diagram |
| API source checks | requests 2.34.2, urllib3; pytest 9.1.1, Ruff 0.17.1 | Downloads, retries, source-contract tests and static checks |
| Final report | Optional ReportLab, pypdf, pypdfium2 | PDF generation, text inspection and visual review |

`requirements.txt` contains the active database, HTTP and test dependencies. `requirements-lock.txt` pins their installed dependency closure for Python 3.14.6 on Windows. Optional diagram/report tools are in `requirements-design.txt`.

The original installed-environment inventory remains in `docs/evidence/environment.json` as historical evidence. Packages appearing in that inventory are not all used by the current code. Web endpoints, a connected UI and ML remain planned components rather than current runtime dependencies.

The PostgreSQL setup and screenshots are documented in [PostgreSQL setup](postgresql.md).
