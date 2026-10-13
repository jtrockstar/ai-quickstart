# Jira Stories – Example Report (Epic 1)

**Epic:** PROJ-1 – Example Report - Daily Open-Item Trends

> **Example.** Filled-in sample of a user-stories doc: an epic description, spikes, stories,
> and bugs, each as a Jira-ready block. Keys like `PROJ-2` are illustrative; `PROJ-XXXX` marks
> a block not yet created in Jira. Start your own from
> [templates/user-stories-template.md](templates/user-stories-template.md).

Jira-ready stories for the first epic (PRD goals **G1 + G2**): collect open-item counts daily,
store them as immutable partitions, and publish a trend dashboard. See the
[PRD](example-report-product-requirements.md) and
[TDD](example-report-technical-design.md); decisions are logged in [decisions/](decisions/).
Sync conventions (issue types, stages, fields) are in
[jira-sync.md](../jira-toolkit/documentation/jira-sync.md).

Stories are ordered to retire risky unknowns first (spikes), then build the foundation, the
core collector, and the dashboard. **Every story updates the relevant docs as part of its
Definition of Done.**

## Epic description (as in Jira – PROJ-1)

{noformat}
h3. Summary

Capture every service's open-item counts once a day, keep the history, and publish a trend dashboard so service owners and leadership can see whether things are getting better. Starts with the first automated capture; ends when the dashboard is live and owners have stopped keeping their own spreadsheets.

h3. Why

The Source API reports only today's counts. History is kept by hand in spreadsheets that drift, miss days, and disagree about day boundaries, so nobody can compare services or measure a cleanup push.

h3. What it delivers

* A daily, automated collection of open-item counts by severity for every service.
* Immutable daily history files plus a rebuilt rollup.
* A static trend dashboard with per-service and all-services views.

h3. Reference

Design: the example-report PRD, TDD, and ADRs 0001-0003.
{noformat}

---

## Story 1 (PROJ-2): Spike - confirm Source API access and rate limits

{noformat}
Title: Spike: confirm Source API access, payload shape, and rate limits
Type: Task
Epic: Example Report - Daily Open-Item Trends (PROJ-1)
Priority: High
Story Points: 3

h3. Description

As a *platform engineer*, I need to prove we can read the service list and per-service counts from the Source API with a service token, so that the collector design rests on facts rather than assumptions.

h3. Acceptance Criteria

* A token-authenticated call lists services and returns counts for at least two services.
* The payload shape (field names, missing severities) is recorded in spike-findings.md.
* Rate-limit behavior is observed and recorded (status code, {{Retry-After}} header).
* Any network requirement for local runs (proxy, trust store, User-Agent) is recorded.

h3. Notes

* Feeds Stories 3 and 5.
{noformat}

---

## Story 2 (PROJ-3): Spike - confirm Jira create/update permissions

{noformat}
Title: Spike: confirm Jira create, update, transition, and comment permissions
Type: Task
Epic: Example Report - Daily Open-Item Trends (PROJ-1)
Priority: High
Story Points: 2

h3. Description

As a *platform engineer*, I need to confirm my account can create, update, transition, and comment on issues in PROJ through the MCP server and the jira-toolkit scripts, so that story sync and decision posting are viable.

h3. Acceptance Criteria

* Through the MCP server, create a test story under the epic, update it, and add a comment.
* {{set_wiki_description.py}} and {{set_story_points.py}} succeed on that story.
* {{post_decisions_to_jira.py --dry-run}} lists the expected targets.
* Gaps and workarounds are recorded in spike-findings.md; the test story is deleted afterwards.
{noformat}

---

## Story 3 (PROJ-4): Project scaffolding and shared foundations

{noformat}
Title: Scaffold example-report (config module, REST helper, date helper)
Type: Story
Epic: Example Report - Daily Open-Item Trends (PROJ-1)
Priority: High
Story Points: 5

h3. Description

As a *developer of this project*, I need {{example-report/}} scaffolded with our shared conventions, so that every later story builds on a consistent base.

h3. Acceptance Criteria

* {{example-report/}} has {{scripts/}} and {{tests/}} per repo conventions; every {{.py}} file starts with a docstring header.
* {{example_report_config.py}} holds all tunables (API paths, severities, data paths, retry, time zone).
* {{example_report_rest.py}} routes all Source API calls with retry/backoff and a per-process cache, and decodes as {{utf-8-sig}}.
* {{example_report_dates.py}} derives every date in the reporting time zone (ADR-0002).
* Unit tests mock all network I/O; {{python -m pytest example-report/tests -q}} passes.
* The TDD §5 table and diagrams are updated.
{noformat}

