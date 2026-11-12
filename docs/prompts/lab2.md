# Lab 2 - AI assistance record

## Prompt 1 - implement Lab 2
- Tool and model: Codex desktop, GPT-6 family; the exact serving variant is not exposed in this session.
- Date: 2026-11-12
- Prompt (exact user text):

> Super, mă bucur că ai înțeles ce avem de făcut. Hai să începem treaba

- Context: the user supplied the Lab 2 PDF and requested careful analysis immediately before this authorization. The preceding exact request was:

> Salut. Mâine fac recuperare. Ar trebui să facem tema necesară. Uite cel mai recent pdf. Analizează-l cu atenție

- Result, extraction/transformation step: added validated WHO, World Bank, OWID and UNICEF downloads, local-file transformations, URL/hash provenance and the Lab 2 catalog. This step is contained in the commit titled `Lab 2: separate raw downloads and local transformations for four sources`.
- Your changes: no manual student code edits have been reported. The assistant selected WHO under-five mortality rather than copying the life-expectancy example, kept UNICEF, retained the documented 2000-2023 / 20-country scope, validated WHO age/wealth dimensions and converted OWID deaths per 100 births to per 1,000 explicitly. These are assistant implementation choices for the student to review, not claimed student edits.

One implementation authorization covers the following incremental commits. Continuation notes identify the files, checks and corrections produced in each step; they are not invented additional user prompts. No code is claimed to have been written independently by the student.

## Prompt 1 continuation - exploratory notebook
- Date: 2026-11-12
- Result: executed `notebooks/lab2_exploration.ipynb`, recorded `docs/evidence/lab2-exploration.json`, and added optional notebook dependencies. Commit: `Lab 2: explore saved source data and report missing-value coverage`.
- Checks and corrections: notebook cells run against verified cached files, with no database access. Distinguish global raw missingness, pilot missingness, absent country-years and WHO dimension exclusions. No additional student edits or additional user prompts were supplied.

## Prompt 1 continuation - cleaning and database migration
- Date: 2026-11-12
- Result: `etl/clean.py`, cleaning profiles/tests, Alembic baseline and revision 0002, model `is_outlier`, and guarded existing-database migration. Commit: `Lab 2: clean observations and migrate retained IQR outlier flags`.
- Checks and corrections: preserve real zero values, reject fractional years before integer conversion, map WHO sex codes, keep exclusive per-rule rejection counts, and retain IQR outliers. Verify an existing Lab 1 schema before stamping it. Test fresh upgrades and a reversible downgrade against a synthetic observation in a rolled-back schema. No manual student edits reported.

## Prompt 1 continuation - PostgreSQL import and idempotency
- Date: 2026-11-12
- Result: shared `etl/load.py`, source import scripts, `scripts/verify_imports.py`, transactional integration test and two-run evidence. Commit: `Lab 2: load source snapshots with transactional idempotent upserts`.
- Checks and corrections: both value and is_outlier are updated on conflict; an indicator and its import_log row commit together; failed indicators roll back and cause a failing exit status. Real source URLs (not local filenames) are written to import_log. rows_loaded means processed upserts, with new/updated counts reported separately. Two real imports preserve 4,309 observations and add 18 logs; isolated tests verify updated flags and rollback of a failed log. No manual student code changes reported.
