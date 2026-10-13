# Documentation

One documentation set for the whole repo. Each doc type below has a filled example (for the
fictional *Example Report* product) and a blank template in [templates/](templates/).

## Reading order for a newcomer

1. [developer-setup.md](developer-setup.md) — get a working machine and workspace.
2. The **PRD**, then the **TDD** — together they describe the current and planned state.
3. The **user stories** — what's being built now, mirrored in Jira.
4. [decisions/](decisions/) — how we got here, when you need the history.

## Documentation flow

Write in this order: **PRD** (interactive) → **TDD** → **epic(s) of user stories**. Scaffold the
end-user guides and the functional test plan **early**, as living docs; every story's
Definition of Done includes updating them.

## Doc types

| Type | Purpose | Audience | Lives in | Example | Template |
|---|---|---|---|---|---|
| **PRD** | Why and what: problem, personas, goals, scope, constraints. | Everyone | `<product>-product-requirements.md` | [example](example-report-product-requirements.md) | [template](templates/prd-template.md) |
| **TDD** | How: architecture, data model, a diagram per module, orchestration. Primary current-state reference. | Developers, architects | `<product>-technical-design.md` | [example](example-report-technical-design.md) | [template](templates/tdd-template.md) |
| **User stories** | Jira-ready epic description, spikes, stories, and bugs. Source of truth for Jira. | Team, Jira | `<product>-user-stories.md` (one per epic or phase) | [example](example-report-user-stories.md) | [template](templates/user-stories-template.md) |
| **ADR** | One decision: context, decision, consequences. Running history, synced to Jira as a comment. | Future maintainers | `decisions/NNNN-title.md` | [0001](decisions/0001-record-architecture-decisions.md), [0002](decisions/0002-store-utc-display-local-time.md), [0003](decisions/0003-immutable-daily-partitions-and-rollup.md) | [template](templates/adr-template.md) |
| **Spike findings** | Results of de-risking spikes and their design impact. | Team | `spike-findings.md` | [example](spike-findings.md) | [template](templates/spike-findings-template.md) |
| **Developer guide** | Deeper how-to for a component: interfaces, knobs, commands, spot checks. Linked from the TDD §5.x. | Developers | `developer/` | [collector](developer/source-api-collector.md), [bug format](developer/bug-report-format.md) | [template](templates/developer-guide-template.md) |
| **Developer setup** | New machine and workspace setup. | Developers | `developer-setup.md` | [guide](developer-setup.md) | — |
| **End-user guide** | How to use the product. Published to the team wiki. | Users | `confluence/` | [overview](confluence/overview.md), [dashboard](confluence/reading-the-dashboard.md) | [template](templates/end-user-guide-template.md) |
| **E2E test plan** | Living list of manual end-to-end scenarios. | Testers, team | `functional-testing/e2e-testing-plan.md` | [example](functional-testing/e2e-testing-plan.md) | [template](templates/e2e-testing-plan-template.md) |
| **E2E test script** | Step-by-step, multi-person test session with pass/fail columns. | Testers | `functional-testing/` | [example](functional-testing/e2e-testing-script.md) | [template](templates/e2e-testing-script-template.md) |
| **Release notes** | What changed and what to do, for readers outside the repo. | Business readers, practitioners | `release-notes/` | [example](release-notes/example-report-1.1-release-notes.md) | [template](templates/release-notes-template.md) |
| **Background** | Point-in-time context: brainstorms, parking lots, research. Not agreed scope. | Team | `background/` | [brainstorm](background/product-scope-brainstorming.md), [parking lot](background/parking-lot.md) | [template](templates/background-template.md) |

Jira conventions (issue types, workflow stages, sizing, epics) live with the toolkit:
[../jira-toolkit/documentation/jira-sync.md](../jira-toolkit/documentation/jira-sync.md).

## Conventions that apply to every doc

- **"Last Updated"** line on the PRD, TDD, guides, and setup doc; update it with every change.
- **Processes get a flowchart, then a walkthrough table** (`Step | At this node | Type | What
  happens | Then… | leading to`), with node IDs shown in both. Class diagrams get prose only.
- **Tunable choices and naming formulas are written down** where a maintainer will find them.
- **One source of truth per fact** — link, don't duplicate.
- **Release notes move with the product:** when a shipped item changes, update its entry in the
  current release notes in the same change.
- **Mermaid:** no `;` in `sequenceDiagram` messages; quote labels containing `()`, `<br/>`,
  or `·`.

## Naming

| Thing | Formula | Example |
|---|---|---|
| PRD / TDD / stories | `<product>-product-requirements.md`, `<product>-technical-design.md`, `<product>-user-stories[-phaseN].md` | `example-report-technical-design.md` |
| ADR | `decisions/<4-digit number>-<kebab-title>.md` | `0002-store-utc-display-local-time.md` |
| Release notes | `release-notes/<product>-<version>-release-notes.md` | `example-report-1.1-release-notes.md` |

Templates live in `templates/`, not `decisions/`, because the ADR sync script posts every
`decisions/[0-9]*.md` file.
