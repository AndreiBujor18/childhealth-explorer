"""Download the Lab 2 study snapshots without loading the database."""
import argparse
from etl.extract_worldbank import download_worldbank_countries, download_worldbank_indicator
from etl.extract_who import download_who_indicator
from etl.extract_owid import download_owid_chart
from etl.extract_unicef import download_unicef_indicator
from etl.study import indicators, study, raw_path
from etl.raw_files import RAW, read_snapshot


def download_indicator(item, *, refresh=False):
    path = raw_path(item)
    if path.exists() and not refresh:
        return path, read_snapshot(path)['requests'][0]['url']
    config = study()
    countries, start, end = config['pilot_countries'], config['start_year'], config['end_year']
    source, code = item['source'], item['code']
    if source == 'worldbank':
        return download_worldbank_indicator(code, countries, start, end)
    if source == 'who':
        return download_who_indicator(code, countries, start, end)
    if source == 'owid':
        return download_owid_chart(code, start, end)
    if source == 'unicef':
        return download_unicef_indicator(code, countries, start, end)
    raise ValueError(f'Unknown source: {source}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh', action='store_true')
    args = parser.parse_args()
    countries = RAW / 'worldbank/countries.json'
    if args.refresh or not countries.exists():
        download_worldbank_countries()
    else:
        read_snapshot(countries)
    for item in indicators():
        path, _ = download_indicator(item, refresh=args.refresh)
        print(f"{item['source']}/{item['code']}: {path.relative_to(RAW)}", flush=True)


if __name__ == '__main__':
    main()
