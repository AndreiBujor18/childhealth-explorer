"""Task 2.3: execute two imports and prove stable values, flags and row counts."""
import hashlib
import json
from datetime import datetime, timezone
from sqlalchemy import text
from app.database import get_engine
from etl.import_all import SOURCES
from etl.import_source import import_source
from etl.raw_files import ROOT


def snapshot():
    with get_engine().connect() as connection:
        counts = [dict(r) for r in connection.execute(text('''
            SELECT s.name AS source, i.code, count(*) AS rows
            FROM observation o JOIN indicator i USING(indicator_id) JOIN source s USING(source_id)
            GROUP BY s.name,i.code ORDER BY s.name,i.code''')).mappings()]
        data = [list(r) for r in connection.execute(text('''
            SELECT s.name,i.code,o.country_iso3,o.year,o.sex,o.value,o.is_outlier
            FROM observation o JOIN indicator i USING(indicator_id) JOIN source s USING(source_id)
            ORDER BY s.name,i.code,o.country_iso3,o.year,o.sex'''))]
        duplicates = connection.scalar(text('''SELECT count(*) FROM (
            SELECT country_iso3,indicator_id,year,sex FROM observation
            GROUP BY country_iso3,indicator_id,year,sex HAVING count(*)>1) d'''))
        logs = [dict(r) for r in connection.execute(text('SELECT * FROM import_log ORDER BY import_id')).mappings()]
    return {'counts': counts, 'total_rows': sum(r['rows'] for r in counts), 'duplicates': duplicates,
            'content_sha256': hashlib.sha256(json.dumps(data, default=str).encode()).hexdigest(),
            'import_log_count': len(logs), 'import_log': logs}


def main():
    result = {'checked_at': datetime.now(timezone.utc).isoformat(), 'before': snapshot(), 'runs': []}
    for run in (1, 2):
        reports = [import_source(source) for source in SOURCES]
        result['runs'].append({'run': run, 'reports': reports, 'after': snapshot()})
    first, second = [r['after'] for r in result['runs']]
    result['passed'] = (first['counts'] == second['counts']
                        and first['content_sha256'] == second['content_sha256']
                        and first['duplicates'] == second['duplicates'] == 0
                        and second['import_log_count'] - first['import_log_count'] == 9
                        and all(p['new_rows'] == 0 for r in result['runs'][1]['reports'] for p in r['indicators']))
    path = ROOT / 'docs/evidence/lab2-imports.json'
    path.write_text(json.dumps(result, indent=2, default=str) + '\n', encoding='utf-8')
    print('Two-run idempotency:', result['passed'], '| observations:', second['total_rows'],
          '| import logs:', second['import_log_count'])
    if not result['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
