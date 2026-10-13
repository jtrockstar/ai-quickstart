"""Set story points on Jira issues, finding the points field by name.

Story points are a Jira Software field whose name (and id) depends on the project type:
"Story point estimate" in team-managed projects, "Story Points" in company-managed ones.
This script reads each issue's edit metadata and uses the first matching name from
``jira_config.STORY_POINT_FIELD_NAMES`` (or ``--field-name``), so no field id is
hard-coded. Paced and retried via ``jira_client``.

Usage:
    python jira-toolkit/scripts/set_story_points.py PROJ-12=3 PROJ-13=5
    python jira-toolkit/scripts/set_story_points.py PROJ-12=8 --dry-run
    python jira-toolkit/scripts/set_story_points.py PROJ-12=2 --field-name "Story Points"

Requires: pip install -r jira-toolkit/scripts/requirements.txt
"""
from __future__ import annotations

import argparse
import re
import time

import jira_client
import jira_config as config

PAIR_RE = re.compile(r"^([A-Z][A-Z0-9_]+-\d+)=(\d+(?:\.\d+)?)$")


def parse_pairs(items: list[str]) -> list[tuple[str, float]]:
    """'PROJ-1=3' -> ('PROJ-1', 3.0). Raises ValueError on a malformed item."""
    pairs = []
    for item in items:
        m = PAIR_RE.match(item.strip())
        if not m:
            raise ValueError(f"expected KEY=POINTS, got {item!r}")
        pairs.append((m.group(1), float(m.group(2))))
    return pairs


def set_points(session, base_url, key, points, names, *, dry_run=False) -> str:
    field_id = jira_client.resolve_field_id_for_issue(session, base_url, key, names)
    if not field_id:
        return f"FAILED (no editable field named {' / '.join(names)})"
    if dry_run:
        return f"would set {field_id} = {points:g}"
    r = jira_client.request(session, "PUT", f"{base_url}/rest/api/2/issue/{key}",
                            json={"fields": {field_id: points}})
    if r.status_code in (200, 204):
        return f"{field_id} = {points:g}"
    return f"FAILED ({r.status_code}: {r.text[:120]})"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pairs", nargs="+", help="KEY=POINTS, e.g. PROJ-12=3")
    ap.add_argument("--field-name", action="append",
                    help="Field name to look for (repeatable; default from jira_config)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    try:
        pairs = parse_pairs(args.pairs)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1
    names = tuple(args.field_name or config.STORY_POINT_FIELD_NAMES)

    try:
        session, base_url = jira_client.connect()
    except jira_client.JiraConfigError as exc:
        print(f"ERROR: {exc}")
        return 1

    failures = 0
    for key, points in pairs:
        result = set_points(session, base_url, key, points, names, dry_run=args.dry_run)
        if result.startswith("FAILED"):
            failures += 1
        print(f"  {key}: {result}")
        time.sleep(config.PACE_SECONDS)

    print(f"Done. {len(pairs) - failures} ok, {failures} failed.")
    return 0 if failures == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
