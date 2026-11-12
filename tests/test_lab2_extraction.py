"""Local snapshots exercise boundary errors and independent transformations."""
import json
import pytest
from etl.raw_files import download_json_pages, save_snapshot, read_snapshot
from etl.transform_worldbank import transform_worldbank_file
from etl.transform_who import transform_who_file
from etl.transform_owid import transform_owid_file


def snapshot(path, payload):
    return save_snapshot(path, json.dumps(payload).encode(), [{'url': 'https://example.org/data'}])[0]


def test_worldbank_transform_and_hash_guard(tmp_path):
    path = snapshot(tmp_path / 'data.json', {'responses': [[{'pages': 1}, [
        {'indicator': {'id': 'TEST'}, 'countryiso3code': 'ROU', 'date': '2023', 'value': None}]]]})
    rows = transform_worldbank_file(path, 'TEST')
    assert rows.iloc[0]['value'] is None
    path.write_text('{}')
    with pytest.raises(ValueError, match='hash mismatch'):
        read_snapshot(path)


def test_who_does_not_collapse_wealth_subdivisions(tmp_path):
    row = {'IndicatorCode': 'TEST', 'SpatialDimType': 'COUNTRY', 'SpatialDim': 'ROU',
           'TimeDim': 2023, 'NumericValue': 6.9, 'Dim1Type': 'SEX', 'Dim1': 'SEX_BTSX',
           'Dim2Type': 'AGEGROUP', 'Dim2': 'AGEGROUP_YEARSUNDER5',
           'Dim3Type': 'WEALTHQUINTILE', 'Dim3': 'WEALTHQUINTILE_TOTL'}
    path = snapshot(tmp_path / 'who.json', {'responses': [{'value': [row, {**row, 'Dim3': 'Q1'}]}]})
    frame = transform_who_file(path, 'TEST')
    assert len(frame) == 1 and frame.attrs['excluded_dimensions'] == 1


def test_owid_unit_conversion_and_changed_unit_fail(tmp_path):
    path = tmp_path / 'owid.csv'
    save_snapshot(path, b'Entity,Code,Year,Rate\nRomania,ROU,2023,0.69\n', [{'url': 'https://example.org'}])
    meta = path.with_suffix('.metadata.json')
    snapshot(meta, {'columns': {'Rate': {'unit': 'deaths per 100 live births'}}})
    assert transform_owid_file(path, 'TEST').iloc[0]['value'] == pytest.approx(6.9)
    snapshot(meta, {'columns': {'Rate': {'unit': 'unknown'}}})
    with pytest.raises(ValueError, match='unit changed'):
        transform_owid_file(path, 'TEST')


def test_bad_http_200_envelope_does_not_replace_snapshot(tmp_path, monkeypatch):
    path = tmp_path / 'data.json'
    path.write_text('previous valid file')

    class Response:
        url = 'https://example.org'
        def raise_for_status(self):
            pass
        def json(self):
            return [{'message': 'Unknown indicator'}]

    class Session:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def get(self, *args, **kwargs):
            return Response()

    monkeypatch.setattr('etl.raw_files.http_session', Session)
    with pytest.raises(ValueError, match='Invalid World Bank envelope'):
        download_json_pages('https://example.org', {}, path, 'worldbank')
    assert path.read_text() == 'previous valid file'
