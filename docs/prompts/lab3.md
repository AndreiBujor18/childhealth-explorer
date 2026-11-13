# Lab 3 - AI assistance record

## Prompt 1 - layered browser application
- Tool and model: Codex desktop, GPT-6 family; the exact serving variant is not exposed in this session.
- Date: 2026-11-13
- Prompt (exact user text):

> I want to see from you one commit for each layer or for each functionality; and to have the application with all the three layers and the web application. Today we will see the data from the database in the browser. Noi avem astea? Cred că trebuie să le facem. Uite noul lab și ce a desenat pe tablă acum

- Context: the user attached the Lab 3 PDF and a whiteboard diagram showing database/ORM, DAL, service and presentation layers.
- Result, first step: immutable domain objects and the observation repository with stable, parameterized queries and isolated PostgreSQL tests. Commit: `Lab 3: add domain objects and the observation data access layer`.
- Your changes: no manual student edits reported. The assistant kept source identity and outlier status in the display records, restricted filter options to observed data and introduced Sex as a Python enum without changing the stored schema.

## Prompt 2 - strict layer boundaries (received during implementation)
- Tool and model: same Codex session as Prompt 1.
- Date: 2026-11-13
- Prompt (exact user text):

> I dont wanna se in the presentation layer extracted data form the database. Just the code meant to be in each layer. Only DAL communicates with the DB. Presentation will just call the service layer and will make the UI.

- Result: repositories own all web SQL; services receive repositories and return immutable values; controllers call services and render templates. Later pipeline refactoring also moves database write/query code behind a data-access repository.
- Your changes: this is an explicit architecture requirement supplied by the student. No independently written student code is claimed.

Further implementation entries refer to these actual prompts; they do not invent extra user prompts.

## Prompts 1-2 continuation - observation service
- Date: 2026-11-13
- Result: `app/services/observation_service.py`, immutable ObservationPage and fake-repository tests. Commit: `Lab 3: add observation service pagination and browsing rules`.
- Checks and corrections: service contains no SQL, session creation or HTTP. Empty results are page 1 of 1; a page beyond the end is clamped to the last real page; reversed year ranges raise a plain ValueError. No manual student code edits reported.

## Prompts 1-2 continuation - server-rendered presentation
- Date: 2026-11-13
- Result: FastAPI app/dependency wiring, HTTP controllers, Jinja templates, local CSS, launch script and dependency-overridden presentation tests. Commit: `Lab 3: render database observations through controllers and templates`.
- Checks and corrections: GET filters preserve selected values and pagination URLs; templates receive immutable records and contain no SQL/ORM operations. Invalid years are ignored, reversed ranges become an HTML error, and external labels are autoescaped. The design carries over the approved restrained colors/type hierarchy without JavaScript or fake data. No student code edits reported.

## Prompts 1-2 continuation - pipeline actions and write DAL
- Date: 2026-11-13
- Result: import_repository moves existing SQL into the DAL; import_runner returns typed StepResult objects; EtlService runs injected extraction/import jobs; POST controllers render a result table. Commit: `Lab 3: run shared ETL jobs through services and POST actions`.
- Checks and corrections: repositories never commit; the import runner owns per-indicator transactions. Legacy Lab 2 imports keep their report format and exit behavior through compatibility wrappers. Expected errors become failed results, programming exceptions propagate, simultaneous local pipeline actions are serialized, and GET never starts an action. UI displays loaded/new/updated/rejected counts. Tests use stubs and rolled-back schemas, not live downloads or production writes. No manual student code edits reported.
