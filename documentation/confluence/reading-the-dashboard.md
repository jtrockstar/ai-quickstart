# Reading the dashboard

> **End-user guide (example).** Updated by every story that changes what users see.

## The chart

- The horizontal axis is the date (Eastern calendar).
- There is one line per severity: **High**, **Medium**, **Low**.
- Each point is the number of open items at that day's capture.

## The service filter _(planned — Story PROJ-XXXX)_

Choose a service above the chart to see only that service. *All services* adds every service
together. Your choice is kept in the page address, so you can bookmark it.

## What the numbers mean

| You see | It means |
|---|---|
| A line going down | Items are being closed faster than they're opened. |
| A one-day spike | Usually a batch of new findings; check the next few days before reacting. |
| A gap | No capture that day (the job didn't run). The next day's point is still correct. |

## Common questions

**Why doesn't today's number match what I see in the Source API right now?** The dashboard
shows the morning capture. Counts change during the day.

**Can I see older history than the start date?** No. The Source API never kept history, so the
dashboard starts on the first day it collected.

**A service is missing.** New services appear the day after they're added to the Source API.
If one is still missing after two days, ask the platform team.
