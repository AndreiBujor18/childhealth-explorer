"""World Bank JSON adapter with explicit pagination and country filtering."""
from etl.contracts import ObservationRecord, numeric

BASE = 'https://api.worldbank.org/v2'


class WorldBankAdapter:
    def __init__(self, client):
        self.client = client

    def pages(self, path, params):
        page = 1
        while True:
            doc = self.client.get(f'{BASE}/{path}', {**params, 'format': 'json', 'per_page': 1000, 'page': page})
            if not isinstance(doc, list) or len(doc) != 2 or not isinstance(doc[0], dict):
                raise ValueError(f'Unexpected World Bank response: {str(doc)[:250]}')
            yield from doc[1] or []
            if page >= int(doc[0].get('pages', 1)):
                break
            page += 1

    def countries(self):
        return {
            row['id']: row for row in self.pages('country', {})
            if row['region']['id'] != 'NA' and len(row['id']) == 3
        }

    def metadata(self, code):
        return list(self.pages(f'indicator/{code}', {}))

    def fetch(self, indicator, countries, start, end):
        result = []
        path = f'country/{";".join(countries)}/indicator/{indicator}'
        for row in self.pages(path, {'date': f'{start}:{end}'}):
            iso3 = row['countryiso3code']
            if iso3 not in countries:
                continue
            result.append(ObservationRecord('worldbank', indicator, iso3, int(row['date']),
                                            'BTSX', numeric(row['value'])))
        return result
