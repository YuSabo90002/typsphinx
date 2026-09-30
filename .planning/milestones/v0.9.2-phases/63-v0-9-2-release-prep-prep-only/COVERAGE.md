# Phase 63: External API Coverage Declaration

No external API integration: this phase edits four product-tree files (`pyproject.toml`, `uv.lock`,
`README.md`, `CHANGELOG.md`) and one test file (`tests/test_changelog_page_gate.py`), runs the
project's own test, lint, type and documentation tooling (`pytest`, `black`, `ruff`, `mypy`, the
`docs-html`/`docs-pdf` tox environments), dispatches the project's own CI workflow once
(`ci.yml`, never `release.yml`), and writes planning documents under
`.planning/phases/63-v0-9-2-release-prep-prep-only/`. No third-party API client, SDK, HTTP
integration, or webhook is introduced, and no `typsphinx/` source file is touched — the prep-only
fence is absolute in this phase (`63-CONTEXT.md` § `<domain>`).

Plan-time detector result, recorded verbatim (run over `63-CONTEXT.md`, the phase scope document
that existed before any plan in this phase existed):

```json
{"detected": false, "signals": []}
```

This result was produced by the deterministic detector run by the plan-phase orchestrator over the
phase scope, and it is transcribed here rather than re-derived.

**What this phase's `gh` usage actually is.** This phase's plans use the `gh` CLI for read-only
probes against this project's own GitHub repository — `gh release list`, `gh release view`,
`gh run list`, `gh run view`, and `gh run watch` — plus one `gh workflow run ci.yml --ref <branch>`
dispatch of this project's own continuous-integration workflow. That is the project's own CI
tooling, not a third-party service integration. `release.yml` is **named and recorded** in this
phase's plans and in `63-HANDOFF.md` but is **never triggered**, by tag push or by
`workflow_dispatch` — every plan's `<prohibitions>` block forbids it, and no command in any task of
any plan in this phase writes to a remote in a way that could trigger it.

**Why this file exists.** The seal-time coverage gate re-runs the same detector over the
concatenated PLAN bodies rather than over the phase scope document, and this phase's plan prose is
unavoidably dense with `gh`, workflow, release-pipeline and PyPI vocabulary — the version-bump
commit, the CI dispatch, the release-list and tag probes, the `release.yml` workflow name itself —
exactly the false-positive surface a bare integration-verb-plus-API-noun detector matches on. Phase
57's own `COVERAGE.md` hit this precise case: its plan-time detector run against the phase scope
returned `{"detected": false, "signals": []}`, but a later re-run over the finished PLAN bodies
returned `detected: true` on a self-referential match inside its own declaration's `must_haves`
citation — the words "API integration" appearing inside prose *about* the detector itself. This
file exists so that such a re-run meets a reasoned declaration rather than a fabricated capability
matrix, which for an API this phase does not touch would be worse than none.

`63-RESEARCH.md` § "Package Legitimacy Audit" measured this phase as installing, adding or
upgrading **zero packages** — so there is no package-legitimacy checkpoint owed anywhere in the
phase.

---
*Phase: 63-v0-9-2-release-prep-prep-only*
*Plan: 02*
