---
mode: agent
description: Deploy/sync markdown user stories to Jira via the Atlassian MCP server (markdown is the source of truth).
---

# Sync user stories to Jira

Push the user stories in the target `*-user-stories.md` file to Jira using the Atlassian MCP
tools. The **markdown is the source of truth**; Jira is the mirror. See
`../documentation/jira-sync.md` for the model and conventions.

## Inputs (ask if not provided)
- **Scope:** all stories, a single story (e.g. "Story 5"), or an epic.
- **Target file:** the `*-user-stories.md` to sync (default: the one in `documentation/`).
- **Dry run?** If yes, report the planned create/update actions but call no write tools.

## Procedure
1. Parse the target markdown. For each in-scope block capture: heading key (`PROJ-####` or
   the `PROJ-XXXX` placeholder), Title, Type, Epic (key), Priority, Story Points, and the
   `h3.` sections.
2. Map the Type to an issue type per jira-sync.md: Story → `Story`, Spike → `Task` (summary
   starts with `Spike:`), Bug → `Bug`.
3. For each block:
   - **Placeholder key (`PROJ-XXXX`)** → create the issue, set its parent epic
     (`jira_link_to_epic`), set story points (find the field with `jira_search_fields`, or run
     `jira-toolkit/scripts/set_story_points.py`), then **write the returned key back** into the
     markdown heading.
   - **Real key** → get the issue to compare, then update it only if the markdown differs
     (summary, description, points, parent epic). Skip if already in sync.
4. Descriptions containing `_`, `+`, `<...>`, or `{...}`: write them with
   `jira-toolkit/scripts/set_wiki_description.py` instead of the MCP converter.
5. Never delete Jira issues. Never invent epic keys — if a block's epic key is a placeholder,
   stop and ask. Never transition an issue to `Done`.

## Output
A concise table: Story | Jira key | action (created / updated / unchanged / skipped) | notes.
If any markdown headings were updated with new keys, list them.

## Guardrails
- Confirm the Jira MCP server is available (`.vscode/mcp.json`) and that `JIRA_URL`,
  `JIRA_USERNAME`, and `JIRA_API_TOKEN` are set in `.env` before making write calls.
- On dry run, do not call any create / update / transition / comment tool.
