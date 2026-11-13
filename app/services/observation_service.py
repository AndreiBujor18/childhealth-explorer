"""Pagination and browsing rules over an injected repository."""
from dataclasses import dataclass
from math import ceil
from typing import Protocol
from app.domain import ObservationCriteria, ObservationListItem, FilterOptions, Option
from app.models import Sex


class ObservationReader(Protocol):
    def find(self, criteria: ObservationCriteria, *, limit: int, offset: int) -> tuple[ObservationListItem, ...]: ...
    def count(self, criteria: ObservationCriteria) -> int: ...
    def list_countries(self) -> tuple[Option, ...]: ...
    def list_indicators(self) -> tuple[Option, ...]: ...
    def list_regions(self) -> tuple[Option, ...]: ...
    def list_sources(self) -> tuple[Option, ...]: ...


@dataclass(frozen=True)
class ObservationPage:
    items: tuple[ObservationListItem, ...]
    number: int
    size: int
    total_items: int

    @property
    def total_pages(self):
        return max(1, ceil(self.total_items / self.size))

    @property
    def has_previous(self):
        return self.number > 1

    @property
    def has_next(self):
        return self.number < self.total_pages

    @property
    def first_item(self):
        return (self.number - 1) * self.size + 1 if self.items else 0

    @property
    def last_item(self):
        return (self.number - 1) * self.size + len(self.items) if self.items else 0


class ObservationService:
    def __init__(self, repository: ObservationReader, page_size: int = 25):
        if page_size < 1:
            raise ValueError('Page size must be positive')
        self._repository = repository
        self._page_size = page_size

    def get_page(self, criteria: ObservationCriteria, number: int) -> ObservationPage:
        if number < 1:
            raise ValueError('Page numbers start at 1')
        if criteria.year_from is not None and criteria.year_to is not None and criteria.year_from > criteria.year_to:
            raise ValueError('The start year must not be later than the end year.')
        total = self._repository.count(criteria)
        number = min(number, max(1, ceil(total / self._page_size)))
        items = self._repository.find(criteria, limit=self._page_size, offset=(number - 1) * self._page_size)
        return ObservationPage(tuple(items), number, self._page_size, total)

    def get_filter_options(self) -> FilterOptions:
        labels = {Sex.BOTH: 'Both sexes (BTSX)', Sex.MALE: 'Male (MLE)', Sex.FEMALE: 'Female (FMLE)'}
        return FilterOptions(self._repository.list_countries(), self._repository.list_indicators(),
                             self._repository.list_regions(), self._repository.list_sources(),
                             tuple(Option(s.value, labels[s]) for s in Sex))
