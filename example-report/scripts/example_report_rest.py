"""REST helper for the Source API: the single doorway every example-report module uses.

Handles Bearer auth, a browser-like User-Agent, the OS trust store (when installed),
retry with backoff on rate-limit / transient errors, a per-process GET cache, and
``utf-8-sig`` decoding (tolerates a byte-order mark).
"""
from __future__ import annotations

import json
import os
import time

import requests
from dotenv import load_dotenv

import example_report_config as config


class SourceConfigError(RuntimeError):
    """Raised when the Source API settings are missing."""


def request_with_retry(session: requests.Session, method: str, url: str, **kwargs) -> requests.Response:
    kwargs.setdefault("timeout", config.TIMEOUT_SECONDS)
    resp = None
    for attempt in range(1, config.MAX_ATTEMPTS + 1):
        resp = session.request(method, url, **kwargs)
        if resp.status_code in config.RETRY_STATUSES and attempt < config.MAX_ATTEMPTS:
            time.sleep(config.BACKOFF_BASE ** attempt)
            continue
        return resp
    return resp


class SourceClient:
    """Authenticated, cached client for the Source API."""

    def __init__(self, base_url: str, token: str, session: requests.Session | None = None):
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "User-Agent": config.USER_AGENT,
        })
        self._cache: dict[tuple, object] = {}

    @classmethod
    def from_env(cls, env_file=None) -> "SourceClient":
        load_dotenv(env_file or config.ENV_FILE)
        base_url = os.getenv(config.ENV_SOURCE_URL)
        token = os.getenv(config.ENV_SOURCE_TOKEN)
        if not base_url or not token:
            raise SourceConfigError(
                f"Set {config.ENV_SOURCE_URL} and {config.ENV_SOURCE_TOKEN} in the repo-root .env.")
        try:
            import truststore
            truststore.inject_into_ssl()
        except ImportError:
            pass
        return cls(base_url, token)

    def get_json(self, path: str, params: dict | None = None, cache: bool = True):
        key = (path, tuple(sorted((params or {}).items())))
        if cache and key in self._cache:
            return self._cache[key]
        resp = request_with_retry(self.session, "GET", f"{self.base_url}/{path.lstrip('/')}",
                                  params=params)
        resp.raise_for_status()
        data = json.loads(resp.content.decode("utf-8-sig"))
        if cache:
            self._cache[key] = data
        return data
