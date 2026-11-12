"""OWID Grapher CSV and metadata downloads; values stay in source units."""
import csv
import io
import re
from etl.raw_files import RAW, http_session, save_snapshot

BASE = 'https://ourworldindata.org/grapher'


def download_owid_chart(slug, year_from=2000, year_to=2023, *, output_dir=None):
    if not re.fullmatch(r'[a-z0-9-]+', slug):
        raise ValueError('Invalid chart slug')
    path = (output_dir or RAW / 'owid') / f'{slug}_{year_from}_{year_to}.csv'
    with http_session() as session:
        response = session.get(f'{BASE}/{slug}.csv', timeout=(15, 120))
        response.raise_for_status()
        reader = csv.DictReader(io.StringIO(response.content.decode('utf-8-sig')))
        fields = reader.fieldnames or []
        if not {'Entity', 'Code', 'Year'} <= set(fields) or len(fields) != 4:
            raise ValueError('Expected OWID entity, code, year and one value column')
        rows = list(reader)
        if not rows or any(None in r or any(v is None for v in r.values()) for r in rows):
            raise ValueError('Empty or malformed OWID CSV')
        metadata = session.get(f'{BASE}/{slug}.metadata.json', timeout=(15, 120))
        metadata.raise_for_status()
        info = metadata.json()
        if not isinstance(info, dict) or not isinstance(info.get('columns'), dict):
            raise ValueError('Missing OWID column metadata')
        save_snapshot(path.with_suffix('.metadata.json'), metadata.content,
                      [{'url': metadata.url, 'status': metadata.status_code}])
        return save_snapshot(path, response.content,
                             [{'url': response.url, 'status': response.status_code}])


def download_owid_for_year(slug, year, **kwargs):
    """Grapher serves the complete chart; transformation applies the year window."""
    return download_owid_chart(slug, year, year, **kwargs)
