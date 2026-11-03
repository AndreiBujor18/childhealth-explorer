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
