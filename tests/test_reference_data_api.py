"""JSON lookups use the same services/repositories as the HTML browser."""
from app.database import get_db
from app.dependencies import get_observation_service
from app.repositories.observation_repository import ObservationRepository
from app.services.observation_service import ObservationService


def use_seed(client, repository_session):
    client.app.dependency_overrides[get_db] = lambda: repository_session
    client.app.dependency_overrides.pop(get_observation_service, None)


def test_country_region_lookup_and_json_contract(client, repository_session):
    use_seed(client, repository_session)
    assert client.get('/api/countries', params={'region': 'Europe & Central Asia'}).json() == [
        {'iso3': 'FRA', 'name': 'France'}, {'iso3': 'ROU', 'name': 'Romania'}]
    assert len(client.get('/api/countries').json()) == 4
    assert client.get('/api/countries?region=Unknown').json() == []
    assert client.get('/api/regions').json() == [
        'Europe & Central Asia', 'North America', 'Sub-Saharan Africa']
    indicators = client.get('/api/indicators').json()
    assert {r['code'] for r in indicators} == {'MORT', 'GDP'}
    assert all(set(r) == {'code', 'name'} for r in indicators)


def test_only_json_endpoints_in_openapi_and_docs_need_no_database(client):
    response = client.get('/api/openapi.json')
    assert response.status_code == 200
    paths = response.json()['paths']
    assert {'/api/regions', '/api/countries', '/api/indicators'} <= paths.keys()
    assert all(path.startswith('/api/') for path in paths)
    assert client.get('/api/docs').status_code == 200


def test_service_countries_does_not_change_ssr_labels(repository_session):
    repository = ObservationRepository(repository_session)
    assert ObservationService(repository).list_countries('North America')[0].label == 'United States'
    assert repository.list_countries('North America')[0].label == 'United States (USA)'
