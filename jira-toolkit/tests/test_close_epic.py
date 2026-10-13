"""Tests for jira-toolkit/scripts/close_epic.py (network mocked)."""
from unittest.mock import MagicMock

import close_epic as ce
import jira_client

DONE = {"id": "31", "to": {"name": "Done", "statusCategory": {"key": "done"}}}
CLOSED = {"id": "41", "to": {"name": "Closed", "statusCategory": {"key": "done"}}}
PROGRESS = {"id": "21", "to": {"name": "In Progress", "statusCategory": {"key": "indeterminate"}}}


def _issue(make_response, status_cat="indeterminate", resolution=None):
    return make_response(200, {"fields": {"status": {"statusCategory": {"key": status_cat}},
                                          "resolution": resolution}})


def _router(make_response, *, status_cat="indeterminate", resolution=None,
            transitions=(DONE,), transition_statuses=(204,), agile_status=204):
    transition_results = iter(transition_statuses)
    calls = []

    def handler(method, url, **kwargs):
        calls.append((method, url, kwargs))
        if method == "GET" and url.endswith("/transitions"):
            return make_response(200, {"transitions": list(transitions)})
        if method == "GET":
            return _issue(make_response, status_cat, resolution)
        if url.endswith("/transitions"):
            return make_response(next(transition_results), text="err")
        return make_response(agile_status, text="agile")
    session = MagicMock()
    session.request.side_effect = handler
    return session, calls


def test_find_done_transition_prefers_named_done(make_response):
    session = MagicMock()
    session.request.return_value = make_response(200, {"transitions": [PROGRESS, CLOSED, DONE]})
    assert ce.find_done_transition(session, "https://j", "P-1") == "31"


def test_find_done_transition_falls_back_to_any_done_category(make_response):
    session = MagicMock()
    session.request.return_value = make_response(200, {"transitions": [PROGRESS, CLOSED]})
    assert ce.find_done_transition(session, "https://j", "P-1") == "41"


def test_close_epic_transitions_with_resolution_and_sets_agile_flag(make_response):
    session, calls = _router(make_response)
    actions = ce.close_epic(session, "https://j", "P-1")
    assert actions == ["status -> Done", "agile done flag -> true"]
    transition_post = [c for c in calls if c[0] == "POST" and c[1].endswith("/transitions")][0]
    assert transition_post[2]["json"]["fields"] == {"resolution": {"name": "Done"}}


def test_close_epic_retries_without_resolution_on_400(make_response):
    session, calls = _router(make_response, transition_statuses=(400, 204))
    actions = ce.close_epic(session, "https://j", "P-1")
    assert actions[0] == "status -> Done"
    posts = [c for c in calls if c[0] == "POST" and c[1].endswith("/transitions")]
    assert len(posts) == 2 and "fields" not in posts[1][2]["json"]


def test_close_epic_agile_not_applicable_is_not_failure(make_response):
    session, _ = _router(make_response, status_cat="done", resolution={"name": "Done"}, agile_status=404)
    actions = ce.close_epic(session, "https://j", "P-1")
    assert actions == ["agile done flag n/a for this project"]
    assert not any("FAILED" in a for a in actions)


def test_close_epic_flags_missing_resolution(make_response):
    session, _ = _router(make_response, status_cat="done", resolution=None)
    assert ce.close_epic(session, "https://j", "P-1")[0].startswith("note: already Done")


def test_close_epic_reports_no_done_transition(make_response):
    session, _ = _router(make_response, transitions=(PROGRESS,))
    assert ce.close_epic(session, "https://j", "P-1")[0].startswith("status FAILED")


def test_close_epic_dry_run_makes_no_writes(make_response):
    session, calls = _router(make_response)
    actions = ce.close_epic(session, "https://j", "P-1", dry_run=True)
    assert len(actions) == 2
    assert all(c[0] == "GET" for c in calls)


def test_main_uses_jql(jira_env, monkeypatch, make_response):
    session, _ = _router(make_response, status_cat="done", resolution={"name": "Done"})
    monkeypatch.setattr(jira_client, "make_session", lambda *_: session)
    monkeypatch.setattr(jira_client, "search_keys", lambda *_a: ["P-1", "P-2"])
    assert ce.main(["--jql", "project = P"]) == 0


def test_main_without_keys_returns_1(jira_env, monkeypatch):
    monkeypatch.setattr(jira_client, "make_session", lambda *_: MagicMock())
    assert ce.main([]) == 1
