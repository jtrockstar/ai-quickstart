"""Tests for jira-toolkit/scripts/post_decisions_to_jira.py (network mocked)."""
from pathlib import Path
from unittest.mock import MagicMock

import post_decisions_to_jira as pdj


def test_parse_jira_key():
    assert pdj.parse_jira_key("- Status: Accepted\n- Jira: PROJ-42\n") == "PROJ-42"
    assert pdj.parse_jira_key("- Jira: EPIC_1-9\n") == "EPIC_1-9"
    assert pdj.parse_jira_key("no key here") is None


def test_adr_id():
    assert pdj.adr_id(Path("0002-store-utc.md")) == "ADR-0002"
    assert pdj.adr_id(Path("0010-x.md")) == "ADR-0010"


def test_md_to_jira():
    out = pdj.md_to_jira("# Title\n## Context\n- a **bold** and `code`\n### Sub")
    assert "h2. Title" in out
    assert "h3. Context" in out
    assert "h4. Sub" in out
    assert "* a *bold* and {{code}}" in out


def _adr_file(tmp_path, name="0002-store-utc.md", key="PROJ-1"):
    p = tmp_path / name
    p.write_text(f"# 2. Store UTC\n\n- Status: Accepted\n- Jira: {key}\n\n## Decision\n\n- do it\n",
                 encoding="utf-8")
    return p


def _session(make_response, comments, write_status=201):
    session = MagicMock()

    def handler(method, url, **_kwargs):
        if method == "GET":
            return make_response(200, {"comments": comments, "total": len(comments)})
        return make_response(write_status)
    session.request.side_effect = handler
    return session


def _writes(session):
    return [c for c in session.request.call_args_list if c.args[0] in ("POST", "PUT")]


def test_sync_one_creates_when_absent(tmp_path, make_response):
    session = _session(make_response, [])
    assert pdj.sync_one(session, "https://j", _adr_file(tmp_path), None, dry_run=False) == "created"
    (call,) = _writes(session)
    assert call.args[0] == "POST"
    assert "decision-sync id:ADR-0002" in call.kwargs["json"]["body"]


def test_sync_one_unchanged_skips_write(tmp_path, make_response):
    p = _adr_file(tmp_path)
    h = pdj.content_hash(p.read_text(encoding="utf-8-sig"))
    session = _session(make_response, [{"id": "5", "body": f"_(decision-sync id:ADR-0002 hash:{h})_"}])
    assert pdj.sync_one(session, "https://j", p, None, dry_run=False) == "unchanged"
    assert _writes(session) == []


def test_sync_one_updates_when_changed(tmp_path, make_response):
    session = _session(make_response, [{"id": "7", "body": "_(decision-sync id:ADR-0002 hash:OLD)_"}], 200)
    assert pdj.sync_one(session, "https://j", _adr_file(tmp_path), None, dry_run=False) == "updated"
    (call,) = _writes(session)
    assert call.args[0] == "PUT" and "/comment/7" in call.args[1]


def test_find_marked_comment_paginates(make_response):
    session = MagicMock()
    session.request.side_effect = [
        make_response(200, {"comments": [{"id": "1", "body": "x"}], "total": 2}),
        make_response(200, {"comments": [{"id": "2", "body": "decision-sync id:ADR-0003 hash:a"}],
                            "total": 2}),
    ]
    assert pdj.find_marked_comment(session, "https://j", "P-1", "ADR-0003")[0] == "2"
    assert session.request.call_args_list[1].kwargs["params"]["startAt"] == 1


def test_sync_one_skips_without_key(tmp_path):
    p = tmp_path / "0003-x.md"
    p.write_text("# 3. X\n\n- Status: Accepted\n\n## Decision\n- y\n", encoding="utf-8")
    session = MagicMock()
    assert pdj.sync_one(session, "https://j", p, None, dry_run=False) == "skipped"
    session.request.assert_not_called()


def test_sync_one_dry_run_no_write(tmp_path, make_response):
    session = _session(make_response, [])
    assert pdj.sync_one(session, "https://j", _adr_file(tmp_path), None, dry_run=True) == "dry-run"
    assert _writes(session) == []


def test_sync_one_override_issue(tmp_path, make_response):
    session = _session(make_response, [])
    pdj.sync_one(session, "https://j", _adr_file(tmp_path, key="PROJ-1"), "PROJ-999", dry_run=False)
    assert "/issue/PROJ-999/comment" in _writes(session)[0].args[1]
