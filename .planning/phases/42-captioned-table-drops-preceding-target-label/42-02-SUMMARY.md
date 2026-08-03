---
phase: 42-captioned-table-drops-preceding-target-label
plan: 02
subsystem: testing
tags: [pytest, sphinx, typst, docutils, propagatetargets, regression-gate]

requires:
  - phase: 42-01
    provides: "the table-side RED gate for the same defect class (parallel wave, no file overlap)"
provides:
  - "A dedicated figure-side fixture covering D-10's three measured shapes via standalone .. _label: target directives"
  - "A permanent 7-method regression gate (TestFigurePropagatedTargetRenderGate) proving the figure path is unaffected by the table-side defect"
  - "42-GATE-EVIDENCE-02.md discharging ROADMAP SC#2 with an in-repo measurement"
affects: [42-04, 42-06]

tech-stack:
  added: []
  patterns:
    - "Class-scoped pytest fixture (scope=\"class\") builds the fixture ONCE through -b typstpdf; each test method makes one assertion against the shared artifacts (mirrors test_signature_page_boundary_render_gate.py's pattern)."
    - "Negative-lookbehind-on-link( regex scan (`(?<!link\\()<(index:[^>]+)>`) extracts label DEFINITIONS (both the metadata(none) anchor form and the figure self-anchor postfix form) distinct from label REFERENCES, after stripping raw(\"...\") segments."

key-files:
  created:
    - tests/fixtures/figure_propagated_target_render_gate/conf.py
    - tests/fixtures/figure_propagated_target_render_gate/index.rst
    - tests/fixtures/figure_propagated_target_render_gate/image.png
    - tests/test_figure_propagated_target_render_gate.py
    - .planning/phases/42-captioned-table-drops-preceding-target-label/42-GATE-EVIDENCE-02.md
  modified: []

key-decisions:
  - "Gate is GREEN from its first run against unfixed production source (D-09) — not a RED-to-GREEN recording, because the figure path was never defective. This plan changes zero production code."
  - "Reused figure_target_caption_render_gate/'s image.png byte-for-byte but built a wholly new fixture directory and index.rst, since that fixture's :target: directive OPTION is a different docutils mechanism (reference-wrapped figure) that never invokes PropagateTargets."

patterns-established:
  - "42-GATE-EVIDENCE-NN.md convention: quote the exact ROADMAP success criterion verbatim, answer it up front, then back the answer with a live command + verbatim output taken in the executing worktree (never transcribed from CONTEXT.md/RESEARCH.md scratchpad measurements)."

requirements-completed: [TBL-03]

coverage:
  - id: D1
    description: "Figure propagated-target render-gate fixture covers D-10's three shapes (named figure, unnamed figure, figure inside a bullet-list item) via standalone target directives only, image.png byte-identical to the source fixture"
    requirement: "TBL-03"
    verification:
      - kind: integration
        ref: "uv run python -m sphinx -b typst -q -E tests/fixtures/figure_propagated_target_render_gate <build> (all three metadata(none) anchors present, exit 0)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Permanent 7-method regression gate TestFigurePropagatedTargetRenderGate, green against unfixed production source"
    requirement: "TBL-03"
    verification:
      - kind: unit
        ref: "tests/test_figure_propagated_target_render_gate.py::TestFigurePropagatedTargetRenderGate (7 tests)"
        status: pass
    human_judgment: false
  - id: D3
    description: "42-GATE-EVIDENCE-02.md answers ROADMAP SC#2 (captioned figures do NOT share the drop) with an in-repo measurement and the code-level reason (add_text gates only on in_table)"
    requirement: "TBL-03"
    verification:
      - kind: other
        ref: ".planning/phases/42-captioned-table-drops-preceding-target-label/42-GATE-EVIDENCE-02.md — grep-verified for required literals per task 3 acceptance criteria"
        status: pass
    human_judgment: false

duration: 22min
completed: 2026-08-03
status: complete
---

# Phase 42 Plan 02: Figure-Side Permanent Regression Gate + SC#2 Evidence Summary

**Added a dedicated figure-side fixture and a 7-method permanent regression gate proving the propagated-target-drop defect (TBL-03) is table-only — the figure path was already correct and stays green with zero production changes.**

## Performance

- **Duration:** ~22 min (base checkout to final task commit)
- **Started:** 2026-08-03T23:18:00+09:00 (approx., fixture directory creation)
- **Completed:** 2026-08-03T23:24:59+09:00 (final task commit)
- **Tasks:** 3
- **Files modified:** 5 (all new)

