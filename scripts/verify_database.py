"""Task 1.9: compare actual DDL with the reference in a rolled-back schema."""
import json
import os
from pathlib import Path
import subprocess

from sqlalchemy import inspect, text

from app.database import get_engine

ROOT = Path(__file__).resolve().parent.parent


def describe(connection, schema):
    inspector = inspect(connection)
    result = {}
    for name in sorted(inspector.get_table_names(schema=schema)):
        columns = [{
            'name': c['name'], 'type': str(c['type']), 'nullable': c['nullable'],
            'default': 'sequence' if 'nextval' in str(c['default']) else c['default'],
        } for c in inspector.get_columns(name, schema=schema)]
        result[name] = {
            'columns': columns,
            'primary_key': inspector.get_pk_constraint(name, schema=schema)['constrained_columns'],
            'unique': sorted([sorted(c['column_names'])
                              for c in inspector.get_unique_constraints(name, schema=schema)]),
            'foreign_keys': sorted([
                (f['constrained_columns'], f['referred_table'], f['referred_columns'])
                for f in inspector.get_foreign_keys(name, schema=schema)
            ]),
            'checks': sorted(c['sqltext'] for c in inspector.get_check_constraints(name, schema=schema)),
            'indexes': sorted((i['name'], i['column_names']) for i in inspector.get_indexes(name, schema=schema)
                              if not i.get('duplicates_constraint')),
        }
    return result


def main():
    engine = get_engine()
    result = {}
    with engine.connect() as connection:
        result['version'] = connection.scalar(text('SELECT version()'))
        result['database'] = connection.scalar(text('SELECT current_database()'))
        result['user'] = connection.scalar(text('SELECT current_user'))
        result['public_schema'] = describe(connection, 'public')
        result['row_counts'] = {
            table: connection.scalar(text(f'SELECT count(*) FROM public.{table}'))
            for table in result['public_schema']
        }
        connection.rollback()
        with connection.begin() as transaction:
            connection.execute(text('CREATE SCHEMA lab1_design_check'))
            connection.execute(text('SET LOCAL search_path TO lab1_design_check'))
            connection.exec_driver_sql((ROOT / 'db/schema.sql').read_text())
            reference = describe(connection, 'lab1_design_check')
            result['schema_matches_design'] = result['public_schema'] == reference
            if not result['schema_matches_design']:
                result['reference_schema'] = reference
            transaction.rollback()
    url = engine.url
    binary = ROOT / '.local/pgsql/bin/pg_dump.exe'
    if not binary.exists():
        binary = 'pg_dump'
    env = {**os.environ, 'PGPASSWORD': url.password}
    subprocess.run([str(binary), '-h', url.host, '-p', str(url.port or 5432), '-U', url.username,
                    '--schema-only', '--no-owner', '--no-privileges', '--file', str(ROOT / 'db/schema_dump.sql'),
                    url.database], env=env, check=True, capture_output=True, text=True)
    out = ROOT / 'docs/evidence/database_verification.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(result['version'])
    print('Table row counts:', result['row_counts'])
    print('Schema matches SQL design:', result['schema_matches_design'])
    if not result['schema_matches_design']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
