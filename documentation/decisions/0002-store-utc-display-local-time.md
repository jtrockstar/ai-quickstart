# 2. Store UTC, derive dates in the reporting time zone

- Status: Accepted
- Date: 2026-10-05
- Jira: PROJ-4

## Context

Collection timestamps are stored in UTC (portable, unambiguous). But the team works on
Eastern time, and every *date* the report shows — partition names, chart axes, "today",
month boundaries — must match how people think about days. A UTC day boundary files
late-evening Eastern activity under the next calendar day and shifts month edges.

## Decision

**Store UTC; bucket and display every derived date in the reporting time zone**
(`America/New_York`, set once as `REPORT_TIMEZONE` in the project config module).
- Stored timestamps stay UTC ISO-8601 (`...Z`).
- All date derivation goes through one helper (`example_report_dates.local_date`, using
  `zoneinfo`) and, in the dashboard, one JS helper using `Intl.DateTimeFormat` with the same
  IANA zone id — never a raw UTC `slice(0, 10)`.

## Consequences

- Dates match the team's lived calendar; daylight saving is handled by the zone database.
- Date logic must always go through the helper (slicing an ISO string is a bug).
- Python and JS must use the same zone id; changing zones is a one-line config change plus
  this ADR being superseded.
