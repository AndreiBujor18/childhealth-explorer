"""Stable data contract: new APIs implement this interface."""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Protocol


@dataclass(frozen=True)
class ObservationRecord:
    source_name: str
    indicator_code: str
    country_iso3: str
    year: int
    sex: str
    value: Decimal | None


class SourceAdapter(Protocol):
    def fetch(self, indicator: str, countries: list[str], start: int, end: int) -> list[ObservationRecord]:
        """Return normalized records; preserve missing values as None."""
        ...


def numeric(value) -> Decimal | None:
    if value is None or value == '':
        return None
    try:
        number = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f'Invalid numeric observation: {value!r}') from exc
    if not number.is_finite():
        raise ValueError(f'Non-finite observation: {value!r}')
    return number


def validate(records, indicator, countries, start, end):
    """Reject inconsistent records before any eventual database write."""
    seen = set()
    for record in records:
        if record.source_name != indicator['source'] or record.indicator_code != indicator['code']:
            raise ValueError('Source/indicator mismatch')
        if record.country_iso3 not in countries or not start <= record.year <= end:
            raise ValueError('Unexpected country/year')
        if record.sex not in {'BTSX', 'MLE', 'FMLE'}:
            raise ValueError('Unexpected sex code')
        key = (record.source_name, record.indicator_code, record.country_iso3, record.year, record.sex)
        if key in seen:
            raise ValueError(f'Duplicate observation: {key}')
        seen.add(key)
        if record.value is not None:
            if not record.value.is_finite():
                raise ValueError('Non-finite observation')
            for bound, operator in [('minimum', lambda x, y: x < y), ('maximum', lambda x, y: x > y)]:
                value = indicator.get(bound)
                if value is not None and operator(record.value, Decimal(str(value))):
                    raise ValueError(f'Observation outside {bound}: {record}')
    return records
