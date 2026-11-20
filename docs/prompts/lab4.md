# Lab 4 - AI assistance record

## Prompt 1 - analyse the new laboratory
- Tool and model: Codex desktop, GPT-6 family; the exact serving variant is not exposed in this session.
- Date: 2026-11-20
- Prompt (exact user text):

> Salut, s-a terminat laboratorul. Nu a trebuit să prezint nimic. Uite noul pdf, analizează-l cu atenție

- Context: the attached Lab 4 PDF has 15 pages. It references Tasks 4.1, 4.2 and 4.4 without including their statements. Its life-expectancy example is outside this project's approved topic.
- Result: read-only review and comparison with Lab 3; no application code changed.
- Your changes: no manual student code changes reported.

## Prompt 2 - implementation scope
- Tool and model: same Codex session as Prompt 1.
- Date: 2026-11-20
- Prompt (exact user text):

> Ignoră acele 3 task-uri, dacă nu au enunțuri. Sigur, noi nu avem speranță de viață, așa că vom adapta cerința la ce avem noi. Succes

- Scope: implement the stated API, period averages, layered JavaScript page, tests and delivery documents. Use existing vaccination, socioeconomic and mortality series; do not add life expectancy or infer unstated tasks (sex choice or an individual-indicator route) from sample commit messages.
- First result: lookup DTOs/routes, region-aware country lookups, API-only OpenAPI paths and tests. Commit: `Lab 4: expose region country and indicator lookups through REST`.
- Your changes: the student explicitly excluded the missing tasks and approved topic adaptation. No independently written student code is claimed. Existing SSR labels are preserved while the API returns plain country names. A history bundle was saved before changes.

## Prompt 2 continuation - PostgreSQL period averages and JSON contract
- Date: 2026-11-20
- Result: immutable period/report types, `PeriodAverageRepository`, `PeriodAverageService`, DTO mappings, route and dependency wiring, plus service/repository/API tests. Commit: `Lab 4: compute and expose per-period averages through the existing layers`.
- Checks and corrections: PostgreSQL computes AVG/count over BTSX observations in a bucket subquery. The service rounds half up to two decimals and retains known countries with entirely missing series. Unknown indicators become JSON 404, invalid queries become JSON 422. FastAPI resolves independent dependency factories even for invalid query parameters, so the test checks that the service method is never called, rather than incorrectly requiring its factory not to run. No manual student code edits reported.

## Prompt 2 continuation - client-side filters and request coordination
- Date: 2026-11-20
- Result: database-independent page shell, shared navigation, four JavaScript modules, country selection, API error messages and AbortController/identity guards for stale responses. Commit: `Lab 4: add client-side filters and cancellable API requests`.
- Checks and corrections: defaults use IM_DTP3 and five European study countries. Only api-client.js performs fetch; the model has no DOM. Browser verification loaded all controls and a real report. Six JavaScript tests cover selections, stable colors, encoded URLs and HTTP errors; shell tests forbid database dependencies. Optional Node tests use only built-in modules, with no npm packages or build step. No manual student edits reported.

## Prompt 2 continuation - client-rendered table and Chart.js lines
- Date: 2026-11-20
- Result: accessible table, Chart.js line chart, units, explicit missing-data gaps, adaptive colors and clear/error states. Commit: `Lab 4: render period-average tables and comparison charts in the browser`.
- Checks and corrections: Chart.js 4.4.1 is loaded from the CDN specified by the lab; the table still works if that library is unavailable. No smoothing, fabricated zeroes or chart animation. Ten JavaScript tests include late report and region responses that deliberately ignore cancellation. Real browser checks confirmed European DTP3 and African mortality comparisons, an eight-country maximum, and clearing results for an empty selection. No JavaScript warnings/errors or manual student code edits reported.

## Prompt 2 continuation - keyboard focus and singular labels
- Date: 2026-11-20
- Result: preserve the active country checkbox when its list redraws and use singular labels for one country/period. Commit: `Lab 4: preserve country checkbox focus and singular selection labels`.
- Actual defect: replacing the checkbox list after a selection removed the focused element, interrupting keyboard navigation. The view restores focus to the same ISO3 code without scrolling. Verified in the browser with Space: Romania stayed focused and selection changed from five to four, then back. Ten JavaScript tests still pass. No manual student edits reported.

## Prompt 2 continuation - final verification and delivery
- Date: 2026-11-20
- Result: read-only HTTP audit command, real screenshots, HTTP/database evidence, results/checklist, current README and API response documentation. Commit: `Lab 4: verify API contracts and document browser comparisons`.
- Checks and corrections: 59 Python tests, 10 JavaScript tests and 19 live HTTP checks; an independent SQL AVG/round matches the API. Existing data remains 4,309 observations, 335 outlier flags, 36 logs and zero duplicates. Alembic/pip checks pass. Swagger Try it out returned actual JSON 200. The user's scope exclusions remain explicit. No fresh production import or extraction, no invented task statements, and no manual student code changes reported.
- Delivery: implementation commits 9c9ab42 (lookups), 9edc9e8 (averages backend), 1baebb9 (filters/modules), c4deb34 (table/chart), af7f4a5 (keyboard focus/labels), and the verification commit identified by its full title above. Publish these on main while preserving the Lab 2 master branch.
