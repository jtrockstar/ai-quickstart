# Source API collector — developer guide

_Last updated: 2026-10-12 — Story PROJ-6._

> **Example developer guide.** Deeper how-to reference for the collector and its REST helper.
> The TDD (§5.2, §5.4) points here; this guide holds the detail so the TDD stays
> architectural. Start a new guide from
> [../templates/developer-guide-template.md](../templates/developer-guide-template.md).

## What it does

`example_report_collect.py` lists services, reads each one's open-item counts, writes today's
immutable partition, and rebuilds the rollup. Architecture and decisions: TDD §5.0, ADR-0002,
ADR-0003.

## Interfaces

| Function | Input | Output |
|---|---|---|
| `collect_counts(client)` | a `SourceClient` | `{service_key: {high, medium, low}}` (missing severities = 0) |
| `build_partition(counts, collected_at)` | counts + an aware datetime | `{date, collectedAt, services}` |
| `write_partition(partition, daily_dir, force=False)` | partition + folder | `(path, written)`; never overwrites unless `force` |
| `build_rollup(daily_dir)` | folder of partitions | `{severities, days: [{date, totals, services}]}` |

## Tunable knobs (all in `example_report_config.py`)

| Constant | Default | Effect |
|---|---|---|
| `SEVERITIES` | `("high", "medium", "low")` | Which counts are stored and summed |
| `DAILY_DIR` / `ROLLUP_FILE` | `example-report/data/...` | Where output goes |
| `MAX_ATTEMPTS` / `BACKOFF_BASE` | `4` / `2` | Retry policy: waits 2, 4, 8 s |
| `REPORT_TIMEZONE` | `America/New_York` | Day boundaries and partition names |

## Running locally

```powershell
$py = '.venv\Scripts\python.exe'
$env:PYTHONUNBUFFERED = '1'
& $py example-report\scripts\example_report_collect.py *> .scratch\collect.log
```

Then open `.scratch\collect.log`. Expected output:

```
wrote C:\...\example-report\data\daily\2026-10-12.json
rollup: 1 day(s) -> C:\...\example-report\data\rollup.json
```

A second run the same day prints `kept existing …`. Use `--force` only to repair a known-bad
capture, and say why in the commit message.

## Spot checks

1. Delete nothing; run twice; confirm the partition's `collectedAt` is unchanged.
2. Run with `--rollup-only`; confirm the rollup's last day matches the newest partition.
3. Run the tests: `& $py -m pytest example-report\tests -q`.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `ERROR: Set SOURCE_API_URL and SOURCE_API_TOKEN …` | `.env` missing values | Copy `.env.example` to `.env` and fill it in |
| `RemoteDisconnected` locally | Gateway dropped the request | Confirm the browser-like User-Agent is set (it is, in `config.USER_AGENT`) |
| SSL certificate error locally | TLS-inspecting proxy | `pip install truststore` (in requirements) |
| Repeated HTTP 429 | Rate limit | Wait and re-run; raise `BACKOFF_BASE` if it persists |
