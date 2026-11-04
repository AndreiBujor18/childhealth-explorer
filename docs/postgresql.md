# Task 1.4 - Portable PostgreSQL and pgAdmin

**Status: complete.** Initially verified on 21 October 2026; connection and empty tables rechecked on 4 November.

- Official EDB PostgreSQL 18.6 distribution, Windows x86-64, extracted into `.local/pgsql`.
- Server data: `.local/pgdata`; local address `127.0.0.1:5432`.
- Database `global_health`, UTF8 encoding, owner and user `gh_user`.
- pgAdmin 4 version 9.18, with a separate profile in `.local/pgadmin`.
- Connection verified in the actual pgAdmin interface, with access to the project database.
- `SELECT version();` executed in Query Tool, confirming PostgreSQL 18.6.

## Evidence screenshots

1. `docs/evidence/screenshots/pgadmin-global-health.jpg`: database tree, owner `gh_user` and UTF8 encoding.
2. `docs/evidence/screenshots/pgadmin-select-version.jpg`: `SELECT version();` and its actual Query Tool result.
3. `docs/evidence/screenshots/pgadmin-ready-2026-11-04.jpg`: connection and version query rechecked for the presentation.

These screenshots show the real pgAdmin interface and query results. The latest read-only database check is in `docs/evidence/recheck-2026-11-04.json`.

## Starting a later session

From the project folder in PowerShell:

```powershell
.\scripts\start-postgres.ps1
.\scripts\start-pgadmin.ps1
```

Open `http://127.0.0.1:5051/` in a browser. pgAdmin is installed locally in the portable distribution; the browser displays its local interface. To stop PostgreSQL, run `.\scripts\stop-postgres.ps1`.

Local passwords are stored in `.env` and `.local/`, both excluded from Git. They are not included in the screenshots or submission documents.

Initial setup through `scripts/setup_pgadmin.py` configures PostgreSQL library paths, initializes the pgAdmin configuration database and imports the server definition. These steps do not need to be repeated at every startup.
