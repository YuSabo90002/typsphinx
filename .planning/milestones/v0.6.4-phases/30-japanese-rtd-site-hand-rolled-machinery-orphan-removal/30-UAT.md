---
status: complete
phase: 30-japanese-rtd-site-hand-rolled-machinery-orphan-removal
source: [30-VERIFICATION.md]
started: 2026-07-26T12:10:00Z
updated: 2026-07-27T13:35:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Observed green docs.yml CI run on the post-deletion tree

expected: On the milestone PR against `main`, the `build-docs` job completes green; the `Build HTML documentation` step runs `uv run tox -e docs-html`; the `documentation-html` artifact uploads from `docs/_build/html`. (Structurally unobservable inside the phase: `docs.yml` has no `workflow_dispatch` and triggers only on push to `main`, a `v*` tag, or a PR targeting `main` — deferred by design, recorded as `backstop` in 30-01/30-04 plans and 30-EVIDENCE.md.)
result: pass
note: "Measured 2026-07-27 on milestone PR #124 (gsd/v0.6.4-read-the-docs-migration → main, opened 13:21Z). docs.yml run 30269906943 (event: pull_request) completed success; build-docs job green in 37s; 'Build HTML documentation' step (uv run tox -e docs-html) success; documentation-html artifact uploaded (380,116 bytes) from docs/_build/html. Blocker resolved — PR opened, docs.yml fired as designed."

### 2. Live RTD /en/latest/ drops the switcher markup

expected: After Read the Docs rebuilds the tracked `main` branch, fetching `https://typsphinx.readthedocs.io/en/latest/` shows zero occurrences of the switcher wrapper class and zero references to `custom.css` (both measured at one occurrence pre-phase; re-confirmed still present during verification because RTD has not yet rebuilt).
result: pass
note: "Measured 2026-07-26 after pushing the milestone branch (RTD tracks it as latest; owner-authorized push). RTD build 33763874 finished success; live fetch of /en/latest/: language-switcher = 0, custom.css = 0 (both were 1 pre-phase)."

### 3. Furo READTHEDOCS-gated sidebar slots on the hosted site

expected: At the same post-merge RTD rebuild, record the counts of `furo-sidebar-ad-placement` and `furo-readthedocs-versions` on `https://typsphinx.readthedocs.io/en/latest/`. A non-zero count is the accepted, documented side effect of deleting `html_sidebars` (Furo's upstream default sidebar), NOT a regression to fix — just record what appears.
result: pass
note: "Measured 2026-07-26 on RTD build 33763874: furo-sidebar-ad-placement = 0, furo-readthedocs-versions = 0. The open question resolves: under RTD's Addons build neither READTHEDOCS-gated slot renders on the hosted site — no ad placement appeared."

## Summary

total: 3
passed: 3
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps
