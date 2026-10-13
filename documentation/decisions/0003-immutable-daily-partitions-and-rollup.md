# 3. Immutable daily partitions plus a rebuilt rollup

- Status: Accepted
- Date: 2026-10-06
- Jira: PROJ-6

## Context

The Source API exposes only current counts, so history exists only if we capture it. We
considered three storage shapes:

| Option | Pros | Cons |
|---|---|---|
| One growing file, appended daily | Simple to read | Every run rewrites history; merge conflicts; one bad write corrupts everything |
| A database | Queryable | New infrastructure to run and secure for ~60 numbers a day |
| **One immutable file per day + a rollup rebuilt from them** | History can't be rewritten by accident; diffs are tiny and reviewable; the rollup is disposable | Many small files over years |

## Decision

Write **one immutable JSON partition per reporting-zone day** (`data/daily/<YYYY-MM-DD>.json`).
A partition is never overwritten unless the operator passes `--force`. **Rebuild
`data/rollup.json` from all partitions on every run**; the dashboard reads only the rollup.

## Consequences

- Re-runs are safe: the same day keeps its first capture.
- A bad rollup is fixed by rerunning with `--rollup-only`; no history is lost.
- File count grows by one per day (≈365 a year), well within git's comfort zone. Revisit with
  yearly compaction if retention becomes a concern (TDD §7).
