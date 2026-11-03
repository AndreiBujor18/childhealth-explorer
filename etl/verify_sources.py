"""Task 1.7: verify all selected indicators; never write to the project database."""
import argparse
import csv
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from etl.contracts import validate
from etl.extract_worldbank import WorldBankAdapter
from etl.http_client import JsonClient
from etl.registry import get_adapter

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh', action='store_true', help='Download fresh copies instead of using raw cache.')
    args = parser.parse_args()
    client = JsonClient(refresh=args.refresh)
    study = json.loads((ROOT / 'config/study.json').read_text())
    indicators = json.loads((ROOT / 'config/indicators.json').read_text())
    countries = study['pilot_countries']
    start, end = study['start_year'], study['end_year']
    catalog = WorldBankAdapter(client).countries()
    if set(countries) - catalog.keys():
        raise ValueError('Pilot contains invalid/aggregate country codes')
    result = {'checked_at': datetime.now(timezone.utc).isoformat(), 'study': study,
              'indicators': [], 'purpose': 'API feasibility check only; no database imports'}
    records = []
    expected = len(countries) * (end - start + 1)
    complete_sets = []
    for indicator in indicators:
        before = len(client.calls)
        rows = get_adapter(indicator['source'], client).fetch(indicator['code'], countries, start, end)
        validate(rows, indicator, countries, start, end)
        if not rows:
            raise ValueError(f'No data for {indicator["code"]}')
        if any(r.sex != 'BTSX' for r in rows):
            raise ValueError('Pilot must use total sex only')
        nonnull = [r for r in rows if r.value is not None]
        keys = {(r.country_iso3, r.year) for r in nonnull}
        complete_sets.append(keys)
        item = {**indicator, 'rows_returned': len(rows), 'nonnull': len(nonnull),
                'expected_country_years': expected, 'missing_country_years': expected - len(keys),
                'coverage_percent': round(100 * len(keys) / expected, 2),
                'countries_with_data': len({r.country_iso3 for r in nonnull}),
                'requests': client.calls[before:],
                'romania_2023': next((str(r.value) for r in rows if r.country_iso3 == 'ROU'
                                     and r.year == 2023 and r.value is not None), None)}
        if indicator['source'] == 'worldbank':
            item['official_metadata'] = WorldBankAdapter(client).metadata(indicator['code'])
        result['indicators'].append(item)
        records.extend(rows)
        print(f'{indicator["source"]}/{indicator["code"]}: {len(nonnull)}/{expected} non-null', flush=True)
    common = set.intersection(*complete_sets)
    result['complete_country_years_all_indicators'] = len(common)
    result['complete_countries_all_indicators'] = len({c for c, y in common})
    result['complete_country_years_by_country'] = {c: sum(1 for country, year in common if country == c)
                                               for c in countries}
    result['all_requests'] = client.calls
    out = ROOT / 'docs/evidence'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'api_validation.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    with (out / 'sample_observations.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(ObservationFields))
        writer.writeheader()
        writer.writerows(asdict(r) for r in records)
    with (out / 'coverage.csv').open('w', newline='', encoding='utf-8') as f:
        fields = ['source', 'code', 'nonnull', 'expected_country_years', 'coverage_percent']
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(result['indicators'])
    print(f'Complete country-years across all seven indicators: {len(common)}/{expected}')


ObservationFields = ('source_name', 'indicator_code', 'country_iso3', 'year', 'sex', 'value')

if __name__ == '__main__':
    main()
