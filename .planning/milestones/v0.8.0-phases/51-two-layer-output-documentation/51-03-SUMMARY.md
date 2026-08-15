---
phase: 51-two-layer-output-documentation
plan: 03
subsystem: docs
tags: [sphinx, typst, documentation, pytest]

# Dependency graph
requires:
  - phase: 51-two-layer-output-documentation
    provides: "51-01's output_layout.rst page (Wrapper and Content Files / Which File to Compile / Where the Wrapper Is Written) and the two-class gate shape (TestOutputLayoutBuildFileSets / TestPublishedOutputLayoutTextMatchesBuild) this plan extends"
provides:
  - "docs/source/user_guide/output_layout.rst — 'Targets that are refused' and 'Targets That Stop the Build' sections, publishing SC#2's refusal contract and D-05's collision-abort contract"
  - "Six new gate methods in tests/test_output_layout_docs_gate.py proving both contracts against real -b typst builds"
  - "Three new tests/fixtures/output_layout_refused_*_gate/ Sphinx projects, literal copies of 51-RESEARCH.md Part C builds 3a/3b/3c"
affects: [51-04, 51-05, 51-06]

# Actuals (#2632) — pairs with the plan's estimate to calibrate future estimates.
actuals:
  tokens: 5158
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Reused the two-class docs-gate shape from 51-01 (real -b typst build class + never-skipping prose-match class), extended with methods rather than new classes"
    - "Reused an EXISTING Phase 47 fixture (bld03_self_collision_gate) for a new documentation gate rather than duplicating its configuration a fourth time"

key-files:
  created:
    - tests/fixtures/output_layout_refused_parent_gate/conf.py
    - tests/fixtures/output_layout_refused_parent_gate/index.rst
    - tests/fixtures/output_layout_refused_absolute_gate/conf.py
    - tests/fixtures/output_layout_refused_absolute_gate/index.rst
    - tests/fixtures/output_layout_refused_drive_gate/conf.py
    - tests/fixtures/output_layout_refused_drive_gate/index.rst
  modified:
    - docs/source/user_guide/output_layout.rst
    - tests/test_output_layout_docs_gate.py

key-decisions:
  - "Reworded the three new fixtures' header comments and the new test module's constant comment to avoid the literal substrings 'typst_documents' (beyond the one real assignment line) and '_resolve_target_stem' / '_escapes_outdir' / '_is_drive_qualified', because the plan's own acceptance criteria grep for exactly those counts (1 and 0 respectively) — caught and fixed before the Task 1 commit, not after."
  - "Verified the collision-abort literal block against a real build of the reused bld03_self_collision_gate fixture before writing it into the page, rather than deriving it from the RESEARCH.md summary alone — the exact ExtensionError text (including the docname/target parenthetical) matched on the first measurement, so no rewrite was needed."

patterns-established: []

requirements-completed: [DOC-14]

coverage:
  - id: D1
    description: "output_layout.rst's 'Targets that are refused' subsection names all three refused target shapes (parent-traversal, absolute, drive-qualified), quotes the builder's refusal warning verbatim in a code-block:: text literal, and states the build still succeeds with a basename fallback"
    requirement: "DOC-14"
    verification:
      - kind: unit
        ref: "tests/test_output_layout_docs_gate.py::TestPublishedOutputLayoutTextMatchesBuild::test_page_quotes_the_verbatim_refusal_warning"
        status: pass
      - kind: unit
        ref: "tests/test_output_layout_docs_gate.py::TestOutputLayoutBuildFileSets::test_refused_parent_target_falls_back_to_basename"
        status: pass
      - kind: unit
        ref: "tests/test_output_layout_docs_gate.py::TestOutputLayoutBuildFileSets::test_refused_absolute_target_falls_back_to_basename"
        status: pass
      - kind: unit
        ref: "tests/test_output_layout_docs_gate.py::TestOutputLayoutBuildFileSets::test_refused_drive_qualified_target_falls_back_to_basename"
        status: pass
    human_judgment: false
  - id: D2
    description: "The parent-traversal refusal case is proved to write nothing outside the build directory (OUT-02's escape guard), observed against the filesystem rather than re-derived from the builder's logic"
    requirement: "DOC-14"
    verification:
      - kind: unit
        ref: "tests/test_output_layout_docs_gate.py::TestOutputLayoutBuildFileSets::test_refused_parent_target_falls_back_to_basename"
        status: pass
    human_judgment: false
  - id: D3
    description: "output_layout.rst's 'Targets That Stop the Build' section names the three collision claimant kinds, shows the canonical self-collision configuration, quotes the ExtensionError verbatim, and states the check runs before any file is written"
    requirement: "DOC-14"
    verification:
      - kind: unit
        ref: "tests/test_output_layout_docs_gate.py::TestPublishedOutputLayoutTextMatchesBuild::test_page_states_the_collision_abort"
        status: pass
      - kind: unit
        ref: "tests/test_output_layout_docs_gate.py::TestOutputLayoutBuildFileSets::test_self_collision_target_aborts_the_build_with_no_typ_files"
        status: pass
    human_judgment: false

# Metrics
duration: ~35min
completed: 2026-08-15
status: complete
---

# Phase 51 Plan 03: The Two Ways a Target Can Fail Summary

**Documented and machine-proved the two `typst_documents` target-failure modes — refused-with-fallback (parent-traversal, absolute, drive-qualified) and refused-outright (the Phase 47 collision abort) — against real `-b typst` builds, extending the Wave 1 `output_layout.rst` page and its permanent gate.**

