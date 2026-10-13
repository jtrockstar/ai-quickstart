"""Shared constants and tunables for the example-report project.

Everything a maintainer might change lives here: the Source API settings, the severity
levels we count, where data is written, the retry policy, and the reporting time zone.
Other modules import this as ``config``.
"""
from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parent
ENV_FILE = REPO_ROOT / ".env"

# --- Source API ---------------------------------------------------------------------
ENV_SOURCE_URL = "SOURCE_API_URL"      # e.g. https://api.example.com
ENV_SOURCE_TOKEN = "SOURCE_API_TOKEN"  # sent as a Bearer token
SERVICES_PATH = "api/v1/services"
OPEN_ITEMS_PATH = "api/v1/services/{key}/open-items"
USER_AGENT = "Mozilla/5.0 (example-report)"
TIMEOUT_SECONDS = 60

# --- Retry --------------------------------------------------------------------------
RETRY_STATUSES = (429, 500, 502, 503, 504)
MAX_ATTEMPTS = 4
BACKOFF_BASE = 2

# --- Data model ---------------------------------------------------------------------
SEVERITIES = ("high", "medium", "low")
DATA_DIR = PROJECT_ROOT / "data"
DAILY_DIR = DATA_DIR / "daily"          # one immutable file per day: <YYYY-MM-DD>.json
ROLLUP_FILE = DATA_DIR / "rollup.json"  # rebuilt from the daily files on every run

# --- Time ---------------------------------------------------------------------------
# Timestamps are stored in UTC; every date shown or bucketed uses this zone (ADR-0002).
REPORT_TIMEZONE = "America/New_York"
