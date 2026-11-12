# Lab 2 - study and extraction

Scope: 20 pilot countries, 2000-2023 inclusive, both sexes. This retains the approved Lab 1 study rather than silently extending to 2024 from the lab examples. The sample demonstrates integration; it is not a representative world sample.

Use Python 3.12+ and the existing PostgreSQL setup in [the README](../README.md). From the repository root:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m etl.extract
```

Add `--refresh` to deliberately replace snapshots. Raw files and SHA-256/URL metadata are under `data/raw/<source>/`, excluded from Git. JSON page envelopes are preserved inside a `responses` list; no observations are cleaned during extraction. World Bank country metadata exercises real pagination (100 entries per page). World Bank indicators use the official bulk country/all route because selected-country requests returned HTTP 502 during verification. Full country responses are preserved; cleaning applies the 20-country scope. WHO follows `@odata.nextLink` without resending the original filter. Invalid response shapes do not replace a successful snapshot. OWID serves a complete chart, so its study/country filtering is a later cleaning step; its single-year helper still downloads that full CSV and is explicitly documented as such.

`etl.transform.transform_indicator(item)` reads these files only. It returns the five normalized columns: `country_iso3`, `indicator_code`, `year`, `sex`, `value`. Checksums detect edited or incomplete snapshots.

## Source choices

The mandatory sources are WHO, World Bank and OWID. UNICEF is retained as a fourth source for the vaccination series agreed in Lab 1. The nine source-specific series are in `config/lab2_indicators.json`; the original Lab 1 catalog is preserved.

- [WHO GHO OData documentation](https://www.who.int/data/gho/info/gho-odata-api): `MDG_0000000007`, under-five mortality per 1,000 live births. Only national, both-sex, under-five, total-wealth observations are used; age/wealth subdivisions are never collapsed into duplicate national values.
- [World Bank API documentation](https://datahelpdesk.worldbank.org/knowledgebase/articles/898581-api-basic-call-structures): the five original mortality and socioeconomic series; aggregate economies are excluded from country metadata.
- [OWID chart API documentation](https://docs.owid.io/projects/etl/api/chart-api/) and [child mortality chart](https://ourworldindata.org/grapher/child-mortality): source unit is deaths per 100 live births. The transformer checks the saved metadata unit before multiplying values by 10 to match per 1,000 births. CSV column labels and metadata labels can differ; both must contain exactly one value series.
- [UNICEF SDMX documentation](https://data.unicef.org/sdmx-api-documentation/): DTP3 and first-dose measles coverage remain separate indicators.

These providers may redistribute UN IGME estimates. They are source-specific comparison series, not independent measurements or additional ML training examples. Differences can reflect revisions, precision and processing. Metadata and retrieval times remain with every snapshot. Public aggregates contain no patient records; source attribution and original-provider terms still apply.

## Notebook (Task 2.1)

Install `requirements-notebook.txt`, then open `notebooks/lab2_exploration.ipynb` in JupyterLab using the project environment. To reproduce the executed outputs from the root:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-notebook.txt
.\.venv\Scripts\python.exe -m ipykernel install --prefix .venv --name childhealth --display-name "Python (ChildHealth Explorer)"
.\.venv\Scripts\python.exe -m jupyter lab
```

The committed notebook includes actual outputs from all nine series, plus the per-indicator missing-value summary in `docs/evidence/lab2-exploration.json`. Existing valid snapshots allow execution without network requests.
