"""Plain in-memory observations for presentation tests; no SQL or network."""
from decimal import Decimal
from app.domain import ObservationListItem, Option
from app.models import Sex


def example_items():
    return tuple(ObservationListItem(
        country_name={'ROU': 'Romania', 'KEN': 'Kenya', 'FRA': 'France'}[country],
        country_iso3=country, region='Sub-Saharan Africa' if country == 'KEN' else 'Europe & Central Asia',
        source_name='worldbank', indicator_code='MORT', indicator_name='Mortality', unit='per 1,000 births',
        year=year, sex=Sex(sex), value=Decimal('6.9'), is_outlier=False
    ) for country, year, sex in [('ROU', 2023, 'MLE'), ('ROU', 2023, 'FMLE'), ('ROU', 2022, 'BTSX'),
                                 ('KEN', 2023, 'BTSX'), ('KEN', 2022, 'BTSX'), ('KEN', 2021, 'BTSX'),
                                 ('FRA', 2023, 'BTSX'), ('FRA', 2022, 'BTSX'), ('FRA', 2021, 'BTSX')])


class MemoryRepository:
    def __init__(self, items=None):
        self.items = example_items() if items is None else items

    def matches(self, criteria):
        return tuple(r for r in self.items if
                     (criteria.country_iso3 is None or r.country_iso3 == criteria.country_iso3)
                     and (criteria.indicator_code is None or r.indicator_code == criteria.indicator_code)
                     and (criteria.region is None or r.region == criteria.region)
                     and (criteria.source_name is None or r.source_name == criteria.source_name)
                     and (criteria.year_from is None or r.year >= criteria.year_from)
                     and (criteria.year_to is None or r.year <= criteria.year_to))

    def count(self, criteria): return len(self.matches(criteria))
    def find(self, criteria, *, limit, offset): return self.matches(criteria)[offset:offset + limit]
    def list_countries(self): return (Option('ROU', 'Romania'), Option('KEN', 'Kenya'), Option('FRA', 'France'))
    def list_indicators(self): return (Option('MORT', 'Mortality'),)
    def list_regions(self): return (Option('Sub-Saharan Africa', 'Sub-Saharan Africa'),)
    def list_sources(self): return (Option('worldbank', 'World Bank'),)
