---
phase: 34-inline-math-after-text-separator-fix
plan: 01
subsystem: testing
tags: [typst, sphinx, pytest, typst-py, pypdf, render-gate, math]

requires: []
provides:
  - "GATE-01 fixture Sphinx project exercising inline math in a list item, a collapsed confval field body, a definition-list term, display math in a list item, a single-element list item, and a control top-level paragraph"
  - "tests/test_inline_math_after_text_render_gate.py covering both the mitex default and native (-D typst_use_mitex=0) emission paths"
  - "34-GATE-EVIDENCE.md with verbatim pre-fix Typst errors, a construct reproduction matrix, and a clean pre-fix full-suite baseline for Plan 03 to diff against"
affects: [34-02, 34-03]

tech-stack:
  added: []
  patterns:
    - "GATE-0x real-typst.compile() regression-gate fixture shape (fixture Sphinx project + skipif(not TYPST_AVAILABLE) test class + sys.executable -m sphinx subprocess helper), reused verbatim from tests/test_confval_field_body_render_gate.py"

key-files:
  created:
    - tests/fixtures/inline_math_after_text_render_gate/conf.py
    - tests/fixtures/inline_math_after_text_render_gate/index.rst
    - tests/test_inline_math_after_text_render_gate.py
    - .planning/phases/34-inline-math-after-text-separator-fix/34-GATE-EVIDENCE.md
  modified: []

key-decisions:
  - "Recorded a clean (zero-environmental-failure) pre-fix full-suite baseline by applying the documented .venv/bin/uv symlink fix for the NixOS stub-ld ELF hazard, rather than accepting the previously-documented ~45-test environmental-failure baseline"

patterns-established:
  - "The GATE-01 fixture drives BOTH math emission paths (mitex default, native via -D typst_use_mitex=0) from a SINGLE fixture project instead of two, since the branch selection happens downstream of the shared separator-emission code"

requirements-completed: [MATH-01]

coverage:
  - id: D1
    description: "GATE-01 fixture project and gate test module reproduce the inline-math-after-text separator fatal in a list item, a collapsed confval field body, and a definition-list term, on both the mitex and native emission paths"
    requirement: MATH-01
    verification:
      - kind: integration
        ref: "tests/test_inline_math_after_text_render_gate.py::TestInlineMathAfterTextRenderGate::test_typstpdf_separates_inline_math_mitex_path"
        status: fail
      - kind: integration
        ref: "tests/test_inline_math_after_text_render_gate.py::TestInlineMathAfterTextRenderGate::test_typstpdf_separates_inline_math_native_path"
        status: fail
    human_judgment: true
    rationale: "This plan's deliverable is a gate PROVEN RED against the unfixed translator (SC#4, D-02) — the 'fail' status above is the intended, correct outcome, not a defect. Auto-pass classifiers must not read a non-pass status here as a broken deliverable; a human (or Plan 02's own re-run) should confirm the failure is on the returncode/separator assertion, matching 34-GATE-EVIDENCE.md, before this plan is considered verified."
  - id: D2
    description: "34-GATE-EVIDENCE.md records the verbatim RED pytest failure output, verbatim Typst compile errors per construct, a construct reproduction matrix (A-F), and a pre-fix full-suite baseline for Plan 03 to diff against"
    requirement: MATH-01
    verification:
      - kind: other
        ref: "grep -cF '## RED — pre-fix run' / '## RED — verbatim Typst errors' / '## RED — construct reproduction matrix' / '## Pre-fix full-suite baseline' .planning/phases/34-inline-math-after-text-separator-fix/34-GATE-EVIDENCE.md (each returns 1)"
        status: pass
    human_judgment: false

duration: 15min
completed: 2026-07-28
status: complete
---

# Phase 34 Plan 01: GATE-01 Fixture and RED Evidence Summary

**Real-`typst.compile()` regression fixture reproducing the inline-math-after-text separator fatal in a list item, a collapsed confval field body, and a definition-list term, on both the mitex and native math paths, recorded RED against the unfixed translator**

## Performance

- **Duration:** ~15 min
- **Completed:** 2026-07-28T13:47:33Z
- **Tasks:** 3 completed
- **Files created:** 4

