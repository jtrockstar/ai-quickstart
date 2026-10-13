---
applyTo: ".github/workflows/**,.github/actions/**"
---
# GitHub Actions review checklist

Review-focused subset of the repo's agent instructions. Source of truth: `AGENTS.md` at the repo
root; keep this file in step with it.

- **Least-privilege permissions.** Every workflow has an explicit top-level `permissions:` block
  set to the minimum (`contents: read`, or `{}`). Jobs elevate only what they need:
  `contents: write` to commit, `pull-requests: write` to comment on a PR, `pages: write` +
  `id-token: write` to deploy Pages. Flag missing blocks and broad or unused grants.
- **Never access secrets dynamically.** No `secrets[format(...)]` and no `toJSON(secrets)`; both
  expose every secret to the runner (CodeQL `actions/excessive-secrets-exposure`). Reference
  named secrets, choosing per input with a conditional, e.g.
  `API_TOKEN: ${{ inputs.environment == 'prod' && secrets.PROD_TOKEN || secrets.TEST_TOKEN }}`.
  Pass a job only the secrets it uses.
- **Structure.** Logic lives in composite actions (scripts invoked via `github.action_path`).
  Per-repo caller workflows are thin, prefixed `rollout-ci_`, and only mint a token and call
  the action. Scheduled or org-wide jobs are singleton workflows (`schedule` +
  `workflow_dispatch`).
- **Auth.** Tokens come from `actions/create-github-app-token` with secrets `GH_APP_ID` and
  `GH_APP_PRIVATE_KEY`, not personal tokens.
- **Python steps** set `PYTHONUNBUFFERED: "1"` so logs stream live, and install from the
  project's `requirements.txt`.
- **Untrusted input.** Don't interpolate `github.event.*` text (titles, bodies, branch names)
  directly into `run:` scripts; pass it through `env:` and quote it.
- **Pinning.** Third-party actions use a version tag or commit SHA, never a branch.
- Workflow changes only take effect once merged to the default branch; the PR description
  should say how the change will be tested after merge.
