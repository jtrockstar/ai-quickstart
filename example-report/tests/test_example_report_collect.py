"""Tests for example-report/scripts/example_report_collect.py (Source API mocked)."""
import json
from datetime import datetime, timezone
from unittest.mock import MagicMock

import example_report_collect as collect


def _client():
    client = MagicMock()
    responses = {
        "api/v1/services": [{"key": "billing"}, {"key": "search"}],
        "api/v1/services/billing/open-items": {"counts": {"high": 2, "low": 5}},
        "api/v1/services/search/open-items": {"counts": {"high": 1, "medium": 3, "low": "4"}},
    }
    client.get_json.side_effect = lambda path, *a, **k: responses[path]
    return client


def test_collect_counts_fills_missing_severities_with_zero():
    assert collect.collect_counts(_client()) == {
        "billing": {"high": 2, "medium": 0, "low": 5},
        "search": {"high": 1, "medium": 3, "low": 4},
    }


def test_build_partition_uses_local_date():
    moment = datetime(2026, 1, 15, 2, 30, tzinfo=timezone.utc)
    partition = collect.build_partition({"a": {}}, moment)
    assert partition["date"] == "2026-01-14"
    assert partition["collectedAt"] == "2026-01-15T02:30:00Z"


def test_write_partition_is_immutable_unless_forced(tmp_path):
    first = {"date": "2026-01-14", "services": {"a": {"high": 1}}}
    path, written = collect.write_partition(first, tmp_path)
    assert written
    second = {"date": "2026-01-14", "services": {"a": {"high": 9}}}
    assert collect.write_partition(second, tmp_path) == (path, False)
    assert json.loads(path.read_text())["services"]["a"]["high"] == 1
    assert collect.write_partition(second, tmp_path, force=True)[1]
    assert json.loads(path.read_text())["services"]["a"]["high"] == 9


def test_build_rollup_totals_by_day(tmp_path):
    for day, high in (("2026-01-02", 3), ("2026-01-01", 1)):
        (tmp_path / f"{day}.json").write_text(json.dumps({
            "date": day,
            "services": {"x": {"high": high, "medium": 0, "low": 1},
                         "y": {"high": 1, "medium": 2, "low": 0}},
        }), encoding="utf-8")
    rollup = collect.build_rollup(tmp_path)
    assert [d["date"] for d in rollup["days"]] == ["2026-01-01", "2026-01-02"]
    assert rollup["days"][1]["totals"] == {"high": 4, "medium": 2, "low": 1}
    assert rollup["days"][0]["services"] == 2
