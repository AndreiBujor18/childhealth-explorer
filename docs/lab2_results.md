# Lab 2 - results

Verified on 12 November 2026. SQL check time: 2026-11-12T16:31:36.873064+00:00. Source comparison time: 2026-11-12T16:31:39.405713+00:00.

The study retains 20 pilot countries, 2000-2023 inclusive, both sexes. WHO, World Bank and Our World in Data are the three mandatory sources; UNICEF is retained for the approved vaccination indicators. The database contains 4,309 observations across nine source-specific indicators and four providers. The pilot demonstrates integration and is not a representative global sample.

## Task 2.1 - exploration and missing values

The executed notebook is [lab2_exploration.ipynb](../notebooks/lab2_exploration.ipynb). It calls each downloader, transforms the saved file, and shows head(), info() and isna().sum(). [Exploration evidence](evidence/lab2-exploration.json) records full-download and study-subset missingness.

| Source | Indicator | Pilot rows | Missing values | Missing % | Country-year gaps |
|---|---|---|---|---|---|
| unicef | IM_DTP3 | 480 | 0 | 0.0 | 0 |
| unicef | IM_MCV1 | 480 | 0 | 0.0 | 0 |
| worldbank | SH.DYN.MORT | 480 | 0 | 0.0 | 0 |
| worldbank | NY.GDP.PCAP.PP.KD | 480 | 0 | 0.0 | 0 |
| worldbank | SH.XPD.CHEX.GD.ZS | 480 | 0 | 0.0 | 0 |
| worldbank | SH.H2O.BASW.ZS | 480 | 10 | 2.083 | 10 |
| worldbank | SH.STA.BASS.ZS | 480 | 1 | 0.208 | 1 |
| who | MDG_0000000007 | 480 | 0 | 0.0 | 0 |
| owid | child-mortality | 480 | 0 | 0.0 | 0 |

Ten water observations and one sanitation observation have no value in the pilot. They are not imputed as zero. Explicit missing values and absent country-year combinations are different coverage measures; neither is a successful import. Missing values outside the pilot are described in the notebook but do not inflate the pilot missingness rate.

## Task 2.2 - cleaning and retained outliers

The cleaner standardizes identifiers, converts types, harmonizes sex codes, checks valid economies and the study scope, removes missing/non-finite values and fractional years, checks plausible ranges, and deduplicates the natural key. Last duplicate wins. Every dropped row is counted once, under the first applicable rule.

For each source-specific indicator, Q1 and Q3 are computed across its cleaned pilot observations with linear quantiles. Values below Q1 - 1.5*IQR or above Q3 + 1.5*IQR are flagged; values on the fences are not. IQR=0 uses the same definition. The flag does not establish that a value is erroneous or clinically abnormal.

| Source | Indicator | Normalized input | Excluded by cleaning | Retained | IQR flagged |
|---|---|---|---|---|---|
| unicef | IM_DTP3 | 480 | 0 | 480 | 43 |
| unicef | IM_MCV1 | 480 | 0 | 480 | 50 |
| worldbank | SH.DYN.MORT | 6384 | 5904 | 480 | 45 |
| worldbank | NY.GDP.PCAP.PP.KD | 6384 | 5904 | 480 | 0 |
| worldbank | SH.XPD.CHEX.GD.ZS | 6384 | 5904 | 480 | 1 |
| worldbank | SH.H2O.BASW.ZS | 6384 | 5914 | 470 | 54 |
| worldbank | SH.STA.BASS.ZS | 6384 | 5905 | 479 | 52 |
| who | MDG_0000000007 | 4800 | 4320 | 480 | 45 |
| owid | child-mortality | 17066 | 16586 | 480 | 45 |

Total: **54,746 normalized input rows, 50,437 excluded by cleaning, 4,309 retained, including 335 outliers**. Most exclusions select the study countries/year window; they are not malformed data. The 11 missing values inside the pilot are separately identified below.

| First applicable rejection rule | Rows |
|---|---|
| invalid_country_or_aggregate | 7185 |
| country_outside_study | 41344 |
| unknown_indicator | 0 |
| missing_or_non_numeric_year_value | 11 |
| fractional_year | 0 |
| year_outside_study | 1897 |
| unknown_sex | 0 |
| sex_outside_study | 0 |
| outside_plausible_bounds | 0 |
| duplicate_natural_key | 0 |

WHO transformation separately excludes 12,720 records with incompatible age, wealth or other disaggregation dimensions before producing the 4,800 normalized national totals. Those dimension exclusions are not counted again as cleaning rejections. All raw response envelopes remain saved.

[Cleaning evidence](evidence/lab2-cleaning.json) includes each indicator's Q1, Q3, IQR, fences and rejection counts. The non-null is_outlier field was added by Alembic revision 0002 after the existing five-table Lab 1 schema was verified and stamped at revision 0001. Existing values are preserved. Upgrade/downgrade behavior was tested on a synthetic observation in an isolated, rolled-back PostgreSQL schema.

## Task 2.3 - two real imports

| State | Observations | Import logs | Duplicate keys |
|---|---|---|---|
| Before | 0 | 0 | 0 |
| After first run | 4309 | 9 | 0 |
| After second run | 4309 | 18 | 0 |

The first run inserted 4,309 new observations. The second processed 4,309 upserts, inserted zero new observations and updated all 4,309 existing observations. Per-indicator counts and a digest of source/country/year/sex/value/outlier remained identical. Refresh timestamps are intentionally excluded from that digest.

