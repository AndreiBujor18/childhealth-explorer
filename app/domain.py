"""Immutable values crossing layer boundaries; no ORM rows or HTTP objects."""
from dataclasses import dataclass
from decimal import Decimal
from app.models import Sex


@dataclass(frozen=True)
class ObservationCriteria:
    country_iso3: str | None = None
    indicator_code: str | None = None
    region: str | None = None
    year_from: int | None = None
    year_to: int | None = None
    source_name: str | None = None
    sex: Sex | None = None


@dataclass(frozen=True)
class ObservationListItem:
    country_name: str
    country_iso3: str
    region: str | None
    source_name: str
    indicator_code: str
    indicator_name: str
    unit: str | None
    year: int
    sex: Sex
    value: Decimal | None
    is_outlier: bool


@dataclass(frozen=True)
class Option:
    value: str
    label: str


@dataclass(frozen=True)
class FilterOptions:
    countries: tuple[Option, ...]
    indicators: tuple[Option, ...]
    regions: tuple[Option, ...]
    sources: tuple[Option, ...]
    sexes: tuple[Option, ...] = ()


@dataclass(frozen=True)
class IndicatorInfo:
    code: str
    name: str
    unit: str | None


@dataclass(frozen=True)
class PeriodAverageQuery:
    indicator_code: str
    country_iso3s: tuple[str, ...] = ()
    first_year: int = 2000
    last_year: int = 2023
    period_years: int = 5


@dataclass(frozen=True)
class Period:
    start: int
    end: int

    @property
    def label(self) -> str:
        return f'{self.start}\N{EN DASH}{self.end}'


@dataclass(frozen=True)
class PeriodAverage:
    country_iso3: str
    period_start: int
    average: Decimal
    observation_count: int


@dataclass(frozen=True)
class CountrySeries:
    country_iso3: str
    country_name: str
    averages: tuple[Decimal | None, ...]


@dataclass(frozen=True)
class PeriodAverageReport:
    indicator: IndicatorInfo
    periods: tuple[Period, ...]
    series: tuple[CountrySeries, ...]
