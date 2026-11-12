"""Opt-in PostgreSQL migration test, rolled back in an isolated schema."""
import os
import uuid
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text
from app.database import get_engine


@pytest.mark.integration
@pytest.mark.skipif(os.getenv('LAB2_TEST_DATABASE') != '1', reason='Set LAB2_TEST_DATABASE=1 for local PostgreSQL')
def test_fresh_migration_preserves_observation_on_upgrade_and_downgrade():
    schema = 'lab2_test_' + uuid.uuid4().hex
    with get_engine().connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(text(f'CREATE SCHEMA {schema}'))
            connection.execute(text(f'SET LOCAL search_path TO {schema}'))
            config = Config('alembic.ini')
            config.attributes['connection'] = connection
            command.upgrade(config, '0001')
            connection.execute(text("INSERT INTO source (source_id,name) VALUES (1,'test')"))
            connection.execute(text("INSERT INTO country (iso3,name) VALUES ('ROU','Romania')"))
            connection.execute(text("INSERT INTO indicator (indicator_id,code,concept_code,name,source_id) "
                                    "VALUES (1,'TEST','test','Test',1)"))
            connection.execute(text("INSERT INTO observation (country_iso3,indicator_id,year,value) "
                                    "VALUES ('ROU',1,2020,7.5)"))
            command.upgrade(config, 'head')
            row = connection.execute(text('SELECT value,is_outlier FROM observation')).one()
            assert float(row.value) == 7.5 and row.is_outlier is False
            command.downgrade(config, '0001')
            assert 'is_outlier' not in {c['name'] for c in inspect(connection).get_columns('observation', schema=schema)}
            assert float(connection.scalar(text('SELECT value FROM observation'))) == 7.5
            command.upgrade(config, 'head')
            assert connection.scalar(text('SELECT count(*) FROM observation')) == 1
        finally:
            transaction.rollback()
