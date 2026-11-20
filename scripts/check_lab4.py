"""Read-only HTTP checks against a running local app; save reproducible API evidence."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import requests


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://127.0.0.1:8000')
    parser.add_argument('--output', type=Path, default=Path('docs/evidence/lab4-http-checks.json'))
    args = parser.parse_args()
    averages = '/api/indicators/IM_DTP3/period-averages'
    too_many = '&'.join(f'country=AA{chr(65 + index)}' for index in range(21))
    cases = [
        ('SSR page preserved', '/', 200), ('CSR shell', '/period-averages', 200),
        ('Interactive API docs', '/api/docs', 200), ('OpenAPI', '/api/openapi.json', 200),
        ('Regions', '/api/regions', 200), ('European countries', '/api/countries?region=Europe+%26+Central+Asia', 200),
        ('Unknown region is empty', '/api/countries?region=UNKNOWN', 200),
        ('Indicators', '/api/indicators', 200),
        ('DTP3 comparison', averages + '?country=ROU&country=FRA', 200),
        ('Duplicate country removed', averages + '?country=ROU&country=ROU', 200),
        ('No countries is valid', averages, 200),
        ('No observations stays null', averages + '?country=ROU&first_year=2025&last_year=2025', 200),
        ('Unknown indicator', '/api/indicators/UNKNOWN/period-averages', 404),
        ('Zero-length period', averages + '?period_years=0', 422),
        ('Reversed years', averages + '?first_year=2024&last_year=2023', 422),
        ('Malformed year', averages + '?first_year=abc', 422),
        ('Too many countries', averages + '?' + too_many, 422),
        ('Unknown ISO3', averages + '?country=XXX', 422),
        ('GET never starts import', '/actions/load', 405),
    ]
    records = []
    with requests.Session() as client:
        for name, path, expected in cases:
            response = client.get(args.base_url.rstrip('/') + path, timeout=15)
            assert response.status_code == expected, f'{name}: HTTP {response.status_code}, expected {expected}'
            is_json = 'application/json' in response.headers.get('content-type', '')
            body = response.json() if is_json else {'html': True}
            if name == 'OpenAPI':
                assert all(route.startswith('/api/') for route in body['paths'])
                body = {'paths': body['paths']}
            elif name == 'SSR page preserved':
                assert '<script' not in response.text and 'matching observations' in response.text
            elif name == 'CSR shell':
                assert 'period-averages-page.js' in response.text and 'chart.js@4.4.1' in response.text
            elif name == 'DTP3 comparison':
                assert [row['country_iso3'] for row in body['series']] == ['FRA', 'ROU']
                assert len(body['periods']) == 5 and body['periods'][-1]['end'] == 2023
                assert all(isinstance(value, (int, float)) or value is None
                           for row in body['series'] for value in row['averages'])
            elif name == 'Duplicate country removed':
                assert len(body['series']) == 1
            elif name == 'No countries is valid':
                assert body['series'] == []
            elif name == 'No observations stays null':
                assert body['series'][0]['averages'] == [None]
            if path.startswith('/api/') and path != '/api/docs':
                assert is_json
            records.append({'name': name, 'path': path, 'status': response.status_code, 'body': body})
    evidence = {'verified_at': datetime.now(timezone.utc).isoformat(), 'base_url': args.base_url,
                'passed': len(records), 'requests': records}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'{len(records)} live HTTP checks passed; evidence: {args.output}')


if __name__ == '__main__':
    main()
