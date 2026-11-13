# Lab 3 - layer boundaries

Presentation -> service -> repository -> PostgreSQL. Only repositories contain database queries. HTTP parsing/templates belong to presentation; pagination/validation/orchestration belong to services. Repository constructors receive sessions and never commit. Domain objects are immutable and do not expose ORM rows.

First step: `app/domain.py`, `app/repositories/observation_repository.py`, shared Sex enum, and isolated synthetic PostgreSQL tests. No production data is added by those tests. Each page has a total stable ordering ending in observation_id. Source identity remains visible to avoid treating republished series as independent observations.

The service receives an ObservationReader and page size. It validates year ordering and page numbers, computes offsets/page counts and returns ObservationPage. Fake-repository tests need no database or network.

## Run the observation browser

Install requirements, start PostgreSQL, then run `.\scripts\start-web.ps1` or `.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload`. Open http://127.0.0.1:8000/.

FastAPI and Uvicorn serve the application; Jinja2 builds complete HTML pages on the server. httpx2 supports TestClient, as required by the PDF and the installed Starlette version. Controllers parse form strings, call services and provide template context. app/dependencies.py is the composition root; it alone wires get_db -> repository -> service. No controller imports sessions, models or repositories. No JavaScript runs in the page, and no JSON API/docs endpoints are enabled.

## Browser pipeline actions

`POST /actions/extract` calls EtlService.extract_all. `POST /actions/load` calls EtlService.transform_and_load_all. Jobs are composed from the same nine-indicator catalog; World Bank imports its country catalog first. Both return typed results and render an action table without JavaScript. These synchronous actions can take a minute. Refreshing the POST result can repeat the action; the page states this explicitly.

All SQL writes and country lookups now live in `app/repositories/import_repository.py`; `etl/load.py` is a compatibility export. `etl/import_runner.py` coordinates transform/clean/repository calls and owns commit/rollback. It receives a session factory. Each source exposes import_all() returning StepResult values, while the CLI retains its reports and failing exit status. Dependency wiring supplies the session factory and a shared process lock; services contain no SQL/session creation/HTTP code.

## Sex filtering

The shared criterion uses Sex | None. The HTTP parser accepts BTSX/MLE/FMLE and ignores unknown codes. The repository adds a bound sex predicate; the service provides all three enum choices and forwards the criteria unchanged. Repository, service and presentation tests cover this path. `/?sex=MLE&country=ROU` returns exactly one row in the isolated nine-observation fixture. It returns no live rows because the approved Lab 2 pilot contains only BTSX totals; test data never enters the project database.
