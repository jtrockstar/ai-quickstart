# 1. Record architecture decisions

- Status: Accepted
- Date: 2026-10-01
- Jira: PROJ-1

## Context

We define products deliberately and over many working sessions, often across separate agent
chats and contributors. Earlier agreements, decisions, and the reasoning behind them must stay
available so later sessions stay grounded, without drift.

We evaluated two options for capturing the "why" of decisions:
1. Keep rationale only inside the PRD/TDD.
2. Keep a separate, append-only decision log (ADRs).

## Decision

We use **both**, with a clear division of responsibility:

- The **PRD and TDD are the primary, current-state documents.** The *why* of the design lives
  there (more often the TDD). A reader — human or agent — should be able to read the PRD + TDD
  alone and understand the current (and planned) state.
- We **also keep a lightweight ADR log** in `documentation/decisions/` as a running history of
  decisions and changes. ADRs are for *tracking how we got here*, not for day-to-day
  understanding of the product.

ADR format: one short markdown file per decision, numbered sequentially (`NNNN-title.md`), with
Context / Decision / Consequences. Convention based on Michael Nygard, "Documenting
Architecture Decisions" (2011) and adr.github.io. Blank starting point:
[../templates/adr-template.md](../templates/adr-template.md).

## Consequences

- Every non-trivial decision or change of direction gets a short ADR, and the PRD/TDD are
  updated to reflect the new current state in the same change.
- Prior agreements are amendable guardrails: we change them intentionally, record the change
  as a new ADR (marking the old one `Superseded by NNNN`), and update the PRD/TDD — we do not
  silently rewrite history.
- Small extra overhead per decision, in exchange for a durable, searchable history that
  survives across chats and contributors.
- Each ADR declares a `- Jira: <KEY>` target (a story, or the epic when the decision is
  cross-cutting) and is posted/updated as a comment on that issue via
  `jira-toolkit/scripts/post_decisions_to_jira.py`, so decisions are visible where the team
  works.
