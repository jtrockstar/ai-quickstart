# Example Report 1.1: release notes

_Last updated: 2026-10-12._

> **Example.** Release notes are written for readers who don't have access to the repo: no
> file paths, repo links, or internal review status. Start from
> [../templates/release-notes-template.md](../templates/release-notes-template.md).

This document describes what changes in **Example Report 1.1** and what it means for you.

- **If you lead a team or plan work**, read [At a glance](#at-a-glance).
- **If you own a service**, read [Change by change](#change-by-change) for exactly what you'll
  see and anything you need to do.

## At a glance

- **History no longer shifts.** Running the report twice on the same day used to replace the
  morning's numbers. Each day's numbers are now fixed once captured.
- **Late-evening captures land on the right day.** Captures after 8 p.m. Eastern used to appear
  under the next day. They now appear under the day they were taken.
- **New service filter.** The dashboard can now show a single service.

## Change by change

### Fixed: same-day re-runs changed history

| | |
|---|---|
| **What changed** | The first capture of each day is kept; later runs that day leave it alone. |
| **What you'll see** | Day-to-day lines stop jumping when someone re-runs the report. |
| **What to do** | Nothing. |

### Fixed: late-evening captures filed under the next day

| | |
|---|---|
| **What changed** | Dates now follow the Eastern calendar, including daylight saving changes. |
| **What you'll see** | Points near midnight move to the correct day. Monthly totals near month-end may shift by one day's values. |
| **What to do** | If you exported monthly totals before this release, re-export them. |

### New: service filter

| | |
|---|---|
| **What changed** | A filter above the chart narrows it to one service. |
| **What you'll see** | The filter defaults to *All services*; your choice is kept in the page address so you can bookmark it. |
| **What to do** | Bookmark your service's view. |
