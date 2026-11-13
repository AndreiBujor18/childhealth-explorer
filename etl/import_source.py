"""CLI compatibility and result reporting over the shared import runner."""
import json
import logging
from app.database import get_session_factory
from etl.import_runner import run_source_import
from etl.raw_files import ROOT


def import_results(source, session_factory=None):
    return run_source_import(source, session_factory or get_session_factory()).steps


def import_source(source):
    run = run_source_import(source, get_session_factory())
    out = ROOT / '.local/imports'
    out.mkdir(parents=True, exist_ok=True)
    (out / f'{source}-latest.json').write_text(json.dumps(run.report, indent=2) + '\n', encoding='utf-8')
    for step in run.steps:
        print(f'{step.source}/{step.item}: {step.status.value} raw={step.raw_rows} clean={step.clean_rows} '
              f'rejected={step.rejected_rows} loaded={step.rows_loaded} new={step.new_rows} '
              f'updated={step.updated_rows} | {step.message}', flush=True)
    if run.report['failed']:
        raise RuntimeError(f"Failed {source} indicators: {', '.join(run.report['failed'])}")
    return run.report


def main(source):
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    import_source(source)
