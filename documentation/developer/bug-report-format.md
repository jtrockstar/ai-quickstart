# Bug report format

_Last updated: 2026-10-12._

How a bug is written up in Jira, so anyone — including an external team or vendor — can
reproduce it without asking questions. The user-stories doc holds each bug as a Jira-ready
block (examples in [example-report-user-stories.md](../example-report-user-stories.md)).

## When to file

File a bug when shipped behavior differs from what the PRD, TDD, user guide, or an accepted
story says. If nobody agreed on the behavior yet, it's a story, not a bug.

## Before filing against a vendor: check their release notes

When a third-party product (a library, SaaS API, or tool) misbehaves, or behaves differently
between two environments running different versions, the cause is often a fix or change the
vendor already shipped. Before treating it as our bug, search the vendor's release notes for
the affected feature.

- **A release note alone is not proof.** The change may have been made for a different reason,
  or fixed a different problem in the same feature.
- **Mark a bug "fixed upstream" only when it's confirmed independently:** the same
  reproduction passes on a version at or after the one the note names. Record that version in
  **Fix version** and the description, link the note, and keep the bug open until every
  environment we run has reached that version.
- **Found a note but can't confirm it?** Attach the note to the bug and keep it at
  **Ready for Dev** until the vendor confirms.
- **No note?** File the bug normally (for an external vendor, follow the step-by-step rules
  below).

## Title

```
<What is wrong> <when / where>
```

Example: `Re-running the collector on the same day overwrites that day's partition`.

## Jira fields

| Field | Value |
|---|---|
| Issue type | `Bug` |
| Parent | the epic the affected feature belongs to (or the current maintenance epic) |
| Priority | `High` if it corrupts data or blocks users; otherwise `Medium` |
| Story points | size the fix with the rubric in jira-sync.md |
| Fix version | the release that will carry the fix, if releases are tracked |

## Description (sections, in order)

Author in **Jira wiki markup** and write it with `set_wiki_description.py` when it contains
`_`, `+`, `<…>`, or `{…}`.

| Section | Content |
|---|---|
| `h3. Summary` | One or two sentences: what's wrong and why it matters. |
| `h3. Environment` | Version or commit, where it ran (local / workflow), OS and runtime when relevant. |
| `h3. Steps to Reproduce` | Numbered (`#`) steps someone else can follow exactly. |
| `h3. Expected` | What should happen, citing the doc or story that says so. |
| `h3. Actual` | What happened instead. |
| `h3. Evidence` | Log lines, payloads, or code in `{code}` blocks, copied exactly. Attach the same files. |
| `h3. Notes` | Suspected cause, workaround, related issues. |

## Bugs for an external team or vendor

Lead them step by step:
- Inline **every** snippet you mention in `{code}` blocks, copied exactly from the repo, and
  **attach** the same files.
- For each one, state the environment and version, the line, and what happened versus what
  was expected.
- Don't make their support team look anything up (no links into private repos).

## Board stage

New bugs start at **New**; they become **Ready for Dev** (comment) once fully written, and
follow the same stages and status-change comments as stories (see jira-sync.md). Close only
with explicit confirmation, after the fix is verified by a test or spot check.

## Wiki-markup gotchas

- `<…>` can be rewritten to `[…]` by markdown converters — even inside `{code}` blocks — so
  write wiki markup directly.
- `[…]` in prose is read as a link and `{…}` as a macro; keep them inside `{code}` blocks.
- `-` pairs become strikethrough; use `→` instead of `->`.
