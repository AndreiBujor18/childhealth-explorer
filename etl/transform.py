"""Dispatch local file transformations, independent of extraction and loading."""
from etl.transform_worldbank import transform_worldbank_file
from etl.transform_who import transform_who_file
from etl.transform_owid import transform_owid_file
from etl.transform_unicef import transform_unicef_file
from etl.study import raw_path

TRANSFORMS = {'worldbank': transform_worldbank_file, 'who': transform_who_file,
              'owid': transform_owid_file, 'unicef': transform_unicef_file}


def transform_indicator(item):
    return TRANSFORMS[item['source']](raw_path(item), item['code'])
