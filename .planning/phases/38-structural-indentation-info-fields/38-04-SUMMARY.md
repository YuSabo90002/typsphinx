---
phase: 38-structural-indentation-info-fields
plan: 04
subsystem: testing
tags: [test-census, sc5-migration, docutils, typst-translator, sphinx]

# Dependency graph
requires:
  - phase: 38-structural-indentation-info-fields (plans 01-03)
    provides: 38-EMISSION-CONTRACT.md's normative byte specification for the desc_content/field_list
      wrapper, the field-body inline reflow, the literal_strong/literal_emphasis monospace leaves, and
      the depart_desc break-marker fix — this plan re-measures the pre-existing exact-string blast
      radius against that contract.
provides:
  - "38-TEST-CENSUS.md: a read-not-grepped inventory of every existing test assertion Phase 38's emitted
    bytes will break, bucketed A (will break) / B (stays green) / C (conditionally at risk) / D
    (page-count measurements), each Bucket-A row assigned to its owning plan (38-05/38-06/38-07/38-08)"
  - "the D-14 migration strategy: per-plan-owned migration at the point bytes change, the golden.typ
    hand-derivation rule (never regenerate from the new code's output), and the one documented
    exception for PDF-text goldens (re-measure-then-verify, mirroring Phase 37's 37-09 precedent)"
  - "a real 659-passed, 0-failed whole-suite baseline (uv run pytest -m \"not slow\" -q) plus clean
    black/ruff/mypy runs, for every later plan's set-difference check"
affects: [38-05-body-wrapper-and-break-marker, 38-06-field-list-wrapper-and-field-body-reflow,
  38-07-literal-strong-emphasis-monospace, 38-08-page-count-remeasure-and-closeout]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "read-the-assertion-not-the-node-name: every census row traces to an opened file and a read
      assertion, never a grep hit on a node-family name"
    - "PDF-extracted-text goldens are measurements, not hand-derivable expected strings — migrated by
      re-measure-then-manually-verify-the-diff, distinct from the golden.typ hand-derivation rule"

key-files:
  created:
    - .planning/phases/38-structural-indentation-info-fields/38-TEST-CENSUS.md
  modified: []

key-decisions:
  - "D-14 honoured: 37-TEST-CENSUS.md's content was not inherited; the blast radius was re-measured
    against the current tree by opening every candidate file this plan's read_first names."
  - "Two Phase-34 PDF-text goldens (inline_math_pdf_text_mitex.golden.txt /
    inline_math_pdf_text_native.golden.txt) are REACHED by Phase 38 -- Construct C's confval combines a
    field_list and a following paragraph inside desc_content, exactly the shape section 2+3's nested pad
    wrappers touch -- flagged for re-measurement, not silently trusted to stay green by analogy."
  - "test_desc_rubric_decoupling_render_gate.py's SC1 delegation guard (RETAINED_DELEGATION_METHODS /
    DUMMY_STRONG_LITERAL count) is a second, previously-unlisted Bucket A row in a file 38-EMISSION-
    CONTRACT.md section 7 only cited for its golden.typ half -- D-09 inverts its 'must still delegate'
    claim once literal_strong/literal_emphasis stop delegating."
  - "tests/test_translator.py's desc/field-list structural tests (test_full_api_description_structure,
    test_field_list_rendering) are found, on reading, to STAY GREEN despite 38-EMISSION-CONTRACT.md
    section 7 predicting breakage for this file -- their assertions are loose substring checks that
    survive both the wrapper and the field-body reflow."

requirements-completed: [IND-01, IND-04, FLD-01, FLD-02, FLD-03]

coverage:
  - id: D1
    description: "38-TEST-CENSUS.md exists with Buckets A-D, a counts section, a disagreement section
      (both directions), a must-not-touch section, a D-13 row, a migration-strategy section, and a
      whole-suite baseline, each Bucket A row citing a contract section and an owning plan."
    requirement: "FLD-02"
    verification:
      - kind: other
        ref: "test -s 38-TEST-CENSUS.md && grep -qE 'Bucket A' ... && grep -qE 'Bucket D' ..."
        status: pass
    human_judgment: true
    rationale: "The plan's own must_haves truths (e.g. 'every row produced by reading, never grepping',
      'the census names two pre-existing PDF-text goldens Phase 37's census missed and states whether
      this phase's changes reach them') are judgment calls about the QUALITY and HONESTY of the reading
      pass, not mechanically checkable by a script -- a human/verifier must read the census's own
      Disagreement and Bucket A/D reasoning to confirm it was produced by reading."

# Metrics
duration: 55min
completed: 2026-08-01
status: complete
---

# Phase 38 Plan 04: Test Census Summary

**Read-not-grepped SC#5 test census: 4 Bucket-A breaking rows (including a previously-unlisted SC#1 delegation-guard break and both reached Phase-34 PDF-text goldens), 11 Bucket-B stays-green groups, 3 Bucket-C conditional rows, 2 Bucket-D page-count constants, plus the D-14 migration strategy and a real 659-passed whole-suite baseline.**

## Performance

- **Duration:** 55 min
- **Started:** 2026-08-01T20:00:00+09:00
- **Completed:** 2026-08-01T20:30:00+09:00
- **Tasks:** 2 completed
- **Files modified:** 1 (created)

## Accomplishments

- Opened and read every candidate test/fixture file this plan's `read_first` names (25 files total),
  producing a bucketed census (A/B/C/D) instead of a node-name grep pass.
