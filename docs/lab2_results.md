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

## Tasks 2.3 and 2.4

Import repetition and SQL verification are the next implementation step; no database-import result is claimed in this commit.
