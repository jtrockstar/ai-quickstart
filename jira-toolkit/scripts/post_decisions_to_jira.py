"""Post ADR decisions as comments on their Jira story/epic (idempotent).

Each ADR under the decisions directory declares its Jira target with a
`- Jira: <KEY>` line in its header (a story key, or the epic key when the decision
is cross-cutting / not tied to a single story). This script posts (or updates) a
single marked comment on that issue containing the ADR content.

Re-running is safe:
- unchanged decision  -> skipped (matched by a hidden marker + content hash),
- changed decision    -> the existing comment is updated,
- new decision        -> a comment is created.

Usage:
    python jira-toolkit/scripts/post_decisions_to_jira.py                 # all ADRs
    python jira-toolkit/scripts/post_decisions_to_jira.py --adr documentation/decisions/0002-....md
    python jira-toolkit/scripts/post_decisions_to_jira.py --adr 0007-....md --adr 0008-....md  # repeatable
    python jira-toolkit/scripts/post_decisions_to_jira.py --adr <file> --issue PROJ-42
    python jira-toolkit/scripts/post_decisions_to_jira.py --dry-run

Reads JIRA_URL / JIRA_USERNAME / JIRA_API_TOKEN from the repo-root .env.
Requires: pip install -r jira-toolkit/scripts/requirements.txt
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
import time
from pathlib import Path

import requests

import jira_client
import jira_config as config

DEFAULT_DECISIONS_DIR = config.REPO_ROOT / "documentation" / "decisions"

JIRA_LINE_RE = re.compile(r"^\s*[-*]\s*Jira:\s*([A-Z][A-Z0-9_]+-\d+)\s*$", re.MULTILINE)


def adr_id(path: Path) -> str:
    """'0002-store-utc.md' -> 'ADR-0002'."""
    m = re.match(r"(\d+)", path.name)
    return f"ADR-{m.group(1)}" if m else f"ADR-{path.stem}"


def parse_jira_key(text: str) -> str | None:
    m = JIRA_LINE_RE.search(text)
    return m.group(1) if m else None


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def md_to_jira(md: str) -> str:
    """Light Markdown -> Jira wiki conversion (headings, bold, code, bullets)."""
    out = []
    for line in md.splitlines():
        s = line
        if s.startswith("### "):
            s = "h4. " + s[4:]
        elif s.startswith("## "):
            s = "h3. " + s[3:]
        elif s.startswith("# "):
            s = "h2. " + s[2:]
        else:
            s = re.sub(r"^(\s*)[-*] ", r"\1* ", s)
        s = re.sub(r"\*\*(.+?)\*\*", r"*\1*", s)
        s = re.sub(r"`([^`]+)`", r"{{\1}}", s)
        out.append(s)
    return "\n".join(out)


def build_comment(adr: str, h: str, wiki_body: str) -> str:
    marker = f"_(decision-sync id:{adr} hash:{h} — auto-managed; edit the ADR, not this comment)_"
    return f"{marker}\n\n{wiki_body}"


def find_marked_comment(session, base_url, key, adr):
    """Return (comment_id, body) of the existing decision-sync comment, or (None, None)."""
    token = f"decision-sync id:{adr}"
    start = 0
    while True:
        r = jira_client.request(session, "GET", f"{base_url}/rest/api/2/issue/{key}/comment",
                                params={"startAt": start, "maxResults": 100})
        r.raise_for_status()
        data = r.json()
        comments = data.get("comments", [])
        for c in comments:
            if token in (c.get("body") or ""):
                return c.get("id"), c.get("body")
        start += len(comments)
        if not comments or start >= data.get("total", 0):
            return None, None


def sync_one(session, base_url, path: Path, override_issue: str | None, dry_run: bool) -> str:
    text = path.read_text(encoding="utf-8-sig")
    adr = adr_id(path)
    key = override_issue or parse_jira_key(text)
    if not key:
        print(f"  {adr}: SKIP (no `- Jira: KEY` line and no --issue)")
        return "skipped"

    h = content_hash(text)
    body = build_comment(adr, h, md_to_jira(text))
    existing_id, existing_body = find_marked_comment(session, base_url, key, adr)

    if existing_id and f"hash:{h}" in (existing_body or ""):
        print(f"  {adr} -> {key}: unchanged")
        return "unchanged"

    if dry_run:
        action = "would update" if existing_id else "would create"
        print(f"  {adr} -> {key}: {action}")
        return "dry-run"

    if existing_id:
        r = jira_client.request(session, "PUT",
                                f"{base_url}/rest/api/2/issue/{key}/comment/{existing_id}",
                                json={"body": body})
        r.raise_for_status()
        print(f"  {adr} -> {key}: updated")
        return "updated"

    r = jira_client.request(session, "POST", f"{base_url}/rest/api/2/issue/{key}/comment",
                            json={"body": body})
    r.raise_for_status()
    print(f"  {adr} -> {key}: created")
    return "created"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Post ADR decisions as Jira comments.")
    ap.add_argument("--decisions-dir", default=str(DEFAULT_DECISIONS_DIR))
    ap.add_argument("--adr", action="append",
                    help="Sync a specific ADR file (repeatable; default: all in decisions-dir)")
    ap.add_argument("--issue", help="Override the target issue key for a single --adr")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    if args.adr:
        paths = [Path(p) for p in args.adr]
    else:
        paths = sorted(Path(args.decisions_dir).glob("[0-9]*.md"))
    if not paths:
        print("ERROR: no ADR files found")
        return 1
    if args.issue and len(paths) != 1:
        print("ERROR: --issue can only be used with a single --adr")
        return 1

    try:
        session, base_url = jira_client.connect()
    except jira_client.JiraConfigError as exc:
        print(f"ERROR: {exc}")
        return 1

    print(f"Syncing {len(paths)} decision(s) to {base_url}"
          + (" [dry-run]" if args.dry_run else ""))
    failures = 0
    for p in paths:
        try:
            sync_one(session, base_url, p, args.issue, args.dry_run)
        except requests.RequestException as exc:
            failures += 1
            print(f"  {adr_id(p)}: FAIL {exc}")
        time.sleep(config.PACE_SECONDS)

    print(f"Done. {failures} failure(s).")
    return 0 if failures == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
