# Jira Stories – <Product> (Epic N)

**Epic:** PROJ-XXXX – <Epic name>

Jira-ready blocks for this epic (PRD goals **G?**). See the PRD, the TDD, and
[decisions/](../decisions/). Sync conventions (issue types, stages, fields, sizing) are in
`jira-toolkit/documentation/jira-sync.md`. `PROJ-XXXX` marks a block not yet created in Jira;
the sync writes the real key back into the heading.

Order: spikes that retire risky unknowns first, then foundations, then features. **Every story
updates the relevant docs as part of its Definition of Done.**

## Epic description (as in Jira – PROJ-XXXX)

{noformat}
h3. Summary

_Elevator pitch: what it is, where it starts and ends._

h3. Why

_The problem it solves, and why now._

h3. What it delivers

* _Deliverable and its value._

h3. Reference

_PRD / TDD / ADRs._
{noformat}

---

## Story 1 (PROJ-XXXX): Spike - <question to answer>

{noformat}
Title: Spike: <question to answer>
Type: Task
Epic: <Epic name> (PROJ-XXXX)
Priority: High
Story Points: 3

h3. Description

As a *<persona>*, I need to prove <unknown>, so that <decision it unblocks>.

h3. Acceptance Criteria

* <Observable result recorded in spike-findings.md>

h3. Notes

* Feeds Stories <n>.
{noformat}

---

## Story 2 (PROJ-XXXX): <title>

{noformat}
Title: <title>
Type: Story
Epic: <Epic name> (PROJ-XXXX)
Priority: Medium
Story Points: 5

h3. Description

As a *<persona>*, I need <capability>, so that <outcome>.

h3. Acceptance Criteria

* <Testable criterion>
* The TDD, end-user guides, and e2e plan are updated as relevant.

h3. Notes

* <Constraints, related ADRs, dependencies>
{noformat}

---

## Bug (PROJ-XXXX): <what is wrong> <when / where>

{noformat}
Title: <what is wrong> <when / where>
Type: Bug
Epic: <Epic name> (PROJ-XXXX)
Priority: Medium
Story Points: 2

h3. Summary

<What's wrong and why it matters.>

h3. Environment

* Version: <version or commit>
* Where: <local / workflow / OS / runtime>

h3. Steps to Reproduce

# <step>

h3. Expected

<What should happen, citing the doc or story.>

h3. Actual

<What happened.>

h3. Evidence

{code}
<exact log lines or code>
{code}

h3. Notes

* <Suspected cause, workaround, related issues>
{noformat}
