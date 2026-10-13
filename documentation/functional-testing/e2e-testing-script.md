# End-to-end testing script

**Story:** PROJ-XXXX — Trend dashboard on GitHub Pages
**Epic:** PROJ-1 — Example Report - Daily Open-Item Trends

> **Example.** A step-by-step script for testers acting together. Each step names who acts and
> what everyone should see. Start from
> [../templates/e2e-testing-script-template.md](../templates/e2e-testing-script-template.md).

---

## Overview

Validates the daily workflow and the dashboard end to end with three participants.

**Estimated duration:** 45–60 minutes

---

## Personas

| ID | Role | Access | Description |
|---|---|---|---|
| **Maint** | Maintainer | Write access to the repo; can dispatch workflows | Runs the workflow and checks commits. |
| **Owner** | Service owner | Read access to the dashboard | Checks their service's view. |
| **Lead** | Engineering leadership | Read access to the dashboard | Checks the all-services view. |

---

## Prerequisites

- [ ] The daily workflow is merged to `main` (workflows only run from the default branch).
- [ ] The `SOURCE_API_TOKEN` repository secret is set.
- [ ] GitHub Pages is enabled for the repo.
- [ ] Everyone has the dashboard open in a browser tab.

---

## How to use this script

1. **Read your column.** Each step names the actor and who verifies.
2. **Wait for workflows.** After a dispatch, wait for the run to finish (about 2 minutes).
3. **Record results** in the Pass/Fail column as you go.
4. **If a step fails,** note it and continue unless the facilitator says otherwise.

---

## Part A: Daily run

### Test A1 — Dispatch publishes a new day

**Goal:** a dispatched run commits today's data and updates the dashboard.

| Step | Actor | Action | Expected Result | Pass/Fail |
|---|---|---|---|---|
| A1.1 | **Maint** | Dispatch the daily workflow from `main`. | The run starts; jobs `collect` and `deploy` appear. | |
| A1.2 | **Maint** | Open the run when it finishes. | Both jobs are green. The `collect` log shows `wrote …/<today>.json`. | |
| A1.3 | **Maint** | Open the latest commit on `main`. | It adds `data/daily/<today>.json` and changes `data/rollup.json`. | |
| A1.4 | **All** | Refresh the dashboard. | Today's date appears as the last point. | |

### Test A2 — Re-run keeps history

**Goal:** a second run the same day changes nothing.

| Step | Actor | Action | Expected Result | Pass/Fail |
|---|---|---|---|---|
| A2.1 | **Maint** | Dispatch the workflow again. | The `collect` log shows `kept existing …/<today>.json`. | |
| A2.2 | **Maint** | Check commits on `main`. | No new data commit. | |

---

## Part B: Dashboard views

### Test B1 — Service filter

| Step | Actor | Action | Expected Result | Pass/Fail |
|---|---|---|---|---|
| B1.1 | **Owner** | Choose your service in the filter. | The chart shows only your service; the page address includes the service key. | |
| B1.2 | **Owner** | Reload the page. | The filter is still set to your service. | |
| B1.3 | **Lead** | Leave the filter on *All services*. | Totals equal the sum of the per-service values for the latest day. | |

---

## Results summary

| Test | Result | Notes |
|---|---|---|
| A1 | | |
| A2 | | |
| B1 | | |
