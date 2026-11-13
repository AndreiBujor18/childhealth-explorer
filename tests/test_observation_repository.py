"""Repository queries use only a rolled-back synthetic PostgreSQL dataset."""
from app.domain import ObservationCriteria
from app.repositories.observation_repository import ObservationRepository


def test_stable_pagination_and_domain_values(repository_session):
    repo = ObservationRepository(repository_session)
    all_rows = repo.find(ObservationCriteria(), limit=100, offset=0)
    assert repo.count(ObservationCriteria()) == 9
    assert [r.country_iso3 for r in all_rows] == ['FRA', 'FRA', 'KEN', 'KEN', 'ROU', 'ROU', 'ROU', 'ROU', 'USA']
    pages = tuple(r for n in (0, 4, 8) for r in repo.find(ObservationCriteria(), limit=4, offset=n))
    assert pages == all_rows
    assert all(type(r).__name__ == 'ObservationListItem' for r in all_rows)


def test_region_country_indicator_and_year_filters(repository_session):
    repo = ObservationRepository(repository_session)
    criteria = ObservationCriteria(region='Sub-Saharan Africa', indicator_code='MORT', year_from=2023)
    rows = repo.find(criteria, limit=25, offset=0)
    assert repo.count(criteria) == 1 and rows[0].country_iso3 == 'KEN'
    assert repo.count(ObservationCriteria(country_iso3='ROU', year_to=2022)) == 1
    assert repo.count(ObservationCriteria(country_iso3="ROU' OR 1=1 --")) == 0


def test_filter_options_come_from_observed_data(repository_session):
    repo = ObservationRepository(repository_session)
    assert [r.value for r in repo.list_countries()] == ['FRA', 'KEN', 'ROU', 'USA']
    assert {r.value for r in repo.list_indicators()} == {'MORT', 'GDP'}
    assert len(repo.list_regions()) == 3
    assert repo.list_sources()[0].value == 'worldbank'
