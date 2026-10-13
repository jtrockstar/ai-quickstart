"""Tests for example-report/scripts/example_report_rest.py (network mocked)."""
from unittest.mock import MagicMock

import pytest

import example_report_rest as rest


def _resp(status=200, body=b"{}"):
    r = MagicMock()
    r.status_code = status
    r.content = body
    r.raise_for_status.side_effect = None if status < 400 else RuntimeError(status)
    return r


def _client(*responses):
    session = MagicMock()
    session.headers = {}
    session.request.side_effect = list(responses)
    return rest.SourceClient("https://api.example.com/", "tok", session=session), session


def test_get_json_decodes_bom_and_sets_headers():
    client, session = _client(_resp(body="\ufeff{\"a\": 1}".encode("utf-8")))
    assert client.get_json("api/v1/x") == {"a": 1}
    assert session.headers["Authorization"] == "Bearer tok"
    assert session.request.call_args.args[1] == "https://api.example.com/api/v1/x"


def test_get_json_caches_per_path_and_params():
    client, session = _client(_resp(body=b"[1]"), _resp(body=b"[2]"))
    assert client.get_json("p", {"a": 1}) == [1]
    assert client.get_json("p", {"a": 1}) == [1]
    assert client.get_json("p", {"a": 2}) == [2]
    assert session.request.call_count == 2


def test_retry_on_rate_limit_then_success():
    client, session = _client(_resp(429), _resp(body=b"{\"ok\": true}"))
    assert client.get_json("p") == {"ok": True}
    assert session.request.call_count == 2


def test_client_error_raises():
    client, _ = _client(_resp(404))
    with pytest.raises(RuntimeError):
        client.get_json("missing")


def test_from_env_requires_settings(monkeypatch):
    monkeypatch.setattr(rest, "load_dotenv", lambda *_a, **_k: None)
    monkeypatch.delenv("SOURCE_API_URL", raising=False)
    monkeypatch.delenv("SOURCE_API_TOKEN", raising=False)
    with pytest.raises(rest.SourceConfigError):
        rest.SourceClient.from_env()
