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
