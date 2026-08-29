# Phase 61: External API Coverage Declaration

No external API integration: this phase edits one markdown file in the product tree
(`CHANGELOG.md`'s `## [Unreleased]` block), runs the project's own test, lint, type and
documentation tooling (`pytest`, `black`, `ruff`, `mypy`, the `docs-html`/`docs-pdf` tox
environments), and writes planning documents under
`.planning/phases/61-v0-9-1-release-prep-prep-only/`. No third-party API client, SDK, or HTTP
integration is introduced, and no `typsphinx/` source file is touched — the prep-only fence is
absolute in this phase (`61-CONTEXT.md` "Out of scope").

Plan-time detector result, recorded verbatim (run over `61-CONTEXT.md`, the phase scope document
that existed before any plan in this phase existed):

```json
{"detected":false,"signals":[]}
```

**What this phase's `gh` usage actually is.** This phase's plans use the `gh` CLI for read-only
probes (`gh release list`, `gh run list`, `gh tag`) against this project's own GitHub repository,
and one `gh workflow run ci.yml --ref <branch>` dispatch of this project's own CI workflow — the
project's own continuous-integration tooling, not a third-party service integration. No external
vendor API, SDK, or webhook is called by anything this phase does.

`scripts/extract_changelog_section.py` is named in `61-HANDOFF.md` as an inheritance record for
the v0.9.2 milestone's own release-prep phase, but it is **not invoked at all this phase** — there
is no `## [0.9.1]` CHANGELOG section for it to extract (D-01, D-03: no version bump, no `## [0.9.1]`
heading this phase).

**Why this file exists.** The seal-time `api-coverage.verify-pre` gate re-runs the same detector
over the concatenated plan bodies, not over `61-CONTEXT.md` alone, and this phase's plans are
unavoidably dense with `gh`, workflow, and release-pipeline prose (CI dispatch, release-list
probes, tag probes, the `release.yml` workflow name itself) — which is exactly the false-positive
surface a bare integration-verb-plus-API-noun detector is prone to matching on. Phase 57's own
`COVERAGE.md` hit this precise case: its plan-time detector run against the phase scope returned
`{"detected":false,"signals":[]}`, but a later re-run over the finished PLAN bodies returned
`detected: true` on a self-referential match inside its own declaration's `must_haves` citation —
the words "API integration" appearing inside prose *about* the detector itself. This file exists
so that a seal-time false-positive detector run over Phase 61's own gh-and-workflow-dense plan
prose is met with a reasoned declaration rather than a fabricated capability matrix — a matrix for
an API this phase does not touch would be worse than no matrix.

---
*Phase: 61-v0-9-1-release-prep-prep-only*
*Plan: 02*
