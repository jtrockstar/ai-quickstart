"""Shared constants and tunables for the jira-toolkit scripts.

Change Jira-specific choices here, in one place: connection defaults, retry policy,
pacing, workflow names, and the candidate names used to find fields that differ
between Jira project types (for example the story-points field).
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = REPO_ROOT / ".env"

# --- Connection (Jira Cloud: email + API token over HTTP Basic) ----------------------
ENV_URL = "JIRA_URL"            # e.g. https://example.atlassian.net
ENV_USERNAME = "JIRA_USERNAME"  # the Atlassian account email
ENV_API_TOKEN = "JIRA_API_TOKEN"
USER_AGENT = "Mozilla/5.0 (jira-toolkit)"
TIMEOUT_SECONDS = 60

# --- Retry / pacing -----------------------------------------------------------------
RETRY_STATUSES = (429, 500, 502, 503, 504)
MAX_ATTEMPTS = 4
BACKOFF_BASE = 2        # seconds; attempt n waits BACKOFF_BASE ** n unless Retry-After is sent
PACE_SECONDS = 0.4      # pause between issues in bulk scripts

# --- Workflow -----------------------------------------------------------------------
DONE_STATUS_NAME = "Done"   # preferred target when several transitions reach the Done category
RESOLUTION_DONE = "Done"    # sent during the Done transition when the screen allows it

# --- Field discovery ----------------------------------------------------------------
# Story points are a Jira Software field whose name depends on the project type:
# team-managed projects use "Story point estimate", company-managed use "Story Points".
# Scripts look these up by name on each issue, so no field id is hard-coded.
STORY_POINT_FIELD_NAMES = ("Story point estimate", "Story Points")

# --- Search -------------------------------------------------------------------------
SEARCH_PAGE_SIZE = 100
