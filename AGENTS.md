# Agent Instructions

**Purpose:** a template repo that carries our working agreements, documentation set, Jira
toolkit, and engineering conventions. Copy it to start a new repo, then replace the
`example-report` project and the example docs with your own.

> **This file is the single source of agent instructions.** Codex and other `AGENTS.md`-aware
> tools read it directly, Claude Code imports it from [CLAUDE.md](CLAUDE.md), and GitHub
> Copilot reads it (VS Code `chat.useAgentsMdFile`) with
> [.github/copilot-instructions.md](.github/copilot-instructions.md) as a pointer. Edit this
> file, not the pointers.
>
> **Copilot code review** can't follow a pointer or import, and reads only about the first
> 4,000 characters of each instruction file. So `.github/instructions/*.instructions.md` hold
> short, self-contained review checklists (Python, GitHub Actions, documentation), each scoped
> with `applyTo`. **When a rule here changes, update the matching checklist in the same
> change**, and keep each checklist under 4,000 characters.

## Start here (grounding for a new chat)

Read these first so you build on prior agreements, design, and conventions:
- **New machine / workspace setup (tools, workspace file, venv, `.env`, extensions, Jira MCP, chat history):** [documentation/developer-setup.md](documentation/developer-setup.md)
- **Documentation map (every doc type, when to write it, and its template):** [documentation/README.md](documentation/README.md)
- **PRD (why + scope):** [documentation/example-report-product-requirements.md](documentation/example-report-product-requirements.md)
- **TDD (architecture + per-module diagrams; current + planned state):** [documentation/example-report-technical-design.md](documentation/example-report-technical-design.md)
- **User stories (epics, spikes, stories, bugs):** [documentation/example-report-user-stories.md](documentation/example-report-user-stories.md)
- **Decisions (ADRs):** [documentation/decisions/](documentation/decisions/)
- **Everything Jira (issue types, workflow stages, sync, sizing, comments, creating & closing epics):** [jira-toolkit/documentation/jira-sync.md](jira-toolkit/documentation/jira-sync.md); scripts + setup in [jira-toolkit/](jira-toolkit/README.md)

## Working agreement (how we collaborate)

- Move deliberately; get the requirements right before building. Don't rush to code.
- Persist shared understanding as markdown in-repo **as we go**, so this and future agent
  chats stay grounded in prior agreements, decisions, and reasoning.
- The **why lives in the PRD/TDD** (primary, current-state reading — more often the TDD). A
  reader should understand the current and planned state from PRD + TDD alone. A separate
  **ADR log** (`documentation/decisions/NNNN-*.md`) records the running history of
  decisions/changes for tracking, not day-to-day understanding.
- **Open questions are short-lived todos**, not a saved Q&A transcript: once answered, codify
  the answer into the PRD/TDD, an ADR, the Jira issue, or a code comment, and drop the question.
- Prior agreements are **amendable guardrails**, not immutable: change them intentionally, add
  an ADR, and update the PRD/TDD in the same change.
- **Ask when intent is unclear.** A question is often just a question — do not infer a change
  is needed unless it clearly is. Ask **one or a few questions at a time** when topics are
  dependent (later answers may change earlier ones).
- **Version control is the user's to drive.** Work only in the **current local branch** and
  just update the working copy — do **not** create branches, commit, push, or open PRs on
  your own initiative. Only do so when the user **explicitly asks**. **Prompt the user** when
  a change must be merged to `main` before it can be functionally tested — e.g. GitHub Actions
  workflow changes, which only take effect once on the default branch.
- **Never transition a Jira issue to `Done` without explicit user confirmation.** Finish the
  work, provide a runnable spot check, then ask — only close when the user says so.
- **Anti-freeze guard: act before you announce.** A turn that ends with "it's running in the
  background" and **no tool call** looks exactly like a freeze. Rules:
  1. Never say work is running, started, or about to start unless the tool call for it has
     **already been made in this turn**. Make the call first, then describe it.
  2. Every turn must end with one of three things: a **finished result**, a **question**, or
     an explicit **background wait** naming the terminal ID and the log path the run writes
     to. Never end on a promise ("I'll now…", "Starting…", "Running…").
  3. Self-check before ending a turn: if the last message has future-tense action wording and
     no matching tool call above it, **make the call instead of sending the message**.
  4. Long runs (big pytest/REST jobs): start them in `sync` mode redirected to a log (see
     Local shell), with `$env:PYTHONUNBUFFERED='1'` set first. Without it, Python buffers
     stdout, so the log stays **empty** until the run exits and looks like a hang. If the run
     times out to the background, say so with the terminal ID and log path, then read the log
     when notified. If later commands queue behind a still-running one, don't pile on more
     checks — tell the user it's still running, give the log path, and ask them to say when
     the prompt returns.
  5. **If the user reports another freeze, this approach isn't working.** Change it (e.g. one
     tool call per turn, or give the user the exact command to run) and update this rule.
  6. **Never search large generated trees** (e.g. `data/`, `reports/`, `results/`, `.venv/`)
     with a recursive glob; it can run until it times out. Scope searches to one folder, or
     list the folder and read files directly.
