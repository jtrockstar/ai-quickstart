"""Shared pytest setup for the jira-toolkit tests: import path, fake responses, cache reset."""
import os
import sys
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import jira_client  # noqa: E402


def _response(status=200, json_data=None, text="", headers=None):
    r = MagicMock()
    r.status_code = status
    r.ok = 200 <= status < 300
    r.json.return_value = {} if json_data is None else json_data
    r.text = text
    r.headers = headers or {}
    if r.ok:
        r.raise_for_status.return_value = None
    else:
        r.raise_for_status.side_effect = RuntimeError(f"HTTP {status}")
    return r


@pytest.fixture
def make_response():
    return _response


@pytest.fixture(autouse=True)
def _no_sleep_and_clean_cache(monkeypatch):
    monkeypatch.setattr(jira_client.time, "sleep", lambda *_: None)
    jira_client._EDITMETA_CACHE.clear()
    yield
    jira_client._EDITMETA_CACHE.clear()


@pytest.fixture
def jira_env(monkeypatch):
    monkeypatch.setenv("JIRA_URL", "https://example.atlassian.net/")
    monkeypatch.setenv("JIRA_USERNAME", "pat@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "tok")
    monkeypatch.setattr(jira_client, "load_dotenv", lambda *_a, **_k: None)
    monkeypatch.setattr(jira_client, "_use_os_trust_store", lambda: None)
