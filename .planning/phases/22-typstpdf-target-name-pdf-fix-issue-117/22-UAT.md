---
status: testing
phase: 22-typstpdf-target-name-pdf-fix-issue-117
source: [22-VERIFICATION.md]
started: 2026-07-21T14:10:00Z
updated: 2026-07-21T14:10:00Z
---

## Current Test

number: 1
name: Non-ASCII filesystem round-trip across macOS/Linux (backstop truth)
expected: |
  Either (a) a non-ASCII `typst_documents` target name is usable and consistent enough across
  macOS (HFS+/APFS, NFD-normalizing) and Linux (byte-preserving NFC) that no silent duplicate or
  corrupted file is produced, or (b) the project explicitly accepts this as an inherent OS-level
  limitation outside typsphinx's control — which is what 22-01-PLAN.md's `verification: backstop`
  marker already states in prose, but which no code or test enforces or proves.
awaiting: user response

## Tests

### 1. Non-ASCII filesystem round-trip across macOS/Linux (backstop truth)

expected: On a real macOS filesystem, configure `typst_documents = [("index", "マニュアル.typ", ...)]`,
run `sphinx-build -b typstpdf`, and compare the on-disk filename bytes against the same build on
Linux. Pass if the filenames are usable and consistent across platforms, OR if the project records an
explicit decision to accept this as out of scope.
result: [pending]

why_human: This is a `verification: backstop` truth (22-01-PLAN.md `must_haves.truths`, 8th entry).
The plan's own text says filesystem-level Unicode normalization "is outside typsphinx's control and
is not asserted" — no test in the corpus exercises it and there is no macOS runner available. Per the
backstop-truth contract the verifier abstained rather than silently passing it. Code reading cannot
produce OS-level filesystem-encoding evidence.

**Note on scope:** this does NOT block the Issue #117 fix, which is fully proven — the part typsphinx
actually controls (a non-ASCII target passes through verbatim, with no `unicodedata.normalize`, case
folding, or transliteration applied) IS covered, by
`tests/test_builder_output_stem.py::test_resolve_output_stem_preserves_non_ascii_target`. Only the
OS-level half is open.

**Cheapest way to close this:** accept option (b) — record the limitation as a documented,
out-of-scope OS behavior. That matches the plan's existing prose and requires no macOS access.

## Summary

total: 1
passed: 0
issues: 0
pending: 1
skipped: 0
blocked: 0

## Gaps