- Proactively offer better conventions/approaches and **cite a source** when you can. No
  sycophancy — push back with reasoning.
- Audience is an **architect**: give tradeoffs/pros-cons and show reasoning on non-trivial
  design/architecture decisions; don't over-simplify.
- Keep the TDD, user stories, and end-user docs **in sync with code changes automatically** as
  we go, so code and paperwork can be reviewed together.
- The **TDD's components section must carry a class and/or flow diagram (Mermaid) for each
  script/module**, kept in sync as code changes. Every story that adds/changes a module
  updates its diagram.
- **Document every process in two parts — a flowchart, then a combined walkthrough table** —
  so a reader who cannot see the diagram still gets the full picture. Section format: heading,
  a brief high-level description, the flowchart, then the table.
  - **Flowchart (`flowchart TD`).** Give every node a stable short ID (A, B, C…) shown as a
    prefix on the label (e.g. `E. Eligible?`) so boxes and table rows match. Consistent shapes
    by type — Start/End (stadium), Process (rectangle), Decision (diamond). Every arrow leaving
    a decision carries an explicit branch label (e.g. Yes/No).
  - **Walkthrough table** with columns `Step | At this node | Type | What happens | Then… |
    leading to`, ordered to follow the natural flow. One row should read like a spoken
    sentence; the whole table should narrate the flowchart in order. Give each decision node
    two rows (one per branch) using `if **No**` / `but if **Yes**`. Name the next node in
    `leading to`. List a convergence node **once**. No per-arrow audit table.
  - **Structural (class) diagrams** are not processes: describe the types and relationships
    briefly in prose — no walkthrough table.
- **Write documentation in clear, human-readable language, but never label the style** (no
  "plain English" or similar meta-labels) — just write that way.
- **Document naming conventions and other tunable choices explicitly** (branch names, project
  keys, tags, run IDs, file names) so a future maintainer can find and change them in one
  place. When a name is derived, state the exact formula.
- **The TDD is the architectural view; deeper how-to references live as standalone guides in
  `documentation/developer/`.** Every such guide MUST be pointed to from the TDD with a
  **"Detailed guide" pointer at the end of the relevant `§5.x` section**. Keep one source of
  truth per fact — link, don't duplicate.
- Concise by default; elaborate only when necessary.

## Documentation flow (do in order)

1. **PRD** (interactive) → 2. **Technical Design** → 3. **Epic(s) of user stories**

- Keep a "Last Updated" line in the PRD/TDD and update docs whenever behavior changes.
- **One documentation set for the whole repo**, under `documentation/` (map:
  [documentation/README.md](documentation/README.md)). Blank starting points for every doc
  type live in `documentation/templates/`.
- End-user docs (`documentation/confluence/`) and the end-to-end functional testing plan
  (`documentation/functional-testing/`) are **living docs created early**, not trailing
  deliverables: scaffold them up front and make "update the relevant docs" part of **every
  story's Definition of Done**.
- Decisions are recorded as **ADRs** in `documentation/decisions/` (numbered `NNNN-title.md`;
  Context / Decision / Consequences). See `0001-record-architecture-decisions.md`. Each ADR
  declares a `- Jira: <KEY>` target and is synced to that issue as a comment via
  `jira-toolkit/scripts/post_decisions_to_jira.py` (a story key, or the epic when the decision
  is cross-cutting).
- **Release notes** (`documentation/release-notes/`) are written for readers **outside** the
  repo: a short "At a glance" for business readers and a change-by-change section for
  practitioners. They must not mention the repo, its files, or internal review status.
  **Whenever a shipped item changes, update its release-notes entry (and any summary table) in
  the same change.**

When authoring **Mermaid**: do **not** use `;` in `sequenceDiagram` message text (Mermaid
treats it as a statement separator) — use `,` or `then`. Quote flowchart node/edge labels that
contain `()`, `<br/>`, or `·`.

## Jira

Jira mechanics — built-in issue types (spikes are `Task`s prefixed `Spike:`), how our working
stages map onto the default `To Do` / `In Progress` / `Done` workflow, required fields,
status-change comments, description-vs-comments, story sizing, and creating/closing epics —
live in [jira-toolkit/documentation/jira-sync.md](jira-toolkit/documentation/jira-sync.md).
Key rules:
- The user-stories markdown is the **source of truth**; Jira mirrors it.
- **Author descriptions in Jira wiki markup and write them with
  `jira-toolkit/scripts/set_wiki_description.py`** when they contain `_`, `+`, `<…>`, or
  `{…}` — the MCP markdown converter can mangle them. Keep `<`/`[`/`{` out of prose; put code
  in `{code}` blocks.
- **Issues for an external team or vendor must lead them step by step.** Inline every code
  snippet you mention in `{code}` blocks copied exactly from the repo, attach the same files,
  and state the environment, version, line, and what happened versus what was expected. Don't
  make their support team look anything up.
- Bugs follow [documentation/developer/bug-report-format.md](documentation/developer/bug-report-format.md).
- **Before calling vendor behavior our bug, check the vendor's release notes.** A release note
  alone isn't proof of a fix; mark a bug fixed upstream only when the same reproduction passes
  on a version at or after the one the note names. Otherwise attach the note and keep the bug
  at Ready for Dev until the vendor confirms.

