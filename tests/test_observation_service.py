"""Business rules tested with a fake repository: no database or network."""
import pytest
from app.domain import ObservationCriteria
from app.services.observation_service import ObservationService
from app.models import Sex


class FakeRepository:
    def __init__(self, items=tuple(range(9))):
        self.items = items
        self.calls = []

    def count(self, criteria):
        return len(self.items)

    def find(self, criteria, *, limit, offset):
        self.calls.append((criteria, limit, offset))
        return self.items[offset:offset + limit]

    def list_countries(self): return ()
    def list_indicators(self): return ()
    def list_regions(self): return ()
    def list_sources(self): return ()


def test_pagination_requests_only_one_page():
    repo = FakeRepository()
    criteria = ObservationCriteria(region='Sub-Saharan Africa')
    page = ObservationService(repo, page_size=4).get_page(criteria, 2)
    assert repo.calls == [(criteria, 4, 4)]
    assert page.items == (4, 5, 6, 7) and page.total_pages == 3
    assert page.first_item == 5 and page.last_item == 8
    assert page.has_next and page.has_previous


def test_empty_results_and_page_beyond_the_end():
    page = ObservationService(FakeRepository(())).get_page(ObservationCriteria(), 999)
    assert (page.number, page.total_pages, page.first_item, page.last_item) == (1, 1, 0, 0)
    assert not page.has_next and not page.has_previous
    page = ObservationService(FakeRepository(), 4).get_page(ObservationCriteria(), 999)
    assert page.number == 3 and page.items == (8,)


def test_invalid_page_and_year_order_raise_domain_errors():
    with pytest.raises(ValueError):
        ObservationService(FakeRepository(), 0)
    with pytest.raises(ValueError):
        ObservationService(FakeRepository()).get_page(ObservationCriteria(), 0)
    with pytest.raises(ValueError, match='start year'):
        ObservationService(FakeRepository()).get_page(ObservationCriteria(year_from=2023, year_to=2000), 1)


def test_sex_criteria_is_forwarded_and_enum_options_are_complete():
    repo = FakeRepository()
    criteria = ObservationCriteria(country_iso3='ROU', sex=Sex.MALE)
    service = ObservationService(repo, 4)
    service.get_page(criteria, 1)
    assert repo.calls == [(criteria, 4, 0)]
    assert [r.value for r in service.get_filter_options().sexes] == ['BTSX', 'MLE', 'FMLE']
