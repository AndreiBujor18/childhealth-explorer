"""Adopt an exactly matching Lab 1 database or migrate a fresh database."""
from pathlib import Path
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text
from app.database import get_engine
from scripts.verify_database import describe

ROOT = Path(__file__).resolve().parents[1]
TABLES = {'source', 'country', 'indicator', 'observation', 'import_log'}


def main():
    config = Config(str(ROOT / 'alembic.ini'))
    engine = get_engine()
    with engine.connect() as connection:
        names = set(inspect(connection).get_table_names(schema='public'))
        adopt = bool(names) and 'alembic_version' not in names
        if adopt:
            if names != TABLES:
                raise RuntimeError('Unrecognized database; refusing to stamp the Lab 1 baseline')
            actual = describe(connection, 'public')
            connection.rollback()
            with connection.begin() as transaction:
                connection.execute(text('CREATE SCHEMA lab2_baseline_check'))
                connection.execute(text('SET LOCAL search_path TO lab2_baseline_check'))
                connection.exec_driver_sql((ROOT / 'db/schema.sql').read_text(encoding='utf-8'))
                expected = describe(connection, 'lab2_baseline_check')
                transaction.rollback()
            if actual != expected:
                raise RuntimeError('Existing schema differs from Lab 1; baseline stamping refused')
    if adopt:
        command.stamp(config, '0001')
    command.upgrade(config, 'head')
    print('Database at revision 0002; original observations preserved.')


if __name__ == '__main__':
    main()
