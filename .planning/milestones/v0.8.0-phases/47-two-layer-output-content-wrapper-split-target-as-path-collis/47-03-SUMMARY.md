---
phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis
plan: 03
subsystem: infra
tags: [sphinx, typst, typst-py, path-security, pytest]

requires:
  - phase: 47-02
    provides: "typsphinx.builder._escapes_outdir() -- the OUT-02-only escape guard split out of the old four-term is_guarded expression; the content/wrapper split _resolve_output_stem() and _wrapper_output_relpath() build on"
provides:
  - "tests/test_builder_output_stem.py -- OUT-01's separator-membership reversal expectations (posix/backslash path-bearing targets resolve as-is, no warning), OUT-02's three escape-shape guard tests kept verbatim as regression tests, and a wrapper-vs-content path test replacing the two old _directory_preserving_relpath tests"
  - "tests/test_out02_escape_target_gate.py + tests/fixtures/out02_escape_target_gate/ -- a real-sphinx-build, real-subprocess gate proving all three OUT-02 escape shapes (traversal/absolute/drive-qualified) are refused with a warning AND an outdir-containment proof (every written file resolves under the build directory), one fixture serving all three shapes via TYPSPHINX_ESCAPE_SHAPE"
  - "typsphinx.builder._is_drive_qualified() -- the single, now-unduplicated drive-letter detection predicate both _escapes_outdir() and _resolve_output_stem() call"
  - "typsphinx.builder._resolve_output_stem() OUT-01 backslash normalization and the new empty-trailing-segment fallback (a path-bearing, non-escaping target whose basename is itself empty falls back to the docname with the standard single warning)"
  - "47-RED-EVIDENCE.md 'A3: second path-rejection site search' -- RESEARCH.md's Assumptions-Log A3 closed by a real repo-wide grep, concluding no second independent path-rejection site exists"
affects: [47-09]

actuals:
  tokens: 9300
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "A path-bearing typst_documents target is normalized to posix-style separators once, up front, in _resolve_output_stem() -- so a Windows-authored backslash target and its forward-slash equivalent always resolve to byte-identical output paths, regardless of the running platform"
    - "Drive-letter detection is a single shared predicate (_is_drive_qualified()) called from both the accept/reject site (_escapes_outdir()) and its own downstream fallback-basename computation, rather than the same string-shape test being re-derived inline in two places"
    - "A real-sphinx-build security gate parametrizes one fixture directory over an environment variable (TYPSPHINX_ESCAPE_SHAPE) read by conf.py, rather than maintaining three near-duplicate fixture directories -- and asserts containment by resolving every written file against the resolved build directory, not by trusting the warning text alone"

key-files:
  created:
    - tests/test_out02_escape_target_gate.py
    - tests/fixtures/out02_escape_target_gate/conf.py
    - tests/fixtures/out02_escape_target_gate/index.rst
  modified:
    - tests/test_builder_output_stem.py
    - typsphinx/builder.py
    - .planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/47-RED-EVIDENCE.md

key-decisions:
  - "Task 1's <files> officially names only tests/test_builder_output_stem.py, but making the plan's own acceptance criteria pass (the full module green apart from the two CR-01 tests) required a Rule 1 bug fix in typsphinx/builder.py: 47-02's OUT-01 rewrite left a Windows-authored backslash-separated stem unnormalized (diverging from its forward-slash equivalent) and left a path-bearing target whose final path segment is itself empty (a trailing separator, e.g. \"sub/manual.typ/\") falling through unguarded to a nonsensical write path instead of the standard single-warning docname fallback. Both are in the plan's own overall files_modified scope (typsphinx/builder.py is listed at the plan level), so this was fixed rather than left as a plan-authoring gap."
  - "The caplog-based test_resolve_output_stem_warns_on_path_bearing_target was renamed and inverted (to test_resolve_output_stem_emits_no_warning_for_path_bearing_target) alongside the two explicitly-named separator tests, even though the plan's action text names only 'the two separator tests' by description -- this third test pinned the exact same D-06/D-07 warning behavior via caplog instead of a return-value assertion, was one of the four originally-failing tests, and had no other instruction under which it could legitimately keep passing while preserving the reversed behavior."
  - "Task 3's repo-wide grep surfaced one literal (non-independent) duplication of the drive-letter idiom inside typsphinx/builder.py -- extracted into a shared _is_drive_qualified() helper. This was not a second, independently-diverging accept/reject site (the duplicate only ran downstream of _escapes_outdir()'s own decision), so no new 'the two sites agree' unit test was added per the task's own conditional instruction; the existing 41-test regression suite re-passing after the extraction is the evidence the refactor preserved behavior."

