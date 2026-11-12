"""Transactional PostgreSQL upserts for the five application tables."""
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert
from app.models import Source, Country, Indicator, Observation, ImportLog

SOURCE_URLS = {'worldbank': 'https://data.worldbank.org/', 'who': 'https://www.who.int/data/gho',
               'owid': 'https://ourworldindata.org/', 'unicef': 'https://data.unicef.org/'}


def upsert_countries(session, rows):
    if not rows:
        raise ValueError('No valid countries in source metadata')
    statement = insert(Country).values(rows)
    session.execute(statement.on_conflict_do_update(
        index_elements=[Country.iso3],
        set_={name: getattr(statement.excluded, name) for name in ['iso2', 'name', 'region', 'income_group']}))


def get_or_create_source(session, name):
    statement = insert(Source).values(name=name, url=SOURCE_URLS[name])
    return session.scalar(statement.on_conflict_do_update(
        index_elements=[Source.name], set_={'url': statement.excluded.url}).returning(Source.source_id))


def get_or_create_indicator(session, item, source_id):
    fields = {k: item[k] for k in ['code', 'concept_code', 'name', 'unit', 'age_group']}
    statement = insert(Indicator).values(**fields, source_id=source_id)
    return session.scalar(statement.on_conflict_do_update(
        constraint='uq_indicator_source_code',
        set_={k: getattr(statement.excluded, k) for k in fields if k != 'code'}
    ).returning(Indicator.indicator_id))


def upsert_observations(session, frame, indicator_id, chunk_size=500):
    if chunk_size < 1:
        raise ValueError('chunk_size must be positive')
    if frame.empty:
        raise ValueError('No cleaned observations to load')
    if frame.duplicated(['country_iso3', 'year', 'sex']).any():
        raise ValueError('Duplicate natural keys reached the loader')
    existing = set(session.execute(select(Observation.country_iso3, Observation.year, Observation.sex)
                                   .where(Observation.indicator_id == indicator_id)))
    rows = [{'country_iso3': r.country_iso3, 'indicator_id': indicator_id, 'year': int(r.year),
             'sex': r.sex, 'value': Decimal(str(r.value)), 'is_outlier': bool(r.is_outlier)}
            for r in frame.itertuples()]
    new = sum((r['country_iso3'], r['year'], r['sex']) not in existing for r in rows)
    for start in range(0, len(rows), chunk_size):
        statement = insert(Observation).values(rows[start:start + chunk_size])
        session.execute(statement.on_conflict_do_update(
            constraint='uq_observation', set_={'value': statement.excluded.value,
                                             'is_outlier': statement.excluded.is_outlier,
                                             'imported_at': func.now()}))
    return {'rows_loaded': len(rows), 'new_rows': new, 'updated_rows': len(rows) - new}


def log_import(session, source, code, url, rows_loaded):
    session.add(ImportLog(source_name=source, indicator_code=code, url=url, rows_loaded=rows_loaded))
    session.flush()
