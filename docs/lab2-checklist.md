# Lab 2 - submission checklist

- [x] Task 2.1: executed notebook with extraction, local transforms, head/info/missingness per indicator: `notebooks/lab2_exploration.ipynb`, `docs/evidence/lab2-exploration.json`.
- [x] Task 2.2: shared cleaning and retained IQR flags, Alembic revision 0002, per-indicator counts: `etl/clean.py`, `migrations/`, `docs/lab2_results.md`.
- [x] Task 2.3: four-source import, two runs, stable observations and populated import_log: `etl/import_*.py`, `docs/evidence/lab2-imports.json`.
- [x] Task 2.4: seven SQL checks with explanations and three official source comparisons: `db/lab2_checks.sql`, `docs/lab2_results.md`, SQL/comparison JSON evidence.
- [x] README and guide cover setup, extraction and imports from scratch; notebook tooling is documented separately.
- [x] Incremental runnable commits use the `Lab 2:` prefix; the completed delivery is published on `main` and the PDF-requested `master` branch.
- [x] Exact user prompts, tool/model disclosure, dates, outputs, commit references and correction notes: `docs/prompts/lab2.md`.
- [x] Required results: `docs/lab2_results.md`.

Verification: 18 tests including two PostgreSQL integration tests; Ruff; pip dependency consistency; Alembic schema check; executed notebook; all seven SQL checks and three independent source-export comparisons. Secrets, local database files and raw downloads are ignored. There is no separate Lab 2 PDF or UI implementation.

For the demonstration, open the repository's results page, the executed notebook and pgAdmin with `db/lab2_checks.sql`. The full reproduction sequence is in `docs/lab2_setup.md`.
