---
applyTo: "**/*.py"
---
# Python review checklist

Review-focused subset of the repo's agent instructions. Source of truth: `AGENTS.md` at the repo
root; keep this file in step with it.

- Every `.py` file (scripts and tests) starts with a module-level docstring saying what it's for.
- Shared constants and tunables live in the project's config module
  (`<project>/scripts/<project>_config.py`, imported as `config`), not scattered inline. Flag
  magic values that other modules or maintainers would need to change.
- Use Python constants for code-level config; don't add a config-file dependency for it.
- Every REST/API call goes through the project's shared helper, which provides rate-limit
  retry/backoff and a per-process cache, and decodes text as `utf-8-sig`. Flag direct
  `requests.get/post` calls that bypass it.
- Never disable TLS verification (`verify=False`). Behind a TLS-inspecting proxy, use the OS
  trust store (`truststore`).
- Secrets come from `.env` (local) or named CI secrets, never from code or committed files.
- Timestamps are stored in UTC. Any derived date (bucketing, file names, display) goes through
  the shared reporting-time-zone helper. Slicing a UTC ISO string to get a date is a bug.
- Jira writes use REST API v2 with wiki markup through `jira-toolkit/scripts/jira_client.py`;
  never hard-code Jira field ids (find fields by name).
- Tests: one `tests/test_<module>.py` per script, all network I/O mocked, and new behavior
  covered. A change to a script without a matching test change deserves a question.
- A new or changed module also updates its diagram in the TDD's components section (§5) and
  any affected developer guide; flag code changes with no matching doc change.
- Keep changes minimal: no unrelated refactors, speculative error handling, or comments that
  restate the code.
