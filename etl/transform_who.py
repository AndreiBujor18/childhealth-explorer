"""WHO under-five national totals; age and wealth dimensions are explicit."""
import pandas as pd
from etl.raw_files import json_pages
from etl.transform_worldbank import COLUMNS, require_keys


def transform_who_file(path, code):
    rows = []
    excluded = 0
    for envelope in json_pages(path):
        for r in envelope['value']:
            require_keys(r, ['IndicatorCode', 'SpatialDimType', 'SpatialDim', 'TimeDim',
                             'NumericValue', 'Dim1Type', 'Dim1', 'Dim2Type', 'Dim2', 'Dim3Type', 'Dim3'])
            if r['IndicatorCode'] != code:
                raise ValueError('WHO indicator mismatch')
            if (r['SpatialDimType'] != 'COUNTRY' or r['Dim1Type'] != 'SEX'
                    or r['Dim2Type'] != 'AGEGROUP' or r['Dim2'] != 'AGEGROUP_YEARSUNDER5'
                    or r['Dim3Type'] not in (None, 'WEALTHQUINTILE')
                    or r['Dim3'] not in (None, 'WEALTHQUINTILE_TOTL')):
                excluded += 1
                continue
            rows.append([r['SpatialDim'], code, r['TimeDim'], r['Dim1'], r['NumericValue']])
    frame = pd.DataFrame(rows, columns=COLUMNS)
    frame.attrs['excluded_dimensions'] = excluded
    return frame
