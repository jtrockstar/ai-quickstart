---
applyTo: "documentation/**,jira-toolkit/documentation/**,**/README.md"
---
# Documentation review checklist

Review-focused subset of the repo's agent instructions. Source of truth: `AGENTS.md` at the repo
root; keep this file in step with it. Doc types and templates: `documentation/README.md`.

- **Current state.** The PRD and TDD describe the current and planned state. A changed decision
  also updates them in the same change, plus a new ADR in `documentation/decisions/` (numbered
  `NNNN-title.md`, Context / Decision / Consequences, with a `- Jira: <KEY>` line). Existing ADRs
  are never renumbered.
- **"Last Updated"** lines on the PRD, TDD, guides, and setup doc change when the content does.
- **Processes** are documented as a flowchart (`flowchart TD`, node IDs like `A.` shown in the
  labels, Start/End stadium, Process rectangle, Decision diamond, every decision arrow labeled)
  followed by a walkthrough table with columns
  `Step | At this node | Type | What happens | Then… | leading to`. Each decision gets two rows
  (`if **No**` / `but if **Yes**`). Class diagrams get prose only, no table.
- **TDD §5** has a class or flow diagram for every module, and a "Detailed guide" pointer at the
  end of a section whenever a guide in `documentation/developer/` covers it.
- **One source of truth per fact:** link instead of copying content between docs.
- **Release notes** (`documentation/release-notes/`) are for readers outside the repo: no file
  paths, repo links, or internal review status. When a shipped item changes, its entry changes
  in the same PR.
- **User stories** are Jira-ready `{noformat}` blocks; undeployed ones use `PROJ-XXXX` in the
  heading. Acceptance criteria live in the description.
- **Tunable choices and naming formulas** (keys, file names, paths) are written down where a
  maintainer will look, with the exact formula when a name is derived.
- **Mermaid:** no `;` in `sequenceDiagram` message text; quote labels that contain `()`, `<br/>`,
  or `·`.
- **Style:** clear, direct language. Don't label the style ("plain English" and similar).
