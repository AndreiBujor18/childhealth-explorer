"""Real PostgreSQL aggregation in a rolled-back schema, never project data."""
from decimal import Decimal
from app.domain import PeriodAverageQuery
from app.models import Observation, Sex
from app.repositories.period_average_repository import PeriodAverageRepository
from app.services.period_average_service import PeriodAverageService


def test_buckets_boundaries_nulls_and_only_both_sexes(repository_session):
    repository_session.add_all([
        Observation(country_iso3='ROU', indicator_id=1, year=2020, sex='BTSX', value=Decimal('9.1')),
        Observation(country_iso3='ROU', indicator_id=1, year=2019, sex='BTSX', value=Decimal('12')),
        Observation(country_iso3='ROU', indicator_id=1, year=2018, sex='BTSX', value=None),
        Observation(country_iso3='ROU', indicator_id=1, year=2024, sex='BTSX', value=Decimal('100')),
    ])
    repository_session.flush()
    repository = PeriodAverageRepository(repository_session)
    rows = repository.average_by_period(PeriodAverageQuery('MORT', ('ROU',), 2015, 2023, 5), sex=Sex.BOTH)
    assert [(r.period_start, r.average, r.observation_count) for r in rows] == [
        (2015, Decimal('12'), 1), (2020, Decimal('8'), 2)]
    assert repository.find_indicator('UNKNOWN') is None
    assert repository.find_indicator('MORT').unit == 'per 1,000 births'
    assert repository.average_by_period(PeriodAverageQuery('MORT'), sex=Sex.BOTH) == ()


def test_known_country_without_indicator_data_stays_as_null_series(repository_session):
    repository_session.query(Observation).filter(Observation.country_iso3 == 'KEN',
                                                Observation.indicator_id == 1).delete()
    report = PeriodAverageService(PeriodAverageRepository(repository_session)).get_report(
        PeriodAverageQuery('MORT', ('KEN',)))
    assert report.series[0].country_iso3 == 'KEN'
    assert report.series[0].averages == (None,) * 5
