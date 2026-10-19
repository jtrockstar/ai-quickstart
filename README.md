# dtc-codescan-template

A template repo that packages how we work: the working agreements for people and AI agents,
a complete documentation set with filled examples and blank templates, a portable Jira
toolkit for a default Jira Cloud site, and a small Python example project that shows the code
conventions end to end.

## What's inside

| Path | What it is |
|---|---|
| [AGENTS.md](AGENTS.md) | Working agreements and conventions every AI agent follows (and people can read). The single source; the files below point to it. |
| [CLAUDE.md](CLAUDE.md), [.github/copilot-instructions.md](.github/copilot-instructions.md) | Pointers so Claude Code and GitHub Copilot find `AGENTS.md`. Codex reads `AGENTS.md` directly. |
| [.mcp.json](.mcp.json) | Jira MCP server for Claude Code (VS Code uses `.vscode/mcp.json`). |
| [.github/instructions/](.github/instructions/) | Short, path-scoped review checklists (Python, GitHub Actions, documentation) for Copilot code review, which can't read `AGENTS.md`. Kept in step with it. |
| [documentation/](documentation/README.md) | One documentation set for the whole repo: PRD, TDD, user stories, ADRs, developer guides, end-user guides, functional testing, release notes, background, and templates. |
| [jira-toolkit/](jira-toolkit/README.md) | Jira MCP config, sync prompt, and paced REST scripts (descriptions, story points, assignees, epic closure, ADR comments). |
| [example-report/](example-report/README.md) | A working example project: config module, REST helper, date helper, CLI, and mocked tests. |
| [.vscode/](.vscode/) | MCP server, prompt locations, interpreter, and recommended extensions. |
| [ai-quickstart.code-workspace](ai-quickstart.code-workspace) | Workspace file for opening this repo (alone or with sibling repos). |
| [.env.example](.env.example) | The settings `.env` needs (copy to `.env`, which is gitignored). |

## Quick start

1. Follow [documentation/developer-setup.md](documentation/developer-setup.md).
2. Run the tests:

   ```powershell
   .venv\Scripts\python.exe -m pytest jira-toolkit\tests -q
   .venv\Scripts\python.exe -m pytest example-report\tests -q
   ```

3. Ask Copilot Chat: *"Use Jira to list the open issues in PROJ."* to confirm the MCP server.

## Starting a new repo from this template

1. Copy the repo (or use it as a GitHub template repository).
2. Rename `PROJ` to your Jira project key in
   [jira-toolkit/documentation/jira-sync.md](jira-toolkit/documentation/jira-sync.md) (see its
   *Tunable choices*) and in your user-stories doc.
3. Replace `example-report/` with your project, keeping the `scripts/` + `tests/` layout and
   the config / REST / dates split.
4. Start your docs from [documentation/templates/](documentation/templates/) in the order PRD →
   TDD → user stories. Keep or delete the `example-report-*` docs as reference.
5. Keep [ADR-0001](documentation/decisions/0001-record-architecture-decisions.md); replace the
   other example ADRs with your own.
