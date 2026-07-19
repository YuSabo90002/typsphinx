---
status: complete
phase: 18-fidelity-fixes-regression-gate-close
source: [18-VERIFICATION.md]
started: 2026-07-19T14:09:31Z
updated: 2026-07-19T14:25:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Whole-corpus residual silent-collision check (backstop)
expected: |
  GATE-03's automated gate proves fatal-free compilation + empty unknown_visit catalogue,
  but does not text-scan every table for the collision signature. Spot-check additional
  wide tables in the freshly built corpus index.pdf (beyond pages 239/241/245 already
  checked) — e.g. other multi-column API/parameter tables — and confirm cells wrap within
  their columns with no cross-column merge and no right-margin clip. This is a plan-
  acknowledged backstop (D-02: no reliable translate-time is-this-table-too-wide test),
  explicitly scoped as a future-audit candidate.
result: pass
note: |
  Held-out full-corpus scan performed (2026-07-19) against the fresh post-fix build
  (/tmp/pytest-of-yuta/pytest-57/.../_build/index.pdf, 689 pp., built 23:05 after the
  22:53 FID-01a fix commit). All 689 pages text-extracted (pdftotext -layout via
  poppler); wide-table pages detected heuristically and rendered to PNG (150/300 DPI).

  BODY CELLS (the FID-01a target): PASS. The extdev/deprecated "Deprecated APIs" table
  (pp.239/242/245) wraps every long dotted identifier within its column — no cross-column
  merge, no right-margin clip. The only other strongly-multicolumn page (p459, the
  restructuredtext "Tables" example) renders correctly.

  NEW finding (HEADER row): the same table's header labels "Deprecated"/"Removed" overflow
  their narrow fr-sized columns and collide → renders "DeprecatedRemoved" on pp.239/242/245.
  Introduced by the fr-column change (narrow numeric columns; plain-text headers get no ZWSP).
  Per this test's expected clause ("any instance found is triaged as a next-milestone backlog
  item, NOT a Phase 18 regression"), user triaged it to backlog. Recorded as F16 in
  17-AUDIT-CATALOGUE.md "Post-Phase-17 Additions". Test verdict: PASS (backlog-triaged).

## Summary

total: 1
passed: 1
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[none — the one new finding (F16, header-row collision) was user-triaged to next-milestone
backlog per test 1's plan-acknowledged allowance, not opened as a Phase 18 gap]

## Deferred Follow-Ups

- test: 1
  idea: "F16 — table header labels ('Deprecated'/'Removed') overflow narrow fr-sized columns and collide (extdev/deprecated pp.239/242/245). New regression from the FID-01a fr-column change; body cells wrap correctly. Recorded in 17-AUDIT-CATALOGUE.md; fix in a future milestone (min column width / header wrap / max(header,body) fr sizing)."
  deferred_at: 2026-07-19
