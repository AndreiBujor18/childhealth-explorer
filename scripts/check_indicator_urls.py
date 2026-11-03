"""Check the seven documented URLs live without replacing the study snapshot."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from etl.contracts import ObservationRecord, numeric, validate
from etl.extract_unicef import parse_sdmx

ROOT = Path(__file__).resolve().parent.parent
CHECK_DATE = datetime.now(timezone.utc).date().isoformat()


def check(item):
    indicator, url = item
    session = requests.Session()
    session.headers['User-Agent'] = 'ChildHealthExplorer/0.1 (academic URL verification)'
    session.mount('https://', HTTPAdapter(max_retries=Retry(
        total=2, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=['GET'], respect_retry_after_header=True)))
    result = {'code': indicator['code'], 'source': indicator['source'], 'requested_url': url}
    try:
        response = session.get(url, timeout=(15, 50))
        result.update(status=response.status_code, final_url=response.url,
                      checked_at=datetime.now(timezone.utc).isoformat(),
                      content_type=response.headers.get('Content-Type'),
                      content_disposition=response.headers.get('Content-Disposition'),
                      sha256=hashlib.sha256(response.content).hexdigest(), bytes=len(response.content))
        response.raise_for_status()
        document = response.json()
        cache = ROOT / f'data/raw/url-check-{CHECK_DATE}'
        cache.mkdir(parents=True, exist_ok=True)
        (cache / (indicator['code'] + '.json')).write_bytes(response.content)
        if indicator['source'] == 'unicef':
            records = parse_sdmx(document, indicator['code'], ['ROU'], 2000, 2023)
            result['response_shape'] = 'data.structure + data.dataSets (SDMX dimension indexes)'
        else:
            assert isinstance(document, list) and len(document) == 2
            assert int(document[0]['pages']) == 1, 'The documented URL now needs pagination.'
            assert all(row['indicator']['id'] == indicator['code'] for row in document[1])
            records = [ObservationRecord('worldbank', indicator['code'], row['countryiso3code'],
                                        int(row['date']), 'BTSX', numeric(row['value']))
                       for row in document[1]]
            result['response_shape'] = '[pagination metadata, records]'
        validate(records, indicator, ['ROU'], 2000, 2023)
        assert len(records) == 24 and {r.year for r in records} == set(range(2000, 2024))
        latest = max(records, key=lambda r: r.year)
        result.update(valid=True, records=len(records), non_null=sum(r.value is not None for r in records),
                      country='ROU', sex='BTSX', first_year=min(r.year for r in records),
                      last_year=latest.year, latest_value=str(latest.value), unit=indicator['unit'])
    except (requests.RequestException, ValueError, KeyError, AssertionError, TypeError) as exc:
        result.update(valid=False, error=str(exc))
    finally:
        session.close()
    return result


def main():
    indicators = json.loads((ROOT / 'config/indicators.json').read_text(encoding='utf-8'))
    urls = re.findall(r'\]\((https://[^)]+)\)', (ROOT / 'docs/indicators.md').read_text(encoding='utf-8'))
    assert len(urls) == len(indicators) == 7
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(check, zip(indicators, urls, strict=True)))
    evidence = {'checked_at': datetime.now(timezone.utc).isoformat(),
                'method': 'Live HTTP GET of every documented URL; source-specific decoding and validation',
                'country': 'ROU', 'years': '2000-2023', 'study_snapshot_replaced': False,
                'database_modified': False, 'all_valid': all(r['valid'] for r in results), 'urls': results}
    path = ROOT / f'docs/evidence/url-check-{CHECK_DATE}.json'
    path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for row in results:
        print(row['code'], 'HTTP', row.get('status'), 'valid=' + str(row['valid']),
              'records=' + str(row.get('records')), flush=True)
    if not evidence['all_valid']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
