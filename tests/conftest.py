"""Seeded PostgreSQL schemas; browser/service tests must never use live data."""
import os
import uuid
from decimal import Decimal
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from app.database import get_engine
from app.models import Base, Source, Country, Indicator, Observation


@pytest.fixture
def repository_session():
    try:
        url = os.environ.get('TEST_DATABASE_URL') or get_engine().url
        engine = create_engine(url, connect_args={'connect_timeout': 3})
        connection = engine.connect()
    except (OperationalError, RuntimeError):
        pytest.skip('PostgreSQL unavailable; use TEST_DATABASE_URL or start the project database')
    schema = 'lab3_test_' + uuid.uuid4().hex
    transaction = connection.begin()
    try:
        connection.execute(text(f'CREATE SCHEMA {schema}'))
        connection.execute(text(f'SET LOCAL search_path TO {schema}'))
        Base.metadata.create_all(connection)
        with Session(bind=connection, join_transaction_mode='create_savepoint') as session:
            session.add(Source(source_id=1, name='worldbank'))
            session.add_all([Country(iso3='ROU', name='Romania', region='Europe & Central Asia'),
                             Country(iso3='FRA', name='France', region='Europe & Central Asia'),
                             Country(iso3='KEN', name='Kenya', region='Sub-Saharan Africa'),
                             Country(iso3='USA', name='United States', region='North America')])
            session.add_all([Indicator(indicator_id=1, code='MORT', concept_code='mortality', name='Mortality',
                                       unit='per 1,000 births', source_id=1),
                             Indicator(indicator_id=2, code='GDP', concept_code='gdp', name='GDP',
                                       unit='international $', source_id=1)])
            session.flush()
            for country, indicator, year, sex, value in [
                ('FRA', 1, 2020, 'BTSX', '4'), ('FRA', 2, 2015, 'BTSX', '40000'),
                ('ROU', 1, 2023, 'BTSX', '6.9'), ('ROU', 1, 2023, 'MLE', '7.4'),
                ('ROU', 1, 2023, 'FMLE', '6.3'), ('ROU', 2, 2022, 'BTSX', '39000'),
                ('KEN', 1, 2023, 'BTSX', '40'), ('KEN', 2, 2021, 'BTSX', '5000'),
                ('USA', 1, 2023, 'BTSX', '6.5')]:
                session.add(Observation(country_iso3=country, indicator_id=indicator, year=year,
                                        sex=sex, value=Decimal(value), is_outlier=False))
            session.flush()
            yield session
    finally:
        transaction.rollback()
        connection.close()
        engine.dispose()


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from app.main import create_app
    from app.database import get_db
    from app.dependencies import get_observation_service, get_etl_service

    def forbidden():
        raise AssertionError('Presentation test reached a real data/service dependency')

    app = create_app()
    app.dependency_overrides[get_db] = forbidden
    app.dependency_overrides[get_observation_service] = forbidden
    app.dependency_overrides[get_etl_service] = forbidden
    with TestClient(app) as test_client:
        yield test_client