patterns-established: []

requirements-completed: [OUT-01, OUT-02]

coverage:
  - id: D1
    description: "OUT-01: a POSIX- or backslash-separator-bearing typst_documents target resolves exactly where written (normalized to posix-style separators), with no warning -- the separator-membership guard Phase 44's D-06/D-07 imposed is reversed"
    requirement: "OUT-01"
    verification:
      - kind: unit
        ref: "tests/test_builder_output_stem.py::test_resolve_output_stem_resolves_posix_path_bearing_target"
        status: pass
      - kind: unit
        ref: "tests/test_builder_output_stem.py::test_resolve_output_stem_normalizes_backslash_path_bearing_target"
        status: pass
      - kind: unit
        ref: "tests/test_builder_output_stem.py::test_resolve_output_stem_emits_no_warning_for_path_bearing_target"
        status: pass
    human_judgment: false
  - id: D2
    description: "OUT-01: a nested docname's WRAPPER path is no longer force-relocated into that docname's own directory, while its CONTENT path stays unconditionally docname-derived regardless of the wrapper's target"
    requirement: "OUT-01"
    verification:
      - kind: unit
        ref: "tests/test_builder_output_stem.py::test_wrapper_path_ignores_docname_directory_but_content_path_does_not"
        status: pass
    human_judgment: false
  - id: D3
    description: "OUT-02: the three escape-shaped terms (parent traversal, absolute path, drive-qualified path) are still refused with a basename fallback -- kept verbatim as OUT-02 regression tests"
    requirement: "OUT-02"
    verification:
      - kind: unit
        ref: "tests/test_builder_output_stem.py::test_resolve_output_stem_guards_parent_traversal"
        status: pass
      - kind: unit
        ref: "tests/test_builder_output_stem.py::test_resolve_output_stem_guards_absolute_target"
        status: pass
      - kind: unit
        ref: "tests/test_builder_output_stem.py::test_resolve_output_stem_guards_drive_qualified_target"
        status: pass
    human_judgment: false
  - id: D4
    description: "OUT-02: each of the three escape shapes is refused in a real sphinx-build with a warning naming the offending target AND an outdir-containment proof -- every regular file under the build directory resolves under the resolved build directory, and no escape.typ leaks to the build directory's parent"
    requirement: "OUT-02"
    verification:
      - kind: integration
        ref: "tests/test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof[traversal]"
        status: pass
      - kind: integration
        ref: "tests/test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof[absolute]"
        status: pass
      - kind: integration
        ref: "tests/test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof[drive]"
        status: pass
    human_judgment: false
  - id: D5
    description: "RESEARCH.md Assumptions-Log A3 closed by measurement: a repo-wide grep over typsphinx/ for os.sep/os.altsep/isabs/normpath/relpath/basename/the drive-letter idiom found no second, independent path-rejection site for a typst_documents target string; the one literal (non-independent) duplication found (the drive-letter idiom) was extracted into a single shared helper"
    requirement: null
    verification:
      - kind: other
        ref: ".planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/47-RED-EVIDENCE.md 'A3: second path-rejection site search' (grep commands + raw output recorded verbatim)"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-08-11
status: complete
---

# Phase 47 Plan 03: OUT-01/OUT-02 Unit and Real-Build Gate Summary

