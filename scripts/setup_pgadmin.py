"""Prepare a separate, project-local pgAdmin desktop profile; no global settings changed."""
import json
import os
from pathlib import Path
import sqlite3
import subprocess

from sqlalchemy.engine import make_url
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parent.parent


def main():
    base = ROOT / '.local/pgsql/pgAdmin 4'
    profile = ROOT / '.local/pgadmin'
    profile.mkdir(exist_ok=True)
    config = {
        'SERVER_MODE': False, 'DEFAULT_SERVER': '127.0.0.1', 'DEFAULT_SERVER_PORT': 5051,
        'DATA_DIR': str(profile), 'SQLITE_PATH': str(profile / 'pgadmin4.db'),
        'LOG_FILE': str(profile / 'pgadmin4.log'), 'SESSION_DB_PATH': str(profile / 'sessions'),
        'STORAGE_DIR': str(profile / 'storage'), 'CHECK_EMAIL_DELIVERABILITY': False,
        'UPGRADE_CHECK_ENABLED': False,
        'DEFAULT_BINARY_PATHS': {'pg': str(ROOT / '.local/pgsql/bin'), 'pg-18': str(ROOT / '.local/pgsql/bin')},
    }
    (base / 'web/config_local.py').write_text(
        'import os\n_pg_dll_directory = os.add_dll_directory('
        + repr(str(ROOT / '.local/pgsql/bin')) + ')\n'
        + '\n'.join(f'{k} = {v!r}' for k, v in config.items()) + '\n', encoding='utf-8')
    url = make_url(dotenv_values(ROOT / '.env')['DATABASE_URL'])
    passfile = profile / 'pgpass.conf'
    escaped_password = url.password.replace('\\', '\\\\').replace(':', '\\:')
    passfile.write_text(f'{url.host}:{url.port}:*:{url.username}:{escaped_password}\n', encoding='utf-8')
    servers = {'Servers': {'1': {
        'Name': 'ChildHealth Explorer - PostgreSQL 18', 'Group': 'Servers',
        'Host': url.host, 'Port': url.port, 'MaintenanceDB': url.database,
        'Username': url.username, 'SSLMode': 'prefer', 'PassFile': str(passfile),
    }}}
    server_file = profile / 'servers.json'
    server_file.write_text(json.dumps(servers, indent=2), encoding='utf-8')
    child_env = {
        **os.environ, 'PGADMIN_SERVER_MODE': 'OFF',
        'PATH': str(ROOT / '.local/pgsql/bin') + os.pathsep + os.environ.get('PATH', ''),
    }
    settings_db = profile / 'pgadmin4.db'
    if settings_db.exists() and settings_db.stat().st_size == 0:
        settings_db.replace(profile / 'pgadmin4.empty.db')
    subprocess.run([str(base / 'python/python.exe'), str(base / 'web/setup.py'),
                    'setup-db'], env=child_env, check=True)
    with sqlite3.connect(settings_db) as db:
        exists = db.execute('SELECT count(*) FROM server WHERE name = ?',
                            ('ChildHealth Explorer - PostgreSQL 18',)).fetchone()[0]
    if not exists:
        subprocess.run([str(base / 'python/python.exe'), str(base / 'web/setup.py'),
                        'load-servers', str(server_file)], env=child_env, check=True)
    with sqlite3.connect(settings_db) as db:
        if not db.execute('SELECT count(*) FROM server').fetchone()[0]:
            raise RuntimeError('pgAdmin did not import the server definition.')
    print('Separate pgAdmin profile created. Start with scripts/start-pgadmin.ps1.')


if __name__ == '__main__':
    main()
