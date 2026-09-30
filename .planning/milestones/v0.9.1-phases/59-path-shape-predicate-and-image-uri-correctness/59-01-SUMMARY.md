---
phase: 59-path-shape-predicate-and-image-uri-correctness
plan: 01
subsystem: builder
tags: [path-predicate, windows-path, typsphinx-builder, gate]

requires: []
provides:
  - "PATH-01 closed: _escapes_outdir() normalizes backslash-to-slash before deciding isabs/drive-qualified, matching _is_absolute_image_uri()'s idiom"
  - "59-WINDOWS-URI-EVIDENCE.md spine (Phase base SHA + PATH-01 section filled; IMG-04/IMG-06/IMG-05/IMG-07/SC#5 sections empty, for plans 02-05)"
  - "COVERAGE.md external-API declaration for the whole phase"
  - "tests/test_path_shape_predicate_gate.py — reusable direct-call + characterization test module other plans in this phase may extend"
affects: [59-02, 59-03, 59-04, 59-05]

actuals:
  tokens: 21000
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns:
    - "normalize-then-decide: bind one `normalized = stem.replace(\"\\\\\", \"/\")` local, pass it to every shape-decision term instead of the raw string"
    - "two-tree characterization: a permanent parametrized test proves post-fix call-site classification; a temporary git checkout + captured transcript in an evidence file proves before-and-after equality (D-09/D-10)"

key-files:
  created:
    - tests/test_path_shape_predicate_gate.py
    - .planning/phases/59-path-shape-predicate-and-image-uri-correctness/59-WINDOWS-URI-EVIDENCE.md
    - .planning/phases/59-path-shape-predicate-and-image-uri-correctness/COVERAGE.md
  modified:
    - typsphinx/builder.py

key-decisions:
  - "PATH-01's RED gate calls _escapes_outdir() directly (never through _resolve_target_stem() or _track_image()), per ROADMAP constraint 8 -- both call sites pre-normalize or always carry '..' before reaching the predicate, so a call-site-routed gate would be tautologically green before and after"
  - "The characterization pin's five-shape table and expected _resolve_target_stem() outputs were verified empirically (a standalone Python script against a real TypstBuilder/temp_sphinx_app) before being encoded as test assertions, not derived by hand-tracing alone"

requirements-completed: [PATH-01]

coverage:
  - id: D1
    description: "_escapes_outdir() classifies the driveless-absolute and UNC Windows-shaped stems as escaping outdir (True), where it previously returned False"
    requirement: "PATH-01"
    verification:
      - kind: unit
        ref: "tests/test_path_shape_predicate_gate.py::TestEscapesOutdirDirectCall::test_escapes_outdir_direct_driveless_absolute_is_true"
        status: pass
      - kind: unit
        ref: "tests/test_path_shape_predicate_gate.py::TestEscapesOutdirDirectCall::test_escapes_outdir_direct_unc_is_true"
        status: pass
    human_judgment: false
  - id: D2
    description: "The pre-fix False for both shapes is recorded verbatim in 59-WINDOWS-URI-EVIDENCE.md, captured before typsphinx/builder.py was edited"
    requirement: "PATH-01"
    verification:
      - kind: other
        ref: "59-WINDOWS-URI-EVIDENCE.md § PATH-01 ### RED (pre-fix, direct call) — verbatim 2-failure pytest transcript"
        status: pass
    human_judgment: false
  - id: D3
    description: "_resolve_target_stem() and _track_image() classify all five documented shapes identically before and after the fix (byte-identical two-tree measurement)"
    requirement: "PATH-01"
    verification:
      - kind: unit
        ref: "tests/test_path_shape_predicate_gate.py::TestEscapesOutdirCallSiteCharacterization (10 parametrized tests)"
        status: pass
      - kind: other
        ref: "59-WINDOWS-URI-EVIDENCE.md § PATH-01 ### Characterization: byte-identical at both call sites — pre-fix and post-fix transcripts, both 12 passed / 2 deselected"
        status: pass
    human_judgment: false
  - id: D4
    description: "Empty and single-component stems, and Unicode NFC/NFD normalization-form variants, all classify False -- unchanged edge behavior"
    requirement: "PATH-01"
    verification:
      - kind: unit
        ref: "tests/test_path_shape_predicate_gate.py::TestEscapesOutdirEdgeShapes (2 tests)"
        status: pass
    human_judgment: false