**Inverted `tests/test_builder_output_stem.py`'s separator-guard expectations for OUT-01's deliberate reversal of Phase 44's D-05/D-06/D-07, kept OUT-02's three escape-shape guards as pinned regression tests, added a real-`sphinx-build` `tests/test_out02_escape_target_gate.py` proving all three escape shapes stay contained inside `outdir`, and closed RESEARCH.md's Assumptions-Log A3 by a real repo-wide grep that found no second independent path-rejection site.**

## Performance

- **Duration:** ~55 min
- **Tasks:** 3
- **Files modified:** 6 (1 production module, 2 test modules, 2 fixture files, 1 planning-evidence file)

## Accomplishments

- `tests/test_builder_output_stem.py`: renamed and inverted the two separator-guard tests (`test_resolve_output_stem_guards_posix_path_separator` -> `test_resolve_output_stem_resolves_posix_path_bearing_target`, `test_resolve_output_stem_guards_backslash_path_separator` -> `test_resolve_output_stem_normalizes_backslash_path_bearing_target`) plus the caplog-based warning test (`test_resolve_output_stem_warns_on_path_bearing_target` -> `test_resolve_output_stem_emits_no_warning_for_path_bearing_target`), each now asserting a path-bearing, non-escaping target resolves exactly where written with no warning.
- Kept the three OUT-02 escape-shape tests (`test_resolve_output_stem_guards_parent_traversal`, `test_resolve_output_stem_guards_absolute_target`, `test_resolve_output_stem_guards_drive_qualified_target`) verbatim, each carrying a new docstring line recording that a still-passing assertion here is OUT-02 confirming evidence per RESEARCH.md's own warning sign.
- Replaced the two `_directory_preserving_relpath` unit tests with one (`test_wrapper_path_ignores_docname_directory_but_content_path_does_not`) asserting a nested docname's WRAPPER path resolves at the output root (not force-relocated into the docname's own directory) while the same docname's CONTENT path stays unconditionally docname-derived.
- `typsphinx/builder.py`: `_resolve_output_stem()` now normalizes a path-bearing target's backslashes to posix-style separators up front (so `"sub\\manual.typ"` and `"sub/manual.typ"` resolve to the byte-identical `"sub/manual"`), and gained a new fallback for a path-bearing, non-escaping target whose final path segment is itself empty (a trailing separator, e.g. `"sub/manual.typ/"`) -- it now falls back to the docname with the standard single "empty target" warning instead of writing a nonsensical path.
- Added `tests/test_out02_escape_target_gate.py` and `tests/fixtures/out02_escape_target_gate/`, a real-`sphinx-build`-subprocess, parametrized-over-shape gate proving each of the three OUT-02 escape shapes (parent traversal, absolute, drive-qualified) exits 0, warns naming the offending target, writes the basename fallback inside the build directory, and -- the containment proof a warning-text assertion alone cannot give -- that every regular file under the build directory resolves, via `Path.resolve()`, under the resolved build directory.
- Closed RESEARCH.md's Assumptions-Log A3 in `47-RED-EVIDENCE.md` with a real repo-wide grep over `typsphinx/` for `os.sep`, `os.altsep`, `isabs`, `normpath`, `relpath`, `basename`, and the drive-letter detection idiom. Conclusion: no second, independent path-rejection site exists for a `typst_documents` target string. The grep did surface one literal (non-independent) duplication of the drive-letter idiom inside `builder.py`, extracted into a single shared `_is_drive_qualified()` helper both `_escapes_outdir()` and `_resolve_output_stem()` now call.

## Task Commits

1. **Task 1: Move the OUT-01 expectations and keep the OUT-02 guard tests verbatim** - `b569721` (feat) - `tests/test_builder_output_stem.py`, `typsphinx/builder.py`
2. **Task 2: Add a real-sphinx-build gate with one fixture per escape shape and an outdir-containment assertion** - `c889177` (test) - `tests/test_out02_escape_target_gate.py`, `tests/fixtures/out02_escape_target_gate/conf.py`, `tests/fixtures/out02_escape_target_gate/index.rst`
3. **Task 3: Close RESEARCH.md Assumptions-Log A3 by measurement** - `41dd456` (refactor) - `typsphinx/builder.py`, `.planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/47-RED-EVIDENCE.md`

