"""Compose pipeline callbacks from the same catalog used by the CLI."""
from functools import partial
from pathlib import Path
import requests
from etl.extract import download_indicator
from etl.extract_worldbank import download_worldbank_countries
from etl.step_result import StepResult, StepStatus, PipelineError
from etl.study import indicators
from etl.import_runner import run_source_import
from app.services.etl_service import ExtractJob, ImportJob


def extract_step(source, code, download):
    try:
        path, _ = download()
        path = Path(path)
        return StepResult(source, code, StepStatus.OK, f'{path.name} ({path.stat().st_size:,} bytes)')
    except (ValueError, OSError, requests.RequestException) as error:
        raise PipelineError(f'Download failed: {str(error)[:200]}') from error


def extraction_jobs():
    jobs = [ExtractJob('worldbank', 'countries', partial(extract_step, 'worldbank', 'countries',
                                                     download_worldbank_countries))]
    for item in indicators():
        jobs.append(ExtractJob(item['source'], item['code'], partial(
            extract_step, item['source'], item['code'], partial(download_indicator, item, refresh=True))))
    return tuple(jobs)


def import_steps(source, session_factory):
    return run_source_import(source, session_factory).steps


def import_jobs(session_factory):
    return tuple(ImportJob(source, partial(import_steps, source, session_factory))
                 for source in ['worldbank', 'who', 'owid', 'unicef'])
