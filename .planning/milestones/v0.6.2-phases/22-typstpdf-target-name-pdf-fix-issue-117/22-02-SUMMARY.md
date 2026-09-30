---
phase: 22-typstpdf-target-name-pdf-fix-issue-117
plan: 02
subsystem: testing
tags: [render-gate, typstpdf, gate-01, issue-117, pytest]

# Dependency graph
requires:
  - phase: 22-typstpdf-target-name-pdf-fix-issue-117 (plan 01)
    provides: "TypstBuilder._resolve_output_stem and the three rewired output-path sites"
provides:
  - "tests/test_target_name_render_gate.py -- real -b typstpdf render gate proving typst_documents' target name governs both .typ and .pdf output filenames"
affects: [22.1-typstpdf-compile-root-alignment]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "GATE-01 render gate: real -b typstpdf subprocess build (sys.executable -m sphinx, never a PATH-resolved sphinx-build binary) with bidirectional presence/absence assertions, mirroring tests/test_cross_doc_label_namespace_render_gate.py"

key-files:
  created:
    - tests/test_target_name_render_gate.py
  modified: []

key-decisions:
  - "Rephrased the analog's docstring/error-message mentions of the literal token 'sphinx-build' (e.g. 'Run sphinx-build -b typstpdf') to equivalent prose ('Run a -b typstpdf Sphinx build', 'PATH-resolved build console-script') so the plan's acceptance criterion `grep -c 'sphinx-build' == 0` is satisfied, while still preserving the sys.executable-vs-PATH-resolved-binary rationale the analog documents. The analog file itself contains the literal token 3 times, so a byte-identical structural mirror would have failed this specific grep criterion."

requirements-completed: [PDF-01]

coverage:
  - id: D1
    description: "Real -b typstpdf render gate proves typst_documents target name ('output.typ') governs both emitted .typ and .pdf filenames, and that the docname-named pair (index.typ/index.pdf) is absent (D-08 clean-break)"
    requirement: "PDF-01"
    verification:
      - kind: integration
        ref: "tests/test_target_name_render_gate.py::TestTargetNameRenderGate::test_typstpdf_emits_target_named_artifacts_and_not_docname_named"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-07-21
status: complete
---

# Phase 22 Plan 02: Target-Name Render Gate Summary

**Real `-b typstpdf` compile gate (`tests/test_target_name_render_gate.py`) driving `tests/roots/test-basic`'s `typst_documents = [("index", "output.typ", ...)]` config, proving `output.typ`/`output.pdf` are emitted and `index.typ`/`index.pdf` are NOT — the automated GATE-01 proof for Issue #117 / PDF-01.**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-07-21T13:40:00Z
- **Completed:** 2026-07-21T13:52:11Z
- **Tasks:** 1
- **Files modified:** 1 (created)

## Accomplishments
- New `tests/test_target_name_render_gate.py` module, the first consumer of `tests/roots/test-basic`, structurally mirroring `tests/test_cross_doc_label_namespace_render_gate.py`'s established GATE-01 house style (module docstring stating the bug/fix, `TYPST_AVAILABLE` skip-guard, `sys.executable -m sphinx` subprocess driver, banner-commented test-body concerns)
- Drives the build through `-b typstpdf` (not `-b typst`), since the `.pdf` half of the Issue #117 contract only materializes inside `TypstPDFBuilder.finish()`'s real `typst.compile()` call
- Asserts the full bidirectional contract in one test: `output.typ`/`output.pdf` PRESENT (non-empty, PDF-magic-byte validated) AND `index.typ`/`index.pdf` ABSENT — the D-08 clean-break requirement that makes the gate fail against the pre-fix builder on both counts
- Guards against `TypstPDFBuilder.finish()`'s log-not-raise failure mode by asserting `"Typst compilation failed"` and `"Master document not found"` are absent from stderr, in addition to `returncode == 0`
- `tests/roots/test-basic/` (the fixture under test) is untouched -- confirmed via `git status --porcelain tests/roots/` producing no output

## Task Commits

Each task was committed atomically:

1. **Task 1: Create the target-name render gate driven by tests/roots/test-basic** - `a7eef36` (test)

_No plan-metadata commit in worktree mode -- SUMMARY.md is committed separately per the parallel-executor protocol; the orchestrator handles STATE.md/ROADMAP.md centrally after the wave merges._

## Files Created/Modified
- `tests/test_target_name_render_gate.py` - new module: `target_name_render_gate_source_dir` and `temp_build_dir` fixtures, `_run_sphinx_build_typstpdf` subprocess helper, `TestTargetNameRenderGate` class with one real-compile test method proving PDF-01's target-name contract

## Decisions Made
- Rephrased the mandated structural-mirror docstrings/error-messages to avoid the literal token `sphinx-build` (used equivalent prose like "a -b typstpdf Sphinx build" and "PATH-resolved build console-script" instead), because the plan's own acceptance criterion requires `grep -c 'sphinx-build' == 0` while the analog file being mirrored contains that literal token 3 times. This is a plan-authoring tension (read_first mandates a structural mirror of a file that itself fails the grep bar the acceptance criteria set); resolved in favor of satisfying the explicit, machine-checkable acceptance criterion while preserving the same explanatory content and the `sys.executable -m sphinx` invocation itself (verified via `grep -c 'sys.executable' == 2`).

## Deviations from Plan

None requiring the Rule 1-4 framework -- see "Decisions Made" above for a plan-internal acceptance-criteria/read_first wording tension that was resolved via rephrasing (no code-behavior change, no scope change).

## Issues Encountered

None. `uv run pytest tests/test_target_name_render_gate.py -q` passes (1 passed) in the per-worktree-provisioned venv. `uv run black --check` passes. `ruff check` had to run via `nix-shell -p ruff --run "ruff check ..."` (documented NixOS-sandbox dynamically-linked-binary limitation, matching Plan 01's summary) and passed with no findings. The broader fast-suite run (`uv run python -m pytest -m "not slow" -q` with the four documented pre-existing environmentally-failing integration modules excluded) shows 470 passed, 3 failed -- the 3 failures are in `tests/test_examples_basic.py` (uses `uv run sphinx-build` internally, a separate pre-existing NixOS PATH-resolution issue unrelated to this change) and are outside this plan's scope.

## Next Phase Readiness
- ROADMAP Phase 22 SC#1 and SC#3 are now automated by a real-compile gate; PDF-01 has both a unit-level proof (Plan 01) and a real-compile proof (this plan)
- Phase 22.1 (typstpdf compile-root alignment, PDF-02) can proceed independently
- No blockers

## Self-Check: PASSED

- FOUND: tests/test_target_name_render_gate.py
- FOUND commit: a7eef36 (test — Task 1)

---
*Phase: 22-typstpdf-target-name-pdf-fix-issue-117*
*Completed: 2026-07-21*
