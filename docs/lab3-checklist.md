# Lab 3 - delivery checklist

- [x] PostgreSQL observations displayed by a real server-rendered FastAPI/Jinja page.
- [x] Presentation -> service -> DAL; constructors/dependency injection supply repositories and sessions.
- [x] Controllers/templates contain no queries, sessions, ORM objects or direct repository calls.
- [x] Stable parameterized filtering and pagination; countries, indicators, region, source, years and sex.
- [x] Extract and Transform & load POST actions call shared typed pipeline jobs; CLI remains usable.
- [x] Task 3.1: two filtered screenshots and one real action result in `docs/img/`, with URL and call-chain explanation in `docs/lab3_results.md`.
- [x] Task 3.2: region traced through every layer; exact Sub-Saharan Africa URL tested across two pages.
- [x] Task 3.3: sex criterion/predicate/parser/select and tests at repository, service and presentation levels; synthetic vs live results clearly distinguished.
- [x] Task 3.4: AST architecture rules and a captured intentional failure, followed by restored passing code.
- [x] Layer-specific tests, test data isolated from project observations, and dependency-overridden presentation safety guards.
- [x] English README/setup/results, exact AI prompt record and incremental `Lab 3:` commits on main.
- [x] Private connection settings and raw files remain ignored; no separate PDF or fabricated production observations.

Demonstration: open http://127.0.0.1:8000/?country=ROU&year_from=2023&year_to=2023, show the three layer folders and their commits, then demonstrate region pagination. The existing BTSX-only pilot explains why a live male/female filter is empty.
