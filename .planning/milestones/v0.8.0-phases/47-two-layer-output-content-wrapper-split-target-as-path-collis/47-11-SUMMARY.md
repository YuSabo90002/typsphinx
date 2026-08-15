---
phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis
plan: 11
subsystem: build-output
tags: [sphinx-extension, typst, path-collision-detection, builder]

# Dependency graph
requires:
  - phase: 47-09
    provides: TypstBuilder._collision_key() and _validate_output_path_collisions(), the shared pre-write collision validator
  - phase: 47-10
    provides: OUT-01/OUT-02 target-as-path semantics and the content/wrapper output split this plan builds on
provides:
  - "posixpath.normpath() inside _collision_key() -- path SHAPE (redundant ./, doubled //, embedded /./) is now comparison-equivalent to its plain form, closing the BLD-02 false negative"
  - "_is_usable_typst_documents_entry() -- the single entry-usability predicate now consulted by all four wrapper-path-resolving sites, closing the BLD-03 false negative"
  - "tests/test_collision_predicate_completeness_gate.py -- 11-test regression gate (3 fixtures x subprocess + unit halves) pinning both closed gaps"
affects: [phase-48-cross-reference-guard, phase-49-per-master-include-graph]

# Actuals (#2632)
actuals:
  tokens: 15900
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Single-predicate ownership for a concept four call sites had independently drifted on (_is_usable_typst_documents_entry) -- same shape as the existing _is_drive_qualified/_escapes_outdir single-source extraction"
    - "Comparison-only key normalization (posixpath.normpath inside _collision_key) proven safe by a three-ground argument (separation, monotonicity, non-collapse) rather than by inspection alone"

key-files:
  created:
    - tests/test_collision_predicate_completeness_gate.py
    - tests/fixtures/bld02_path_shape_collision_gate/
    - tests/fixtures/bld02_template_clobber_gate/
    - tests/fixtures/bld03_under_length_entry_gate/
    - .planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/47-GAP-RED-EVIDENCE.md
  modified:
    - typsphinx/builder.py
    - tests/test_pdf_generation.py

key-decisions:
  - "Order path-shape normalization before case-folding inside _collision_key() (fold separators -> posixpath.normpath -> casefold) -- correctness-neutral (the two foldings commute) but keeps the function's existing separator contract legible"
  - "The entry-usability warning fires exactly once per build, inside _validate_output_path_collisions() only -- not repeated per-docname inside _write_typst_files()'s wrapper loop, which runs N times"
  - "Rule 1 auto-fix: tests/test_pdf_generation.py's test_builder_appends_failure_for_malformed_entry_but_not_short_entry asserted the exact pre-fix silent-fallback behavior BLD-03 reverses; renamed and rewritten to the corrected, locked contract rather than left failing"

patterns-established:
  - "A concept spelled ad-hoc at N call sites that have already drifted apart is a promote-to-named-predicate signal, not a routine refactor -- extract once, wire all N sites through it, and state in the predicate's own docstring which sites previously diverged and how"

requirements-completed: [BLD-02, BLD-03]

coverage:
  - id: D1
    description: "Two typst_documents targets differing only in path shape (./manual.typ vs manual.typ) now collide with a pre-write ExtensionError naming both entries, and no .typ file is written"
    requirement: BLD-02
    verification:
      - kind: unit
        ref: "tests/test_collision_predicate_completeness_gate.py::TestBld02PathShapeCollisionGate::test_bld02_path_shape_duplicate_rejected_typst"
        status: pass
      - kind: unit
        ref: "tests/test_collision_predicate_completeness_gate.py::TestBld02PathShapeCollisionGate::test_bld02_path_shape_duplicate_rejected_typstpdf"
        status: pass
    human_judgment: false
  - id: D2
    description: "A ./-prefixed target that normalizes onto the reserved _template.typ infrastructure file is reported as a collision instead of silently overwriting the template"
    requirement: BLD-02
    verification:
      - kind: unit
        ref: "tests/test_collision_predicate_completeness_gate.py::TestBld02TemplateClobberGate::test_bld02_dot_slash_template_clobber_rejected_typst"
        status: pass
      - kind: unit
        ref: "tests/test_collision_predicate_completeness_gate.py::TestBld02TemplateClobberGate::test_bld02_dot_slash_template_clobber_rejected_typstpdf"
        status: pass
    human_judgment: false
  - id: D3
    description: "_collision_key() folds path shape via posixpath.normpath() while still folding case and NOT folding Unicode normalization, and never collapses a leading parent-traversal segment"
    requirement: BLD-02
    verification:
      - kind: unit
        ref: "tests/test_collision_predicate_completeness_gate.py::TestCollisionKeyPathShapeUnit (4 tests)"
        status: pass
    human_judgment: false
  - id: D4
    description: "A typst_documents entry with fewer than two elements produces NO wrapper file -- the docname's own content survives intact, a warning names the skipped entry under -b typst, and -b typstpdf reports it in finish()'s aggregate ExtensionError while the well-formed sibling master still gets its PDF"
    requirement: BLD-03
    verification:
      - kind: unit
        ref: "tests/test_collision_predicate_completeness_gate.py::TestBld03UnderLengthEntryGate (3 tests)"
        status: pass
      - kind: unit
        ref: "tests/test_collision_predicate_completeness_gate.py::TestIsUsableTypstDocumentsEntryUnit::test_is_usable_typst_documents_entry_predicate"
        status: pass
    human_judgment: false
  - id: D5
    description: "_is_usable_typst_documents_entry() is the single predicate consulted by all four wrapper-path-resolving sites (collision validator, D-07 wrapper report, write-phase wrapper loop, TypstPDFBuilder.finish())"
    requirement: BLD-03
    verification:
      - kind: unit
        ref: "grep -c _is_usable_typst_documents_entry typsphinx/builder.py -> 13 (1 definition + docstring mentions + 4 call sites)"
        status: pass
    human_judgment: false
  - id: D6
    description: "Full suite, black, and mypy all green; existing OUT-02/D-04/D-05/WR-01/BLD-01 regression modules pass unmodified"
    verification:
      - kind: unit
        ref: "uv run pytest -q -> 1038 passed, 5 skipped, 0 xfailed"
        status: pass
      - kind: other
        ref: "uv run black --check . && uv run mypy typsphinx/"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-08-11