## Accomplishments
- Created `tests/fixtures/inline_math_after_text_render_gate/` (conf.py + index.rst) with six labelled constructs (A-F): a byte-identical top-level-paragraph control, a bullet list item, a collapsed confval field body (both the sole-math `:type:` boundary case and the prose-then-math `:default:` case), a definition-list term, display math inside a list item, and a list item whose sole content is inline math
- Created `tests/test_inline_math_after_text_render_gate.py` — two test methods driving `-b typstpdf` through `sys.executable -m sphinx`, one for the mitex default and one for the native path via `-D typst_use_mitex=0` — with exact-string separator assertions, juxtaposition/stray-operator guards, and NFKC-normalized PDF text-fidelity checks
- Recorded `34-GATE-EVIDENCE.md`: verbatim RED pytest failure output, verbatim Typst compile errors + juxtaposed `.typ` lines for constructs B/C/D/E, a full A-F construct reproduction matrix, and a pre-fix full-suite baseline (647 passed, 1 skipped, 2 intentionally-RED gate tests — zero environmental noise once the NixOS `uv` ELF shim was applied)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create the GATE-01 fixture Sphinx project** - `921f694` (test)
2. **Task 2: Create the GATE-01 gate test module (mitex + native paths)** - `26f8395` (test)
3. **Task 3: Record the RED (fail-pre-fix) run and the pre-fix full-suite baseline** - `58ae7cd` (docs)

**Plan metadata:** commit pending (this SUMMARY + final docs commit)

## Files Created/Modified
- `tests/fixtures/inline_math_after_text_render_gate/conf.py` - Fixture Sphinx config, single master document so `TypstPDFBuilder.finish()` actually compiles
- `tests/fixtures/inline_math_after_text_render_gate/index.rst` - Six labelled constructs (A-F) exercising list items, a collapsed confval field body, a definition-list term, and display math
- `tests/test_inline_math_after_text_render_gate.py` - GATE-01 test module, both mitex and native emission paths, exact-string separator assertions
- `.planning/phases/34-inline-math-after-text-separator-fix/34-GATE-EVIDENCE.md` - RED evidence record (verbatim Typst errors, construct reproduction matrix, pre-fix full-suite baseline)

## Decisions Made
- Applied the project-memory-documented `.venv/bin/uv` symlink fix (replacing the generic-linux ELF `uv` wheel `uv sync` installs into a fresh worktree venv with a symlink to the Nix-store `uv`) before running the full-suite baseline, so Plan 03's post-fix baseline diff is against a genuinely clean signal (0 environmental failures) rather than the previously-documented ~45-test NixOS-environmental noise floor.
- Derived the exact-string separator assertions for constructs B/C/D/E by tracing the concat-context and list-item separator helpers (`_emit_inline_concat_separator`, `_mark_inline_concat_content`, `self.in_list_item`/`self.list_item_needs_separator`) through the fix shape specified in 34-PATTERNS.md, then confirmed each derived literal against the real emitted `.typ` from a direct scratch build of the unfixed translator (Task 3) — all derivations matched exactly, so no assertion needed correction.

## Deviations from Plan

None - plan executed exactly as written. `typsphinx/` was not modified (`git status --porcelain typsphinx/` is empty at every task boundary).

## Issues Encountered

None. The RED run failed exactly as predicted: both test methods fail on the `result.returncode == 0` assertion with the verbatim Typst error `TypstError: expected semicolon or line break` — a real compile fatal, not a collection error, ImportError, missing fixture, or skip.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 02 has everything it needs to land the fix: the RED evidence in `34-GATE-EVIDENCE.md` shows exactly which constructs (B, C's `:default:`, D, E) reproduce the fatal and which (A control, C's `:type:` boundary, F single-element edge) do not, matching the fix-shape analysis in `34-PATTERNS.md` and `34-RESEARCH.md`.
- Plan 03's regression sweep has a clean pre-fix full-suite baseline (647 passed, 1 skipped, 0 environmentally-failing) to diff its post-fix run against — any new failure beyond the two gate tests flipping to PASS is a real regression.
- No blockers.

---
*Phase: 34-inline-math-after-text-separator-fix*
*Completed: 2026-07-28*

## Self-Check: PASSED

- FOUND: tests/fixtures/inline_math_after_text_render_gate/conf.py
- FOUND: tests/fixtures/inline_math_after_text_render_gate/index.rst
- FOUND: tests/test_inline_math_after_text_render_gate.py
- FOUND: .planning/phases/34-inline-math-after-text-separator-fix/34-GATE-EVIDENCE.md
- FOUND: commit 921f694 (Task 1)
- FOUND: commit 26f8395 (Task 2)
- FOUND: commit 58ae7cd (Task 3)
