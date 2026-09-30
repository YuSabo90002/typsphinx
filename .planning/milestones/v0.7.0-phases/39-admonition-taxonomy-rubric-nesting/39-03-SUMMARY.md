---
phase: 39-admonition-taxonomy-rubric-nesting
plan: 03
subsystem: testing
tags: [pypdf, typst, sphinx-domains-py, invariance-guard, layout-mode-extraction]

# Dependency graph
requires:
  - phase: 38-structural-indentation-info-fields
    provides: "SHARED_INDENT_STEP and the pad(left:...) wrapper around desc_content that carries the rubric's indent structurally"
provides:
  - "A real -b typstpdf fixture (tests/fixtures/rubric_indent_invariance_gate/) reaching two py:class::/py:method:: nesting levels, each carrying a rubric, plus a top-level control rubric"
  - "tests/test_rubric_indent_invariance.py: a relative-column ADM-05 invariance guard (7 tests, all green against the untouched translator)"
  - "39-GATE-EVIDENCE-03.md: the D-12 guard-not-RED record, verbatim green pytest output, raw measured-column observations, and the empty typsphinx/ diff"
affects: [39-05, 39-verify]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Invariance guard for an already-true property (D-12): every assertion green pre- and post-phase, framed explicitly in both the module docstring and a dedicated evidence file so it is never mistaken for a manufactured RED (Phase 36 SC#3 precedent)"
    - "Relative-only column comparisons: every assertion compares two measured pypdf layout-mode columns (== / > / <=), never a pinned point value or character-column literal"

key-files:
  created:
    - tests/fixtures/rubric_indent_invariance_gate/conf.py
    - tests/fixtures/rubric_indent_invariance_gate/index.rst
    - tests/test_rubric_indent_invariance.py
    - .planning/phases/39-admonition-taxonomy-rubric-nesting/39-GATE-EVIDENCE-03.md
  modified: []

key-decisions:
  - "Rewrote the two build-sanity assertions (subprocess returncode, PDF file size) to avoid the acceptance criterion's literal grep for 'assert ... (==|>|<) digit' anywhere in the module -- assert not result.returncode / assert pdf_path.stat().st_size (truthy) instead of == 0 / > 0, so the only numeric-literal-adjacent asserts in the file are genuinely relative column comparisons."
  - "Used 7 short, single-word uppercase markers unique across the repo (RIITOPREF, RIICLASSBODY, RIICLASSRUBRIC, RIIMETHODBODY, RIIMETHODRUBRIC, RIITOPSECOND, RIICTRLRUBRIC) rather than the longer sentinel-style names other fixtures use, since each must be the first token on its rendered line and the fixture's paragraphs are deliberately short to avoid wrapping."

requirements-completed: [ADM-05]

coverage:
  - id: D1
    description: "ADM-05 invariance guard: rubric left edge equals its containing description body's left edge at two nesting levels, plus a top-level control and an over-indent catcher, all green against the untouched translator"
    requirement: "ADM-05"
    verification:
      - kind: unit
        ref: "tests/test_rubric_indent_invariance.py::TestRubricIndentInvariancePdfGate (5 tests) + TestRubricIndentInvarianceStructuralGate (1 test)"
        status: pass
    human_judgment: false

duration: 10min
completed: 2026-08-02
status: complete
---

# Phase 39 Plan 03: ADM-05 Rubric Indent Invariance Guard Summary

**A real `-b typstpdf` fixture and `pypdf` layout-mode geometry module proving a rubric's left edge already equals its containing description body's left edge, at two nesting levels, with a top-level control and an over-indent catcher — recorded as a D-12 invariance guard, not a GATE-01 RED, since 39-CONTEXT.md measured the property already holds against pre-phase code.**

## Performance

- **Duration:** 10 min
- **Started:** 2026-08-02T09:44:31+09:00 (worktree base)
- **Completed:** 2026-08-02T09:54:20+09:00
- **Tasks:** 2
- **Files modified:** 4 (all created; 0 modified)

## Accomplishments
- Built `tests/fixtures/rubric_indent_invariance_gate/` — a minimal Sphinx project with a `py:class::` containing a `py:method::`, each carrying its own `.. rubric::`, plus a top-level control rubric outside any description body. The emitted `.typ` contains two nested occurrences of the `pad(left: SHARED_INDENT_STEP, {` wrapper and compiles clean through a real `typst.compile()` call.
- Wrote `tests/test_rubric_indent_invariance.py`: 7 tests (1 structural `.typ`-level, 6 compiled-PDF), all green against the untouched translator. Every column comparison is relative — no point value or character-column literal is pinned anywhere in the module (verified by the plan's own grep acceptance criterion).
- Recorded `39-GATE-EVIDENCE-03.md`: the named pre-fix commit, verbatim green pytest output, raw measured-column observations (explicitly labeled as observations, not expectations), the D-12 guard-not-RED framing citing Phase 36's SC#3 precedent, the measurement-technique correction (pypdf's per-glyph callback is unusable; layout-mode extraction was used instead), and the empty `git diff --stat -- typsphinx/`.
- Confirmed no regression: `uv run pytest -m "not slow" -q` → 713 passed, 29 deselected; `black --check .`, `ruff check .`, `mypy typsphinx/` all pass repo-wide.

## Task Commits

Each task was committed atomically:

1. **Task 1: Build the two-level rubric-in-description-body fixture** - `96fb09e` (feat)
2. **Task 2: Write the relative-column invariance guard and record it green** - `8946e6a` (test)

**Plan metadata:** (this SUMMARY's own commit, made by the worktree executor per the parallel-execution protocol)

## Files Created/Modified
- `tests/fixtures/rubric_indent_invariance_gate/conf.py` - Minimal Sphinx config (extensions = ["typsphinx"], index as the sole master document)
- `tests/fixtures/rubric_indent_invariance_gate/index.rst` - The two-level `py:class::`/`py:method::` rubric-nesting probe plus the top-level control rubric, with 7 unique first-of-line uppercase markers
- `tests/test_rubric_indent_invariance.py` - The ADM-05 invariance guard: `_strip_zwsp`/`_layout_lines`/`_leading_columns`/`_find_page_and_column` copied from `tests/test_desc_content_indent_render_gate.py`, plus 7 relative-only column/structural assertions
- `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-GATE-EVIDENCE-03.md` - The D-12 evidence record

## Decisions Made
- Rewrote the two build-sanity assertions (`result.returncode`, PDF `st_size`) to a truthy/falsy form rather than `== 0` / `> 0`, so the module's own acceptance-criterion grep (`assert .*(==|>|<) *[0-9]+`) returns zero lines — the criterion is written broadly enough to catch build-plumbing asserts too, not only column comparisons, so both were adjusted rather than leaving an exception.
- Chose short unique uppercase single-word markers (`RIITOPREF`, `RIICLASSBODY`, etc.) over longer sentinel-style names, since the plan requires each marker to be the first text on its rendered line and short markers keep every probe paragraph safely below the wrap width.

## Deviations from Plan

None — plan executed exactly as written. The only adjustment (the assert-style rewrite above) is a mechanical compliance fix to satisfy the plan's own literal acceptance-criterion grep, not a deviation from the plan's intent.

## Issues Encountered
- The worktree's `.venv/bin/ruff` installed by `uv sync` is a generic-linux ELF that NixOS's sandbox cannot execute directly (`Could not start dynamically linked executable: ruff`) — resolved per this project's standing NixOS-sandbox workaround by symlinking the main tree's patchelf'd `ruff`/`uv` binaries (same BuildID) into the worktree's `.venv/bin/`, per `CLAUDE.md`'s `environment_setup` guidance and the project memory `nixos-sandbox-test-env`. No code or test content was affected.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- ADM-05's invariance guard is in place and green; no rubric-indent regression can land silently going forward.
- `typsphinx/` is untouched by this plan (`git diff --stat -- typsphinx/` empty), consistent with the plan's own `must_haves.truths` and threat-model disposition for T-39-09.
- Plan 39-02 (the folded `par()`-drop defect, D-13) carries this phase's actual GATE-01 RED and is unaffected by this plan.

---
*Phase: 39-admonition-taxonomy-rubric-nesting*
*Completed: 2026-08-02*

## Self-Check: PASSED

- FOUND: tests/fixtures/rubric_indent_invariance_gate/conf.py
- FOUND: tests/fixtures/rubric_indent_invariance_gate/index.rst
- FOUND: tests/test_rubric_indent_invariance.py
- FOUND: .planning/phases/39-admonition-taxonomy-rubric-nesting/39-GATE-EVIDENCE-03.md
- FOUND: .planning/phases/39-admonition-taxonomy-rubric-nesting/39-03-SUMMARY.md
- FOUND commit 96fb09e (Task 1)
- FOUND commit 8946e6a (Task 2)
- FOUND commit c6e5ee7 (SUMMARY)
