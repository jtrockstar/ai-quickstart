"""Date helpers: store UTC, bucket and display in the reporting time zone (ADR-0002).

All date derivation goes through these functions — never slice a UTC ISO string to get a
date, or late-evening local activity lands on the next day.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

import example_report_config as config

_ZONE = ZoneInfo(config.REPORT_TIMEZONE)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def to_utc_iso(moment: datetime) -> str:
    """Serialize an aware datetime as a UTC ISO-8601 string (``...Z``)."""
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def local_date(moment: datetime | str) -> date:
    """The reporting-zone calendar date for an aware datetime or a UTC ISO string."""
    if isinstance(moment, str):
        moment = datetime.fromisoformat(moment.replace("Z", "+00:00"))
    return moment.astimezone(_ZONE).date()
