"""Validated downloads and local snapshots; no observation transformation."""
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qsl, urlencode, urlsplit, urlunsplit

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw'


def http_session():
    session = requests.Session()
    session.headers['User-Agent'] = 'ChildHealthExplorer/0.2 (university project)'
    session.mount('https://', HTTPAdapter(max_retries=Retry(
        total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=['GET'], respect_retry_after_header=True,
    )))
    return session


def save_snapshot(path, content, requests_meta):
    """Replace only a complete, validated download; retain source URLs and hash."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_bytes(content)
    os.replace(tmp, path)
    metadata = {'retrieved_at': datetime.now(timezone.utc).isoformat(),
                'sha256': hashlib.sha256(content).hexdigest(), 'requests': requests_meta}
    path.with_suffix(path.suffix + '.meta.json').write_text(
        json.dumps(metadata, indent=2), encoding='utf-8')
    return path, requests_meta[0]['url']


def read_snapshot(path):
    path = Path(path)
    meta = json.loads(path.with_suffix(path.suffix + '.meta.json').read_text(encoding='utf-8'))
    if hashlib.sha256(path.read_bytes()).hexdigest() != meta['sha256']:
        raise ValueError(f'Snapshot hash mismatch: {path}')
    return meta


def download_json_pages(url, params, path, kind):
    """Preserve untransformed response envelopes, including every page."""
    pages, calls, visited = [], [], set()
    first_host = urlparse(url).netloc
    with http_session() as session:
        while url:
            response = session.get(url, params=params, timeout=(15, 120))
            response.raise_for_status()
            if response.url in visited:
                raise ValueError('Pagination loop')
            visited.add(response.url)
            body = response.json()
            if kind == 'worldbank':
                if (not isinstance(body, list) or len(body) != 2 or not isinstance(body[0], dict)
                        or 'pages' not in body[0] or not isinstance(body[1], (list, type(None)))):
                    raise ValueError(f'Invalid World Bank envelope at {response.url}')
                meta, records = body
                page, count = int(meta['page']), int(meta['pages'])
                if count < 1 or page != len(pages) + 1:
                    raise ValueError('Invalid World Bank pagination')
                if any(not isinstance(r, dict) for r in records or []):
                    raise ValueError('World Bank record is not an object')
                parts = urlsplit(response.url)
                query = dict(parse_qsl(parts.query))
                query['page'] = page + 1
                next_url = urlunsplit(parts._replace(query=urlencode(query, safe=':'))) if page < count else None
                params = None
            elif kind == 'who':
                if not isinstance(body, dict) or not isinstance(body.get('value'), list):
                    raise ValueError(f'Invalid WHO envelope at {response.url}')
                if any(not isinstance(r, dict) for r in body['value']):
                    raise ValueError('WHO record is not an object')
                link = body.get('@odata.nextLink')
                if link is not None and not isinstance(link, str):
                    raise ValueError('Invalid WHO nextLink')
                next_url = urljoin(url, link) if link else None
                if next_url and urlparse(next_url).netloc != first_host:
                    raise ValueError('Unexpected pagination host')
                params = None
            else:
                raise ValueError(f'Unknown envelope: {kind}')
            pages.append(body)
            calls.append({'url': response.url, 'status': response.status_code})
            url = next_url
    content = json.dumps({'responses': pages}, ensure_ascii=False).encode('utf-8')
    return save_snapshot(path, content, calls)


def json_pages(path):
    read_snapshot(path)
    body = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(body, dict) or not isinstance(body.get('responses'), list):
        raise ValueError('Expected saved response envelopes')
    return body['responses']
