"""Shared Jira Cloud REST helper used by every jira-toolkit script.

Centralizes the parts each script would otherwise repeat:
- loading ``JIRA_URL`` / ``JIRA_USERNAME`` / ``JIRA_API_TOKEN`` from the repo-root ``.env``;
- HTTP Basic auth (account email + API token), JSON headers, and a browser-like User-Agent;
- the OS trust store (``truststore``) when present, for networks that inspect TLS;
- retry with backoff on rate limits and transient errors (honors ``Retry-After``);
- a per-process cache for field metadata;
- JQL search using the paginated ``/rest/api/3/search/jql`` endpoint.

Writes use REST API **v2**, which still accepts Jira wiki markup for descriptions and
comments on Jira Cloud (v3 requires Atlassian Document Format).
"""
from __future__ import annotations

import os
import time
from typing import Iterable

import requests
from dotenv import load_dotenv

import jira_config as config


class JiraConfigError(RuntimeError):
    """Raised when the Jira connection settings are missing."""


def load_settings(env_file=None) -> tuple[str, str, str]:
    """Return (base_url, username, api_token) from the environment / .env."""
    load_dotenv(env_file or config.ENV_FILE)
    base_url = (os.getenv(config.ENV_URL) or "").rstrip("/")
    username = os.getenv(config.ENV_USERNAME) or ""
    token = os.getenv(config.ENV_API_TOKEN) or ""
    missing = [name for name, value in (
        (config.ENV_URL, base_url),
        (config.ENV_USERNAME, username),
        (config.ENV_API_TOKEN, token),
    ) if not value]
    if missing:
        raise JiraConfigError(f"Missing {', '.join(missing)} (set in the repo-root .env).")
    return base_url, username, token


def make_session(username: str, token: str) -> requests.Session:
    session = requests.Session()
    session.auth = (username, token)
    session.headers.update({
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": config.USER_AGENT,
    })
    return session


def _use_os_trust_store() -> None:
    try:
        import truststore
        truststore.inject_into_ssl()
    except ImportError:
        pass


def connect(env_file=None) -> tuple[requests.Session, str]:
    """Load settings and return a ready (session, base_url) pair."""
    base_url, username, token = load_settings(env_file)
    _use_os_trust_store()
    return make_session(username, token), base_url


def _retry_delay(resp: requests.Response, attempt: int) -> float:
    retry_after = (resp.headers or {}).get("Retry-After")
    try:
        return float(retry_after)
    except (TypeError, ValueError):
        return float(config.BACKOFF_BASE ** attempt)


def request(session: requests.Session, method: str, url: str, **kwargs) -> requests.Response:
    """Send one HTTP request, retrying on rate-limit / transient statuses."""
    kwargs.setdefault("timeout", config.TIMEOUT_SECONDS)
    resp = None
    for attempt in range(1, config.MAX_ATTEMPTS + 1):
        resp = session.request(method, url, **kwargs)
        if resp.status_code in config.RETRY_STATUSES and attempt < config.MAX_ATTEMPTS:
            time.sleep(_retry_delay(resp, attempt))
            continue
        return resp
    return resp


_EDITMETA_CACHE: dict[str, dict] = {}


def resolve_field_id_for_issue(session, base_url: str, key: str, names: Iterable[str]) -> str | None:
    """Return the id of the first field in ``names`` that is editable on issue ``key``.

    Uses the issue's edit metadata, so the result matches that issue's project type
    (e.g. "Story point estimate" in team-managed vs "Story Points" in company-managed).
    """
    if key not in _EDITMETA_CACHE:
        r = request(session, "GET", f"{base_url}/rest/api/2/issue/{key}/editmeta")
        r.raise_for_status()
        _EDITMETA_CACHE[key] = r.json().get("fields", {})
    fields = _EDITMETA_CACHE[key]
    by_name = {(meta.get("name") or "").lower(): field_id for field_id, meta in fields.items()}
    for name in names:
        field_id = by_name.get(name.lower())
        if field_id:
            return field_id
    return None


def search_keys(session, base_url: str, jql: str) -> list[str]:
    """Return every issue key matching ``jql`` (token-paginated enhanced search)."""
    keys: list[str] = []
    token = None
    while True:
        params = {"jql": jql, "fields": "key", "maxResults": config.SEARCH_PAGE_SIZE}
        if token:
            params["nextPageToken"] = token
        r = request(session, "GET", f"{base_url}/rest/api/3/search/jql", params=params)
        r.raise_for_status()
        data = r.json()
        keys += [issue["key"] for issue in data.get("issues", [])]
        token = data.get("nextPageToken")
        if not token or data.get("isLast", False):
            return keys
