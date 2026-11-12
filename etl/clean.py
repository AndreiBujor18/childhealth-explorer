"""Shared cleaning rules with exclusive rejection counts and retained IQR flags."""
import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)
KEY = ['country_iso3', 'indicator_code', 'year', 'sex']
SEX_MAP = {'SEX_BTSX': 'BTSX', 'SEX_MLE': 'MLE', 'SEX_FMLE': 'FMLE',
           '_T': 'BTSX', 'BOTH': 'BTSX', 'TOTAL': 'BTSX', 'M': 'MLE', 'F': 'FMLE'}


def clean_observations(frame, valid_iso3, catalog, *, countries=None, year_window=(2000, 2023), sex='BTSX'):
    required = set(KEY + ['value'])
    if not required <= set(frame.columns):
        raise ValueError(f'Missing normalized columns: {required - set(frame.columns)}')
    cleaned = frame.copy()
    counts = {}

    def drop(mask, reason):
        nonlocal cleaned
        mask = mask.fillna(False)
        count = int(mask.sum())
        counts[reason] = count
        if count:
            logger.info('dropped %d rows: %s', count, reason)
        cleaned = cleaned.loc[~mask].copy()

    for col in ['country_iso3', 'indicator_code', 'sex']:
        cleaned[col] = cleaned[col].astype('string').str.strip().str.upper()
    # Code comparison is case-insensitive; preserve canonical provider spelling.
    by_code = {r['code'].upper(): r for r in catalog}
    drop(~cleaned['country_iso3'].isin(valid_iso3), 'invalid_country_or_aggregate')
    if countries is not None:
        drop(~cleaned['country_iso3'].isin(countries), 'country_outside_study')
    drop(~cleaned['indicator_code'].isin(by_code), 'unknown_indicator')
    for col in ['year', 'value']:
        cleaned[col] = pd.to_numeric(cleaned[col], errors='coerce').astype(float)
    drop(~np.isfinite(cleaned['year']) | ~np.isfinite(cleaned['value']), 'missing_or_non_numeric_year_value')
    drop(cleaned['year'] % 1 != 0, 'fractional_year')
    cleaned['year'] = cleaned['year'].astype(int)
    drop(~cleaned['year'].between(*year_window), 'year_outside_study')
    cleaned['sex'] = cleaned['sex'].fillna('BTSX').replace(SEX_MAP)
    drop(~cleaned['sex'].isin(['BTSX', 'MLE', 'FMLE']), 'unknown_sex')
    if sex is not None:
        drop(cleaned['sex'] != sex, 'sex_outside_study')
    invalid = pd.Series(False, index=cleaned.index)
    for code, item in by_code.items():
        selected = cleaned['indicator_code'] == code
        if item.get('minimum') is not None:
            invalid |= selected & (cleaned['value'] < item['minimum'])
        if item.get('maximum') is not None:
            invalid |= selected & (cleaned['value'] > item['maximum'])
    drop(invalid, 'outside_plausible_bounds')
    drop(cleaned.duplicated(subset=KEY, keep='last'), 'duplicate_natural_key')
    cleaned['is_outlier'] = False
    thresholds = {}
    for code, group in cleaned.groupby('indicator_code'):
        q1, q3 = group['value'].quantile([0.25, 0.75])
        iqr = q3 - q1
        low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        cleaned.loc[group.index, 'is_outlier'] = (group['value'] < low) | (group['value'] > high)
        thresholds[by_code[code]['code']] = {'q1': float(q1), 'q3': float(q3),
                                           'iqr': float(iqr), 'lower': float(low), 'upper': float(high)}
    cleaned['indicator_code'] = cleaned['indicator_code'].map({k: v['code'] for k, v in by_code.items()})
    cleaned['is_outlier'] = cleaned['is_outlier'].astype(bool)
    cleaned.attrs = {'raw_rows': len(frame), 'clean_rows': len(cleaned),
                     'rejected_rows': sum(counts.values()), 'rejections': counts, 'iqr': thresholds,
                     'excluded_dimensions': frame.attrs.get('excluded_dimensions', 0)}
    assert len(frame) == len(cleaned) + sum(counts.values())
    return cleaned.reset_index(drop=True)
