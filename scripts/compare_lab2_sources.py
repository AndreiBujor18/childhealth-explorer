"""Fresh official website data exports vs stored values for Romania, 2023."""
import io
import json
import hashlib
from datetime import datetime, timezone
from decimal import Decimal
import pandas as pd
from sqlalchemy import text
from app.database import get_engine
from etl.raw_files import http_session, ROOT

WHO_SITE = ('https://www.who.int/data/gho/data/indicators/indicator-details/GHO/'
            'under-five-mortality-rate-(probability-of-dying-by-age-5-per-1000-live-births)')


def main():
    checks = [
        {'source': 'worldbank', 'code': 'SH.DYN.MORT',
         'website': 'https://data.worldbank.org/indicator/SH.DYN.MORT?locations=RO',
         'data_url': 'https://api.worldbank.org/v2/country/ROU/indicator/SH.DYN.MORT?format=json&date=2000:2023'},
        {'source': 'who', 'code': 'MDG_0000000007', 'website': WHO_SITE,
         'data_url': 'https://ghoapi.azureedge.net/api/MDG_0000000007',
         'params': {'$filter': "SpatialDim eq 'ROU' and TimeDim eq 2023 and Dim1 eq 'SEX_BTSX'"}},
        {'source': 'owid', 'code': 'child-mortality',
         'website': 'https://ourworldindata.org/grapher/child-mortality?tab=table&time=2023&country=~ROU',
         'data_url': 'https://ourworldindata.org/grapher/child-mortality.csv'},
    ]
    rows = []
    with http_session() as session, get_engine().connect() as connection:
        connection.execute(text('SET TRANSACTION READ ONLY'))
        for item in checks:
            response = session.get(item['data_url'], params=item.get('params'), timeout=(15, 90))
            response.raise_for_status()
            factor = Decimal(1)
            if item['source'] == 'worldbank':
                body = response.json()
                if not isinstance(body, list) or len(body) != 2 or not isinstance(body[1], list):
                    raise ValueError('Unexpected World Bank source check response')
                candidates = [r for r in body[1] if r['countryiso3code'] == 'ROU' and r['date'] == '2023'
                              and r['indicator']['id'] == item['code']]
                field = 'value'
            elif item['source'] == 'who':
                candidates = [r for r in response.json()['value'] if r['SpatialDim'] == 'ROU'
                              and r['TimeDim'] == 2023 and r['Dim1'] == 'SEX_BTSX'
                              and r['Dim2'] == 'AGEGROUP_YEARSUNDER5'
                              and r['Dim3'] in (None, 'WEALTHQUINTILE_TOTL')]
                field = 'NumericValue'
            else:
                chart = pd.read_csv(io.BytesIO(response.content))
                fields = set(chart.columns) - {'Entity', 'Code', 'Year'}
                if len(fields) != 1:
                    raise ValueError('OWID comparison needs exactly one value column')
                metadata = session.get('https://ourworldindata.org/grapher/child-mortality.metadata.json',
                                       timeout=(15, 90))
                metadata.raise_for_status()
                if next(iter(metadata.json()['columns'].values()))['unit'] != 'deaths per 100 live births':
                    raise ValueError('OWID comparison unit changed')
                candidates = chart.loc[(chart.Code == 'ROU') & (chart.Year == 2023)].to_dict(orient='records')
                field = fields.pop()
                factor = Decimal(10)
            if len(candidates) != 1:
                raise ValueError(f'Expected exactly one Romania 2023 total for {item["source"]}')
            published = Decimal(str(candidates[0][field]))
            normalized = published * factor
            stored = connection.execute(text('''
                SELECT o.value FROM observation o JOIN indicator i USING(indicator_id)
                JOIN source s USING(source_id) WHERE s.name=:source AND i.code=:code
                AND o.country_iso3='ROU' AND o.year=2023 AND o.sex='BTSX'
            '''), item).scalar_one()
            delta = abs(normalized - stored)
            rows.append({'source': item['source'], 'indicator': item['code'], 'country': 'ROU', 'year': 2023,
                         'website': item['website'], 'download_url': response.url,
                         'response_sha256': hashlib.sha256(response.content).hexdigest(),
                         'source_value': str(published), 'conversion_factor': str(factor),
                         'normalized_value': str(normalized), 'stored_value': str(stored),
                         'absolute_difference': str(delta), 'tolerance': '0.00005',
                         'passed': delta <= Decimal('0.00005')})
            print(item['source'], published, '-> stored', stored, '| match:', rows[-1]['passed'], flush=True)
    result = {'checked_at': datetime.now(timezone.utc).isoformat(),
              'method': 'Fresh official website API/CSV data exports, not reused ETL snapshots or a visual reading of rounded chart labels.',
              'comparisons': rows, 'all_passed': all(r['passed'] for r in rows)}
    (ROOT / 'docs/evidence/lab2-source-comparison.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    if not result['all_passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