## Files Created/Modified

- `tests/test_builder_output_stem.py` - inverted separator-guard expectations for OUT-01, kept OUT-02 escape tests verbatim with confirming-evidence docstrings, replaced two `_directory_preserving_relpath` tests with one wrapper-vs-content path test
- `typsphinx/builder.py` - `_resolve_output_stem()` backslash normalization and empty-trailing-segment fallback (Task 1); `_is_drive_qualified()` extraction, both call sites routed through it (Task 3)
- `tests/test_out02_escape_target_gate.py` - new real-sphinx-build OUT-02 containment gate, parametrized over the three escape shapes
- `tests/fixtures/out02_escape_target_gate/conf.py` - new fixture, `TYPSPHINX_ESCAPE_SHAPE`-driven target selection
- `tests/fixtures/out02_escape_target_gate/index.rst` - new fixture body carrying `ESCAPE-GATE-MARKER`
- `.planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/47-RED-EVIDENCE.md` - new "A3: second path-rejection site search" section with grep commands, raw output, and the closed conclusion

## Decisions Made

- Rule 1 bug fix in `typsphinx/builder.py` beyond Task 1's own `<files>` list (test file only), justified because `typsphinx/builder.py` is in the PLAN's own `files_modified` scope and the fix was required for Task 1's own acceptance criteria (the full module green apart from the two CR-01 tests) to be achievable: backslash normalization and the empty-trailing-segment fallback -- see key-decisions above for the full rationale.
- Renamed/inverted the caplog-based `test_resolve_output_stem_warns_on_path_bearing_target` alongside the two explicitly plan-named separator tests, since it pinned the identical D-06/D-07 warning behavior via a different assertion style and was one of the four originally-failing tests with no other legitimate path to green.
- Extracted `_is_drive_qualified()` as a Task 3 refactor even though the duplication found was not an independently-diverging decision site, because Task 3's own `<done>` criterion states "OUT-02 has exactly one rule in exactly one place" -- literal duplication of the same string-shape test in two locations was worth closing as a latent-divergence risk, not just a functional one.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `_resolve_output_stem()` left a Windows-authored backslash target unnormalized and a trailing-separator target unguarded**
- **Found during:** Task 1 (running `uv run pytest tests/test_builder_output_stem.py -q` after moving the test expectations, before touching production code)
- **Issue:** 47-02's OUT-01 rewrite reversed the separator-membership guard but left two gaps: (a) a backslash-separated stem (`"sub\\manual"`) was returned as-is, diverging byte-for-byte from its forward-slash equivalent (`"sub/manual"`) for no OUT-01-motivated reason; (b) a path-bearing, non-escaping stem whose final path segment is itself empty (a trailing separator, e.g. `"sub/manual.typ/"`) fell through `_escapes_outdir()`'s False branch unguarded, producing a nonsensical write path (a file literally named `.typ` inside a directory named `manual.typ`) instead of the standard docname-fallback-with-warning every other degenerate target gets.
- **Fix:** Added an unconditional `stem = stem.replace("\\", "/")` normalization immediately after suffix-stripping, and a new `elif "/" in stem and not path.basename(stem).strip():` branch that routes a trailing-separator stem to the same single "empty typst_documents target name" warning + docname fallback the empty/whitespace/bare-`.typ` cases already use.
- **Files modified:** `typsphinx/builder.py`
- **Verification:** `uv run pytest tests/test_builder_output_stem.py -q` (26 passed, 0 failed), `uv run black --check .`, `uv run mypy typsphinx/`, `python -m doctest typsphinx/builder.py` (unaffected, 4/4 `_escapes_outdir` doctests still pass).
- **Committed in:** `b569721` (Task 1 commit)

