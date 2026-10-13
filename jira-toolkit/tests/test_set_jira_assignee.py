"""Tests for jira-toolkit/scripts/set_jira_assignee.py (network mocked)."""
from unittest.mock import MagicMock

import pytest

import jira_client
import set_jira_assignee as sja


def test_resolve_account_id_matches_display_name(make_response):
    session = MagicMock()
    session.request.return_value = make_response(200, [
        {"accountId": "a-1", "displayName": "Pat Example", "emailAddress": "pat@example.com"},
        {"accountId": "a-2", "displayName": "Other Person"},
    ])
    assert sja.resolve_account_id(session, "https://j", "Pat Example") == "a-1"


def test_resolve_account_id_matches_email(make_response):
    session = MagicMock()
    session.request.return_value = make_response(200, [
        {"accountId": "a-2", "displayName": "Other"},
        {"accountId": "a-1", "displayName": "Pat", "emailAddress": "pat@example.com"},
    ])
    assert sja.resolve_account_id(session, "https://j", "PAT@example.com") == "a-1"


def test_resolve_account_id_falls_back_to_first_then_literal(make_response):
    session = MagicMock()
    session.request.return_value = make_response(200, [{"accountId": "first", "displayName": "Z"}])
    assert sja.resolve_account_id(session, "https://j", "nobody") == "first"
    session.request.return_value = make_response(200, [])
    assert sja.resolve_account_id(session, "https://j", "5b10ac8d82e05b22cc7d4ef5") == "5b10ac8d82e05b22cc7d4ef5"


@pytest.fixture
def session(jira_env, monkeypatch):
    s = MagicMock()
    monkeypatch.setattr(jira_client, "make_session", lambda *_: s)
    monkeypatch.setattr(sja.time, "sleep", lambda *_: None)
    return s


def _route(make_response, users, put_status=204):
    def handler(method, url, **_kwargs):
        if method == "GET":
            return make_response(200, users)
        return make_response(put_status, text="boom")
    return handler


def test_main_assign_resolves_and_puts(session, make_response):
    session.request.side_effect = _route(make_response, [{"accountId": "a-1", "displayName": "Pat"}])
    assert sja.main(["--assignee", "Pat", "P-1", "P-2"]) == 0
    puts = [c for c in session.request.call_args_list if c.args[0] == "PUT"]
    assert len(puts) == 2
    assert puts[-1].kwargs["json"] == {"accountId": "a-1"}


def test_main_unassign_sends_null_and_skips_lookup(session, make_response):
    session.request.return_value = make_response(204)
    assert sja.main(["--unassign", "P-9"]) == 0
    assert session.request.call_count == 1
    assert session.request.call_args.kwargs["json"] == {"accountId": None}


def test_main_keys_csv_and_positional_combine(session, make_response):
    session.request.side_effect = _route(make_response, [{"accountId": "u", "displayName": "u"}])
    assert sja.main(["--assignee", "u", "P-1", "--keys", "P-2,P-3"]) == 0
    assert len([c for c in session.request.call_args_list if c.args[0] == "PUT"]) == 3


def test_main_reports_failure(session, make_response):
    session.request.side_effect = _route(make_response, [{"accountId": "u", "displayName": "u"}], 403)
    assert sja.main(["--assignee", "u", "P-1"]) == 2


def test_main_validates_arguments(jira_env):
    assert sja.main(["--assignee", "X"]) == 1
    assert sja.main(["P-1"]) == 1
