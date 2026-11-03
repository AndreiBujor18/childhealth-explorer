# PostgreSQL schema verification

The project uses portable PostgreSQL 18.6 and pgAdmin 4 version 9.18,
with the database `global_health` owned by `gh_user` and encoded as UTF8.

Five tables are defined in `db/schema.sql` and `app/models.py`:
`source`, `country`, `indicator`, `observation` and `import_log`.

Create them with `python -m app.create_tables`. Run
`python -m scripts.verify_database` to compare the SQLAlchemy schema with
the SQL design and export `db/schema_dump.sql`.

The schema comparison checks columns, primary and foreign keys, unique
constraints, check constraints and indexes. Its temporary schema is
rolled back. The five project tables are empty.

Evidence: `docs/evidence/database_verification.json` and
`docs/evidence/recheck-2026-11-02.json`.

Screenshots:

- `docs/evidence/screenshots/pgadmin-global-health.jpg`: database owner and UTF8 encoding.
- `docs/evidence/screenshots/pgadmin-select-version.jpg`: actual `SELECT version();` result.