**2. [Rule 1 - Bug/Cleanup] Drive-letter detection idiom was written twice in `typsphinx/builder.py`**
- **Found during:** Task 3 (the repo-wide `isalpha()` grep RESEARCH.md's Assumptions-Log A3 requires)
- **Issue:** `is_drive_qualified = len(stem) >= 2 and stem[0].isalpha() and stem[1] == ":"` was computed inline both inside `_escapes_outdir()` (the real accept/reject decision) and again, verbatim, inside `_resolve_output_stem()` (used only downstream, to decide whether to strip a two-character drive prefix from the fallback basename -- never itself deciding acceptance, since it only runs after `_escapes_outdir()` has already returned `True`). Not an independently-diverging decision site, but literal duplication of the same string-shape test, in tension with Task 3's own `<done>` criterion ("OUT-02 has exactly one rule in exactly one place").
- **Fix:** Extracted a new module-level `_is_drive_qualified(stem)` function (with its own doctest examples), and both call sites now delegate to it instead of each computing the check inline.
- **Files modified:** `typsphinx/builder.py`
- **Verification:** `uv run pytest tests/test_builder_output_stem.py tests/test_out02_escape_target_gate.py tests/test_two_layer_output_gate.py -q` (41 passed), `uv run black --check .`, `uv run mypy typsphinx/`; `git diff --stat` confirms only `typsphinx/builder.py` and `47-RED-EVIDENCE.md` changed for this task, with no hunk touching `_track_image` or `copy_image_files` (the plan's own scope-fence check).
- **Committed in:** `41dd456` (Task 3 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1 bugs/cleanup). Both were required for this plan's own designated acceptance criteria and `<done>` wording to hold, not scope creep -- neither touches image path handling (Phase 50's territory) or any file outside the plan's declared `files_modified`.

## Issues Encountered

None beyond the two auto-fixed deviations above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `_is_drive_qualified()`, the OUT-01 backslash-normalization behavior, and the empty-trailing-segment fallback in `typsphinx/builder.py` are the load-bearing new/changed symbols in this plan's own scope; later plans should build on them, not re-derive.
- `tests/test_builder_output_stem.py tests/test_out02_escape_target_gate.py` (29 tests) and `tests/test_two_layer_output_gate.py` (12 tests) all pass together (41 passed), matching this plan's own `<verification>` command exactly.
- RESEARCH.md's Assumptions-Log A3 is closed; no further OUT-02 grep work is owed forward.
- Per this plan's own scope fence, the full `uv run pytest` suite remains KNOWINGLY RED outside this plan's own designated files (~87 fixture projects still configure a self-colliding target; ~68 modules still assert the pre-split file shape) -- that is plans 47-04 through 47-08's job, and plan 47-09 is the phase's full-suite-green gate. This plan did not attempt to fix anything outside `tests/test_builder_output_stem.py`, `tests/test_out02_escape_target_gate.py`, `tests/fixtures/out02_escape_target_gate/`, and `typsphinx/builder.py`. Measured full-suite result after this plan (`uv run pytest -q`, ~206s): **223 failed, 681 passed, 5 skipped, 7 xfailed, 101 errors** -- down from 47-02-SUMMARY.md's recorded baseline of 227 failed / 672 passed, a delta of exactly -4 failed / +9 passed, matching this plan's own scope (the 4 tests it fixed in `tests/test_builder_output_stem.py` plus the 3 new `tests/test_out02_escape_target_gate.py` cases, net of the two-tests-merged-into-one rename in the same file). No new failures were introduced anywhere in the corpus.
- `ruff check .` could not run in this sandbox (pre-existing NixOS generic-linux-ELF limitation, unrelated to this plan, tracked separately per earlier phases' own notes); `black --check .` and `mypy typsphinx/` both pass and take lint/type authority per CI.
- No blockers for downstream plans.

## Self-Check: PASSED

All modified/created files verified present on disk. All three task commits (`b569721`, `c889177`, `41dd456`) verified present in `git log --oneline --all`.

---
*Phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis*
*Completed: 2026-08-11*
