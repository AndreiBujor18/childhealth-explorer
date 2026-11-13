"""Shared transform/clean/load orchestration; repositories own every query."""
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError
from app.repositories.import_repository import ImportRepository
from etl.clean import clean_observations
from etl.raw_files import RAW, read_snapshot
from etl.step_result import StepResult, StepStatus
from etl.study import study, indicators, raw_path
from etl.transform import transform_indicator
from etl.transform_worldbank import transform_worldbank_countries

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ImportRun:
    report: dict
    steps: tuple[StepResult, ...]


def failure(source, item, error):
    logger.exception('%s/%s: import failed', source, item)
    message = 'Database operation failed. Check the local server log.' if isinstance(error, SQLAlchemyError) else str(error)
    return StepResult(source, item, StepStatus.FAILED, message[:250])


def run_source_import(source, session_factory):
    config = study()
    reports, failures, steps = [], [], []
    with session_factory() as session:
        repository = ImportRepository(session)
        try:
            if source == 'worldbank':
                countries = transform_worldbank_countries(RAW / 'worldbank/countries.json')
                with session.begin():
                    repository.load_countries(countries.to_dict(orient='records'))
            valid = repository.list_valid_countries()
            session.rollback()
            if not valid:
                raise ValueError('Country catalog is empty. Import World Bank countries first.')
        except (ValueError, OSError, SQLAlchemyError) as error:
            session.rollback()
            steps.append(failure(source, 'countries', error))
            failures.append('countries')
            valid = []
        for item in indicators(source) if valid else ():
            try:
                path = raw_path(item)
                meta = read_snapshot(path)
                frame = transform_indicator(item)
                cleaned = clean_observations(frame, valid, [item], countries=config['pilot_countries'],
                                             year_window=(config['start_year'], config['end_year']),
                                             sex=config['sex'])
                with session.begin():
                    indicator_id = repository.ensure_indicator(item)
                    stats = repository.load_observations(cleaned, indicator_id)
                    repository.record_import(source, item['code'], meta['requests'][0]['url'], stats['rows_loaded'])
                reports.append({'source': source, 'indicator': item['code'], **cleaned.attrs, **stats,
                                'outliers': int(cleaned['is_outlier'].sum()), 'snapshot_sha256': meta['sha256'],
                                'requests': meta['requests']})
                steps.append(StepResult(source, item['code'], StepStatus.OK, 'Saved observations and import log.',
                                        raw_rows=len(frame), clean_rows=len(cleaned),
                                        rejected_rows=cleaned.attrs['rejected_rows'], **stats))
            except (ValueError, OSError, SQLAlchemyError) as error:
                session.rollback()
                failures.append(item['code'])
                steps.append(failure(source, item['code'], error))
    return ImportRun({'source': source, 'finished_at': datetime.now(timezone.utc).isoformat(),
                      'indicators': reports, 'failed': failures}, tuple(steps))