duration: 26min
completed: 2026-08-29
status: complete
---

# Phase 59 Plan 01: PATH-01 — `_escapes_outdir()` Normalize-Then-Decide Summary

**`_escapes_outdir()` now reads a backslash-normalized string for its `isabs`/drive-qualified terms, matching `_is_absolute_image_uri()`'s already-shipped idiom, with a two-tree measurement proving both production call sites classify every shape identically before and after.**

## Performance

- **Duration:** ~26 min
- **Started:** ~2026-08-28T15:54:00Z (approximate — venv provisioning + context reading)
- **Completed:** 2026-08-28T16:20:52Z
- **Tasks:** 3 (tracer + auto/tdd + auto)
- **Files modified:** 4 (1 product file, 3 new files)

## Accomplishments
- `_escapes_outdir(r"\manuals\guide")` and `_escapes_outdir(r"\\srv\share\g")` now both return `True` (were `False`) — the driveless-absolute and UNC Windows-shaped stems are correctly refused as escaping outdir
- The pre-fix `False` for both shapes recorded verbatim in `59-WINDOWS-URI-EVIDENCE.md`, captured before `typsphinx/builder.py` was touched (RED-first, ROADMAP constraint 1)
- A two-tree measurement (temporary `git checkout <PHASE_BASE_SHA> -- typsphinx/builder.py`, run, restore, re-run) proves `_resolve_target_stem()` and `_track_image()` classify all five documented shapes byte-identically before and after the fix — the "hardening changed no live behaviour" claim is now evidenced, not asserted
- `59-WINDOWS-URI-EVIDENCE.md` created as the phase's shared evidence spine (Phase base SHA `ec6bd3a4714a578379ee45e02295abc31fdd8fe3`, `## PATH-01` filled; the four other sections left empty for plans 02–05) and `COVERAGE.md` created as the phase's external-API coverage declaration

## Task Commits

Each task was committed atomically:

1. **Task 1: Record the phase base SHA and PATH-01's verbatim RED** — `5b5557d7` (test) + `2b5dda3e` (fix — see Deviations)
2. **Task 2: Rewrite `_escapes_outdir()` to normalize first, then decide** — `1cc6c54f` (feat, tdd)
3. **Task 3: Characterization pin at both call sites + two-tree measurement** — `2cae2b36` (test)

_Task 2 is `tdd="true"`; its `<behavior>` block was verified inline (`e(r'\manuals\guide'), e(r'\\srv\share\g'), e('manuals/guide'), e(''), e('../escape')` → `True True False False True`) and via `python -m doctest typsphinx/builder.py` (exit 0) rather than a separate RED/GREEN commit pair, because the plan's own task-1/task-3 split already carries the RED-then-fix structure ROADMAP constraint 1 requires — task 2's own commit lands the fix directly against task 1's already-recorded RED._

## Files Created/Modified
- `typsphinx/builder.py` — `_escapes_outdir()` rewritten to bind `normalized = stem.replace("\\", "/")` once and pass it to both `posixpath.isabs(...)` and `_is_drive_qualified(...)`; docstring `Examples:` extended with the two newly-`True` shapes
- `tests/test_path_shape_predicate_gate.py` — new module: `TestEscapesOutdirDirectCall` (RED gate, 2 tests), `TestEscapesOutdirEdgeShapes` (edge-probe direct calls, 2 tests), `TestEscapesOutdirCallSiteCharacterization` (D-10 opposite-routing pin, 10 parametrized tests) — 14 tests total
- `.planning/phases/59-path-shape-predicate-and-image-uri-correctness/59-WINDOWS-URI-EVIDENCE.md` — new: Phase base SHA, `## PATH-01`'s RED transcript and two-tree characterization transcripts; four other sections stubbed for plans 02–05
- `.planning/phases/59-path-shape-predicate-and-image-uri-correctness/COVERAGE.md` — new: external-API coverage declaration (Phase 58 precedent) for the whole phase

