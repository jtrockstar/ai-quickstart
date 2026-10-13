"""Tests for jira-toolkit/scripts/jira_client.py (network mocked)."""
from unittest.mock import MagicMock

import pytest

import jira_client


def test_load_settings_reads_env_and_strips_slash(jira_env):
    assert jira_client.load_settings() == ("https://example.atlassian.net", "pat@example.com", "tok")


def test_load_settings_reports_missing(monkeypatch):
    monkeypatch.setattr(jira_client, "load_dotenv", lambda *_a, **_k: None)
    for name in ("JIRA_URL", "JIRA_USERNAME", "JIRA_API_TOKEN"):
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(jira_client.JiraConfigError) as exc:
        jira_client.load_settings()
    assert "JIRA_USERNAME" in str(exc.value)


def test_make_session_uses_basic_auth():
    session = jira_client.make_session("pat@example.com", "tok")
    assert session.auth == ("pat@example.com", "tok")
    assert session.headers["Content-Type"] == "application/json"


def test_request_retries_then_succeeds(make_response):
    session = MagicMock()
    session.request.side_effect = [make_response(429, headers={"Retry-After": "0"}),
                                   make_response(200)]
    r = jira_client.request(session, "GET", "https://j/x")
    assert r.status_code == 200
    assert session.request.call_count == 2


def test_request_gives_up_after_max_attempts(make_response):
    session = MagicMock()
    session.request.return_value = make_response(503)
    r = jira_client.request(session, "GET", "https://j/x")
    assert r.status_code == 503
    assert session.request.call_count == jira_client.config.MAX_ATTEMPTS


def test_request_does_not_retry_client_errors(make_response):
    session = MagicMock()
    session.request.return_value = make_response(400)
    jira_client.request(session, "GET", "https://j/x")
    assert session.request.call_count == 1


def test_resolve_field_id_matches_name_case_insensitively_and_caches(make_response):
    session = MagicMock()
    session.request.return_value = make_response(200, {"fields": {
        "summary": {"name": "Summary"},
        "points_id": {"name": "Story point estimate"},
    }})
    names = ("Story Points", "story point estimate")
    assert jira_client.resolve_field_id_for_issue(session, "https://j", "P-1", names) == "points_id"
    assert jira_client.resolve_field_id_for_issue(session, "https://j", "P-1", names) == "points_id"
    assert session.request.call_count == 1


def test_resolve_field_id_returns_none_when_absent(make_response):
    session = MagicMock()
    session.request.return_value = make_response(200, {"fields": {"summary": {"name": "Summary"}}})
    assert jira_client.resolve_field_id_for_issue(session, "https://j", "P-2", ("Story Points",)) is None


def test_search_keys_follows_next_page_token(make_response):
    session = MagicMock()
    session.request.side_effect = [
        make_response(200, {"issues": [{"key": "P-1"}, {"key": "P-2"}], "nextPageToken": "t2"}),
        make_response(200, {"issues": [{"key": "P-3"}], "isLast": True}),
    ]
    assert jira_client.search_keys(session, "https://j", "project = P") == ["P-1", "P-2", "P-3"]
    second_params = session.request.call_args_list[1].kwargs["params"]
    assert second_params["nextPageToken"] == "t2"
    assert "/rest/api/3/search/jql" in session.request.call_args_list[0].args[1]
