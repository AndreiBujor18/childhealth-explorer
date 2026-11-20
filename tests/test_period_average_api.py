"""DTO shape and error mapping with fake services, plus one seeded full-stack request."""
from decimal import Decimal
import pytest
from app.dependencies import get_period_average_service
from app.domain import CountrySeries, IndicatorInfo, Period, PeriodAverageReport
from app.services.period_average_service import InvalidQueryError, UnknownIndicatorError
from tests.test_reference_data_api import use_seed

URL = '/api/indicators/MORT/period-averages'


class FakeService:
    def __init__(self, error=None):
        self.error = error
        self.query = None

    def get_report(self, query):
        self.query = query
        if self.error:
            raise self.error
        return PeriodAverageReport(IndicatorInfo('MORT', 'Mortality', 'per 1,000 births'),
                                   (Period(2000, 2004), Period(2005, 2009)),
                                   (CountrySeries('ROU', 'Romania', (Decimal('6.90'), None)),))


def test_numeric_dto_deduplicated_countries_and_defaults(client):
    service = FakeService()
    client.app.dependency_overrides[get_period_average_service] = lambda: service
    response = client.get(URL + '?country=ROU&country=FRA&country=ROU')
    assert response.status_code == 200
    data = response.json()
    assert set(data) == {'indicator', 'periods', 'series'}
    assert data['series'][0] == {'country_iso3': 'ROU', 'country_name': 'Romania', 'averages': [6.9, None]}
    assert isinstance(data['series'][0]['averages'][0], float)
    assert service.query.country_iso3s == ('ROU', 'FRA')
    assert (service.query.first_year, service.query.last_year, service.query.period_years) == (2000, 2023, 5)


@pytest.mark.parametrize('error,code', [(UnknownIndicatorError('unknown indicator'), 404),
                                       (InvalidQueryError('invalid years'), 422)])
def test_service_errors_become_json_errors(client, error, code):
    client.app.dependency_overrides[get_period_average_service] = lambda: FakeService(error)
    response = client.get(URL)
    assert response.status_code == code and response.json() == {'detail': str(error)}


@pytest.mark.parametrize('query', ['period_years=0', 'first_year=abc'])
def test_malformed_parameters_rejected_before_service_method(client, query):
    service = FakeService(AssertionError('Malformed input reached the service method'))
    client.app.dependency_overrides[get_period_average_service] = lambda: service
    response = client.get(URL + '?' + query)
    assert response.status_code == 422 and isinstance(response.json()['detail'], list)
    assert service.query is None


def test_real_service_repository_and_dto_together(client, repository_session):
    use_seed(client, repository_session)
    client.app.dependency_overrides.pop(get_period_average_service, None)
    response = client.get(URL + '?country=ROU&country=FRA&first_year=2020&last_year=2023')
    assert response.status_code == 200
    assert [s['averages'] for s in response.json()['series']] == [[4.0], [6.9]]
    assert client.get('/api/indicators/UNKNOWN/period-averages').status_code == 404
    assert client.get(URL + '?first_year=2024&last_year=2023').status_code == 422
