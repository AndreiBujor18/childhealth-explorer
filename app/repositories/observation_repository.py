"""The observation browser's only SQL boundary; never commits transactions."""
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.domain import ObservationCriteria, ObservationListItem, Option
from app.models import Country, Indicator, Observation, Source, Sex

STABLE_ORDER = (Country.name, Observation.year.desc(), Source.name, Indicator.code,
                Observation.sex, Observation.observation_id)


def _conditions(criteria: ObservationCriteria):
    conditions = []
    for value, column in [(criteria.country_iso3, Country.iso3), (criteria.indicator_code, Indicator.code),
                          (criteria.region, Country.region), (criteria.source_name, Source.name)]:
        if value is not None:
            conditions.append(column == value)
    if criteria.year_from is not None:
        conditions.append(Observation.year >= criteria.year_from)
    if criteria.year_to is not None:
        conditions.append(Observation.year <= criteria.year_to)
    if criteria.sex is not None:
        conditions.append(Observation.sex == criteria.sex.value)
    return conditions


def _matching_observations(criteria):
    return (select(Country.name.label('country_name'), Country.iso3.label('country_iso3'),
                   Country.region, Source.name.label('source_name'), Indicator.code.label('indicator_code'),
                   Indicator.name.label('indicator_name'), Indicator.unit, Observation.year,
                   Observation.sex, Observation.value, Observation.is_outlier)
            .select_from(Observation).join(Country).join(Indicator).join(Source)
            .where(*_conditions(criteria)))


class ObservationRepository:
    def __init__(self, session: Session):
        self._session = session

    def find(self, criteria, *, limit: int, offset: int) -> tuple[ObservationListItem, ...]:
        query = _matching_observations(criteria).order_by(*STABLE_ORDER).limit(limit).offset(offset)
        return tuple(ObservationListItem(**{**r, 'sex': Sex(r['sex'])})
                     for r in self._session.execute(query).mappings())

    def count(self, criteria) -> int:
        return self._session.scalar(select(func.count()).select_from(_matching_observations(criteria).subquery())) or 0

    def list_countries(self) -> tuple[Option, ...]:
        query = (select(Country.iso3, Country.name).join(Observation).distinct().order_by(Country.name))
        return tuple(Option(code, f'{name} ({code})') for code, name in self._session.execute(query))

    def list_indicators(self) -> tuple[Option, ...]:
        query = (select(Indicator.code, Indicator.name, Source.name).select_from(Indicator)
                 .join(Source).join(Observation).distinct().order_by(Indicator.name, Source.name))
        return tuple(Option(code, f'{name} / {source}') for code, name, source in self._session.execute(query))

    def list_regions(self) -> tuple[Option, ...]:
        query = (select(Country.region).join(Observation).where(Country.region.is_not(None))
                 .distinct().order_by(Country.region))
        return tuple(Option(r, r) for r in self._session.scalars(query))

    def list_sources(self) -> tuple[Option, ...]:
        query = (select(Source.name).select_from(Observation).join(Indicator).join(Source)
                 .distinct().order_by(Source.name))
        return tuple(Option(s, {'who': 'WHO', 'owid': 'Our World in Data',
                               'unicef': 'UNICEF', 'worldbank': 'World Bank'}.get(s, s))
                     for s in self._session.scalars(query))