## Accomplishments
- Created `tests/fixtures/figure_propagated_target_render_gate/` — a fresh, dedicated fixture covering D-10's three measured shapes (named figure + preceding target, unnamed figure + preceding target, figure inside a bullet-list item), using only standalone `.. _label:` target directives so docutils' `PropagateTargets` transform is genuinely exercised — verified with a real `-b typst` build emitting all three `[#metadata(none) <index:...>]` anchors.
- Authored `tests/test_figure_propagated_target_render_gate.py` (`TestFigurePropagatedTargetRenderGate`, 7 test methods, one class-scoped `-b typstpdf` build): compile-clean, one test per D-10 shape, a no-duplicate-label-definition scan, a dangling-reference sweep, and a PDF magic-byte check. All 7 pass against this worktree's unfixed base commit, discharging D-09 (permanent gate) and D-10 (exactly three shapes, no fourth).
- Wrote `42-GATE-EVIDENCE-02.md`, answering ROADMAP SC#2 with a live in-repo measurement: captioned figures do NOT exhibit the propagated-target drop, because `add_text` (translator.py:423-437) gates buffer diversion on `self.in_table` alone and never consults `self.in_figure` — so `depart_figure`'s trailing `_emit_id_anchors` call is harmless despite its ordering superficially matching `depart_table`'s (the actual root cause of the table-side defect fixed in plan 42-04).

## Task Commits

Each task was committed atomically:

1. **Task 1: Create the figure propagated-target fixture covering D-10's three shapes** - `83be202` (test)
2. **Task 2: Author the permanent figure regression gate module** - `02f1b79` (test)
3. **Task 3: Record the SC#2 answer in 42-GATE-EVIDENCE-02.md** - `3b08b34` (docs)

**Plan metadata:** committed in this SUMMARY's own commit (worktree mode — orchestrator owns STATE.md/ROADMAP.md updates after merge).

_Note: Task 2 carries a `tdd="true"` attribute in the plan, but per D-09 the figure path is already correct — there is no RED phase to record, so a single `test(...)` commit (not a RED/GREEN pair) is correct per the plan's explicit instruction._

## Files Created/Modified
- `tests/fixtures/figure_propagated_target_render_gate/conf.py` - Sphinx config mirroring the paragraph-gate shape; `numfig = True` for the `:numref:` reference; module docstring states the `:target:`-option scoping trap.
- `tests/fixtures/figure_propagated_target_render_gate/index.rst` - D-10's three shapes plus a references section (`:numref:` + explicit-text `:ref:` to each target/name).
- `tests/fixtures/figure_propagated_target_render_gate/image.png` - byte-identical copy of `figure_target_caption_render_gate/image.png`.
- `tests/test_figure_propagated_target_render_gate.py` - `TestFigurePropagatedTargetRenderGate`, 7 test methods over one class-scoped build.
- `.planning/phases/42-captioned-table-drops-preceding-target-label/42-GATE-EVIDENCE-02.md` - SC#2 evidence file: question, live measurement, code-level reason, gate summary + passing output, scope note, verdict table.

## Decisions Made
- Followed D-09/D-10 exactly: the gate is a permanent forward-looking regression guard, not a RED-to-GREEN recording, since the figure path has no defect to reproduce.
- The dangling-reference sweep test (`test_no_dangling_same_document_references`) initially only matched the `[#metadata(none) <name>]` anchor form and produced two false-positive "dangling" names (`index:fig-name`, `index:fig-name-li`) because it missed the figure's own `) <label>]` self-anchor postfix form. Widened the anchor-extraction regex to the same negative-lookbehind-on-`link(` scan the duplicate-definition test uses, so both anchor forms count — auto-fixed inline per Rule 1 (bug in the test I was writing, caught before commit; no separate deviation entry needed since it never reached a commit in a broken state).

## Deviations from Plan

None - plan executed exactly as written. No production source was touched; `git status --porcelain typsphinx/` stayed empty at every task commit, matching the plan's own prohibition.

## Issues Encountered
- The worktree's `.venv/bin/ruff` (freshly `uv sync`'d) is a generic-linux ELF that fails under the NixOS stub loader (`Could not start dynamically linked executable`). The project CLAUDE.md's documented `command -v ruff` shim wasn't directly usable because `ruff` isn't on the outer shell `PATH` in this sandbox; resolved by symlinking to the main checkout's already-patched `.venv/bin/ruff` binary (same underlying build, same version 0.15.20) instead. `uv run ruff --version` and `uv run ruff check .` both confirmed working afterward. This is environment provisioning only — no code or test behavior was affected.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Plan 42-04 (the actual table-side fix, wave 2, `depends_on: ["42-01"]`) is unaffected by this plan's scope — this plan touches no production code.
- `42-GATE-EVIDENCE-02.md` is available for plan 42-06's SC#6 reconciliation pass (CHANGELOG line, SC#4 invariant sweep re-measurement over a SHA range including Phase 42).
- No blockers. All three tasks' acceptance criteria and the plan-level `<verification>` block (figure gate green, `test_pdf_render_gate.py` still green at 31/31, zero `:target:` occurrences in the new fixture, `black`/`ruff` clean repo-wide) were verified directly in this worktree.

---
*Phase: 42-captioned-table-drops-preceding-target-label*
*Completed: 2026-08-03*

## Self-Check: PASSED

All created files confirmed present and all four commits (`83be202`, `02f1b79`, `3b08b34`, `ce12498`) confirmed in `git log --oneline --all`. No missing items.
