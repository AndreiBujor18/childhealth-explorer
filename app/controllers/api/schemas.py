"""Public JSON contracts, kept separate from domain values and ORM models."""
from pydantic import BaseModel
from app.domain import CountrySeries, IndicatorInfo, Option, Period, PeriodAverageReport


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


class IndicatorDetailResponse(BaseModel):
    code: str
    name: str
    unit: str | None

    @classmethod
    def from_domain(cls, indicator: IndicatorInfo) -> 'IndicatorDetailResponse':
        return cls(code=indicator.code, name=indicator.name, unit=indicator.unit)


class PeriodResponse(BaseModel):
    start: int
    end: int
    label: str

    @classmethod
    def from_domain(cls, period: Period) -> 'PeriodResponse':
        return cls(start=period.start, end=period.end, label=period.label)


class CountrySeriesResponse(BaseModel):
    country_iso3: str
    country_name: str
    averages: list[float | None]

    @classmethod
    def from_domain(cls, series: CountrySeries) -> 'CountrySeriesResponse':
        return cls(country_iso3=series.country_iso3, country_name=series.country_name,
                   averages=[float(value) if value is not None else None for value in series.averages])


class PeriodAveragesResponse(BaseModel):
    indicator: IndicatorDetailResponse
    periods: list[PeriodResponse]
    series: list[CountrySeriesResponse]

    @classmethod
    def from_domain(cls, report: PeriodAverageReport) -> 'PeriodAveragesResponse':
        return cls(indicator=IndicatorDetailResponse.from_domain(report.indicator),
                   periods=[PeriodResponse.from_domain(period) for period in report.periods],
                   series=[CountrySeriesResponse.from_domain(series) for series in report.series])
