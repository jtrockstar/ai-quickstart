# Product scope brainstorming

> **Background doc.** A raw idea list captured before the PRD was agreed. It is a source of
> ideas, **not** agreed scope; anything adopted moves into the PRD (and, if it's a decision,
> an ADR). Background docs are kept for context and are not updated as the product changes.

Captured: 2026-09-28

## Ideas raised in the kickoff

| Idea | Raised by | Notes | Outcome |
|---|---|---|---|
| Daily capture of open-item counts | Service owners | The core need | → PRD G1 |
| Trend dashboard | Leadership | Per-service and all-services views | → PRD G2 |
| Alert on a sharp rise in High items | Service owners | Needs a threshold design | → PRD G3 (later epic) |
| CSV export for planning reviews | Leadership | Small | → PRD G4 (later epic) |
| Intraday snapshots | One team | Nobody else needed it | Not adopted (PRD non-goal) |
| Backfill past months | Leadership | The Source API keeps no history | Not possible |
| Item-level drill-down | Service owners | The Source API's own UI already does this | Not adopted |

## Questions we parked

- Who owns the dashboard once it's live? → answered in the end-user overview.
- Do retired services keep their history? → PRD §10 open question.
