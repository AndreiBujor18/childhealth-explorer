# Lab 1 submission

Updated on 4 November 2026. Official topic: **Childhood Vaccination, Socioeconomic Conditions, and Under-Five Mortality**.

## Submitted deliverables

The author submitted both items in Google Classroom, under **Project Phase 1**, on **4 November 2026**. The screenshot supplied by the author shows the submitted status, with the PDF and GitHub link attached.

- Public repository: [AndreiBujor18/childhealth-explorer](https://github.com/AndreiBujor18/childhealth-explorer).
- [Lab-1-Report-ChildHealth-Explorer.pdf](https://github.com/AndreiBujor18/childhealth-explorer/blob/main/output/pdf/Lab-1-Report-ChildHealth-Explorer.pdf): 4 pages in English, also available locally in `output/pdf/`.
- Repository branch: `main`; local remote: `origin`. Public access was verified without authentication.

## Supporting materials

- Code, documentation, diagrams, SQL design and schema export.
- Actual pgAdmin screenshots showing PostgreSQL and the `global_health` database.
- Nine passing Python tests, Ruff checks and a dependency check with no conflicts at the pre-submission audit.

## API verification

On 3 November, all seven Romania URLs returned HTTP 200 and 24 annual records each. JSON structures, indicator codes, years and numeric limits were validated; the missing sanitation value was preserved. Evidence: `docs/evidence/url-check-2026-11-03.json`.

On 4 November, the author opened all seven URLs in Chrome and supplied screenshots of the JSON responses. All seven screenshots were reviewed. Task 1.7 and all eight Lab 1 checklist items are complete. Evidence: `docs/evidence/browser-url-check-2026-11-04.json` and `docs/evidence/screenshots/api-browser-2026-11-04/`. The earlier integrated-browser failure remains in the historical evidence.

## Database demonstration

Run from the repository root in PowerShell:

```powershell
.\scripts\start-postgres.ps1
.\scripts\start-pgadmin.ps1
```

Open `http://127.0.0.1:5051/`. The database is `global_health`; the user is `gh_user`. Stop PostgreSQL afterwards with:

```powershell
.\scripts\stop-postgres.ps1
```

Keep the five tables empty for Lab 1. Full loading, FastAPI/Jinja2/Plotly and ML belong to later stages.

The earlier UI prototype is preserved on [`codex/lab3-ui-prototype`](https://github.com/AndreiBujor18/childhealth-explorer/tree/codex/lab3-ui-prototype) for future Lab 3 design review. It is outside the current `main` branch.
