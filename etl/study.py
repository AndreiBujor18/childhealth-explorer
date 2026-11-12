"""Shared Lab 2 catalog, separate from the immutable Lab 1 feasibility catalog."""
import json
from etl.raw_files import ROOT, RAW


def study():
    return json.loads((ROOT / 'config/study.json').read_text(encoding='utf-8'))


def indicators(source=None):
    rows = json.loads((ROOT / 'config/lab2_indicators.json').read_text(encoding='utf-8'))
    return [r for r in rows if source is None or r['source'] == source]


def raw_path(indicator):
    config = study()
    suffix = 'csv' if indicator['source'] == 'owid' else 'json'
    return RAW / indicator['source'] / (
        f"{indicator['code']}_{config['start_year']}_{config['end_year']}.{suffix}")
