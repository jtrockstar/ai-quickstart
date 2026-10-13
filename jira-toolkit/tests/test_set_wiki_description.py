"""Tests for jira-toolkit/scripts/set_wiki_description.py (network mocked)."""
from unittest.mock import MagicMock

import jira_client
import set_wiki_description as swd


def test_read_body_from_file_strips_bom(tmp_path):
    p = tmp_path / "d.wiki.txt"
    p.write_text("\ufeffh3. Summary\n", encoding="utf-8")
    assert swd.read_body(str(p)) == "h3. Summary\n"


def test_set_description_puts_raw_wiki(make_response):
    session = MagicMock()
    session.request.return_value = make_response(204)
    ok, msg = swd.set_description(session, "https://j", "P-1", "h3. Summary\n{{code}}")
    assert ok and "P-1" in msg
    args, kwargs = session.request.call_args
    assert args[0] == "PUT" and args[1].endswith("/rest/api/2/issue/P-1")
    assert kwargs["json"] == {"fields": {"description": "h3. Summary\n{{code}}"}}


def test_set_description_reports_failure(make_response):
    session = MagicMock()
    session.request.return_value = make_response(400, text="bad field")
    ok, msg = swd.set_description(session, "https://j", "P-1", "x")
    assert not ok and "400" in msg


def test_main_end_to_end(jira_env, tmp_path, monkeypatch, make_response):
    p = tmp_path / "d.txt"
    p.write_text("body", encoding="utf-8")
    session = MagicMock()
    session.request.return_value = make_response(204)
    monkeypatch.setattr(jira_client, "make_session", lambda *_: session)
    assert swd.main(["P-9", str(p)]) == 0
    assert session.request.call_args.args[1] == "https://example.atlassian.net/rest/api/2/issue/P-9"


def test_main_missing_settings_returns_1(monkeypatch, tmp_path):
    p = tmp_path / "d.txt"
    p.write_text("body", encoding="utf-8")
    monkeypatch.setattr(jira_client, "load_dotenv", lambda *_a, **_k: None)
    monkeypatch.delenv("JIRA_API_TOKEN", raising=False)
    assert swd.main(["P-9", str(p)]) == 1
