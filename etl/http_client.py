"""HTTP retries, raw response caching and an audit trail shared by all sources."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT = Path(__file__).resolve().parent.parent


class JsonClient:
    def __init__(self, cache_dir=ROOT / 'data' / 'raw', refresh=False):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.refresh = refresh
        self.calls = []
        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'ChildHealthExplorer/0.1 (academic project)'
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504],
                      allowed_methods=['GET'], respect_retry_after_header=True)
        self.session.mount('https://', HTTPAdapter(max_retries=retry))

    def get(self, url, params=None):
        prepared = requests.Request('GET', url, params=params).prepare().url
        key = hashlib.sha256(prepared.encode()).hexdigest()
        raw_path = self.cache_dir / f'{key}.json'
        meta_path = self.cache_dir / f'{key}.meta.json'
        cached = raw_path.exists() and meta_path.exists() and not self.refresh
        if cached:
            payload = json.loads(raw_path.read_text(encoding='utf-8'))
            meta = json.loads(meta_path.read_text(encoding='utf-8'))
        else:
            response = self.session.get(prepared, timeout=(15, 75))
            response.raise_for_status()
            payload = response.json()
            raw_path.write_bytes(response.content)
            meta = {
                'url': response.url, 'status': response.status_code,
                'retrieved_at': datetime.now(timezone.utc).isoformat(),
                'sha256': hashlib.sha256(response.content).hexdigest(),
                'bytes': len(response.content),
            }
            meta_path.write_text(json.dumps(meta, indent=2), encoding='utf-8')
        self.calls.append({**meta, 'cached': cached, 'cache_file': raw_path.name})
        return payload
