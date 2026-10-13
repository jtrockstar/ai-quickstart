# Jira toolkit (portable)

Jira automation for this repo, designed to be copied into other repos or centralized into a
shared package. Targets a **default Jira Cloud** site (built-in issue types, statuses, and
system fields) using an **Atlassian account email + API token**.

## Contents (inside `jira-toolkit/`)
- `scripts/jira_config.py` — every tunable in one place (env-variable names, retry/pacing,
  Done status name, story-point field names).
- `scripts/jira_client.py` — shared REST helper: `.env` loading, Basic auth, OS trust store,
  retry with backoff (honors `Retry-After`), field lookup by name, JQL search.
- `scripts/set_wiki_description.py` — set an issue's description from raw Jira wiki markup
  (bypasses the lossy MCP markdown converter); used when creating epics.
- `scripts/set_story_points.py` — set story points, finding the field by name on each issue.
- `scripts/set_jira_assignee.py` — bulk set/clear the assignee (resolves a name/email to an
  `accountId`).
- `scripts/close_epic.py` — fully close epic(s): status → Done (+ resolution when the screen
  allows it) and the agile done flag. Accepts keys or `--jql`; idempotent, `--dry-run`.
- `scripts/post_decisions_to_jira.py` — post/update ADR decisions as comments on the Jira
  issue named in each ADR's `- Jira:` line (idempotent).
- `tests/` — pytest, one `test_<module>.py` per script, all network mocked.
- `documentation/jira-sync.md` — the markdown ⇄ Jira model, issue types, workflow stages,
  required fields, epics, sizing, utilities, and tunables.
- `documentation/jira-toolkit-technical-design.md` — TDD: structure, architecture, auth/TLS,
  VS Code integration points, and portability.
- `documentation/jira-mcp-architecture-explainer.md` — how the MCP integration works.
- `prompts/sync-stories-to-jira.prompt.md` — agent prompt to push user stories to Jira.
- `mcp.jira.json` — portable reference copy of the Jira MCP server config.

## Two integration points that must live at VS Code paths
VS Code / Copilot only load these from fixed locations, so they live **outside**
`jira-toolkit/` but are part of this toolkit:
- **`.vscode/mcp.json`** — the active MCP server config (merge in `jira-toolkit/mcp.jira.json`).
- **`.mcp.json`** (repo root) — the same server for Claude Code (`mcp-atlassian --env-file .env`).
  Codex users add it to `~/.codex/config.toml` (see the developer setup guide).
- **`.vscode/settings.json`** or the **workspace file** — `chat.promptFilesLocations` includes
  `jira-toolkit/prompts` so the prompt here is discoverable.

## Setup / porting to another repo
1. Copy this `jira-toolkit/` folder to the new repo root.
2. Merge the `jira` server from `jira-toolkit/mcp.jira.json` into `.vscode/mcp.json`.
3. Add `"jira-toolkit/prompts": true` to `chat.promptFilesLocations`.
4. Put `JIRA_URL`, `JIRA_USERNAME`, and `JIRA_API_TOKEN` in the repo-root `.env` (gitignored).
5. `pip install -r jira-toolkit/scripts/requirements.txt`.
6. Run the tests: `python -m pytest jira-toolkit/tests -q`.

See `documentation/jira-sync.md` for usage and conventions.
