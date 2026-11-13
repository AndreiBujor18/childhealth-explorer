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
