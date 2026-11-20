"""Public JSON contracts, kept separate from domain values and ORM models."""
from pydantic import BaseModel
from app.domain import Option


class CountryResponse(BaseModel):
    iso3: str
    name: str

    @classmethod
    def from_option(cls, option: Option) -> 'CountryResponse':
        return cls(iso3=option.value, name=option.label)


class IndicatorResponse(BaseModel):
    code: str
    name: str

    @classmethod
    def from_option(cls, option: Option) -> 'IndicatorResponse':
        return cls(code=option.value, name=option.label)
