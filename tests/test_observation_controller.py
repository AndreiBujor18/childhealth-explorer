"""HTTP rendering with dependency overrides: no live database or downloads."""
from dataclasses import replace
from app.dependencies import get_observation_service
from app.services.observation_service import ObservationService
from tests.fakes import MemoryRepository, example_items


def use_fake(client, items=None):
    client.app.dependency_overrides[get_observation_service] = lambda: ObservationService(MemoryRepository(items), 2)


def test_server_rendered_table_and_pagination_preserve_region(client):
    use_fake(client)
    response = client.get('/?region=Sub-Saharan+Africa')
    assert response.status_code == 200 and '<script' not in response.text
    assert response.text.count('<td class="country">Kenya') == 2
    assert 'region=Sub-Saharan+Africa&amp;page=2' in response.text
    assert 'value="Sub-Saharan Africa" selected' in response.text
    next_page = client.get('/?region=Sub-Saharan+Africa&page=2')
    assert next_page.text.count('<td class="country">Kenya') == 1


def test_invalid_fields_empty_results_and_error_translation(client):
    use_fake(client)
    assert client.get('/?year_from=abc').status_code == 200
    assert client.get('/?page=0').status_code == 422
    response = client.get('/?year_from=2023&year_to=2000')
    assert response.status_code == 400 and 'start year' in response.text
    assert 'No observations match' in client.get('/?country=XXX').text


def test_external_labels_are_autoescaped(client):
    items = (replace(example_items()[0], country_name='<script>alert(1)</script>'),)
    use_fake(client, items)
    page = client.get('/')
    assert '&lt;script&gt;alert(1)&lt;/script&gt;' in page.text
    assert '<script>' not in page.text


def test_json_documentation_is_disabled(client):
    assert client.get('/docs').status_code == 404
    assert client.get('/openapi.json').status_code == 404