## Project layout

- `documentation/` — the single documentation set (see above).
- `<project>/scripts/` — Python 3.11 modules (e.g. `example-report/scripts/`).
- `<project>/tests/` — pytest; one `test_<module>.py` per script; mock all network I/O.
- `<project>/config/` — hand-maintained data that changes over time (optional).
- `jira-toolkit/` — portable Jira scripts, prompt, and docs.
- `.scratch/` — gitignored drafts and run logs.

## Python conventions

- **Every `.py` file begins with a module-level docstring header** that briefly explains what
  the file is for (scripts and tests alike).
- **Centralize shared constants and tunable config in a per-project config module** (e.g.
  `<project>/scripts/<project>_config.py`, imported as `config`) — names, thresholds, mappings,
  endpoints, paths. Only truly file-local, single-use values stay inline. Use **Python
  constants**, not external config deps, for code-level config; hand-maintained data may be
  YAML.
- Route all REST/API calls through a shared helper with **rate-limit retry/backoff and
  per-process caching**; decode fetched text as `utf-8-sig` (tolerates a BOM).
- Store timestamps in **UTC**; convert to the **reporting time zone** through one shared helper
  for all date bucketing and display (never slice a UTC ISO string to get a date).
- Tests mirror scripts and mock external calls. Run `python -m pytest <project>/tests -q`
  before finishing; only run the suite for the project you changed. Use the venv Python
  (`.venv\Scripts\python.exe`).

## GitHub Actions conventions

- **Composite actions** hold the logic (via `github.action_path`); Python scripts are invoked
  from the action.
- **Caller workflows** are thin, per-repo, prefixed `rollout-ci_`, and just mint a token and
  invoke the composite action.
- **Singleton workflows** (schedule / `workflow_dispatch`) for org-wide / API-driven jobs.
- **Always set least-privilege `permissions`.** Every workflow declares an explicit
  **top-level** `permissions:` block defaulting to the minimum (`contents: read`, or `{}`),
  and **elevates per job** only where needed (`contents: write` to commit,
  `pull-requests: write` to comment on a PR, `pages: write` + `id-token: write` to deploy
  Pages). Never rely on the org default token scope. Check this whenever creating or updating
  any workflow.
- Auth: `actions/create-github-app-token` with `owner: "<github-org>"` and secrets
  `GH_APP_ID` + `GH_APP_PRIVATE_KEY`. Set `PYTHONUNBUFFERED: "1"` for live logs.
- **Never access secrets dynamically** (`secrets[format(...)]` or `toJSON(secrets)`) — CodeQL
  `actions/excessive-secrets-exposure` flags it because the runner then receives every secret.
  Reference **named** secrets, selecting per input with a conditional, e.g.
  `API_TOKEN: ${{ inputs.environment == 'prod' && secrets.PROD_TOKEN || secrets.TEST_TOKEN }}`.
  Pass only the environment's own secrets.

## GitHub Pages

A repo has **one** Pages site. If several reports publish, serve the first at the site root
and the rest at sub-paths (`/<report>/`) in the **same** deploy.

## Local shell (Windows PowerShell)

- The user's shell is **PowerShell**; use `py` (the Windows launcher) or the venv Python, not
  bare `python` (often not on PATH).
- **No bash heredoc.** `python - <<'PY' ... PY` fails in PowerShell. For multi-line Python use
  a here-string piped to Python (`@'` → code → `'@ | py -`, with `'@` at column 0) or a small
  file under `.scratch/` (delete when done).
- **Run REST scripts plainly — do not wrap them in output-capturing pipes.** `2>&1 |
  Out-String`, `| Select-Object`, or chaining after `cd …;` can swallow stdout in the terminal
  integration, so a **successful** run is reported as "Command produced no output". Invoke
  scripts **standalone, with absolute paths**.
- **When you need a command's output (test runs, REST scripts), redirect to a log and read the
  file.** The integrated terminal often returns "Command produced no output" for long runs even
  when they succeed — the #1 cause of apparent stalls. The reliable pattern:
  1. Redirect **all** streams: `<cmd> *> .scratch\run.log` (no pipe/filter).
  2. Read the log with the file-reading tool — not `Get-Content`/`| Select-Object`, which get
     swallowed the same way.
  3. **Never delete the log or script in the same command that creates it.** Read first;
     delete in a separate step.
  4. A run over ~60s may time out to the background — read the log when it finishes, don't
     re-run.

## Network and API learnings (general)

- Behind a TLS-inspecting corporate proxy, use the **OS trust store** (`truststore`) — never
  disable certificate verification.
- Some gateways/WAFs drop the default `python-requests` User-Agent; send a browser-like one.
- Hosted CI runners usually reach public SaaS APIs without the proxy workarounds a laptop needs.
- Jira Cloud: writes through REST API **v2** keep wiki markup; search uses
  `/rest/api/3/search/jql` with `nextPageToken`; users are addressed by `accountId`.
