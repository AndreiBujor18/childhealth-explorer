# Lab 3 - layer boundaries

Presentation -> service -> repository -> PostgreSQL. Only repositories contain database queries. HTTP parsing/templates belong to presentation; pagination/validation/orchestration belong to services. Repository constructors receive sessions and never commit. Domain objects are immutable and do not expose ORM rows.

First step: `app/domain.py`, `app/repositories/observation_repository.py`, shared Sex enum, and isolated synthetic PostgreSQL tests. No production data is added by those tests. Each page has a total stable ordering ending in observation_id. Source identity remains visible to avoid treating republished series as independent observations.

The service receives an ObservationReader and page size. It validates year ordering and page numbers, computes offsets/page counts and returns ObservationPage. Fake-repository tests need no database or network.
