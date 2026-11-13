# Lab 3 - layer boundaries

Presentation -> service -> repository -> PostgreSQL. Only repositories contain database queries. HTTP parsing/templates belong to presentation; pagination/validation/orchestration belong to services. Repository constructors receive sessions and never commit. Domain objects are immutable and do not expose ORM rows.

First step: `app/domain.py`, `app/repositories/observation_repository.py`, shared Sex enum, and isolated synthetic PostgreSQL tests. No production data is added by those tests. Each page has a total stable ordering ending in observation_id. Source identity remains visible to avoid treating republished series as independent observations.

The service receives an ObservationReader and page size. It validates year ordering and page numbers, computes offsets/page counts and returns ObservationPage. Fake-repository tests need no database or network.

## Run the observation browser

Install requirements, start PostgreSQL, then run `.\scripts\start-web.ps1` or `.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload`. Open http://127.0.0.1:8000/.

FastAPI and Uvicorn serve the application; Jinja2 builds complete HTML pages on the server. httpx2 supports TestClient, as required by the PDF and the installed Starlette version. Controllers parse form strings, call services and provide template context. app/dependencies.py is the composition root; it alone wires get_db -> repository -> service. No controller imports sessions, models or repositories. No JavaScript runs in the page, and no JSON API/docs endpoints are enabled.
