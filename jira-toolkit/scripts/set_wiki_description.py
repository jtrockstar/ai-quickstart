"""Set a Jira issue's description from raw Jira wiki markup via the REST API.

We author epic/story descriptions in **Jira wiki markup** and PUT them directly, because
the MCP server's markdown->wiki conversion can mangle content: it may drop `+`, escape `_`
with a backslash, and rewrite `<...>` to `[...]` (even inside `{{code}}`/`{code}` blocks).
Writing the wiki markup straight to REST API v2 (which still accepts wiki markup on Jira
Cloud) keeps identifiers, angle-bracket path templates, and `+` intact.

The description is read from a file (or stdin) so multi-line wiki markup is not subject
to shell quoting. Reads JIRA_URL / JIRA_USERNAME / JIRA_API_TOKEN from the repo-root .env.

Usage:
    python jira-toolkit/scripts/set_wiki_description.py PROJ-123 .scratch/desc.wiki.txt
    Get-Content desc.txt -Raw | python jira-toolkit/scripts/set_wiki_description.py PROJ-123 -

Requires: pip install -r jira-toolkit/scripts/requirements.txt
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import jira_client


def read_body(source: str) -> str:
    if source == "-":
        return sys.stdin.read()
    return Path(source).read_text(encoding="utf-8-sig")


def set_description(session, base_url: str, key: str, body: str) -> tuple[bool, str]:
    resp = jira_client.request(session, "PUT", f"{base_url}/rest/api/2/issue/{key}",
                               json={"fields": {"description": body}})
    if resp.status_code in (200, 204):
        return True, f"OK: description updated on {key}"
    return False, f"FAILED {resp.status_code}: {resp.text[:500]}"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("issue_key", help="Jira issue key, e.g. PROJ-123")
    parser.add_argument("body_file", help="File holding raw Jira wiki markup, or '-' for stdin")
    args = parser.parse_args(argv)

    body = read_body(args.body_file)
    try:
        session, base_url = jira_client.connect()
    except jira_client.JiraConfigError as exc:
        print(f"ERROR: {exc}")
        return 1

    ok, message = set_description(session, base_url, args.issue_key, body)
    print(message)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
