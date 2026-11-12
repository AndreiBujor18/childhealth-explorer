# Lab 2 - results

Study: 20 countries, 2000-2023 inclusive, both sexes. Source series remain separate.

## Task 2.1 - exploration

The executed notebook is `notebooks/lab2_exploration.ipynb`; missingness profiles are in `docs/evidence/lab2-exploration.json`.

## Task 2.2 - retained IQR outliers

| Source | Indicator | Clean rows | Flagged rows |
|---|---|---:|---:|
| unicef | IM_DTP3 | 480 | 43 |
| unicef | IM_MCV1 | 480 | 50 |
| worldbank | SH.DYN.MORT | 480 | 45 |
| worldbank | NY.GDP.PCAP.PP.KD | 480 | 0 |
| worldbank | SH.XPD.CHEX.GD.ZS | 480 | 1 |
| worldbank | SH.H2O.BASW.ZS | 470 | 54 |
| worldbank | SH.STA.BASS.ZS | 479 | 52 |
| who | MDG_0000000007 | 480 | 45 |
| owid | child-mortality | 480 | 45 |

Total: 4,309 cleaned observations, including 335 retained outliers. Exact Q1, Q3, IQR and rejection counts are in `docs/evidence/lab2-cleaning.json`. Thresholds are computed separately by source and indicator across the pilot. An outlier is not automatically an error.

## Task 2.3 - repeated imports

| State | Observation rows | Import log rows | Duplicate keys |
|---|---:|---:|---:|
| Before | 0 | 0 | 0 |
| After first import | 4309 | 9 | 0 |
| After second import | 4309 | 18 | 0 |

Both runs processed 4,309 upserts. The first inserted 4,309 new observations; the second inserted zero and updated 4,309 existing observations. Source-specific counts, values and flags stayed the same. Nine indicators produced nine import_log entries per run. Evidence: `docs/evidence/lab2-imports.json`.

## Task 2.4 - SQL and source comparison

SQL checks and independent source spot checks follow in the next implementation step.