status: complete
---

# Phase 47 Plan 11: Collision Predicate Completeness (BLD-02 path shape + BLD-03 entry-usability drift) Summary

**Closed the two BLD-02/BLD-03 false negatives `47-VERIFICATION.md` found live against this checkout — `posixpath.normpath()` now folds path shape inside `_collision_key()`, and a single `_is_usable_typst_documents_entry()` predicate now owns "can this entry produce a wrapper file" across all four sites that used to spell it independently.**

## Performance

- **Duration:** 55 min
- **Started:** 2026-08-11T22:11:00Z (approx.)
- **Completed:** 2026-08-11T23:02:20Z
- **Tasks:** 3
- **Files modified:** 12 (2 modified, 10 created)

## Accomplishments

- `TypstBuilder._collision_key()` now applies `posixpath.normpath()` between separator-folding and `casefold()`, so `"./manual.typ"` vs `"manual.typ"`, `"a//b.typ"` vs `"a/b.typ"`, and `"./_template.typ"` vs the reserved `"_template.typ"` all collide correctly, with the OUT-02 escape guard and both D-05 comparison behaviours (case-fold on, Unicode normalization off) provably unchanged.
- New module-level `_is_usable_typst_documents_entry(entry) -> bool` in `typsphinx/builder.py`, sited next to `_is_drive_qualified()`/`_escapes_outdir()`, now the single source of truth wired into the collision validator, `write()`'s D-07 wrapper report, `_write_typst_files()`'s wrapper loop (the actual data-destruction site), and `TypstPDFBuilder.finish()` (a new "has no target element" failure branch).
- Three new fixtures and an 11-test gate module (`tests/test_collision_predicate_completeness_gate.py`) reproduce all three pre-fix shapes with content-level RED measurements (per binding constraint #4, since all three exit 0 pre-fix) and pin the post-fix contract.
- `.planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/47-GAP-RED-EVIDENCE.md` records the RED transcript for each shape plus a "Post-fix GREEN" re-measurement section.

## Task Commits

Each task was committed atomically:

1. **Task 1: Record pre-fix RED for all three failing shapes** - `955644a` (test)
2. **Task 2: TRACER — normalize path shape inside the collision key** - `07035c2` (feat)
3. **Task 3: Single-source the entry-usability predicate across all four wrapper-path sites** - `5491d65` (feat)

_Note: no plan-metadata commit yet — this worktree agent does not update STATE.md/ROADMAP.md; the orchestrator commits those centrally after the wave merges._

## Files Created/Modified

- `typsphinx/builder.py` - `_collision_key()` gains `posixpath.normpath()`; new `_is_usable_typst_documents_entry()`; wired into `_validate_output_path_collisions()`, `write()`, `_write_typst_files()`, `TypstPDFBuilder.finish()`
- `tests/test_collision_predicate_completeness_gate.py` - new 11-test gate module (created RED in Task 1, driven GREEN across Tasks 2-3)
- `tests/fixtures/bld02_path_shape_collision_gate/` - `./manual.typ` vs `manual.typ` duplicate-target fixture
- `tests/fixtures/bld02_template_clobber_gate/` - `./_template.typ` reserved-file-clobber fixture
- `tests/fixtures/bld03_under_length_entry_gate/` - 1-element `("index",)` entry fixture
- `tests/test_pdf_generation.py` - one stale test renamed and rewritten to the corrected BLD-03 contract (see Deviations)
- `.planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/47-GAP-RED-EVIDENCE.md` - new RED + Post-fix GREEN evidence document

## Decisions Made

- Fold separators, then `posixpath.normpath()`, then `casefold()` inside `_collision_key()` — the two foldings commute so this ordering is correctness-neutral, chosen purely for docstring/readability clarity.
- The new "produces no wrapper file" warning fires exactly once per build, inside `_validate_output_path_collisions()` only, not repeated per-docname inside the write-phase wrapper loop.
- `TypstPDFBuilder.finish()`'s new "has no target element" branch is checked via the SAME `_is_usable_typst_documents_entry()` predicate as the other three sites, positioned after the two pre-existing exact-message branches (empty-tuple, non-str-docname) so those two legacy messages survive verbatim.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed a stale unit test asserting the exact pre-fix behavior BLD-03 reverses**
- **Found during:** Task 3 (single-sourcing the entry-usability predicate)
- **Issue:** `tests/test_pdf_generation.py::TestPDFErrorHandling::test_builder_appends_failure_for_malformed_entry_but_not_short_entry` asserted that a 1-element `typst_documents` entry "is NOT malformed" and "must still compile" by falling its stem back to the docname — precisely the silent-fallback contract this plan's `must_haves.truths` require reversed (a 1-element entry must produce NO wrapper file). Running the plan's own acceptance-criteria test set against the corrected `finish()` failed this one pre-existing test: it expected `"1 master document(s) failed"` and `valid.pdf` to exist; the corrected code now reports 2 failures and produces no `valid.pdf`.
- **Fix:** Renamed to `test_builder_appends_failure_for_malformed_entry_and_short_entry` and rewrote its assertions to the corrected, locked BLD-03 contract: both the empty-tuple and the 1-element entry now count as failures (`"2 master document(s) failed"`), the second carrying `"has no target element"`, and `valid.pdf` is asserted absent.
- **Files modified:** `tests/test_pdf_generation.py`
- **Verification:** `uv run pytest tests/test_missing_and_malformed_master_gate.py tests/test_non_str_docname_gate.py tests/test_pdf_generation.py -q` → 33 passed; full suite green afterward.
- **Committed in:** `5491d65` (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (1 Rule 1 bug)
**Impact on plan:** Necessary for correctness — the pre-existing test encoded the exact silent-fallback defect this plan closes; updating it does not narrow or weaken any of this plan's own `must_haves`, `prohibitions`, or acceptance criteria. No scope creep — no other file was touched beyond what the plan's own tasks named.

## Issues Encountered

- `mypy` flagged `_is_usable_typst_documents_entry(entry: object)` as "not indexable" for `entry[0]`. Retyped the parameter to `tuple` (matching the existing `_wrapper_output_relpath(self, entry: tuple)` convention already in this module) rather than adding an ignore comment. Re-ran `uv run mypy typsphinx/` → clean.
- `uv run ruff check .` could not run in this worktree — a pre-existing, already-acknowledged NixOS environment limitation (`.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md`; STATE.md Deferred Items records "Does not block SC#3, which takes lint authority from CI"). Unrelated to this plan's changes; `black` and `mypy` both ran and passed locally, and CI's `lint` job is authoritative for `ruff`.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Both BLD-02 and BLD-03 must-haves from `47-VERIFICATION.md`'s gap report are now closed and pinned by a real-`sphinx-build` regression gate; ROADMAP SC#4's "every 'two logical files want one physical path' case is loud" claim now holds for path-shape-equivalent duplicates, the reserved-`_template.typ` clobber, and an under-length wrapper-producing entry.
- Plan `47-12` (the sibling gap-closure plan for the same wave) is unaffected by this plan's changes — no shared file overlap beyond `typsphinx/builder.py`, which this plan's own commits leave in a fully green, lint/type-clean state for the next plan to build on.
- `.planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/47-GAP-RED-EVIDENCE.md` is ready for the phase re-verification pass that should follow both gap-closure plans landing.

---
*Phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis*
*Completed: 2026-08-11*

## Self-Check: PASSED

All 8 referenced files found on disk (`typsphinx/builder.py`, `tests/test_collision_predicate_completeness_gate.py`, the three new fixture `conf.py` files, `47-GAP-RED-EVIDENCE.md`, `tests/test_pdf_generation.py`, this SUMMARY). All 3 task commits (`955644a`, `07035c2`, `5491d65`) found in `git log --oneline --all`.
