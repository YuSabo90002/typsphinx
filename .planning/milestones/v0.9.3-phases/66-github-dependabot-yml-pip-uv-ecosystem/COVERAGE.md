# Phase 66: External API Coverage Declaration

No external API integration: this phase changes one enum value in `.github/dependabot.yml`
(`package-ecosystem` from `"pip"` to `"uv"`), merges that one-file change into `main` behind an owner
checkpoint, and then observes how GitHub's Dependabot service reacts. It introduces no API client,
SDK, HTTP integration or webhook into this repository, adds no workflow, and touches no `typsphinx/`
source file.

Plan-time detector result, recorded verbatim. It ran over the concatenated bodies of
`66-01-PLAN.md` to `66-04-PLAN.md` plus the ROADMAP Phase 66 section (`roadmap.get-phase 66`), which
is the same scope the seal-time gate re-runs:

```json
{"detected":true,"signals":[{"verb":"(surface)","noun":"api","snippet":"<name>Task 1: Tracer: wave-2 gate, then poll the Actions API for the first uv update job and dependabot/uv/ PRs created "}],"terms":{"verbs":["integrate","integrates","integrating","integration","wrap","wraps","wrapping","connect","connects","connecting","consume","consumes","consuming","wire","wires","wiring","onboard","onboarding","adopt","adopts","adopting"],"nouns":["api","apis","sdk","sdks","rest","graphql","grpc","endpoint","endpoints","oauth","oauth2","webhook","webhooks","mcp"]}}
```

**Why the one signal is not an integration.** The only match is "poll the Actions API" in 66-03
Task 1's name. It names read-only `gh run list --workflow "Dependabot Updates"` and `gh run view --log`
calls, which observe dependabot's own jobs. Nothing in the repository calls that API at runtime, and
no capability of it is being built into the project, so there is no capability surface to enumerate
and no matrix row to fabricate.

**What this phase's network use is.**
- **GitHub, this repository, through `git` and `gh`.**
  - Writes: one new branch pushed (`chore/dependabot-uv-ecosystem`), one pull request created, and
    that pull request merged, behind a `checkpoint:decision`.
  - Read-only: pull requests, CI runs and job logs, `Dependabot Updates` runs and logs, branch
    protection and labels.
- **GitHub, public repositories, read-only**, for D-05 leg 1 and DEP-04:
  - `github/docs`: two markdown files
  - `dependabot/dependabot-core`: `uv/Dockerfile`, `uv/helpers/requirements.txt`, and the commit
    named by the deployed updater image tag
  - `astral-sh/uv`: the latest release
- **Registry fetches.** Worktree provisioning (`uv sync --extra dev`) and 66-04's
  `uv lock --check` resolve only packages already pinned in `uv.lock`. No package is added.

That is configuration plus observation of an external service's behaviour, not a service
integration.

---
*Phase: 66-github-dependabot-yml-pip-uv-ecosystem*
*Written by the planner at plan time (2026-09-12)*
