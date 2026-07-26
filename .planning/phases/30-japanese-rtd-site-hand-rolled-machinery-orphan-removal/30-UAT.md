---
status: testing
phase: 30-japanese-rtd-site-hand-rolled-machinery-orphan-removal
source: [30-VERIFICATION.md]
started: 2026-07-26T12:10:00Z
updated: 2026-07-26T12:10:00Z
---

## Current Test

number: 1
name: Observed green docs.yml CI run on the post-deletion tree
expected: |
  On the milestone pull request against `main`, the `Documentation` workflow's `build-docs` job
  completes green; its `Build HTML documentation` step runs `uv run tox -e docs-html`; the
  `documentation-html` artifact is uploaded from `docs/_build/html`.
awaiting: user response

## Tests

### 1. Observed green docs.yml CI run on the post-deletion tree

expected: On the milestone PR against `main`, the `build-docs` job completes green; the `Build HTML documentation` step runs `uv run tox -e docs-html`; the `documentation-html` artifact uploads from `docs/_build/html`. (Structurally unobservable inside the phase: `docs.yml` has no `workflow_dispatch` and triggers only on push to `main`, a `v*` tag, or a PR targeting `main` — deferred by design, recorded as `backstop` in 30-01/30-04 plans and 30-EVIDENCE.md.)
result: [pending]

### 2. Live RTD /en/latest/ drops the switcher markup

expected: After Read the Docs rebuilds the tracked `main` branch, fetching `https://typsphinx.readthedocs.io/en/latest/` shows zero occurrences of the switcher wrapper class and zero references to `custom.css` (both measured at one occurrence pre-phase; re-confirmed still present during verification because RTD has not yet rebuilt).
result: [pending]

### 3. Furo READTHEDOCS-gated sidebar slots on the hosted site

expected: At the same post-merge RTD rebuild, record the counts of `furo-sidebar-ad-placement` and `furo-readthedocs-versions` on `https://typsphinx.readthedocs.io/en/latest/`. A non-zero count is the accepted, documented side effect of deleting `html_sidebars` (Furo's upstream default sidebar), NOT a regression to fix — just record what appears.
result: [pending]

## Summary

total: 3
passed: 0
issues: 0
pending: 3
skipped: 0
blocked: 0

## Gaps
