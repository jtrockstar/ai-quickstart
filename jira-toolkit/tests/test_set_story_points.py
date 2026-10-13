"""Tests for jira-toolkit/scripts/set_story_points.py (network mocked)."""
from unittest.mock import MagicMock

import pytest

import jira_client
import set_story_points as ssp

EDITMETA = {"fields": {"summary": {"name": "Summary"},
                       "points_id": {"name": "Story point estimate"}}}


def test_parse_pairs():
    assert ssp.parse_pairs(["PROJ-1=3", "PROJ-22=0.5"]) == [("PROJ-1", 3.0), ("PROJ-22", 0.5)]
    with pytest.raises(ValueError):
        ssp.parse_pairs(["PROJ-1:3"])


def _session(make_response, editmeta=EDITMETA, put_status=204):
    session = MagicMock()

    def handler(method, url, **_kwargs):
        if method == "GET":
            return make_response(200, editmeta)
        return make_response(put_status, text="nope")
    session.request.side_effect = handler
    return session


def test_set_points_resolves_field_by_name(make_response):
    session = _session(make_response)
    result = ssp.set_points(session, "https://j", "P-1", 5.0, ("Story Points", "Story point estimate"))
    assert result == "points_id = 5"
    put = session.request.call_args
    assert put.args[0] == "PUT" and put.kwargs["json"] == {"fields": {"points_id": 5.0}}


def test_set_points_reports_missing_field(make_response):
    session = _session(make_response, editmeta={"fields": {}})
    assert ssp.set_points(session, "https://j", "P-1", 3.0, ("Story Points",)).startswith("FAILED")


def test_set_points_dry_run_does_not_write(make_response):
    session = _session(make_response)
    assert ssp.set_points(session, "https://j", "P-1", 3.0, ("Story point estimate",),
                          dry_run=True).startswith("would set")
    assert all(c.args[0] == "GET" for c in session.request.call_args_list)


def test_main_counts_failures(jira_env, monkeypatch, make_response):
    session = _session(make_response, put_status=400)
    monkeypatch.setattr(jira_client, "make_session", lambda *_: session)
    assert ssp.main(["PROJ-1=3"]) == 2


def test_main_rejects_bad_pair(jira_env):
    assert ssp.main(["PROJ-1"]) == 1
