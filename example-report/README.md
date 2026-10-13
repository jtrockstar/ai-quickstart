# example-report

A small, working example project that shows the repo's code conventions end to end. It
collects open-item counts per service from a REST API (the "Source API"), stores one
immutable file per day, and rebuilds a rollup that a dashboard can chart.

Design and requirements: [PRD](../documentation/example-report-product-requirements.md) ·
[TDD](../documentation/example-report-technical-design.md) ·
[stories](../documentation/example-report-user-stories.md).

## Layout

| Path | What it is |
|---|---|
| `scripts/example_report_config.py` | Every tunable: API paths, severities, data paths, retry, time zone. |
| `scripts/example_report_rest.py` | `SourceClient`: auth, retry/backoff, per-process cache, `utf-8-sig` decode. |
| `scripts/example_report_dates.py` | Store UTC, bucket/display in the reporting time zone. |
| `scripts/example_report_collect.py` | CLI: collect → immutable daily partition → rollup. |
| `tests/` | pytest, one `test_<module>.py` per script, network mocked. |
| `data/` | Generated output (created on first run). |

## Run

```powershell
$py = '.venv\Scripts\python.exe'
& $py -m pip install -r example-report\scripts\requirements.txt
& $py example-report\scripts\example_report_collect.py          # needs SOURCE_API_URL / SOURCE_API_TOKEN in .env
& $py example-report\scripts\example_report_collect.py --rollup-only
& $py -m pytest example-report\tests -q
```

To start a real project from this one, copy the folder, rename the `example_report_` prefix,
and replace the Source API calls. Keep the config / REST / dates split.
