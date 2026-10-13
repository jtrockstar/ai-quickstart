# End-to-end functional test plan

> **Living doc (Story PROJ-5).** Scenarios are added as capabilities land; each story's
> Definition of Done updates this plan. It complements the automated unit tests
> (`python -m pytest example-report/tests -q`). Start from
> [../templates/e2e-testing-plan-template.md](../templates/e2e-testing-plan-template.md).

## Purpose

Manually verify the product end to end before and after major changes, using real services
rather than mocks.

## Scenario template

For each scenario record: **preconditions**, **steps**, **expected result**, **actual
result**, **pass/fail**. Multi-person scenarios go in the
[e2e testing script](e2e-testing-script.md).

## Scenarios

1. **First capture** — with an empty `data/daily/`, run the collector; one partition and a
   one-day rollup appear. _(Story PROJ-6 — done.)_
2. **Same-day re-run keeps history** — run twice the same day; the second run prints
   `kept existing` and the partition's `collectedAt` is unchanged. _(Bug PROJ-9 — done.)_
3. **Forced repair** — run with `--force`; the partition is replaced and the rollup reflects
   it. _(Story PROJ-6 — done.)_
4. **Late-evening capture** — run after 20:00 Eastern; the partition is named for the Eastern
   date. _(planned — Bug PROJ-XXXX.)_
5. **Scheduled run publishes the dashboard** — dispatch the daily workflow; data is committed
   and the dashboard shows the new day. _(planned — Story PROJ-XXXX.)_
6. **Service filter** — choose one service; the chart shows only its counts and the address
   keeps the choice. _(planned — Story PROJ-XXXX.)_
