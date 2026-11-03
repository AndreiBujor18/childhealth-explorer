"""Decode SDMX-JSON dimension indexes instead of assuming a JSON field order."""
from decimal import Decimal

from etl.contracts import ObservationRecord, numeric

BASE = 'https://sdmx.data.unicef.org/ws/public/sdmxapi/rest'
SEX = {'_T': 'BTSX', 'M': 'MLE', 'F': 'FMLE'}


def dimensions_at(dimensions, key):
    if not dimensions:
        return {}
    positions = str(key).split(':')
    if len(positions) != len(dimensions):
        raise ValueError('Unexpected number of SDMX key dimensions')
    return {d['id']: d['values'][int(pos)]['id'] for d, pos in zip(dimensions, positions, strict=True)}


def parse_sdmx(document, indicator, countries, start, end):
    body = document.get('data', document)
    structure = body['structure']
    dimensions = structure['dimensions']
    allowed_dims = {'REF_AREA', 'INDICATOR', 'SEX', 'TIME_PERIOD'}
    actual_dims = {d['id'] for axis in dimensions.values() for d in axis}
    if not actual_dims <= allowed_dims:
        raise ValueError(f'Additional SDMX dimensions need an explicit mapping: {actual_dims - allowed_dims}')
    attributes = structure.get('attributes', {}).get('observation', [])
    result = []
    for dataset in body['dataSets']:
        dataset_dims = dimensions.get('dataset', [])
        if any(len(d['values']) != 1 for d in dataset_dims):
            raise ValueError('Ambiguous dataset-level dimensions')
        defaults = {d['id']: d['values'][0]['id'] for d in dataset_dims}
        series = dataset.get('series', {'': dataset})
        for series_key, values in series.items():
            fixed = {**defaults, **dimensions_at(dimensions.get('series', []), series_key)}
            for obs_key, observation in values.get('observations', {}).items():
                codes = {**fixed, **dimensions_at(dimensions.get('observation', []), obs_key)}
                iso3, code, year = codes['REF_AREA'], codes['INDICATOR'], int(codes['TIME_PERIOD'])
                if iso3 not in countries or code != indicator or not start <= year <= end:
                    continue
                sex = SEX.get(codes.get('SEX', '_T'))
                if sex is None:
                    raise ValueError(f'Unknown UNICEF sex: {codes["SEX"]}')
                value = numeric(observation[0])
                for pos, attribute in enumerate(attributes, start=1):
                    index = observation[pos] if pos < len(observation) else None
                    if attribute['id'] == 'UNIT_MULTIPLIER' and index is not None and value is not None:
                        value *= Decimal(10) ** int(attribute['values'][int(index)]['id'])
                result.append(ObservationRecord('unicef', code, iso3, year, sex, value))
    return result


class UnicefAdapter:
    def __init__(self, client):
        self.client = client

    def fetch(self, indicator, countries, start, end):
        key = f'{"+".join(countries)}.{indicator}._T'
        document = self.client.get(f'{BASE}/data/UNICEF,GLOBAL_DATAFLOW,1.0/{key}', {
            'format': 'sdmx-json', 'startPeriod': start, 'endPeriod': end,
        })
        return parse_sdmx(document, indicator, countries, start, end)
