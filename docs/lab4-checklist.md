# Lab 4 - delivery checklist

- [x] Existing Lab 3 SSR observation page, filters, pagination and POST actions preserved.
- [x] JSON routes for regions, region-filtered countries, indicators and per-period averages.
- [x] Pydantic DTOs distinct from immutable domain records and SQLAlchemy models.
- [x] API-only OpenAPI at `/api/openapi.json` and interactive docs at `/api/docs`.
- [x] Same presentation -> service -> DAL direction, with constructor/dependency injection.
- [x] PostgreSQL period buckets and AVG; BTSX only, half-up rounding, aligned null gaps.
- [x] API limit of 20 unique countries; UI limit of 8; validated years/periods and JSON 404/422.
- [x] `/period-averages` serves a shell without any database/service dependency.
- [x] Four JavaScript modules separate network, model, view and controller.
- [x] Real table and Chart.js lines update without page reload; source-specific series remain separate.
- [x] Stable country colors, missing-data gaps, loading/error/empty states and stale-request cancellation.
- [x] API labels use textContent; keyboard checkbox focus survives redraw.
- [x] 59 Python tests, 10 JavaScript tests and 19 live HTTP checks pass.
- [x] Browser comparisons and Swagger execution captured in `docs/img/`.
- [x] Independent SQL check matches the API; 4,309 observations and 335 flags preserved.
- [x] English README/results/prompts, incremental `Lab 4:` commits, delivery on main.
- [x] No `.env`, downloaded raw data, local PostgreSQL files or separate report PDF committed.

Scope approved by the student: ignore the PDF's references to Tasks 4.1, 4.2 and
4.4 because their statements are absent. Adapt the life-expectancy example to
existing childhood vaccination, socioeconomic and under-five mortality indicators.
No sex-choice extension or individual-indicator endpoint is inferred from sample
commit messages.
