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
