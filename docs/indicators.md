# Task 1.7 - Indicator catalog and source verification

Period: 2000-2023. Annual country-level data, ISO3 identifiers and both sexes combined where applicable. Under-five mortality is the ML target; the other six indicators are proposed explanatory variables.

| Source | Code | Indicator | Unit | Pilot coverage |
|---|---|---|---|---|
| UNICEF | IM_DTP3 | DTP3 vaccination coverage | % | 480/480 |
| UNICEF | IM_MCV1 | First-dose measles vaccination coverage | % | 480/480 |
| World Bank | SH.DYN.MORT | Under-five mortality | per 1,000 live births | 480/480 |
| World Bank | NY.GDP.PCAP.PP.KD | GDP per capita, PPP | constant 2021 international $ | 480/480 |
| World Bank | SH.XPD.CHEX.GD.ZS | Current health expenditure | % of GDP | 480/480 |
| World Bank | SH.H2O.BASW.ZS | At least basic drinking water services | % of population | 470/480 |
| World Bank | SH.STA.BASS.ZS | At least basic sanitation services | % of population | 479/480 |

The pilot snapshot was downloaded on 21 October 2026. There are 469 country-year combinations with all seven values. Actual request URLs, timestamps, hashes and metadata are recorded in `docs/evidence/api_validation.json`. The seven Romania URLs below were checked live again on 3 November, without replacing the pilot snapshot or writing to the database.

## URLs tested in the browser

Each link requests Romania, 2000-2023:

1. [UNICEF - IM_DTP3](https://sdmx.data.unicef.org/ws/public/sdmxapi/rest/data/UNICEF,GLOBAL_DATAFLOW,1.0/ROU.IM_DTP3._T?format=sdmx-json&startPeriod=2000&endPeriod=2023)
2. [UNICEF - IM_MCV1](https://sdmx.data.unicef.org/ws/public/sdmxapi/rest/data/UNICEF,GLOBAL_DATAFLOW,1.0/ROU.IM_MCV1._T?format=sdmx-json&startPeriod=2000&endPeriod=2023)
3. [World Bank - SH.DYN.MORT](https://api.worldbank.org/v2/country/ROU/indicator/SH.DYN.MORT?format=json&date=2000:2023)
4. [World Bank - NY.GDP.PCAP.PP.KD](https://api.worldbank.org/v2/country/ROU/indicator/NY.GDP.PCAP.PP.KD?format=json&date=2000:2023)
5. [World Bank - SH.XPD.CHEX.GD.ZS](https://api.worldbank.org/v2/country/ROU/indicator/SH.XPD.CHEX.GD.ZS?format=json&date=2000:2023)
6. [World Bank - SH.H2O.BASW.ZS](https://api.worldbank.org/v2/country/ROU/indicator/SH.H2O.BASW.ZS?format=json&date=2000:2023)
7. [World Bank - SH.STA.BASS.ZS](https://api.worldbank.org/v2/country/ROU/indicator/SH.STA.BASS.ZS?format=json&date=2000:2023)

## Live check on 3 November

All seven URLs returned HTTP 200 and were decoded and validated: country ROU, both sexes combined where applicable, exactly 2000-2023, no duplicates and values within the indicator limits. Each URL returned 24 annual records. Sanitation has one missing value, preserved as `NULL`; the other six indicators have 24 non-null values each. Evidence includes the final URL, UTC time, content type, SHA-256 and 2023 value: `docs/evidence/url-check-2026-11-03.json`.

Reproduce with `python -m scripts.check_indicator_urls`. Raw responses from this check are in `data/raw/url-check-2026-11-03/`, excluded from Git. The pilot values were preserved.

## Browser confirmation on 4 November

The author opened all seven URLs in Chrome and supplied one screenshot per URL. Each screenshot was reviewed: UNICEF shows `meta` and `data.dataSets` with the 2000-2023 reporting period; World Bank shows pagination metadata (`total: 24`) and Romania observations with the indicator code, year and value. All seven JSON responses are visible, with no error pages.

Evidence: `docs/evidence/browser-url-check-2026-11-04.json` and `docs/evidence/screenshots/api-browser-2026-11-04/`. Full response validation is documented separately in the live check.

Historical note: on 3 November, the integrated browser blocked all seven URLs with `ERR_BLOCKED_BY_CLIENT`. That attempt is retained in `docs/evidence/browser-url-check-2026-11-03.json`. The successful Chrome check completes the browser requirement in Task 1.7.

## Reading the responses

World Bank returns a two-element array: pagination metadata followed by records. Check `countryiso3code`, the indicator code, date and value. In UNICEF responses, inspect `data.structure` for dimensions and `data.dataSets` for observations; numeric SDMX indexes must be interpreted using the metadata.
