"""Cleaning must not fabricate zeros, truncate years or delete real outliers."""
import pandas as pd
from etl.clean import clean_observations

CATALOG = [{'code': 'X', 'minimum': 0, 'maximum': 100}]


def clean(rows):
    frame = pd.DataFrame(rows, columns=['country_iso3', 'indicator_code', 'year', 'sex', 'value'])
    return clean_observations(frame, ['ROU'], CATALOG)


def test_fractional_year_unknown_sex_missing_and_duplicate_counts():
    rows = [
        [' rou ', 'x', '2020', None, 0], ['ROU', 'X', 2020.5, 'BTSX', 20],
        ['ROU', 'X', 2021, 'BTSX', None], ['WLD', 'X', 2021, 'BTSX', 20],
        ['ROU', 'X', 2021, 'UNKNOWN', 20], ['ROU', 'X', 2022, 'SEX_BTSX', 101],
        ['ROU', 'X', 2023, 'BTSX', 10], ['ROU', 'X', 2023, 'BTSX', 11],
    ]
    frame = clean(rows)
    assert frame['value'].tolist() == [0, 11]
    assert frame.attrs['rejected_rows'] == 6
    assert frame.attrs['rejections']['fractional_year'] == 1
    assert frame.attrs['rejections']['duplicate_natural_key'] == 1


def test_outlier_is_retained_and_iqr_zero_is_well_defined():
    frame = clean([['ROU', 'X', 2000 + n, 'BTSX', v] for n, v in enumerate([1, 1, 1, 1, 90])])
    assert len(frame) == 5
    assert frame['is_outlier'].tolist() == [False, False, False, False, True]
    assert frame.attrs['iqr']['X']['iqr'] == 0


def test_nonfinite_and_unknown_indicator_are_rejected():
    frame = clean([['ROU', 'X', 2020, 'BTSX', float('inf')],
                   ['ROU', 'unknown', 2020, 'BTSX', 1]])
    assert frame.empty and frame.attrs['rejected_rows'] == 2
