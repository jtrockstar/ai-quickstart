# Example Report — Product Requirements Document (PRD)

> Status: **Example.** This PRD is a filled-in sample that shows the shape and depth we expect.
> It describes a small fictional product, *Example Report*, which the `example-report/`
> project implements. Start your own PRD from
> [templates/prd-template.md](templates/prd-template.md).

Last Updated: 2026-10-12

## 1. Problem statement

Service owners can't see how their open work items (defects, alerts, review findings) trend
over time. The Source API reports only today's counts, so every month someone copies numbers
into a spreadsheet by hand. The spreadsheets drift, miss days, and use different day
boundaries, so leadership can't compare services or tell whether a cleanup push worked.

## 2. Users & personas

- **Primary: service owners** (about 20 teams) who need to see their own service's open items
  by severity, and whether the trend is improving.
- **Secondary: engineering leadership**, who need a cross-service view and month-over-month
  movement for planning reviews.
- **Maintainers: the platform team** (a small group) who build and run the collector and
  dashboard. They are the direct users of this repo.

## 3. Primary pain points

1. **No history.** The Source API returns current counts only; past values are lost unless
   someone captures them.
2. **Manual, inconsistent capture.** Copying numbers by hand is slow, misses days, and mixes
   time zones, so the same day can show two different totals.
3. **No shared view.** Each team keeps its own sheet; leadership assembles a summary by hand.

## 4. Domain model & key concepts

### 4.1 Severity model

| Severity | Meaning | Tracked? |
|---|---|---|
| High | Must be fixed within the current sprint | Yes |
| Medium | Planned within the quarter | Yes |
| Low | Fixed opportunistically | Yes |

### 4.2 Days and time zones

A **day** is a calendar day in the reporting time zone (`America/New_York` in this example).
Timestamps are stored in UTC and converted only when a date is derived or shown
([ADR-0002](decisions/0002-store-utc-display-local-time.md)).

### 4.3 Daily partition and rollup

- A **daily partition** is one immutable file holding every service's counts for one day.
- The **rollup** is rebuilt from all partitions on every run and is what the dashboard reads
  ([ADR-0003](decisions/0003-immutable-daily-partitions-and-rollup.md)).

## 5. Goals & objectives

**North star: every service owner can answer "are we getting better?" in under a minute.**

| # | Goal | Notes |
|---|---|---|
| G1 | Capture open-item counts daily, automatically | First epic. No manual steps once deployed. |
| G2 | Publish a trend dashboard | First epic. Per-service and all-services views. |
| G3 | Alert owners when High items rise sharply | Later epic. |
| G4 | Export data for planning reviews | Later epic. CSV download. |

**First epic = G1 + G2.**

## 6. Success metrics

- A partition exists for **every** day after go-live (no gaps longer than one day).
- Service owners stop maintaining their own spreadsheets within one quarter.
- The leadership monthly summary is produced from the dashboard, not by hand.

## 7. Scope & non-goals

- **In scope (first epic):** daily collection, immutable storage, rollup, static dashboard.
- **Later epics:** alerting (G3), export (G4).
- **Non-goals:** editing or resolving items (the Source API's own UI does that); real-time
  updates; backfilling history the Source API never exposed.

## 8. Key capabilities

1. Scheduled daily collection with retry on transient API errors.
2. One immutable file per day; re-running the same day never overwrites history unless
   explicitly forced.
3. A rollup of totals per day, by severity, rebuilt from the partitions.
4. A static dashboard published to the repo's GitHub Pages site.

## 9. Constraints & assumptions

- The Source API offers a service list and per-service open-item counts, authenticated with a
  Bearer token.
- The API applies rate limits; clients must back off on HTTP 429.
- Daily granularity is enough; nobody needs intraday values.
- Data volume is small (about 20 services × 3 severities per day), so JSON files in git are
  fine for several years.

## 10. Open questions

- Should a service that disappears from the Source API keep its history on the dashboard?
  (Current assumption: yes, shown as ended.)

**Resolved:**
- _(2026-10-05)_ Day boundaries use the reporting time zone, not UTC → ADR-0002.
- _(2026-10-06)_ Storage is immutable daily partitions plus a rebuilt rollup → ADR-0003.
