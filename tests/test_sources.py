"""Guard the external-data boundary and the third-source extension point."""
from decimal import Decimal

import pytest

from etl.contracts import ObservationRecord, numeric, validate
from etl.extract_unicef import parse_sdmx
from etl.extract_worldbank import WorldBankAdapter
from etl.registry import ADAPTERS, get_adapter


def test_unicef_indexes_are_decoded_from_metadata():
    document = {'data': {
        'structure': {'dimensions': {
            'series': [
                {'id': 'REF_AREA', 'values': [{'id': 'DEU'}, {'id': 'ROU'}]},
                {'id': 'INDICATOR', 'values': [{'id': 'IM_DTP3'}]},
                {'id': 'SEX', 'values': [{'id': '_T'}]},
            ],
            'observation': [{'id': 'TIME_PERIOD', 'values': [{'id': '2023'}, {'id': '2022'}]}],
        }, 'attributes': {'observation': [
            {'id': 'UNIT_MULTIPLIER', 'values': [{'id': '0'}]},
        ]}},
        'dataSets': [{'series': {'1:0:0': {'observations': {'0': ['79', 0], '1': [None, 0]}}}}],
    }}
    rows = parse_sdmx(document, 'IM_DTP3', ['ROU'], 2000, 2023)
    assert [(r.country_iso3, r.year, r.sex, r.value) for r in rows] == [
        ('ROU', 2023, 'BTSX', Decimal('79')), ('ROU', 2022, 'BTSX', None),
    ]


def test_worldbank_reads_all_pages_and_filters_aggregates():
    class Client:
        def __init__(self):
            self.pages = []

        def get(self, url, params):
            self.pages.append(params['page'])
            values = [
                {'countryiso3code': 'WLD', 'date': '2023', 'value': 5},
                {'countryiso3code': 'ROU', 'date': '2023', 'value': None},
            ] if params['page'] == 1 else [
                {'countryiso3code': 'ROU', 'date': '2022', 'value': 7.1},
            ]
            return [{'pages': 2}, values]

    client = Client()
    rows = WorldBankAdapter(client).fetch('SH.DYN.MORT', ['ROU'], 2000, 2023)
    assert client.pages == [1, 2]
    assert [r.value for r in rows] == [None, Decimal('7.1')]


def test_third_source_needs_only_registration_and_contract(monkeypatch):
    class ThirdSource:
        def __init__(self, client):
            pass

        def fetch(self, indicator, countries, start, end):
            return [ObservationRecord('third_source', indicator, countries[0], end, 'BTSX', Decimal('95'))]

    monkeypatch.setitem(ADAPTERS, 'third_source', ThirdSource)
    config = {'source': 'third_source', 'code': 'NEW', 'minimum': 0, 'maximum': 100}
    rows = get_adapter('third_source', None).fetch('NEW', ['ROU'], 2000, 2023)
    assert validate(rows, config, ['ROU'], 2000, 2023) == rows


@pytest.mark.parametrize('value', ['NaN', 'Infinity', '-Infinity', 'not a number'])
def test_invalid_numeric_values_are_rejected(value):
    with pytest.raises(ValueError):
        numeric(value)


def test_missing_values_remain_missing_and_duplicate_observations_fail():
    assert numeric(None) is None
    assert numeric(0) == Decimal(0)
    row = ObservationRecord('unicef', 'IM_DTP3', 'ROU', 2023, 'BTSX', Decimal('79'))
    with pytest.raises(ValueError, match='Duplicate'):
        validate([row, row], {'source': 'unicef', 'code': 'IM_DTP3'}, ['ROU'], 2000, 2023)


def test_percentage_outside_valid_range_fails():
    row = ObservationRecord('unicef', 'IM_DTP3', 'ROU', 2023, 'BTSX', Decimal('101'))
    with pytest.raises(ValueError, match='maximum'):
        validate([row], {'source': 'unicef', 'code': 'IM_DTP3', 'minimum': 0, 'maximum': 100},
                 ['ROU'], 2000, 2023)
