# User Stories ⇄ Jira Sync

**Model:** the user-stories markdown (`documentation/*-user-stories.md`) is the **source of
truth**. Jira is a mirror that is kept in sync *from* the markdown. We do **not** edit stories
in the Jira UI and sync back; changes start in the markdown and are pushed to Jira.

This guide targets a **default (non-customized) Jira Cloud** site, such as the free developer
site you get from Atlassian. It uses only built-in issue types, statuses, and system fields.
Every name below that you might want to change is collected in
[Tunable choices](#tunable-choices) at the end.

## How the connection works

Jira access is via the **Atlassian MCP server** (see
[jira-mcp-architecture-explainer.md](jira-mcp-architecture-explainer.md)), configured in
[`.vscode/mcp.json`](../../.vscode/mcp.json). The AI agent calls the MCP tools
(`jira_search`, `jira_get_issue`, `jira_create_issue`, `jira_update_issue`,
`jira_transition_issue`, `jira_add_comment`, `jira_link_to_epic`) — there is no Jira UI in
VS Code. Bulk and markup-sensitive operations use the paced REST scripts in
[`../scripts/`](../scripts/) instead (see [Utilities](#utilities)).

**Prerequisites**
- `uv` installed (provides `uvx`, which runs the MCP server).
- In the repo-root `.env` (gitignored; copy from `.env.example`):
  - `JIRA_URL` — your site, e.g. `https://example.atlassian.net`
  - `JIRA_USERNAME` — your Atlassian account email
  - `JIRA_API_TOKEN` — an API token from your Atlassian account's security settings
    (Jira Cloud uses email + API token over HTTP Basic, not a personal access token).
- If your network inspects TLS, the scripts use the OS trust store (`truststore`); never
  turn certificate verification off.
- **Confirm access first (spike):** before relying on the push, verify the account can
  actually create, update, transition, and comment in the target project. Do not assume
  permissions. Record the result in [spike-findings.md](../../documentation/spike-findings.md).

## Issue types we use

Only the built-in Jira Software issue types:

| Our kind of work | Jira issue type | Notes |
|---|---|---|
| Epic | `Epic` | Created directly in Jira (see [Creating epics](#creating-epics)). |
| Story | `Story` | Normal deliverable work. |
| Spike | `Task` | Time-boxed research. The summary starts with `Spike:` so spikes are easy to find (`summary ~ "Spike:"`). |
| Bug | `Bug` | Defects. Follow [bug-report-format.md](../../documentation/developer/bug-report-format.md). |
| Sub-task | `Subtask` | Optional; only when a story needs visible internal steps. |

## Story ↔ Jira key convention

Each story block records its Jira key in the heading:

```
## Story 5 (PROJ-123): <title>
```

- **Not yet deployed** → use the placeholder `PROJ-XXXX` in the heading.
- **Deployed** → the heading carries the real key (e.g. `PROJ-123`); this key is how a later
  sync knows to *update* rather than *create*.
- The `{noformat}` block keeps the Jira fields (Title / Type / Epic / Priority / Story Points
  + `h3.` sections) that are pushed to the issue.

## Required fields for new issues

When creating a story, spike, or bug under an epic, set:
- **Issue type:** per [Issue types we use](#issue-types-we-use).
- **Summary:** the `Title:` line.
- **Description:** the `h3.` sections (see [Description format](#description-format)).
- **Parent:** the epic. In Jira Cloud the epic is the issue's **parent** (`{"parent": {"key":
  "PROJ-1"}}`); the MCP `jira_link_to_epic` tool sets it after creation.
- **Priority:** from the block (`Highest` … `Lowest` are all valid in default Jira).
- **Story points:** from the block. The field's name differs by project type ("Story point
  estimate" in team-managed, "Story Points" in company-managed), so never hard-code its id.
  Either set it with [`set_story_points.py`](../scripts/set_story_points.py), which finds the
  field by name on each issue, or look the id up once per session with the MCP
  `jira_search_fields` tool. When a story's points change, **re-send the points** on the
  update so markdown and Jira stay in step.
- **Assignee:** leave **unassigned** by default. Assign only when the user explicitly directs
  it — then use [`set_jira_assignee.py`](../scripts/set_jira_assignee.py), which resolves a
  display name or email to the Jira Cloud `accountId`.

## Jira workflow (statuses & transitions)

A default Jira Cloud software project has three statuses: **`To Do`**, **`In Progress`**, and
**`Done`**. Our working stages are richer than that, so each stage maps onto a default status
plus a **status-change comment** (see [Comment on every status change](#comment-on-every-status-change)),
which keeps the issue self-documenting without customizing the workflow.

| Our stage | Default Jira status | How the stage is signaled |
|---|---|---|
| **New** — being written | `To Do` | In the backlog; no "fully written" comment yet. |
| **Ready for Dev** — fully written | `To Do` | A "fully written / ready for dev" comment; pulled into a sprint when planned. |
| **In Progress** | `In Progress` | Transition + brief comment. |
| **Testing** — formal QA by another person | `In Progress` | A "ready for test" comment naming the tester; assign to the tester only if told to. |
| **Done** | `Done` | Detailed completion comment (below). |
| **Blocked / On Hold** | unchanged | Use Jira's built-in **Add flag** on the issue, plus a comment giving the reason. |

**Spikes** skip Ready for Dev and Testing: `To Do` → `In Progress` → `Done`.

> **If a project admin later adds board columns** (for example `Ready for Dev` or `In Review`),
> use them for the matching stage and keep the comment convention. Update the table above and
> [Tunable choices](#tunable-choices) in the same change.

**Resolution:** default Jira Cloud workflows set **Resolution = Done** automatically when an
issue reaches `Done`. Don't pass a resolution yourself unless the transition screen asks for
one. If an issue re-opened from `Done` still shows a resolution, that's a workflow setting a
project admin can fix; treat it as cosmetic rather than promising to clear it.

**Closing an issue requires explicit user confirmation.** Do not transition an issue to `Done`
on your own — finish the work, give the user a runnable spot check to confirm it, and only
close it once they say so.

### New-story stage by the parent epic's state

New **Stories** take their starting stage from the epic (**Spikes are excluded** — a spike
stays in `To Do` until work starts, then `In Progress`):
- **Epic in `To Do`:** create the story and leave it at **New** — it's promoted when the epic
  starts (below).
- **Epic `In Progress`:** create the story at **New** while it's being written, then mark it
  **Ready for Dev** (comment) once it is **fully written** (description + acceptance criteria).
- **When an epic moves `To Do` → `In Progress`:** mark **all** its fully written stories
  Ready for Dev (skip spikes) so the team can plan them.

### Comment on every status change

Keep issues self-documenting — post a comment on each stage change (via `jira_add_comment`, or
raw wiki through the REST API for underscore / `<>`-heavy content):
- **Fully written:** when description + acceptance criteria are complete. If the epic is
  already `In Progress`, combine this with the Ready for Dev note.
- **Ready for Dev / In Progress:** a brief note on that change.
- **Done:** a **detailed** comment — what was delivered, a **manifest of new / updated /
  removed source files**, how completion was **confirmed** (unit tests + spot checks), and
  anything **deferred** to a later story.
- **Testing:** some issues get formal QA by another person — when told the work is done and
  asked to move it to test, leave it `In Progress`, comment that it's ready for test, and name
  the tester. Do **not** move it to `Done`.
- **Blocked / On Hold:** only when asked — flag the issue and comment the reason.

## Description vs comments (what goes where)

Applies to **any** Jira issue (epic, story, spike, bug).

- The **description states the complete, current scope** — what the issue is and what "done"
  means, kept up to date. If scope changes or is added, **edit the description** (via
  `set_wiki_description.py` for underscore / `<>` / `+`-heavy content) so a reader gets the
  full picture from the description alone.
- **Comments are informational and historical** — status-change notes, decisions/ADRs, review
  findings, "extension captured from a discussion", and confirmations. A comment may
  *announce* a scope change, but the description must be updated to *carry* it.
- Rule of thumb: if a future reader needs it to understand the issue, it belongs in the
  description; if it only records how/when/why something happened, it's a comment.

## Description format

House style for stories and spikes: `h3.` section headers — **Description**, **Acceptance
Criteria**, **Notes** — with `{{code}}` for identifiers and bold only on the persona in the
Description line. Bugs use the sections in
[bug-report-format.md](../../documentation/developer/bug-report-format.md).

**Acceptance criteria live in the description.** We don't use a separate acceptance-criteria
field, so the description alone tells a reader what "done" means.

The MCP server treats the `description` you pass as **Markdown** and converts it. To land the
house style reliably:
- `### Heading` → `h3. Heading`.
- `**bold**` **only in paragraphs**. Do **not** use `**bold**` inside list items — some
  converters leave the literal `**` in bullets. Avoid raw single-asterisk `*x*` too (it can
  become italic).
- Backticks `` `code` `` → `{{code}}` (safe inside bullets).
- Keep bullets plain text + `{{code}}` (no inline bold).

When the content has `_`, `+`, `<...>`, or `{...}`, skip the converter and write wiki markup
directly with [`set_wiki_description.py`](../scripts/set_wiki_description.py) (see below).

## Creating epics

Epics are created directly in Jira; they are **not** stored as files in this repo (the
user-stories doc quotes the epic description for reference). Draft the name + description
first in a gitignored `.scratch/` file, confirm with the requester, then push.

### Epic fields & defaults

| Field | Value / default |
|---|---|
| Issue type | `Epic` |
| Status | `To Do` for a new epic |
| Summary | the epic name |
| Description | wiki markup via `set_wiki_description.py` (below) |
| Assignee | the requester by default |
| Priority | `Medium` unless the requester says otherwise |

### Epic description — the important part

Author the **Summary** and **Description** so both technical and non-technical readers
understand it. Cover, at minimum:
1. **Summary / elevator pitch** — what it is, in context, including where the epic starts and
   ends.
2. **Why it's needed** — the problem it solves, and (if relevant) why now.
3. **Deliverables** — what you'll see, and the value, when it's done.
4. *Optional:* **References**.
5. *Optional:* a **draft story list** as a starting point (assumed incomplete).

Headings/format are flexible — larger or more complex epics warrant more detail, small ones
less.

**Write the epic description via the REST API in Jira wiki markup, not the MCP markdown
converter.** The converter can drop `+`, escape `_`, and rewrite `<...>` → `[...]`, which
corrupts identifiers and path templates like `src/<type>/`. Draft the body in wiki markup
(`h3.` headings, `*bold*` in paragraphs, `{{code}}` for identifiers, `*`/`-` bullets), then
push it with:

```
python jira-toolkit/scripts/set_wiki_description.py PROJ-123 .scratch/desc.wiki.txt
```

REST API v2 still accepts wiki markup on Jira Cloud, which is why the scripts write through
v2 (v3 requires Atlassian Document Format).

Two wiki-markup traps (`{{...}}` does **not** stop the markup inside it from being parsed):
- **`-` pairs become strikethrough**, even across `{{code}}` spans. Examples:
  `{{plan}} -> {{seed}}`, and placeholder names such as `{{results-<env>-<version>}}`. Use `→`
  instead of `->`, and escape the dashes next to placeholders as `\-`. Escape a literal `*` as
  `\*`.
- **Nested braces break `{{...}}`.** For example, `{{if: ${{ !cancelled() }}}}` closes early.
  Put GitHub Actions expressions in a `{code:yaml}` block instead.

To check what Jira actually displays, use
`GET /rest/api/2/issue/<key>?fields=description&expand=renderedFields`. The MCP read-back can
show a *lossy rendering*, so it may look mangled even when the stored wiki is fine.

### Epic planning states

An epic's planning state is its status plus a comment:

| Planning state | Epic status | Signal |
|---|---|---|
| Candidate, not yet planned | `To Do` | — |
| Active work | `In Progress` | Status-change comment saying work has started and whether it is committed for the current planning period. |
| Complete | `Done` | Closed with [`close_epic.py`](../scripts/close_epic.py). |

Moving an epic from `To Do` to `In Progress` also promotes its fully written stories (see
[New-story stage by the parent epic's state](#new-story-stage-by-the-parent-epics-state)).

### Closing an epic

Use `jira-toolkit/scripts/close_epic.py`, which is idempotent, paced, and supports `--dry-run`:

1. **Workflow status** → a status in the Done category (preferring `Done`).
2. **Resolution** → `Done`, sent during the transition only if the screen accepts it (default
   workflows set it themselves).
3. **Agile done flag** → `POST /rest/agile/1.0/epic/<key>` with `{"done": true}`, the same call
   a board's "Mark as done" makes. Team-managed projects don't use this flag; the script
   reports "n/a" there rather than failing.

```
python jira-toolkit/scripts/close_epic.py PROJ-10
python jira-toolkit/scripts/close_epic.py PROJ-10 PROJ-11 --dry-run
python jira-toolkit/scripts/close_epic.py --jql 'project = PROJ AND issuetype = Epic AND statusCategory = Done AND resolution IS EMPTY'
```

## Story sizing (Fibonacci points)

Size stories with this rubric (a person-week ≈ **13 points**). **13** signals "too big —
consider splitting"; **21+** must be split (spike(s) likely required).

| Points | Effort | Operations / process example | Development example |
|--------|--------|------------------------------|---------------------|
| 1 | 1–2 hrs | small wiki or email update; run an existing process | add a config value, rename a field, tweak a log message |
| 2 | 2–4 hrs | run an audit report, update reference data | small change to an existing script or workflow, static UI change |
| 3 | > half day | recurring audit, update needing approval, short presentation | new CLI flag with tests, small bug fix |
| 5 | 1–2 days | bite-sized process improvement, triage with many findings | new module with tests, significant bug fix, small dashboard panel |
| 8 | 2–3 days | new audit with a report | new integration client, larger UI component |
| 13 | 5 days | "something failed" investigation, new process design — too big, split | major feature, complex interactions — too big, split |
| 21+ | too big | multiple stories, spike(s) likely; needs analysis and design docs | multiple stories, spike(s) likely required |

## Utilities

All scripts read `JIRA_URL` / `JIRA_USERNAME` / `JIRA_API_TOKEN` from the repo-root `.env`,
retry on rate limits (honoring `Retry-After`), and pace bulk operations. Shared code lives in
`jira_client.py`; tunables live in `jira_config.py`. Deps: `jira-toolkit/scripts/requirements.txt`.

- **Wiki description setter:** `set_wiki_description.py` PUTs a raw wiki-markup description
  onto an issue, bypassing the MCP markdown converter. Reads the body from a file or stdin:
  `python jira-toolkit/scripts/set_wiki_description.py PROJ-123 .scratch/desc.wiki.txt`.
- **Story points:** `set_story_points.py` sets points, finding the field by name on each issue:
  `python jira-toolkit/scripts/set_story_points.py PROJ-12=3 PROJ-13=5 [--dry-run]`.
- **Bulk assignee:** `set_jira_assignee.py` sets or clears the assignee, resolving a display
  name or email to an `accountId`:
  - `python jira-toolkit/scripts/set_jira_assignee.py --assignee "Pat Example" PROJ-12 PROJ-13`
  - `python jira-toolkit/scripts/set_jira_assignee.py --assignee pat@example.com --keys PROJ-12,PROJ-13`
  - `python jira-toolkit/scripts/set_jira_assignee.py --unassign PROJ-12`
- **Close an epic:** `close_epic.py` — see [Closing an epic](#closing-an-epic).
- **Decision sync:** `post_decisions_to_jira.py` posts each ADR under `documentation/decisions/`
  as a comment on the issue named in the ADR's `- Jira:` line (a story, or the epic when
  cross-cutting). Idempotent — unchanged decisions are skipped, changed ones update the
  existing comment (matched by a hidden marker + content hash). Run all with
  `python jira-toolkit/scripts/post_decisions_to_jira.py` (or `--adr <file>` / `--dry-run`).
  - **`--adr` is repeatable** — pass it once per file to post several specific ADRs in one
    pass; omit it to process every ADR.
  - **Always `--dry-run` first**, and prefer **per-file** posting when you only mean to sync
    the ADRs you just wrote. A no-`--adr` run also **updates any other ADR whose file drifted**
    from its posted comment, which silently touches unrelated issues. The dry-run plan lists
    each `ADR-NNNN -> PROJ-KEY: created/updated/unchanged` so you can confirm targets first.
  - Each ADR must carry a `- Jira: <KEY>` header line; that line is how the script routes the
    comment.
  - **Never renumber an ADR, and avoid retargeting it.** The comment is matched by ADR number
    (`decision-sync id:ADR-NNNN`) on the target issue. Renumbering posts a second comment
    instead of updating the first, and changing the `- Jira:` key posts to the new issue while
    the old comment stays. Renaming the title part of the file name is safe. To change a
    decision, edit the ADR or supersede it with a new number.

Bulk MCP writes in quick succession can hit Jira Cloud rate limits, so prefer these paced
scripts for multi-issue operations.

## Deploying / syncing (agent-driven, today)

Run the `/sync-stories-to-jira` prompt (`jira-toolkit/prompts/sync-stories-to-jira.prompt.md`),
or ask the agent directly. For each story it will:

1. **No key (`PROJ-XXXX`)** → create the issue, set its parent epic and points, then write the
   returned key back into the markdown heading.
2. **Has a key** → update the issue so it matches the markdown (summary, description, points,
   parent epic).
3. Report a summary of created / updated / unchanged stories.

You can scope it to "all stories", a single story, or an epic.

## Future: automated sync (its own epic, via the PRD flow)

A deterministic, testable **Python + GitHub Actions** sync (parse the markdown, map fields,
idempotent create/update against the Jira REST API, key write-back) can be designed and built
through the PRD → TDD → user-stories flow. The agent-driven MCP path above is the interim
mechanism.

## Tunable choices

Change these in one place and update this guide in the same change.

| Choice | Current value | Where it lives |
|---|---|---|
| Project key in examples | `PROJ` | this guide, the user-stories docs |
| Placeholder key for undeployed stories | `PROJ-XXXX` | this guide, the sync prompt |
| Spike representation | issue type `Task`, summary prefix `Spike:` | this guide |
| Stage → status mapping | [Jira workflow](#jira-workflow-statuses--transitions) table | this guide |
| Preferred Done status / resolution name | `Done` / `Done` | `scripts/jira_config.py` |
| Story-point field names (searched in order) | `Story point estimate`, `Story Points` | `scripts/jira_config.py` |
| Retry policy and pacing | 4 attempts, `2^n` s backoff, 0.4 s between issues | `scripts/jira_config.py` |
| Decisions folder | `documentation/decisions/` | `scripts/post_decisions_to_jira.py` |
