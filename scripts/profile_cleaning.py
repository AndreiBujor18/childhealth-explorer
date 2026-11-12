"""Record cleaning decisions and IQR fences from verified local snapshots."""
import json
from etl.clean import clean_observations
from etl.study import indicators, study
from etl.transform import transform_indicator
from etl.transform_worldbank import transform_worldbank_countries
from etl.raw_files import RAW, ROOT


def main():
    config = study()
    valid = transform_worldbank_countries(RAW / 'worldbank/countries.json')['iso3'].tolist()
    profiles = []
    for item in indicators():
        frame = transform_indicator(item)
        cleaned = clean_observations(frame, valid, [item], countries=config['pilot_countries'],
                                     year_window=(config['start_year'], config['end_year']), sex=config['sex'])
        profiles.append({'source': item['source'], 'indicator': item['code'], **cleaned.attrs,
                         'outliers': int(cleaned['is_outlier'].sum())})
    path = ROOT / 'docs/evidence/lab2-cleaning.json'
    path.write_text(json.dumps(profiles, indent=2) + '\n', encoding='utf-8')
    print('Clean observations:', sum(p['clean_rows'] for p in profiles))
    print('Retained outliers:', sum(p['outliers'] for p in profiles))


if __name__ == '__main__':
    main()
