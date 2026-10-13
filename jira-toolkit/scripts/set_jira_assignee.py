"""Bulk-set (or clear) the assignee on Jira issues.

Jira Cloud assigns by **accountId**. ``--assignee`` accepts a display name or email and
resolves it with the user-search API; if nothing matches, the value is used as an
accountId as-is. Requests are paced and retried (via ``jira_client``) to avoid throttling.
Reads JIRA_URL / JIRA_USERNAME / JIRA_API_TOKEN from the repo-root .env.

Usage:
    python jira-toolkit/scripts/set_jira_assignee.py --assignee "Pat Example" PROJ-12 PROJ-13
    python jira-toolkit/scripts/set_jira_assignee.py --assignee pat@example.com --keys PROJ-12,PROJ-13
    python jira-toolkit/scripts/set_jira_assignee.py --unassign PROJ-12

Requires: pip install -r jira-toolkit/scripts/requirements.txt
"""
from __future__ import annotations

import argparse
import sys
import time

import jira_client
import jira_config as config


def resolve_account_id(session, base_url: str, query: str) -> str:
    """Resolve a display name / email to an accountId (falls back to the literal value)."""
    r = jira_client.request(session, "GET", f"{base_url}/rest/api/3/user/search",
                            params={"query": query, "maxResults": 10})
    users = r.json() if r.ok else []
    if not users:
        return query
    wanted = query.lower()
    for user in users:
        if wanted in ((user.get("displayName") or "").lower(),
                      (user.get("emailAddress") or "").lower()):
            return user["accountId"]
    return users[0]["accountId"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Bulk-set the assignee on Jira issues.")
    ap.add_argument("keys", nargs="*", help="Issue keys (e.g. PROJ-12)")
    ap.add_argument("--keys", dest="keys_csv", help="Comma-separated issue keys")
    ap.add_argument("--assignee", help="Display name, email, or accountId to assign")
    ap.add_argument("--unassign", action="store_true", help="Clear the assignee instead")
    args = ap.parse_args(argv)

    keys = list(args.keys)
    if args.keys_csv:
        keys += [k.strip() for k in args.keys_csv.split(",") if k.strip()]
    if not keys:
        print("ERROR: no issue keys provided")
        return 1
    if not args.unassign and not args.assignee:
        print("ERROR: provide --assignee NAME or --unassign")
        return 1

    try:
        session, base_url = jira_client.connect()
    except jira_client.JiraConfigError as exc:
        print(f"ERROR: {exc}")
        return 1

    if args.unassign:
        account_id, who = None, "(unassigned)"
    else:
        account_id = resolve_account_id(session, base_url, args.assignee)
        who = f"{args.assignee} ({account_id})"
    payload = {"accountId": account_id}  # null clears the assignee

    print(f"Setting assignee = {who} on {len(keys)} issue(s) at {base_url}")
    failures = 0
    for key in keys:
        r = jira_client.request(session, "PUT", f"{base_url}/rest/api/2/issue/{key}/assignee",
                                json=payload)
        if r.status_code in (200, 204):
            print(f"  {key} OK")
        else:
            failures += 1
            print(f"  {key} FAIL {r.status_code} {r.text[:120]}")
        time.sleep(config.PACE_SECONDS)

    print(f"Done. {len(keys) - failures} ok, {failures} failed.")
    return 0 if failures == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
