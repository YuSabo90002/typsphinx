---
status: testing
phase: 48-compile-time-cross-reference-guard
source: [48-VERIFICATION.md]
started: 2026-08-12T07:05:00Z
updated: 2026-08-12T07:05:00Z
---

## Current Test

number: 1
name: Accept the label-collision false-negative trade-off
expected: |
  Owner explicitly accepts that a coincidental docname/label-namespace collision (`a/b` vs
  `a_u2f_b`, via the `/`→`_u2f_` sanitize transform) makes the compile-time guard render a
  WORKING link to the wrong (decoy) document instead of degrading to plain text. This is a
  real, narrow, measured, and already-filed regression versus the deleted build-time
  mechanism, which checked docname membership rather than label-string identity and
  therefore did not have this failure mode.
awaiting: user response

## Tests

### 1. Accept the label-collision false-negative trade-off
expected: Owner accepts that a coincidental docname/label-namespace collision (`a/b` vs `a_u2f_b`, via the `/`→`_u2f_` sanitize transform) makes the guard render a WORKING link to the wrong (decoy) document instead of degrading to plain text. Read `48-EVIDENCE.md` § "Accepted limit — label-collision false negative". Filed as todo `2026-08-12-label-collision-false-negative-in-compile-time-xref-guard.md`; also flagged WARNING by `48-REVIEW.md` (WR-02).
result: [pending]

### 2. Accept the D-11 compile-time cost tier outcome
expected: Owner confirms the -2.37% full-corpus compile-time delta (28.92s/27.21s after vs. 28.93s/28.56s before) is acceptable — bottom tier, "record only", no todo/blocker created. The verifier independently re-derived the arithmetic and confirmed the tier thresholds were fixed before measurement; only the ACCEPTANCE is outstanding. Read `48-EVIDENCE.md` § "D-11 compile-time cost".
result: [pending]

### 3. Accept the D-01 diagnostic-visibility loss
expected: Owner confirms it is acceptable that, post-Phase-48, a reference to a deliberately `:orphan:`-marked target now degrades with ZERO diagnostic at any layer — the D-01 cross-document degrade warning was deleted with no replacement, and Sphinx itself emits no warning for an `:orphan:` target that resolved successfully. The verifier confirmed no published-docs contract broke. Read `48-EVIDENCE.md` § "D-01 — no published contract changed".
result: [pending]

### 4. Visually confirm PDF cross-reference links navigate to the correct destination
expected: Opening the built `docs/_build/pdf/typsphinx.pdf` and clicking a handful of internal `:ref:`/`:doc:` cross-reference links jumps to the CORRECT target section — not merely to any destination or the wrong page. The verifier ran `tox -e docs-pdf` (exit 0, "build succeeded, 5 warnings", no "does not exist in the document"), producing a valid 119-page PDF with 502 `/Link` annotations all carrying a `/Dest` or `/A` action; only semantic correctness of each destination is unverified.
result: [pending]

## Summary

total: 4
passed: 0
issues: 0
pending: 4
skipped: 0
blocked: 0

## Gaps