---

## Story 4 (PROJ-5): Documentation scaffold (living docs, created early)

{noformat}
Title: Create the living documentation set for Example Report
Type: Story
Epic: Example Report - Daily Open-Item Trends (PROJ-1)
Priority: High
Story Points: 3

h3. Description

As a *service owner and future maintainer*, I need the end-user guides and the functional testing plan created up front, so that each later story updates living docs instead of leaving documentation to the end.

h3. Acceptance Criteria

* End-user guides exist in {{documentation/confluence/}}: overview and reading the dashboard.
* An end-to-end test plan and script skeleton exist in {{documentation/functional-testing/}}.
* Every later story's Definition of Done includes updating these docs.
{noformat}

---

## Story 5 (PROJ-6): Daily collector with immutable partitions and rollup

{noformat}
Title: Collect daily open-item counts into immutable partitions and rebuild the rollup
Type: Story
Epic: Example Report - Daily Open-Item Trends (PROJ-1)
Priority: High
Story Points: 8

h3. Description

As a *service owner*, I need my service's open-item counts captured every day without anyone copying numbers, so that a reliable history exists.

h3. Acceptance Criteria

* One run writes {{data/daily/YYYY-MM-DD.json}} named for the reporting-zone date and never overwrites an existing day unless {{--force}} is passed.
* Missing severities are stored as zero.
* {{data/rollup.json}} is rebuilt from all partitions on every run; {{--rollup-only}} skips collection.
* The developer guide and TDD §5.4 are updated; the e2e plan gains a collector scenario.

h3. Notes

* Storage model per ADR-0003.
{noformat}

---

## Story 6 (PROJ-XXXX): Trend dashboard on GitHub Pages

{noformat}
Title: Publish a static trend dashboard from the rollup
Type: Story
Epic: Example Report - Daily Open-Item Trends (PROJ-1)
Priority: Medium
Story Points: 8

h3. Description

As *engineering leadership*, I need a dashboard showing totals by severity per day, with a per-service filter, so that I can see movement without asking each team.

h3. Acceptance Criteria

* The page loads {{rollup.json}} and charts High / Medium / Low per day.
* A service filter narrows the chart to one service.
* The charting library is vendored (no runtime CDN).
* A scheduled workflow with least-privilege permissions collects, commits, and deploys.
* End-user guide "Reading the dashboard" matches the shipped page.
{noformat}

---

## Bug (PROJ-9): Re-running the collector on the same day changes the stored history

{noformat}
Title: Re-running the collector on the same day overwrites that day's partition
Type: Bug
Epic: Example Report - Daily Open-Item Trends (PROJ-1)
Priority: High
Story Points: 2

h3. Summary

A second run on the same day replaces the morning's counts with the afternoon's, so history depends on when someone last ran the tool.

h3. Environment

* Version: example-report at commit {{abc1234}}
* Where: local run on Windows, Python 3.11

h3. Steps to Reproduce

# Run {{example_report_collect.py}}.
# Wait until a count changes in the Source API.
# Run {{example_report_collect.py}} again the same day.

h3. Expected

The second run prints {{kept existing}} and today's partition is unchanged.

h3. Actual

The second run prints {{wrote}} and the partition holds the new counts.

h3. Evidence

{code}
wrote example-report\data\daily\2026-10-08.json
wrote example-report\data\daily\2026-10-08.json
{code}

h3. Notes

* Fixed by checking for an existing file before writing, with {{--force}} as the explicit override (ADR-0003).
{noformat}

---

## Bug (PROJ-XXXX): Late-evening runs are filed under the next day

{noformat}
Title: Runs after 8 p.m. Eastern are saved under the next day's date
Type: Bug
Epic: Example Report - Daily Open-Item Trends (PROJ-1)
Priority: Medium
Story Points: 1

h3. Summary

A run at 21:30 Eastern on October 14 writes {{2026-10-15.json}}, because the date is taken from the UTC timestamp.

h3. Environment

* Version: example-report at commit {{def5678}}
* Where: scheduled workflow

h3. Steps to Reproduce

# Dispatch the daily workflow after 20:00 Eastern (00:00 UTC).
# Look at the new file under {{data/daily/}}.

h3. Expected

The file is named for the Eastern date ({{2026-10-14.json}}).

h3. Actual

The file is named for the UTC date ({{2026-10-15.json}}).

h3. Notes

* Route the date through {{example_report_dates.local_date}} (ADR-0002); add a unit test at the boundary.
{noformat}