Each successful indicator adds one import_log entry with the real source request URL and rows_loaded. Here rows_loaded means processed upserts, not only new inserts. The nine indicators add nine log rows per run. An indicator and its log commit in the same transaction; a failed indicator is rolled back and makes the import command fail. Separate integration tests verify that updates change both value and outlier flag and that a failed import cannot leave a success log.

[Full two-run evidence](evidence/lab2-imports.json) contains all counts, rejection reasons, snapshot hashes, request URLs and the 18 import-log records.

## Task 2.4 - seven SQL checks

The exact queries are in [lab2_checks.sql](../db/lab2_checks.sql). [SQL evidence](evidence/lab2-sql-checks.json) contains every returned row, including trends, import history and the complete coverage-gap list. The life-expectancy examples are adapted to the project's under-five mortality target.

| Check | Observed result | Interpretation |
|---|---|---|
| 1. Countries and regions | 217 economies, 7 regions; ISO3 catalog exactly matches non-aggregate World Bank metadata | Aggregates are excluded. Observation scope remains the 20-country pilot. |
| 2. Duplicate natural keys | No rows returned | Country, source-specific indicator, year and sex are unique. |
| 3. Value ranges | All nine source-specific series satisfy their configured bounds | Plausible limits are checked separately from IQR flags. |
| 4. Sex categories | BTSX: 4,309 rows | This study uses both sexes; no unknown categories are stored. |
| 5. Missing values and years | null_values = 0; out_of_window = 0 | Values are present and years are within 2000-2023. |
| 6. Latest import vs stored rows | All nine counts match | Latest log is selected by source and indicator; import_id breaks timestamp ties. |
| 7. Mortality coverage gaps | 197 economies in the full catalog; zero pilot countries | The 197 economies are outside the chosen study, rather than failed pilot imports. |

All seven checks passed. For check 6, an upsert never deletes historical rows absent from a later revised source snapshot; a mismatch on a future run must be investigated and explained.

### Per-indicator ranges

| source | code | unit | minimum | maximum | average |
|---|---|---|---|---|---|
| owid | child-mortality | per 1,000 live births | 2.4000 | 177.3000 | 23.59 |
| unicef | IM_DTP3 | % | 25.0000 | 99.0000 | 89.15 |
| unicef | IM_MCV1 | % | 30.0000 | 99.0000 | 88.56 |
| who | MDG_0000000007 | per 1,000 live births | 2.3806 | 177.2779 | 23.59 |
| worldbank | NY.GDP.PCAP.PP.KD | constant 2021 international $ | 3010.4216 | 74351.6718 | 31968.46 |
| worldbank | SH.DYN.MORT | per 1,000 live births | 2.4000 | 177.3000 | 23.59 |
| worldbank | SH.H2O.BASW.ZS | % of population | 44.4803 | 100.0000 | 93.01 |
| worldbank | SH.STA.BASS.ZS | % of population | 14.6639 | 100.0000 | 83.49 |
| worldbank | SH.XPD.CHEX.GD.ZS | % of GDP | 1.8530 | 18.5160 | 7.70 |

### Latest import counts

| source | indicator_code | rows_loaded | rows_stored |
|---|---|---|---|
| owid | child-mortality | 480 | 480 |
| unicef | IM_DTP3 | 480 | 480 |
| unicef | IM_MCV1 | 480 | 480 |
| who | MDG_0000000007 | 480 | 480 |
| worldbank | NY.GDP.PCAP.PP.KD | 480 | 480 |
| worldbank | SH.DYN.MORT | 480 | 480 |
| worldbank | SH.H2O.BASW.ZS | 470 | 470 |
| worldbank | SH.STA.BASS.ZS | 479 | 479 |
| worldbank | SH.XPD.CHEX.GD.ZS | 480 | 480 |

### Independent source comparison: Romania, 2023

These are three source-specific indicator series, one from each mandatory provider. Values were retrieved again from the official websites' API/CSV exports, independently of the ETL snapshots. This does not claim a visual reading of rounded chart labels. [Comparison evidence](evidence/lab2-source-comparison.json) records website URLs, exact download URLs, retrieval time, response hashes, conversion and precision tolerance.

| Source | Indicator | Published value | Multiply by | Stored per 1,000 | Absolute difference |
|---|---|---|---|---|---|
| worldbank | SH.DYN.MORT | 6.9 | 1 | 6.9000 | 0.0000 |
| who | MDG_0000000007 | 6.873308064 | 1 | 6.8733 | 0.000008064 |
| owid | child-mortality | 0.69 | 10 | 6.9000 | 0.0000 |

All three values match within 0.00005, the maximum rounding difference for NUMERIC(18,4). WHO retains more original precision; its stored value is 6.8733. OWID's 0.69 deaths per 100 births becomes 6.9 per 1,000. World Bank publishes 6.9 per 1,000. The series are not forced to equal one another.

- [World Bank website](https://data.worldbank.org/indicator/SH.DYN.MORT?locations=RO).
- [WHO indicator website](https://www.who.int/data/gho/data/indicators/indicator-details/GHO/under-five-mortality-rate-(probability-of-dying-by-age-5-per-1000-live-births)).
- [OWID table, Romania 2023](https://ourworldindata.org/grapher/child-mortality?tab=table&time=2023&country=~ROU).

These providers redistribute related UN IGME estimates. Source comparisons verify integration, not independent corroboration of three unrelated measurements. Revisions, processing and display precision can explain differences.

## Reproduction and delivery

Follow [setup, extraction, notebook, migration, import and checks](lab2_setup.md). [AI prompts](prompts/lab2.md) accompany the corresponding commits. The completed [checklist](lab2-checklist.md) maps every delivery requirement to its evidence. The Lab 1 report and historical evidence are preserved; Lab 2 needs no separate PDF.
