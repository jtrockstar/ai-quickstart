"""Collect today's open-item counts per service and rebuild the rollup.

One run:
1. lists the services from the Source API;
2. reads each service's open-item counts by severity;
3. writes an **immutable** daily partition ``data/daily/<YYYY-MM-DD>.json`` (local date) —
   an existing partition is left alone unless ``--force`` is given;
4. rebuilds ``data/rollup.json`` from every daily partition (the dashboard reads this).

Usage:
    python example-report/scripts/example_report_collect.py
    python example-report/scripts/example_report_collect.py --force
    python example-report/scripts/example_report_collect.py --rollup-only
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import example_report_config as config
import example_report_dates as dates
from example_report_rest import SourceClient, SourceConfigError


def collect_counts(client: SourceClient) -> dict[str, dict[str, int]]:
    """Return ``{service_key: {severity: count}}`` for every service."""
    services = client.get_json(config.SERVICES_PATH)
    result = {}
    for service in services:
        key = service["key"]
        counts = client.get_json(config.OPEN_ITEMS_PATH.format(key=key)).get("counts", {})
        result[key] = {sev: int(counts.get(sev, 0)) for sev in config.SEVERITIES}
    return result


def build_partition(counts: dict, collected_at: datetime) -> dict:
    return {
        "date": dates.local_date(collected_at).isoformat(),
        "collectedAt": dates.to_utc_iso(collected_at),
        "services": counts,
    }


def write_partition(partition: dict, daily_dir: Path, force: bool = False) -> tuple[Path, bool]:
    """Write the partition; returns (path, written). Existing files are kept unless forced."""
    daily_dir.mkdir(parents=True, exist_ok=True)
    path = daily_dir / f"{partition['date']}.json"
    if path.exists() and not force:
        return path, False
    path.write_text(json.dumps(partition, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path, True


def build_rollup(daily_dir: Path) -> dict:
    """Combine every daily partition into a per-day series of totals by severity."""
    days = []
    for path in sorted(daily_dir.glob("*.json")):
        partition = json.loads(path.read_text(encoding="utf-8-sig"))
        totals = {sev: 0 for sev in config.SEVERITIES}
        for counts in partition.get("services", {}).values():
            for sev in config.SEVERITIES:
                totals[sev] += counts.get(sev, 0)
        days.append({"date": partition["date"], "totals": totals,
                     "services": len(partition.get("services", {}))})
    return {"severities": list(config.SEVERITIES), "days": days}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true", help="Overwrite today's partition if present.")
    ap.add_argument("--rollup-only", action="store_true", help="Skip collection; rebuild the rollup.")
    args = ap.parse_args(argv)

    if not args.rollup_only:
        try:
            client = SourceClient.from_env()
        except SourceConfigError as exc:
            print(f"ERROR: {exc}")
            return 1
        partition = build_partition(collect_counts(client), dates.utc_now())
        path, written = write_partition(partition, config.DAILY_DIR, force=args.force)
        print(f"{'wrote' if written else 'kept existing'} {path}")

    rollup = build_rollup(config.DAILY_DIR)
    config.ROLLUP_FILE.parent.mkdir(parents=True, exist_ok=True)
    config.ROLLUP_FILE.write_text(json.dumps(rollup, indent=2) + "\n", encoding="utf-8")
    print(f"rollup: {len(rollup['days'])} day(s) -> {config.ROLLUP_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
