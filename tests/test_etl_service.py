"""Injected stub jobs test orchestration without downloads or database access."""
from threading import Lock
import pytest
from app.services.etl_service import EtlService, ExtractJob, ImportJob
from etl.step_result import StepResult, StepStatus, PipelineError


def test_expected_failure_is_visible_and_other_jobs_continue():
    def failed():
        raise PipelineError('Source unavailable')
    ok = StepResult('who', 'test', StepStatus.OK, 'Saved')
    service = EtlService([ExtractJob('worldbank', 'bad', failed), ExtractJob('who', 'good', lambda: ok)], [])
    result = service.extract_all()
    assert result.success_count == 1 and result.failure_count == 1
    assert result.steps[0].message == 'Source unavailable'


def test_import_order_and_programming_errors_are_not_hidden():
    calls = []
    def job(source):
        calls.append(source)
        return (StepResult(source, 'test', StepStatus.OK, 'Loaded'),)
    service = EtlService([], [ImportJob('worldbank', lambda: job('worldbank')), ImportJob('who', lambda: job('who'))])
    assert service.transform_and_load_all().all_succeeded
    assert calls == ['worldbank', 'who']
    def bug():
        raise TypeError('Programming bug')
    with pytest.raises(TypeError):
        EtlService([ExtractJob('who', 'bug', bug)], []).extract_all()


def test_overlapping_actions_are_not_run():
    lock = Lock()
    lock.acquire()
    result = EtlService([], [], lock=lock).extract_all()
    assert result.failure_count == 1 and result.steps[0].item == 'busy'
    lock.release()
