"""World Bank JSON adapter with explicit pagination and country filtering."""
from etl.contracts import ObservationRecord, numeric

BASE = 'https://api.worldbank.org/v2'


def download_worldbank_countries(*, output_dir=None):
    from etl.raw_files import RAW, download_json_pages
    return download_json_pages(f'{BASE}/country', {'format': 'json', 'per_page': 100, 'page': 1},
                               (output_dir or RAW / 'worldbank') / 'countries.json', 'worldbank')


def download_worldbank_indicator(code, countries, year_from=2000, year_to=2023, *, output_dir=None):
    from etl.raw_files import RAW, download_json_pages
    # Bulk country/all is reliable when country-specific API routes return 502.
    # Keep all source records intact; the shared cleaner applies the study scope.
    url = (f'{BASE}/en/country/all/indicator/{code}?format=json'
           f'&date={year_from}:{year_to}&per_page=20000')
    return download_json_pages(url, None,
                               (output_dir or RAW / 'worldbank') / f'{code}_{year_from}_{year_to}.json',
                               'worldbank')


def download_worldbank_for_year(code, countries, year, **kwargs):
    return download_worldbank_indicator(code, countries, year, year, **kwargs)


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
