# Spike findings

Results from the de-risking spikes in the first epic. Feeds the PRD/TDD and the story build
order. Start a new one from [templates/spike-findings-template.md](templates/spike-findings-template.md).

> **Example.** The findings below are illustrative.

Last Updated: 2026-10-08

## Spike 1 (PROJ-2) — Source API access and rate limits

**Access recipe:**
- Auth is a Bearer token (`SOURCE_API_TOKEN` in `.env`).
- From a **local machine** behind the corporate proxy, use the **OS trust store**
  (`truststore.inject_into_ssl()`): the proxy re-signs TLS with its own CA. Do *not* disable
  verification. A **hosted runner** needs no workaround.
- Send a browser-like **User-Agent**; the gateway dropped the default `python-requests` agent
  (seen as `RemoteDisconnected`).

**Confirmed via API:**
- `GET api/v1/services` returns `[{"key", "name"}]` (21 services).
- `GET api/v1/services/{key}/open-items` returns `{"counts": {...}}`. **Severities with no
  items are omitted**, so the collector fills them with zero.
- Bursts above ~10 requests/second return **HTTP 429** with `Retry-After: 2`. The shared retry
  helper's backoff covers this.

**Design impact:** no self-hosted runner needed; retry/backoff and zero-fill go into Story 3.

## Spike 2 (PROJ-3) — Jira permissions

- Jira Cloud site, email + API token in `.env`, loaded by the `jira` MCP server via `envFile`.
- Create / update / comment / transition and parent-epic linking all worked on a test story,
  which was then deleted.
- The project is team-managed, so story points use the **"Story point estimate"** field;
  `set_story_points.py` found it by name without configuration.
- Closing an epic: the agile done flag returned 404 (not used by team-managed projects);
  `close_epic.py` reports this as "n/a".