## Performance

- **Duration:** ~35 min active work
- **Started:** 2026-08-15 (approx.)
- **Completed:** 2026-08-15
- **Tasks:** 2
- **Files modified:** 8 (2 modified, 6 created)

## Accomplishments

- Extended `docs/source/user_guide/output_layout.rst`'s "Where the Wrapper Is Written" section with a new "Targets that are refused" subsection: names all three refused shapes, states the build still succeeds with a basename fallback, and quotes the builder's own refusal warning verbatim inside a `.. code-block:: text` literal block.
- Added a new "Targets That Stop the Build" section naming the three collision claimant kinds (`_template.typ`, every docname's own content file, every other entry's wrapper), showing the canonical self-collision configuration (`typst_documents = [("index", "index.typ", ...)]` — built successfully in v0.7.x, now aborts), and quoting the real `ExtensionError` text verbatim (measured against a fresh build of the reused fixture, not paraphrased).
- Created three new fixtures under `tests/fixtures/output_layout_refused_*_gate/`, each a literal copy of a `51-RESEARCH.md` Part C measured build (3a/3b/3c), with a header comment explaining why the three cannot be merged into one project (the absolute and drive-qualified shapes share the same fallback basename and would collide).
- Added six new gate methods to `tests/test_output_layout_docs_gate.py`: three real-build refusal assertions (exit code, fallback file set, verbatim warning text), one parent-directory escape-guard assertion, one real-build collision-abort assertion reusing the EXISTING `tests/fixtures/bld03_self_collision_gate/` fixture (no fourth copy), and two prose-match assertions binding the published text to the same measured fragments.
- Zero lines changed under `typsphinx/`; the existing collision gate modules (`test_typst_documents_collision_gate.py`, `test_builder_output_stem.py`) and the reused `bld03_self_collision_gate` fixture are byte-unchanged.

## Task Commits

Each task was committed atomically:

1. **Task 1: The three refusal shapes — fixture, build, warning text, page** - `cae8d051` (feat)
2. **Task 2: The collision abort — reuse the Phase 47 fixture, publish the contract** - `03e16b51` (feat)

**Plan metadata:** (this commit)

## Files Created/Modified

- `docs/source/user_guide/output_layout.rst` - Added "Targets that are refused" and "Targets That Stop the Build" sections
- `tests/test_output_layout_docs_gate.py` - Added `REFUSED_PARENT_FIXTURE_DIR`, `REFUSED_ABSOLUTE_FIXTURE_DIR`, `REFUSED_DRIVE_FIXTURE_DIR`, `SELF_COLLISION_FIXTURE_DIR`, `REFUSAL_WARNING_FRAGMENT`, `COLLISION_ERROR_FRAGMENT` constants and six new test methods
- `tests/fixtures/output_layout_refused_parent_gate/conf.py` - Parent-traversal refusal fixture config (`"../escape"`)
- `tests/fixtures/output_layout_refused_parent_gate/index.rst` - Parent-traversal fixture source
- `tests/fixtures/output_layout_refused_absolute_gate/conf.py` - Absolute-target refusal fixture config (`"/abs/manual"`)
- `tests/fixtures/output_layout_refused_absolute_gate/index.rst` - Absolute-target fixture source
- `tests/fixtures/output_layout_refused_drive_gate/conf.py` - Drive-qualified refusal fixture config (`"C:manual"`)
- `tests/fixtures/output_layout_refused_drive_gate/index.rst` - Drive-qualified fixture source

## Decisions Made

- Reworded the three new fixtures' header comments and the new test module's `REFUSAL_WARNING_FRAGMENT` comment to avoid the literal substrings `typst_documents` (beyond the one real assignment line) and `_resolve_target_stem` / `_escapes_outdir` / `_is_drive_qualified`, because the plan's own Task 1 acceptance criteria grep for exactly those counts (1 per fixture, 0 in the test module). Caught and fixed before the Task 1 commit — no separate deviation-fix commit needed.
- Verified the collision-abort literal block against a real build of the reused `bld03_self_collision_gate` fixture (`uv run python -m sphinx -b typst tests/fixtures/bld03_self_collision_gate <tmp>`) before writing it into the page, rather than transcribing `51-RESEARCH.md`'s summary of the message shape. The measured text matched the page's draft on the first build, so no rewrite was needed.

## Deviations from Plan

None — plan executed exactly as written. Both self-caught wording issues above were caught and fixed before their respective task commits.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `output_layout.rst` now covers both target-failure modes (refused-with-fallback, refused-outright) alongside Wave 1's wrapper/content split and worked examples. 51-04 and 51-05 add the remaining prose surfaces (other User Guide pages, README/examples) and do not need to touch this page further per the wave's scope fence.
- `tests/test_output_layout_docs_gate.py` now has 10 tests (up from 4), all real-build, none skipping, zero `typst-py` dependency (D-12).
- Full suite verified green: `uv run python -m pytest -m "not slow" -q` → 1098 passed, 73 deselected. `black --check` clean on both touched files (after one `black` reformat pass on the test module). `mypy typsphinx/` clean (unaffected — zero lines changed under `typsphinx/`).

## Self-Check: PASSED

All created files confirmed present on disk (three fixture `conf.py`/`index.rst` pairs, this SUMMARY.md). Both task commits (`cae8d051`, `03e16b51`) confirmed present in `git log`.

---
*Phase: 51-two-layer-output-documentation*
*Completed: 2026-08-15*