## Decisions Made
- PATH-01's RED gate calls `_escapes_outdir()` directly, never through `_resolve_target_stem()` or `_track_image()`, per ROADMAP constraint 8 — both call sites pre-normalize or always carry `".."` before reaching the predicate, so a call-site-routed gate would be tautologically green before and after and prove nothing
- The characterization pin's five-shape table and `_resolve_target_stem()` expected outputs (`guide`, `g`, `manual`, `manual`, `manuals/guide`) were verified empirically against a real `TypstBuilder`/`temp_sphinx_app` instance in a standalone script before being encoded as test assertions — not derived by hand-tracing the source alone

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Task 1's own gate docstring tripped its own acceptance criterion**
- **Found during:** Task 1, immediately after committing `5b5557d7`
- **Issue:** `tests/test_path_shape_predicate_gate.py`'s module docstring named `TypstBuilder` in prose (explaining what the class does NOT import), which the acceptance criterion's literal `grep -c 'TypstBuilder' tests/test_path_shape_predicate_gate.py` (required to return `0` "at this point in the plan") counted as a hit
- **Fix:** Reworded the sentence to describe the same constraint ("instantiates no builder object and imports neither `_resolve_target_stem` nor `_track_image`") without the literal substring `TypstBuilder`
- **Files modified:** `tests/test_path_shape_predicate_gate.py`
- **Verification:** `grep -c 'TypstBuilder' tests/test_path_shape_predicate_gate.py` → `0`; RED gate re-confirmed still failing 1/2 under `-x` (exit 1)
- **Committed in:** `2b5dda3e`

---

**Total deviations:** 1 auto-fixed (1 bug/self-inconsistency)
**Impact on plan:** Cosmetic — a prose docstring collision with its own acceptance grep. No behavior change, no scope creep.

## Issues Encountered
- The plan's own `<verify>` command for task 1 uses `pytest ... -x`, which stops after the FIRST failure — so a literal run of that exact command shows `1 failed`, not the acceptance criterion's stated "exactly 2 failed tests". Resolved by running the identical selector WITHOUT `-x` to capture both failures in one transcript for the evidence file (both commands agree the tree is RED; the `-x` variant is what the plan's automated `<verify>` block actually checks via `! ... -x`, which only requires non-zero exit). Documented inline in the evidence file so a reader is not confused by the apparent discrepancy.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

`59-WINDOWS-URI-EVIDENCE.md` and `COVERAGE.md` are in place for plans 02–05 to append to. Plan 02 (IMG-04/IMG-06, `_track_image()`'s escape-branch key construction and `copy_image_files()`'s length bound) can proceed — it touches the same ~30-line region of `builder.py` this plan just edited, and `59-CONTEXT.md`'s ROADMAP constraint 3 already sequences it into the next wave rather than a parallel worktree against `builder.py`. No blockers.

## Self-Check: PASSED

- `tests/test_path_shape_predicate_gate.py` — FOUND
- `.planning/phases/59-path-shape-predicate-and-image-uri-correctness/59-WINDOWS-URI-EVIDENCE.md` — FOUND
- `.planning/phases/59-path-shape-predicate-and-image-uri-correctness/COVERAGE.md` — FOUND
- Commits `5b5557d7`, `2b5dda3e`, `1cc6c54f`, `2cae2b36` — all 4 FOUND in `git log --oneline --all`
- `git diff --stat ec6bd3a4714a578379ee45e02295abc31fdd8fe3..HEAD -- tests/` — one added file (`tests/test_path_shape_predicate_gate.py`, 170 insertions), zero modified lines in any pre-existing test module
- Re-ran `uv run pytest tests/test_path_shape_predicate_gate.py -q` immediately before this section: `14 passed in 0.20s`
- All `<acceptance_criteria>` across all three tasks re-verified passing at commit time (see per-task verification runs above); plan-level `<verification>` block (full suite 1451 passed/5 skipped, `black --check .` clean, `mypy typsphinx/` clean, `git diff --stat` scoped to `tests/`, evidence file contents) all re-confirmed

---
*Phase: 59-path-shape-predicate-and-image-uri-correctness*
*Completed: 2026-08-29*
