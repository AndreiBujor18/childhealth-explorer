"""Import saved snapshots; each indicator and its log commit atomically."""
import json
import logging
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.database import get_engine
from app.models import Country
from etl.clean import clean_observations
from etl.load import upsert_countries, get_or_create_source, get_or_create_indicator, upsert_observations, log_import
from etl.raw_files import RAW, ROOT, read_snapshot
from etl.study import study, indicators, raw_path
from etl.transform import transform_indicator
from etl.transform_worldbank import transform_worldbank_countries

logger = logging.getLogger(__name__)


def import_source(source):
    config = study()
    reports, failures = [], []
    with Session(get_engine()) as session:
        if source == 'worldbank':
            countries = transform_worldbank_countries(RAW / 'worldbank/countries.json')
            with session.begin():
                upsert_countries(session, countries.to_dict(orient='records'))
        valid = list(session.scalars(select(Country.iso3)))
        session.rollback()
        if not valid:
            raise ValueError('Country table is empty; run python -m etl.import_worldbank first')
        for item in indicators(source):
            try:
                path = raw_path(item)
                meta = read_snapshot(path)
                frame = transform_indicator(item)
                cleaned = clean_observations(frame, valid, [item], countries=config['pilot_countries'],
                                             year_window=(config['start_year'], config['end_year']),
                                             sex=config['sex'])
                with session.begin():
                    source_id = get_or_create_source(session, source)
                    indicator_id = get_or_create_indicator(session, item, source_id)
                    stats = upsert_observations(session, cleaned, indicator_id)
                    log_import(session, source, item['code'], meta['requests'][0]['url'], stats['rows_loaded'])
                report = {'source': source, 'indicator': item['code'], **cleaned.attrs, **stats,
                          'outliers': int(cleaned['is_outlier'].sum()), 'snapshot_sha256': meta['sha256'],
                          'requests': meta['requests']}
                reports.append(report)
                print(f"{source}/{item['code']}: raw={len(frame)} clean={len(cleaned)} "
                      f"rejected={report['rejected_rows']} loaded={stats['rows_loaded']} "
                      f"new={stats['new_rows']} updated={stats['updated_rows']}", flush=True)
            except (ValueError, OSError, SQLAlchemyError):
                session.rollback()
                logger.exception('%s/%s: import failed', source, item['code'])
                failures.append(item['code'])
    out = ROOT / '.local/imports'
    out.mkdir(parents=True, exist_ok=True)
    result = {'source': source, 'finished_at': datetime.now(timezone.utc).isoformat(),
              'indicators': reports, 'failed': failures}
    (out / f'{source}-latest.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    if failures:
        raise RuntimeError(f"Failed {source} indicators: {', '.join(failures)}")
    return result


def main(source):
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    import_source(source)
