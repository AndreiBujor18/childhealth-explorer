"""Normalize OWID mortality to per 1,000 births using verified metadata."""
import json
from pathlib import Path
import pandas as pd
from etl.raw_files import read_snapshot
from etl.transform_worldbank import COLUMNS


def transform_owid_file(path, code):
    path = Path(path)
    read_snapshot(path)
    metadata_path = path.with_suffix('.metadata.json')
    read_snapshot(metadata_path)
    metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
    columns = metadata.get('columns', {})
    if len(columns) != 1:
        raise ValueError('Expected one OWID metadata value column')
    unit = next(iter(columns.values())).get('unit')
    if unit != 'deaths per 100 live births':
        raise ValueError(f'OWID source unit changed: {unit!r}; review conversion')
    raw = pd.read_csv(path)
    fields = set(raw.columns) - {'Entity', 'Code', 'Year'}
    if not {'Entity', 'Code', 'Year'} <= set(raw.columns) or len(fields) != 1:
        raise ValueError('Unexpected OWID chart columns')
    frame = pd.DataFrame({'country_iso3': raw['Code'], 'indicator_code': code,
                          'year': raw['Year'], 'sex': 'BTSX',
                          'value': pd.to_numeric(raw[next(iter(fields))], errors='coerce') * 10})
    return frame[COLUMNS]
