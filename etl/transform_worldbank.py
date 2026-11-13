"""Transform saved World Bank envelopes; never perform network requests."""
import pandas as pd
from etl.raw_files import json_pages

COLUMNS = ['country_iso3', 'indicator_code', 'year', 'sex', 'value']


def require_keys(row, keys):
    missing = set(keys) - row.keys()
    if missing:
        raise ValueError(f'Missing source fields: {sorted(missing)}')


def transform_worldbank_file(path, code):
    rows = []
    for _, records in json_pages(path):
        for r in records or []:
            require_keys(r, ['countryiso3code', 'date', 'value', 'indicator'])
            if r['indicator'].get('id') != code:
                raise ValueError('World Bank indicator mismatch')
            rows.append([r['countryiso3code'], code, r['date'], 'BTSX', r['value']])
    return pd.DataFrame(rows, columns=COLUMNS)


def transform_worldbank_countries(path):
    rows = []
    for _, records in json_pages(path):
        for r in records or []:
            require_keys(r, ['id', 'iso2Code', 'name', 'region', 'incomeLevel'])
            if r['region']['id'] == 'NA' or r['region']['value'] == 'Aggregates':
                continue
            rows.append({'iso3': r['id'].strip().upper(), 'iso2': r['iso2Code'].strip().upper(),
                         'name': r['name'].strip(), 'region': r['region']['value'].strip(),
                         'income_group': r['incomeLevel']['value'].strip()})
    return pd.DataFrame(rows)
