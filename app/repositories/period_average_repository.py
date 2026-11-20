"""Aggregate in PostgreSQL; return plain values and leave transactions to callers."""
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.domain import IndicatorInfo, Option, PeriodAverage, PeriodAverageQuery
from app.models import Country, Indicator, Observation, Sex


class PeriodAverageRepository:
    def __init__(self, session: Session):
        self._session = session

    def find_indicator(self, code: str) -> IndicatorInfo | None:
        row = self._session.execute(select(Indicator.code, Indicator.name, Indicator.unit)
                                    .where(Indicator.code == code)).one_or_none()
        return IndicatorInfo(*row) if row is not None else None

    def find_countries(self, iso3s: tuple[str, ...]) -> tuple[Option, ...]:
        query = select(Country.iso3, Country.name).where(Country.iso3.in_(iso3s)).order_by(Country.name)
        return tuple(Option(code, name) for code, name in self._session.execute(query))

    def average_by_period(self, query: PeriodAverageQuery, *, sex: Sex) -> tuple[PeriodAverage, ...]:
        period_start = (query.first_year + (Observation.year - query.first_year)
                        // query.period_years * query.period_years)
        bucketed = (select(Observation.country_iso3, period_start.label('period_start'), Observation.value)
                    .join(Indicator).where(Indicator.code == query.indicator_code,
                                           Observation.country_iso3.in_(query.country_iso3s),
                                           Observation.year.between(query.first_year, query.last_year),
                                           Observation.sex == sex.value, Observation.value.is_not(None))
                    .subquery())
        statement = (select(bucketed.c.country_iso3, bucketed.c.period_start,
                            func.avg(bucketed.c.value), func.count())
                     .group_by(bucketed.c.country_iso3, bucketed.c.period_start)
                     .order_by(bucketed.c.country_iso3, bucketed.c.period_start))
        return tuple(PeriodAverage(*row) for row in self._session.execute(statement))
