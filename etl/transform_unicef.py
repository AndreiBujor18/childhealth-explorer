"""Reuse the Lab 1 SDMX decoder against a saved UNICEF response."""
import json
from dataclasses import asdict
from pathlib import Path
import pandas as pd
from etl.extract_unicef import parse_sdmx
from etl.raw_files import read_snapshot
from etl.study import study
from etl.transform_worldbank import COLUMNS


def transform_unicef_file(path, code):
    read_snapshot(path)
    config = study()
    document = json.loads(Path(path).read_text(encoding='utf-8'))
    records = parse_sdmx(document, code, config['pilot_countries'],
                         config['start_year'], config['end_year'])
    return pd.DataFrame([asdict(r) for r in records], columns=COLUMNS)
