"""WHO GHO raw extraction, with server filtering and OData pagination."""
from etl.raw_files import RAW, download_json_pages

BASE = 'https://ghoapi.azureedge.net/api'


def download_who_indicator(code, countries, year_from=2000, year_to=2023, *, output_dir=None):
    if not code.replace('_', '').isalnum() or any(not c.isalpha() or len(c) != 3 for c in countries):
        raise ValueError('Invalid indicator or country code')
    # GHO rejects very large OR filters; scope the years/sex on the server,
    # then apply the pilot country list in the shared cleaner.
    condition = (f"SpatialDimType eq 'COUNTRY' and TimeDim ge {year_from} "
                 f"and TimeDim le {year_to} and Dim1 eq 'SEX_BTSX'")
    path = (output_dir or RAW / 'who') / f'{code}_{year_from}_{year_to}.json'
    return download_json_pages(f'{BASE}/{code}', {'$filter': condition}, path, 'who')


def download_who_for_year(code, countries, year, **kwargs):
    return download_who_indicator(code, countries, year, year, **kwargs)
