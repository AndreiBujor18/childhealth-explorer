"""Periods, rounding and empty gaps using a plain fake repository."""
from dataclasses import replace
from decimal import Decimal
import pytest
from app.domain import IndicatorInfo, Option, PeriodAverage, PeriodAverageQuery
from app.models import Sex
from app.services.period_average_service import InvalidQueryError, PeriodAverageService, UnknownIndicatorError


class FakeAverageRepository:
    def find_indicator(self, code):
        return IndicatorInfo(code, 'Vaccination', '%') if code == 'DTP3' else None

    def find_countries(self, codes):
        return tuple(Option(code, name) for code, name in [('FRA', 'France'), ('ROU', 'Romania')]
                     if code in codes)

    def average_by_period(self, query, *, sex):
        assert sex == Sex.BOTH
        return (PeriodAverage('ROU', 2000, Decimal('12.345'), 2),
                PeriodAverage('ROU', 2020, Decimal('79'), 1))


def test_round_half_up_short_final_period_and_fully_missing_country():
    report = PeriodAverageService(FakeAverageRepository()).get_report(
        PeriodAverageQuery('DTP3', ('ROU', 'FRA')))
    assert [(p.start, p.end) for p in report.periods] == [
        (2000, 2004), (2005, 2009), (2010, 2014), (2015, 2019), (2020, 2023)]
    assert [s.country_iso3 for s in report.series] == ['FRA', 'ROU']
    assert report.series[0].averages == (None,) * 5
    assert report.series[1].averages == (Decimal('12.35'), None, None, None, Decimal('79.00'))


@pytest.mark.parametrize('change', [dict(period_years=0), dict(first_year=2024), dict(first_year=1899),
                                    dict(country_iso3s=('rou',)), dict(country_iso3s=('XXX',)),
                                    dict(country_iso3s=tuple(f'A{chr(65+i)}A' for i in range(21)))])
def test_invalid_queries(change):
    with pytest.raises(InvalidQueryError):
        PeriodAverageService(FakeAverageRepository()).get_report(replace(PeriodAverageQuery('DTP3'), **change))


def test_unknown_indicator_and_single_year():
    service = PeriodAverageService(FakeAverageRepository())
    with pytest.raises(UnknownIndicatorError):
        service.get_report(PeriodAverageQuery('UNKNOWN'))
    report = service.get_report(PeriodAverageQuery('DTP3', first_year=2023, last_year=2023))
    assert len(report.periods) == 1 and report.periods[0].start == report.periods[0].end == 2023
    assert report.series == ()
