"""Actions use fake services; tests cannot download files or modify live data."""
from app.dependencies import get_etl_service
from app.services.etl_service import ActionResult
from etl.step_result import StepResult, StepStatus


class FakeEtlService:
    def __init__(self): self.calls = []
    def extract_all(self):
        self.calls.append('extract')
        return ActionResult((StepResult('who', 'TEST', StepStatus.FAILED, '<script>alert(1)</script>'),))
    def transform_and_load_all(self):
        self.calls.append('load')
        return ActionResult((StepResult('who', 'TEST', StepStatus.OK, 'Saved', rows_loaded=1, updated_rows=1),))


def test_actions_are_post_only_and_render_escaped_results(client):
    service = FakeEtlService()
    client.app.dependency_overrides[get_etl_service] = lambda: service
    assert client.get('/actions/extract').status_code == 405
    assert client.get('/actions/load').status_code == 405
    assert service.calls == []
    response = client.post('/actions/extract')
    assert response.status_code == 200 and 'Failed' in response.text
    assert '&lt;script&gt;' in response.text and '<script>' not in response.text
    response = client.post('/actions/load')
    assert response.status_code == 200 and 'Loaded' in response.text
    assert service.calls == ['extract', 'load']
