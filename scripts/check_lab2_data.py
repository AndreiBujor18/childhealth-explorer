"""Task 2.4: execute the committed SQL and validate the study's invariants."""
import json
import re
from datetime import datetime, timezone
from sqlalchemy import text
from app.database import get_engine
from etl.raw_files import ROOT, RAW
from etl.study import study, indicators
from etl.transform_worldbank import transform_worldbank_countries


def queries():
    chunks = re.split(r'^-- name: (\w+)\s*\n',
                      (ROOT / 'db/lab2_checks.sql').read_text(encoding='utf-8'), flags=re.MULTILINE)
    return dict(zip(chunks[1::2], chunks[2::2], strict=True))


def main():
    config = study()
    with get_engine().connect() as connection:
        connection.execute(text('SET TRANSACTION READ ONLY'))
        results = {name: [dict(r) for r in connection.execute(text(sql)).mappings()]
                   for name, sql in queries().items()}
        actual_countries = set(connection.scalars(text('SELECT iso3 FROM country')))
        flags = connection.scalar(text('SELECT count(*) FROM observation WHERE is_outlier'))
        revision = connection.scalar(text('SELECT version_num FROM alembic_version'))
    expected_countries = set(transform_worldbank_countries(RAW / 'worldbank/countries.json')['iso3'])
    catalog = {(r['source'], r['code']): r for r in indicators()}
    bounds_ok = True
    for row in results['check3']:
        item = catalog.get((row['source'], row['code']))
        if item is None:
            bounds_ok = False
            continue
        bounds_ok &= ((item.get('minimum') is None or row['minimum'] >= item['minimum'])
                      and (item.get('maximum') is None or row['maximum'] <= item['maximum']))
    pilot_gaps = [r for r in results['check7'] if r['iso3'] in config['pilot_countries']]
    passed = {'check1': actual_countries == expected_countries,
              'check2': not results['check2'], 'check3': bool(bounds_ok) and len(results['check3']) == len(catalog),
              'check4': {r['sex'] for r in results['check4']} == {config['sex']},
              'check5': results['check5'] == [{'null_values': 0, 'out_of_window': 0}],
              'check6': len(results['check6']) == len(catalog) and all(
                  r['rows_loaded'] == r['rows_stored'] for r in results['check6']),
              'check7': not pilot_gaps}
    result = {'checked_at': datetime.now(timezone.utc).isoformat(), 'alembic_revision': revision,
              'queries': results, 'checks_passed': passed, 'pilot_mortality_gaps': pilot_gaps,
              'outlier_rows': flags, 'all_passed': all(passed.values())}
    path = ROOT / 'docs/evidence/lab2-sql-checks.json'
    path.write_text(json.dumps(result, indent=2, default=str) + '\n', encoding='utf-8')
    for name, ok in passed.items():
        print(name, 'PASS' if ok else 'FAIL')
    print('Country catalog:', len(actual_countries), '| mortality gaps outside pilot:', len(results['check7']),
          '| pilot gaps:', len(pilot_gaps))
    if not result['all_passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
