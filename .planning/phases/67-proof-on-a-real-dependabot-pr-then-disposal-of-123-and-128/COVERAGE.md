# Phase 67: External API Coverage Declaration

No external API integration: read-only gh/git/PyPI observation plus three owner-gated PR actions (merge #138, close #128 and #123).

The phase reads GitHub and PyPI state through `gh`, `git` and `curl`, merges one dependabot PR (#138) and closes two (#123, #128) behind owner checkpoints, and records evidence under `.planning/`. It builds no API client, SDK, HTTP integration or webhook into this repository, adds no workflow, and touches no `typsphinx/` source file.

Plan-time detector result, recorded verbatim. It ran over the concatenated bodies of
`67-01-PLAN.md` to `67-05-PLAN.md` plus the ROADMAP Phase 67 section (`roadmap.get-phase 67`), the
same scope the seal-time gate re-runs:

```json
{"detected":true,"signals":[{"verb":"(surface)","noun":"api","snippet":"| GitHub API → evidence | run, job, step, check-run and PR JSON authored by GitHub and dependabot enters the repository "}],"terms":{"verbs":["integrate","integrates","integrating","integration","wrap","wraps","wrapping","connect","connects","connecting","consume","consumes","consuming","wire","wires","wiring","onboard","onboarding","adopt","adopts","adopting"],"nouns":["api","apis","sdk","sdks","rest","graphql","grpc","endpoint","endpoints","oauth","oauth2","webhook","webhooks","mcp"]}}
```

**Why the one signal is not an integration.** The only match is a trust-boundary row in 67-01's
threat model ("GitHub API → evidence"). It describes JSON that read-only `gh` calls return and that
is transcribed into evidence markdown. Nothing in the repository calls that API at runtime, and no
capability of it is being built into the project, so there is no capability surface to enumerate
and no matrix row to fabricate.

**What this phase's network use is.**
- **GitHub, this repository, through `gh` and `git`.**
  - Read-only: PRs, CI runs, job step lists and logs, check runs, branch protection, issue events,
    `Dependabot Updates` runs, and `refs/pull/<n>/head` fetches.
  - Writes, each behind its own `checkpoint:decision`: one merge (#138, `gh pr merge --merge
    --match-head-commit`), and two comment-and-closes (#128, then #123), with owner-approved text.
- **PyPI JSON, read-only**: `sphinx` (latest and per-version `requires_dist`), `docutils`, `ruff`.
- **Registry fetches**: worktree provisioning (`uv sync --extra dev`) and 67-02's `uv lock --check`
  resolve only already-pinned packages. 67-02's `uvx --from ruff==<v>` fetches the ruff wheel at
  exactly the version #138's dependabot-written lock pins, inside the FHS runner. No project
  dependency is added.

That is observation plus three owner-gated repository actions, not a service integration.

---
*Phase: 67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128*
*Written by the planner at plan time (2026-09-12)*
