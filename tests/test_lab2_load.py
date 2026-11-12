"""PostgreSQL upserts must update flags and roll back a failed import's log."""
import os
import uuid
import pandas as pd
import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.database import get_engine
from app.models import Base
from etl.load import (get_or_create_source, get_or_create_indicator, upsert_countries,
                      upsert_observations, log_import)


@pytest.mark.integration
@pytest.mark.skipif(os.getenv('LAB2_TEST_DATABASE') != '1', reason='Set LAB2_TEST_DATABASE=1 for local PostgreSQL')
def test_upsert_updates_value_and_outlier_and_failed_log_rolls_back():
    schema = 'lab2_test_' + uuid.uuid4().hex
    with get_engine().connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(text(f'CREATE SCHEMA {schema}'))
            connection.execute(text(f'SET LOCAL search_path TO {schema}'))
            Base.metadata.create_all(connection)
            item = dict(code='TEST', concept_code='test', name='Test', unit='%', age_group='all ages')
            frame = pd.DataFrame([dict(country_iso3='ROU', year=2020, sex='BTSX', value=5.1, is_outlier=False)])
            with Session(bind=connection, join_transaction_mode='create_savepoint') as session:
                with session.begin():
                    upsert_countries(session, [dict(iso3='ROU', iso2='RO', name='Romania', region='Europe',
                                                    income_group='High income')])
                    source_id = get_or_create_source(session, 'worldbank')
                    indicator_id = get_or_create_indicator(session, item, source_id)
                    first = upsert_observations(session, frame, indicator_id)
                    log_import(session, 'worldbank', 'TEST', 'https://example.org', first['rows_loaded'])
                assert first == {'rows_loaded': 1, 'new_rows': 1, 'updated_rows': 0}
                frame.loc[0, ['value', 'is_outlier']] = [9.7, True]
                with session.begin():
                    second = upsert_observations(session, frame, indicator_id)
                    log_import(session, 'worldbank', 'TEST', 'https://example.org', second['rows_loaded'])
                assert second == {'rows_loaded': 1, 'new_rows': 0, 'updated_rows': 1}
                row = connection.execute(text('SELECT value,is_outlier FROM observation')).one()
                assert float(row.value) == 9.7 and row.is_outlier is True
                with pytest.raises(IntegrityError):
                    with session.begin():
                        log_import(session, 'worldbank', 'FAILED', 'https://example.org', 1)
                        frame.loc[0, 'country_iso3'] = 'XXX'
                        upsert_observations(session, frame, indicator_id)
                assert connection.scalar(text('SELECT count(*) FROM import_log')) == 2
                assert connection.scalar(text('SELECT count(*) FROM observation')) == 1
        finally:
            transaction.rollback()
