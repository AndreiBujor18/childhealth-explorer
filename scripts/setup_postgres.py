"""Initialize the project-local PostgreSQL archive and create gh_user/global_health."""
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess

ROOT = Path(__file__).resolve().parent.parent
LOCAL = ROOT / '.local'
PG = LOCAL / 'pgsql' / 'bin'
DATA = LOCAL / 'pgdata'


def run(binary, *args, **kwargs):
    return subprocess.run([str(PG / f'{binary}.exe'), *map(str, args)], check=True,
                          text=True, capture_output=True, **kwargs)


def main():
    if not (PG / 'initdb.exe').exists():
        raise RuntimeError('Extract the official PostgreSQL ZIP into .local/pgsql first.')
    LOCAL.mkdir(exist_ok=True)
    admin_file = LOCAL / 'postgres-admin-password.txt'
    if not admin_file.exists():
        admin_file.write_text(secrets.token_hex(24), encoding='ascii')
    if not (DATA / 'PG_VERSION').exists():
        print(run('initdb', '-D', DATA, '-U', 'postgres', '--pwfile', admin_file,
                  '-E', 'UTF8', '--locale=C', '-A', 'scram-sha-256').stdout)
    local_config = LOCAL / 'postgres.json'
    if local_config.exists():
        port = json.loads(local_config.read_text())['port']
    else:
        with socket.socket() as sock:
            port = 5432 if sock.connect_ex(('127.0.0.1', 5432)) != 0 else 5433
        local_config.write_text(json.dumps({'port': port}), encoding='utf-8')
    status = subprocess.run([str(PG / 'pg_ctl.exe'), '-D', str(DATA), 'status'], capture_output=True)
    if status.returncode != 0:
        # PostgreSQL can inherit pg_ctl's pipe handles on Windows. Use a file
        # instead of capture_output so the parent can finish while it runs.
        with (LOCAL / 'pg_ctl-start.log').open('w') as log:
            subprocess.run([str(PG / 'pg_ctl.exe'), '-D', str(DATA), '-l',
                            str(LOCAL / 'postgres.log'), '-o', f'-h 127.0.0.1 -p {port}',
                            '-w', 'start'], check=True, stdin=subprocess.DEVNULL,
                           stdout=log, stderr=subprocess.STDOUT)
        print('PostgreSQL started.')
    env_file = ROOT / '.env'
    if env_file.exists():
        print('Existing .env preserved; checking its connection is a separate step.')
        return
    password = secrets.token_hex(24)
    env = {**os.environ, 'PGPASSWORD': admin_file.read_text().strip()}
    sql = (f"CREATE USER gh_user WITH PASSWORD '{password}';\n"
           "CREATE DATABASE global_health OWNER gh_user ENCODING 'UTF8';\n")
    run('psql', '-X', '-v', 'ON_ERROR_STOP=1', '-h', '127.0.0.1', '-p', port,
        '-U', 'postgres', '-d', 'postgres', input=sql, env=env)
    env_file.write_text(f'DATABASE_URL=postgresql+psycopg://gh_user:{password}'
                        f'@127.0.0.1:{port}/global_health\n', encoding='utf-8')
    print(f'Created gh_user and global_health on 127.0.0.1:{port}; credentials saved only in .env.')


if __name__ == '__main__':
    main()
