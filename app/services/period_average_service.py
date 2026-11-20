"""Period rules and series alignment; independent of SQL, HTTP and templates."""
from decimal import Decimal, ROUND_HALF_UP
from typing import Protocol
from app.domain import (CountrySeries, IndicatorInfo, Option, Period, PeriodAverage,
                        PeriodAverageQuery, PeriodAverageReport)
from app.models import Sex

DEFAULT_FIRST_YEAR = 2000
DEFAULT_LAST_YEAR = 2023
DEFAULT_PERIOD_YEARS = 5
MAX_API_COUNTRIES = 20


class InvalidQueryError(ValueError):
    pass


class UnknownIndicatorError(ValueError):
    pass


class PeriodAverageReader(Protocol):
    def find_indicator(self, code: str) -> IndicatorInfo | None: ...
    def find_countries(self, iso3s: tuple[str, ...]) -> tuple[Option, ...]: ...
    def average_by_period(self, query: PeriodAverageQuery, *, sex: Sex) -> tuple[PeriodAverage, ...]: ...


def _validate(query: PeriodAverageQuery) -> None:
    if query.period_years < 1:
        raise InvalidQueryError('Period length must be at least one year.')
    if not 1900 <= query.first_year <= query.last_year <= 2100:
        raise InvalidQueryError('Years must be ordered and between 1900 and 2100.')
    if len(query.country_iso3s) > MAX_API_COUNTRIES:
        raise InvalidQueryError(f'Select at most {MAX_API_COUNTRIES} countries.')
    if any(len(code) != 3 or not code.isascii() or not code.isalpha() or not code.isupper()
           for code in query.country_iso3s):
        raise InvalidQueryError('Countries must use uppercase three-letter ISO3 codes.')


class PeriodAverageService:
    def __init__(self, repository: PeriodAverageReader):
        self._repository = repository

    def get_report(self, query: PeriodAverageQuery) -> PeriodAverageReport:
        _validate(query)
        indicator = self._repository.find_indicator(query.indicator_code)
        if indicator is None:
            raise UnknownIndicatorError(f'Unknown indicator {query.indicator_code!r}.')
        periods = tuple(Period(start, min(start + query.period_years - 1, query.last_year))
                        for start in range(query.first_year, query.last_year + 1, query.period_years))
        countries = self._repository.find_countries(query.country_iso3s)
        if len(countries) != len(set(query.country_iso3s)):
            raise InvalidQueryError('One or more country codes are unknown.')
        rows = self._repository.average_by_period(query, sex=Sex.BOTH)
        values = {(row.country_iso3, row.period_start): row.average.quantize(Decimal('0.01'),
                                                                           rounding=ROUND_HALF_UP)
                  for row in rows}
        series = tuple(CountrySeries(country.value, country.label,
                                     tuple(values.get((country.value, period.start)) for period in periods))
                       for country in countries)
        return PeriodAverageReport(indicator, periods, series)
