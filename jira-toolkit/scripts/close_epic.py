"""Fully "close" one or more Jira epics.

Closing an epic means:

1. **Workflow status** -> a status in the *Done* category (preferring one named ``Done``).
2. **Resolution** -> ``Done``, sent *during* that transition when the transition screen
   allows it. Default Jira Cloud workflows set the resolution themselves, so a 400 on the
   first attempt is retried without the resolution field.
3. **Agile "done" flag** -> ``POST /rest/agile/1.0/epic/{key}`` with ``{"done": true}``,
   the same call a board's "Mark as done" makes. Not every project type uses this flag
   (team-managed projects don't); a 400/404 there is reported as "n/a", not a failure.

Idempotent and paced (retry/backoff via ``jira_client``). Works on one epic, a list of
epics, or every epic matching a JQL. Reads JIRA_URL / JIRA_USERNAME / JIRA_API_TOKEN
from the repo-root .env.

Usage:
    python jira-toolkit/scripts/close_epic.py PROJ-10
    python jira-toolkit/scripts/close_epic.py PROJ-10 PROJ-11 --dry-run
    python jira-toolkit/scripts/close_epic.py --jql 'project = PROJ AND issuetype = Epic AND statusCategory = Done AND resolution IS EMPTY'

Requires: pip install -r jira-toolkit/scripts/requirements.txt
"""
from __future__ import annotations

import argparse
import time

import requests

import jira_client
import jira_config as config


def find_done_transition(session, base_url, key):
    """Return the id of a transition landing in a Done-category status, or None."""
    r = jira_client.request(session, "GET", f"{base_url}/rest/api/2/issue/{key}/transitions")
    r.raise_for_status()
    transitions = r.json().get("transitions", [])
    done = [t for t in transitions
            if (t.get("to") or {}).get("statusCategory", {}).get("key") == "done"]
    if not done:
        return None
    wanted = config.DONE_STATUS_NAME.lower()
    exact = [t for t in done if (t.get("to") or {}).get("name", "").lower() == wanted]
    return (exact or done)[0]["id"]


def close_epic(session, base_url, key, *, dry_run=False) -> list[str]:
    """Close one epic (status + resolution, agile done flag). Returns actions taken."""
    r = jira_client.request(session, "GET", f"{base_url}/rest/api/2/issue/{key}",
                            params={"fields": "status,resolution"})
    r.raise_for_status()
    fields = r.json()["fields"]
    status_cat = (fields.get("status") or {}).get("statusCategory", {}).get("key")
    actions: list[str] = []

    if status_cat != "done":
        if dry_run:
            actions.append(f"status -> {config.DONE_STATUS_NAME} (+resolution {config.RESOLUTION_DONE})")
        else:
            actions.append(_transition_to_done(session, base_url, key))
    elif not fields.get("resolution"):
        actions.append("note: already Done but Resolution empty (the workflow did not set it)")

    if dry_run:
        actions.append("agile done flag -> true")
    else:
        er = jira_client.request(session, "POST", f"{base_url}/rest/agile/1.0/epic/{key}",
                                 json={"done": True})
        if er.status_code in (200, 204):
            actions.append("agile done flag -> true")
        elif er.status_code in (400, 404):
            actions.append("agile done flag n/a for this project")
        else:
            actions.append(f"agile done flag FAILED ({er.status_code}: {er.text[:120]})")
    return actions


def _transition_to_done(session, base_url, key) -> str:
    tid = find_done_transition(session, base_url, key)
    if not tid:
        return "status FAILED (no Done transition available)"
    url = f"{base_url}/rest/api/2/issue/{key}/transitions"
    body = {"transition": {"id": tid}, "fields": {"resolution": {"name": config.RESOLUTION_DONE}}}
    tr = jira_client.request(session, "POST", url, json=body)
    if tr.status_code == 400:  # resolution not on this transition's screen
        tr = jira_client.request(session, "POST", url, json={"transition": {"id": tid}})
    if tr.status_code in (200, 204):
        return f"status -> {config.DONE_STATUS_NAME}"
    return f"status FAILED ({tr.status_code}: {tr.text[:120]})"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("keys", nargs="*", help="Epic key(s), e.g. PROJ-10")
    parser.add_argument("--jql", default=None, help="Select epics by JQL instead of listing keys.")
    parser.add_argument("--dry-run", action="store_true", help="Print what would change; make no edits.")
    args = parser.parse_args(argv)

    try:
        session, base_url = jira_client.connect()
    except jira_client.JiraConfigError as exc:
        print(f"ERROR: {exc}")
        return 1

    keys = jira_client.search_keys(session, base_url, args.jql) if args.jql else list(args.keys)
    if not keys:
        print("No epics to close (pass key(s) or --jql).")
        return 1

    print(f"{'[dry-run] ' if args.dry_run else ''}closing {len(keys)} epic(s)")
    failures = 0
    for key in keys:
        try:
            actions = close_epic(session, base_url, key, dry_run=args.dry_run)
        except requests.RequestException as exc:
            print(f"  {key}: ERROR {exc}")
            failures += 1
            continue
        if any("FAILED" in a for a in actions):
            failures += 1
        print(f"  {key}: {'; '.join(actions) or 'already closed'}")
        time.sleep(config.PACE_SECONDS)

    print(f"done ({len(keys) - failures}/{len(keys)} clean)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
