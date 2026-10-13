# Jira MCP Integration Architecture

**Purpose:** Explain how AI agents access Jira data in VS Code via Model Context Protocol (MCP).

---

## Common Misconception

When someone asks "how did you integrate Jira into VS Code?", they're often imagining:

- ❌ A VS Code extension with Jira UI panels
- ❌ A direct VS Code → Jira integration
- ❌ Something "installed" in VS Code that connects to Jira

**This is not what we're doing.**

---

## What We Actually Built

```
┌─────────────────────────────────────────────────────────────────────┐
│                           VS Code                                   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  AI Agent (GitHub Copilot or similar)                        │   │
│  │                                                              │   │
│  │  "Find all bugs in PROJ sprint 12"                           │   │
│  │         │                                                    │   │
│  │         ▼                                                    │   │
│  │  Tool call: jira_search(...)                                 │   │
│  └──────────────────────────────────────────────────────────────┘   │
│              │                                                      │
│              │ MCP Protocol (JSON-RPC over stdio)                   │
│              ▼                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Jira MCP Server (separate process)                          │   │
│  │  - Configured in .vscode/mcp.json                            │   │
│  │  - Holds API token / auth credentials                        │   │
│  │  - Translates MCP tool calls → Jira REST API                 │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                    │
                    │ HTTPS (Jira REST API)
                    ▼
          ┌──────────────────────────┐
          │  Jira Cloud              │
          │  (example.atlassian.net) │
          └──────────────────────────┘
```

---

## Correct Architectural Description

> "We use **Model Context Protocol (MCP)** to give AI coding agents access to Jira. An MCP
> server runs locally, configured with Jira API credentials. When the AI agent needs Jira
> data, it invokes MCP tools (like `jira_search` or `jira_get_issue`), which the MCP server
> translates into Jira REST API calls. VS Code is just the host environment — it doesn't
> 'know' about Jira. The AI agent does."

---

## Key Concepts

| Concept | Explanation |
|---------|-------------|
| **MCP** | Model Context Protocol — a standard for connecting AI models to external tools/data sources |
| **MCP Server** | A process that exposes a set of "tools" the AI can invoke (runs alongside VS Code, not inside it) |
| **Tool** | A function the AI can call, e.g., `jira_search`, `jira_get_issue`, `jira_create_issue` |
| **The AI Agent** | GitHub Copilot (or another agent) — it decides when to call Jira tools based on the conversation |

---

## How It Works Step-by-Step

1. **User asks a question** in VS Code chat:
   > "What stories are in the PROJ 1.2 release?"

2. **AI agent decides** it needs Jira data to answer this question.

3. **AI invokes an MCP tool**:
   ```json
   {
     "tool": "jira_search",
     "parameters": {
       "jql": "project = PROJ AND fixVersion = '1.2' ORDER BY key"
     }
   }
   ```

4. **MCP server receives the call**, translates it to a Jira REST API request, and sends it to Jira.

5. **Jira responds** with JSON data (issues, fields, etc.).

6. **MCP server returns the data** to the AI agent.

7. **AI agent synthesizes a response** for the user, summarizing or analyzing the Jira data.

---

## Why This Matters

This is a **tool-augmented AI agent** pattern, not a traditional IDE integration.

| Traditional Integration | MCP-Based Agent |
|------------------------|-----------------|
| UI panels, buttons, menus in VS Code | No UI — conversational interface |
| Human navigates Jira UI | AI decides when to query Jira |
| Human writes JQL queries | AI formulates queries from natural language |
| Human interprets results | AI synthesizes and summarizes |

The AI has **agency** — it decides when Jira data is needed, formulates queries, and
synthesizes results. There's no Jira UI in VS Code. The human talks to the agent; the agent
talks to Jira.

---

## Configuration

The MCP server is configured in `.vscode/mcp.json`. Credentials load from the gitignored
repo-root `.env` through `envFile`, so nothing secret is in the config file:

```jsonc
{
  "servers": {
    "jira": {
      "type": "stdio",
      "command": "uvx",
      "args": ["mcp-atlassian"],
      "envFile": "${workspaceFolder}/.env"
      // .env supplies JIRA_URL, JIRA_USERNAME (account email), JIRA_API_TOKEN
    }
  }
}
```

Atlassian also offers a hosted MCP server that signs in with OAuth instead of an API token.
Either works with the conventions in [jira-sync.md](jira-sync.md); this repo documents the
local `mcp-atlassian` server because the same `.env` also drives the REST scripts.

---

## Available Jira Tools

The MCP server exposes tools like:

| Tool | Purpose |
|------|---------|
| `jira_search` | Execute JQL queries |
| `jira_get_issue` | Fetch a single issue by key |
| `jira_create_issue` | Create a new issue |
| `jira_update_issue` | Modify an existing issue |
| `jira_transition_issue` | Move an issue to another status |
| `jira_add_comment` | Add a comment to an issue |
| `jira_link_to_epic` | Set an issue's parent epic |
| `jira_search_fields` | Find a field's id by name (e.g. story points) |
| `jira_get_sprint_issues` | Get issues in a sprint |

The AI agent calls these tools as needed based on the user's request.

---

## Summary

- **VS Code** is the host environment (provides the chat UI)
- **AI Agent** is the brain (decides what to do, interprets results)
- **MCP Server** is the bridge (translates AI tool calls to Jira API calls)
- **Jira REST API** is the data source (standard Atlassian API)

No Jira-specific code runs inside VS Code. The AI agent orchestrates everything through MCP
tool calls.
