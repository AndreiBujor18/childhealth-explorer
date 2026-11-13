"""Normalize the strings submitted by an HTML GET form."""
from app.domain import Sex


def blank_to_none(value: str | None) -> str | None:
    return value.strip() or None if value is not None else None


def to_int_or_none(value: str | None) -> int | None:
    try:
        number = int(value) if value else None
        return number if number is not None and 1900 <= number <= 2100 else None
    except ValueError:
        return None


def to_sex_or_none(value: str | None) -> Sex | None:
    try:
        return Sex(value) if value else None
    except ValueError:
        return None