- Found a genuine, previously-unlisted Bucket A row by reading a whole file rather than the two line
  numbers `38-EMISSION-CONTRACT.md` §7 cited for it: `test_desc_rubric_decoupling_render_gate.py`'s SC#1
  delegation guard, whose `RETAINED_DELEGATION_METHODS`/`DUMMY_STRONG_LITERAL`-count assertions invert
  once D-09 removes `literal_strong`/`literal_emphasis`'s delegation.
- Determined `tests/test_translator.py`'s desc/field-list structural tests — which §7's own starting
  table predicted would break — actually stay green on a full read, because their assertions are loose
  substring checks that survive both the new wrapper and the field-body reflow. Recorded as the census's
  primary "grep would flag, reading clears" disagreement.
- Determined both Phase-34 PDF-text goldens (`inline_math_pdf_text_mitex.golden.txt` /
  `inline_math_pdf_text_native.golden.txt`) ARE reached by this phase — Construct C's confval combines a
  collapsed field list and a following paragraph inside `desc_content`, exactly the nested-wrapper shape
  §2+§3 change — and specified their migration methodology (re-measure-then-verify, mirroring Phase 37's
  own `37-09` precedent for these same two files) rather than silently trusting them to stay green.
- Wrote the D-14 migration strategy (per-plan ownership at the point bytes change, the `golden.typ`
  hand-derivation rule stated unambiguously, the PDF-text-golden exception, and the page-count-is-a-
  measurement rule) and a whole-suite baseline: `659 passed, 29 deselected in 46.47s`, plus clean
  `black --check .` / `ruff check .` / `mypy typsphinx/` runs.

## Task Commits

Both tasks target the same single artifact (`38-TEST-CENSUS.md`) — Task 1's buckets/counts/disagreement/
must-not-touch/D-13 sections and Task 2's migration-strategy/baseline sections were written and verified
together, then committed as one atomic commit covering the complete file:

1. **Task 1 + Task 2: produce the census (buckets, counts, disagreements, D-14 strategy, baseline)** -
   `7742b93` (docs)

**Plan metadata:** committed alongside this SUMMARY per the worktree metadata-commit step.

## Files Created/Modified

- `.planning/phases/38-structural-indentation-info-fields/38-TEST-CENSUS.md` - the full SC#5 census: 4
  Bucket A rows, 11 Bucket B groups, 3 Bucket C rows, 2 Bucket D constants, a 25-file counts section, a
  two-direction disagreement section, a must-not-touch (Phase 39 rubric) section, a D-13 restatement, the
  D-14 migration strategy, and the whole-suite/lint/type baseline.

## Decisions Made

- Bucketed `test_confval_field_spacing_render_gate.py`'s two `.typ`-structural assertions as Bucket B
  (contract §4.3(3) guarantees the collapsed-inline case byte-identical) but its PDF-extracted-text
  assertion as Bucket C (the added indentation's effect on real PDF line-wrapping is a measurement claim
  this census cannot hand-verify without running the phase's own not-yet-written code) — deliberately NOT
  asserting a confident B or A verdict for that one row, since D-14 forbids treating an unmeasured guess
  as either a hand-derived expected string or a settled "stays green" claim.
- Classified the two Phase-34 PDF-text goldens' migration as re-measure-then-verify rather than hand-
  derivation, explicitly carving out this one exception to the `golden.typ` rule in the migration-strategy
  section — a PDF-extracted-text golden is a measurement of a real Typst layout pass, not a `.typ`-source
  byte sequence the contract can specify character-for-character in advance.
- Recorded that `test_field_list_in_list_item_render_gate.py`'s top-level `:Author:`/`:Version:` field
  list is the genuine paragraph-wrapped single-value shape §4 targets (confirmed by reading the test's own
  CR-01 comment, not assumed from the confval fixtures' superficially similar `:field:` syntax) — its
  `'par({text("Test Author")})'` literal-substring lookup will raise `ValueError` post-phase, making the
  whole test function Bucket A, while the CR-01 negative-separator checks are Bucket C (correctness depends
  on 38-06's D-12 implementation choice, decided by this exact fixture per the contract).

## Deviations from Plan

None - plan executed exactly as written. Both tasks' acceptance criteria were met without needing any
Rule 1/2/3/4 auto-fix: this plan modifies no test and no source file, so there was no code to fix, only a
document to read into existence.

## Issues Encountered

- `uv run ruff check .` initially failed inside the worktree with the documented NixOS `stub-ld`
  dynamic-linker error (project memory `nixos-sandbox-test-env`) because `uv sync` installs a
  generic-linux ELF `ruff` wheel into a fresh worktree venv. Resolved per the memory's documented fix:
  symlinked the main tree's already-patchelf'd `.venv/bin/ruff` (same pinned 0.15.20) into this worktree's
  `.venv/bin/ruff`. Recorded as a provisioning note inside the census's own baseline section so a later
  plan's executor does not rediscover it as a surprise.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `38-TEST-CENSUS.md` gives 38-05, 38-06, and 38-07 an explicit, per-plan-owned list of Bucket A rows to
  migrate in the same commit that changes their bytes, plus the golden-file hand-derivation rule and the
  PDF-text-golden exception spelled out unambiguously.
- 38-08 has both Bucket D page-count constants named with their consuming tests, ready for re-measurement,
  and owns writing this census's "Finalisation against reality" section at phase closeout (mirroring
  `37-TEST-CENSUS.md`'s own shape), including resolving the two Bucket A3/A4-adjacent Bucket C rows this
  census left conditional.
- The whole-suite baseline (`659 passed, 29 deselected`) is the real, freshly-run number every later plan
  should diff its own post-change suite run against — not a number carried over from a prior phase.
- No blockers. This plan touches no test or source file, so it introduces zero merge risk for the
  parallel waves that follow.

---
*Phase: 38-structural-indentation-info-fields*
*Completed: 2026-08-01*
