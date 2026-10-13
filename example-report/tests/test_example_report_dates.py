"""Tests for example-report/scripts/example_report_dates.py."""
from datetime import date, datetime, timezone

import example_report_dates as dates


def test_late_evening_utc_belongs_to_previous_local_day():
    # 02:30 UTC on Jan 15 is 21:30 on Jan 14 in New York (EST, UTC-5).
    assert dates.local_date("2026-01-15T02:30:00Z") == date(2026, 1, 14)


def test_daylight_saving_offset_is_applied():
    # 03:30 UTC on Jul 15 is 23:30 on Jul 14 in New York (EDT, UTC-4).
    assert dates.local_date(datetime(2026, 7, 15, 3, 30, tzinfo=timezone.utc)) == date(2026, 7, 14)


def test_to_utc_iso_normalizes_offset():
    moment = datetime.fromisoformat("2026-03-01T09:00:00-05:00")
    assert dates.to_utc_iso(moment) == "2026-03-01T14:00:00Z"
