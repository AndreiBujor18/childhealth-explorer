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

The pilot snapshot was downloaded on 21 October 2026. There are 469 country-year combinations with all seven values. Actual request URLs, timestamps, hashes and metadata are recorded in `docs/evidence/api_validation.json`. The Romania URLs below provide reproducible API requests. Source checks do not write to the project database.

## Indicator URLs

Each link requests Romania, 2000-2023:

1. [UNICEF - IM_DTP3](https://sdmx.data.unicef.org/ws/public/sdmxapi/rest/data/UNICEF,GLOBAL_DATAFLOW,1.0/ROU.IM_DTP3._T?format=sdmx-json&startPeriod=2000&endPeriod=2023)
2. [UNICEF - IM_MCV1](https://sdmx.data.unicef.org/ws/public/sdmxapi/rest/data/UNICEF,GLOBAL_DATAFLOW,1.0/ROU.IM_MCV1._T?format=sdmx-json&startPeriod=2000&endPeriod=2023)
3. [World Bank - SH.DYN.MORT](https://api.worldbank.org/v2/country/ROU/indicator/SH.DYN.MORT?format=json&date=2000:2023)
4. [World Bank - NY.GDP.PCAP.PP.KD](https://api.worldbank.org/v2/country/ROU/indicator/NY.GDP.PCAP.PP.KD?format=json&date=2000:2023)
5. [World Bank - SH.XPD.CHEX.GD.ZS](https://api.worldbank.org/v2/country/ROU/indicator/SH.XPD.CHEX.GD.ZS?format=json&date=2000:2023)
6. [World Bank - SH.H2O.BASW.ZS](https://api.worldbank.org/v2/country/ROU/indicator/SH.H2O.BASW.ZS?format=json&date=2000:2023)
7. [World Bank - SH.STA.BASS.ZS](https://api.worldbank.org/v2/country/ROU/indicator/SH.STA.BASS.ZS?format=json&date=2000:2023)

