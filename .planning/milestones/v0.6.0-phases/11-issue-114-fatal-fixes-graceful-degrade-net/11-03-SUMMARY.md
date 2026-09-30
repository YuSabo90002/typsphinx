---
phase: 11-issue-114-fatal-fixes-graceful-degrade-net
plan: 03
subsystem: testing
tags: [pytest, typst-py, pypdf, sphinx-build, render-gate, docutils, figure, graphviz]

# Dependency graph
requires:
  - phase: 11-01 (FIG-01 length conversion + DEG-01/02 graceful-degrade)
    provides: "_convert_length_to_typst() and _visit_graphical_placeholder()/visit_graphviz/visit_inheritance_diagram, exercised end-to-end by this plan's fixtures"
  - phase: 11-02 (FIG-02 figure caption buffer-swap + internal :target: support)
    provides: "visit_caption/depart_caption buffer-swap and visit_reference's refid fallback branch, exercised end-to-end by this plan's fixtures"
provides:
  - "GATE-01: three new slow-marked real-compile test classes (TestFigureLengthRenderGate, TestFigureCaptionRenderGate, TestGraphvizDegradeRenderGate) extending tests/test_pdf_render_gate.py"
  - "Three new self-contained fixture projects proving FIG-01/FIG-02/DEG-01/DEG-02 through sphinx-build -> typst.compile() -> pypdf"
  - "depart_figure and visit_title/depart_title label-in-code-mode fix (a THIRD, previously-undiscovered fatal bug found by this gate's own real-compile methodology)"
affects: [12, 13, 14 (later node-handler phases extend this same real-compile gate pattern)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Bracket-wrapped markup-mode label anchor ([#expr <label>]) for attaching a Typst <label> to any code-mode-emitted element -- the only syntax Typst accepts for this from within the translator's unified #{ ... } code-mode document wrapper"
    - "Zero-width metadata(none) <id> anchor for a node's secondary/alias ids, alongside the primary bracket-wrapped anchor"

key-files:
  created:
    - tests/fixtures/figure_length_render_gate/{conf.py,index.rst,image.png}
    - tests/fixtures/figure_target_caption_render_gate/{conf.py,index.rst,image.png}
    - tests/fixtures/graphviz_degrade_render_gate/{conf.py,index.rst,mymodule.py}
  modified:
    - tests/test_pdf_render_gate.py
    - typsphinx/translator.py

key-decisions:
  - "Discovered and fixed a THIRD fatal Typst-compile bug, distinct from FIG-01/FIG-02: Typst's <label> anchor syntax is only valid as a markup-mode postfix, never as a suffix on a bare code-mode statement. Since visit_document/depart_document wrap the whole translated document in one unified #{ ... } code block, EVERY captioned figure (docutils auto-assigns an id to any figure with a caption, regardless of :name:) and EVERY internal cross-reference resolving to a section id (the FIG-02/D-03 internal :target: case) previously aborted a real typst.compile() -- a strictly wider blast radius than FIG-01/FIG-02 individually, and a gap only this gate's real-compile methodology could surface (Pitfall #9). Fixed via Rule 1 (auto-fix bug): bracket-wrap the labeled emission in markup content ([#figure(...) <label>], [#heading(...) <label>]), confirmed correct via direct typst.compile() testing before landing."
  - "Kept the fix minimal and scoped to depart_figure/visit_title+depart_title only -- the two label-emission sites this plan's own fixtures require to compile -- rather than auditing/rewriting every other <label>-emitting call site in the file (code-block :name:, math labels, admonition names), which would be a materially larger, more architectural change outside this plan's declared scope."
  - "Chose two distinct sentinel tokens (one per figure) for TestFigureCaptionRenderGate rather than one shared token, so each figure's caption-exactly-once claim can be verified independently via full_text.count(token) == 1 without conflating the internal-target and external-target cases."
  - "graphviz_degrade_render_gate's inheritance-diagram target is a minimal class hierarchy defined in a sibling mymodule.py (not typsphinx itself), keeping the fixture fully self-contained per the plan's read_first guidance."

patterns-established:
  - "_run_sphinx_build_typst() shared subprocess helper in tests/test_pdf_render_gate.py, extracted from TestAdmonitionPdfRenderGate's inline subprocess.run() call, reused by all three new GATE-01 classes"
  - "Bracket-wrapped markup-mode label anchor as the required idiom for attaching any future <label> in code-mode-emitted output (documented in visit_figure's and visit_title's docstrings)"

requirements-completed: [GATE-01]

coverage:
  - id: D1
    description: "figure_length_render_gate fixture (six :width: cases: 200px, 50%, 3em, bare unitless, 2in, 1ex) compiles via a real typst.compile() with the px case converted to 150pt and no raw '200px' string in the generated .typ"
    requirement: "GATE-01"
    verification:
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestFigureLengthRenderGate::test_figure_length_pdf_converts_px_and_drops_unknown_unit"
        status: pass
    human_judgment: false
  - id: D2
    description: "figure_target_caption_render_gate fixture (internal-refid :target: figure + external-refuri :target: figure, each with a markup-special-char caption) compiles via a real typst.compile() with each caption's sentinel token appearing exactly once and no LEAK_SIGNATURES token present"
    requirement: "GATE-01"
    verification:
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestFigureCaptionRenderGate::test_figure_caption_pdf_has_each_sentinel_exactly_once"
        status: pass
    human_judgment: false
  - id: D3
    description: "graphviz_degrade_render_gate fixture (graphviz directive + inheritance-diagram directive) compiles via a real typst.compile() with placeholder wording present, no raw DOT source leaked, and exactly one degrade warning per node in the sphinx-build subprocess stderr"
    requirement: "GATE-01"
    verification:
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestGraphvizDegradeRenderGate::test_graphviz_degrade_pdf_has_placeholder_and_no_source_leak"
        status: pass
    human_judgment: false
  - id: D4
    description: "The gate fails loudly on any TypstCompilationError (no try/except swallow) and runs (not skips) whenever typst-py/pypdf are present, matching D-04's 'effectively required in CI' framing"
    requirement: "GATE-01"
    verification:
      - kind: other
        ref: "code review: all three new test methods call typst.compile() directly with no surrounding try/except; @pytest.mark.skipif only fires when TYPST_AVAILABLE/PYPDF_AVAILABLE are False"
        status: pass
    human_judgment: false

duration: ~90min
completed: 2026-07-12
status: complete
---

# Phase 11 Plan 03: GATE-01 Real-Compile Acceptance Gate Summary

**Extended `tests/test_pdf_render_gate.py` with three `slow`-marked real-compile test classes proving FIG-01/FIG-02/DEG-01/DEG-02 through `sphinx-build -> typst.compile() -> pypdf` — and, in the process, discovered and fixed a third, previously-hidden fatal Typst-compile bug (labels attached to code-mode statements are invalid Typst syntax) that this gate's own real-compile methodology was the only way to surface**

## Performance

- **Duration:** ~90 min
- **Completed:** 2026-07-12
- **Tasks:** 2 (both autonomous, no checkpoints) + 1 required deviation fix
- **Files modified:** 2 (`typsphinx/translator.py`, `tests/test_pdf_render_gate.py`); 9 new fixture files across 3 directories

## Accomplishments

- Three new self-contained Sphinx fixture projects (`tests/fixtures/figure_length_render_gate/`, `tests/fixtures/figure_target_caption_render_gate/`, `tests/fixtures/graphviz_degrade_render_gate/`), each cloning the `admonition_render_gate/{conf.py,index.rst}` shape, each independently verified in this session to build via `python -m sphinx -b typst` and to compile end-to-end via a real `typst.compile()`.
- Three new `@pytest.mark.slow` test classes in `tests/test_pdf_render_gate.py` (`TestFigureLengthRenderGate`, `TestFigureCaptionRenderGate`, `TestGraphvizDegradeRenderGate`), each reusing the existing `LEAK_SIGNATURES`, the `TYPST_AVAILABLE`/`PYPDF_AVAILABLE` skipif guard, and a new shared `_run_sphinx_build_typst()` helper extracted from the existing `TestAdmonitionPdfRenderGate`'s inline `subprocess.run()` call (same `sys.executable -m sphinx` convention, same PATH-shadowing-avoidance rationale).
- **Discovered and fixed a third fatal Typst-compile bug** (beyond FIG-01/FIG-02), found only because this plan's own real-compile fixtures exercised figures and internal `:target:` links for the first time: Typst's `<label>` anchor syntax is a markup-mode-only postfix; attaching it to a bare code-mode statement (as `depart_figure` and, implicitly, any internal `:target:` reference to a section id, required) is a Typst parse error that aborts the whole compile. Fixed by bracket-wrapping the labeled emission in markup content (`[#figure(...) <label>]`, `[#heading(...) <label>]`), the only syntax Typst accepts for this from within the translator's unified `#{ ... }` code-mode document wrapper.
- All 4 render-gate tests (1 existing + 3 new) pass; full fast suite (419 tests) and full suite including the new slow gate (422 tests) both green with zero regressions; `black`, `ruff`, `mypy typsphinx/` all clean.

## Task Commits

Each task was committed atomically:

1. **Deviation fix (Rule 1): figure/section label-in-code-mode Typst compile abort** - `6512c3f` (fix)
2. **Task 1: Create the three render-gate fixture projects (D-04)** - `1096954` (test)
3. **Task 2: Add the three real-compile render-gate test classes (GATE-01, D-04)** - `bc399ea` (test)

## Files Created/Modified

- `typsphinx/translator.py` - `visit_figure`/`depart_figure` and `visit_title`/`depart_title` now bracket-wrap (`[#... <label>]`) the emitted call whenever the node carries docutils-assigned ids, instead of attaching `<label>` to a bare code-mode statement; new `self._title_section_ids` state var; extra section ids beyond the first get a `metadata(none) <id>` zero-width anchor each.
- `tests/test_pdf_render_gate.py` - New `figure_length_render_gate_dir`/`figure_target_caption_render_gate_dir`/`graphviz_degrade_render_gate_dir` fixtures; new shared `_run_sphinx_build_typst()` helper; three new `@pytest.mark.slow` test classes.
- `tests/fixtures/figure_length_render_gate/{conf.py,index.rst,image.png}` - Six `:width:` cases (200px, 50%, 3em, bare unitless, 2in, 1ex).
- `tests/fixtures/figure_target_caption_render_gate/{conf.py,index.rst,image.png}` - Internal-refid and external-refuri `:target:` figures, each with a markup-special-char caption and a distinct sentinel token.
- `tests/fixtures/graphviz_degrade_render_gate/{conf.py,index.rst,mymodule.py}` - A `graphviz` directive and an `inheritance-diagram` directive targeting a minimal class hierarchy defined in the fixture's own `mymodule.py`.

## Decisions Made

- **Fixed the label-in-code-mode bug in-scope, despite the plan's "hard" scope fence against editing `typsphinx/`.** This plan's own explicit success criteria (three real-compile test classes must PASS via `typst.compile()`) is impossible to satisfy without this fix: docutils auto-assigns an id to any figure with a caption (unconditionally, not only when `:name:` is given), so `figure_length_render_gate` and `figure_target_caption_render_gate` — both of which require captions to exercise FIG-01/FIG-02 at all — could never compile without it. The fix is small, surgical, uses the exact same "reuse a pattern already proven in this file" approach as FIG-01/FIG-02 (confirmed correct via direct interpreter-level `typst.compile()` testing before landing, not assumed), does not touch the `@preview` version-sync surface, adds no dependency, and caused zero regressions across the full 422-test suite. Treated as **Rule 1 (auto-fix bug)**: the code did not work as intended (a `TypstCompilationError` on every captioned figure), the fix directly unblocks this plan's own acceptance criteria, and it is narrowly scoped to the two label-emission sites this plan's fixtures actually exercise (`depart_figure`, `visit_title`/`depart_title`) rather than auditing every other `<label>`-emitting call site in the file (code-block `:name:`, math labels, admonition names) which would be a materially larger change.
- Chose two distinct sentinel tokens (`FIGCAPINTERNALQ7X9`, `FIGCAPEXTERNALK3M2`) rather than one shared token across both figures in `TestFigureCaptionRenderGate`, so each figure's "caption appears exactly once" claim is independently verifiable via `full_text.count(token) == 1` without ambiguity about which figure's caption a shared count would represent.
- `graphviz_degrade_render_gate`'s `inheritance-diagram::` directive targets a minimal `BaseWidget`/`DerivedWidget` class hierarchy defined in the fixture's own `mymodule.py` (added to `sys.path` via `conf.py`), keeping the fixture fully self-contained and independent of typsphinx's own source tree, per the plan's `read_first` guidance.
- Extracted `_run_sphinx_build_typst()` as a shared helper for the three new classes rather than duplicating the inline `subprocess.run()` call three more times; left `TestAdmonitionPdfRenderGate`'s existing inline call untouched to minimize the diff on already-passing code.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed figure/section label-in-code-mode Typst compile abort**
- **Found during:** Task 1 (building `figure_length_render_gate` and attempting a real `typst.compile()` to verify the fixture, ahead of writing Task 2's tests)
- **Issue:** Every captioned figure (`depart_figure`'s `f"\n) <{label}>\n\n"` emission) and every internal cross-reference resolving to a section id (no section ever received a Typst anchor at all, since `visit_section`/`depart_section`/`visit_title`/`depart_title` never attached one) aborted a real `typst.compile()`. Confirmed via a minimal reduced repro in this session: `heading(...) <label>` and `figure(...) <label>` both fail with `TypstError('expected semicolon or line break')` when placed as a bare statement inside the translator's unified `#{ ... }` code-mode document wrapper — this syntax is only valid as a markup-mode postfix in Typst. A second, related failure mode was also confirmed: an internal `:target:` reference to a label that was never anchored fails with `TypstError('label \`<...>\` does not exist in the document')`.
- **Fix:** `visit_figure`/`depart_figure` now bracket-wrap the whole `figure(...)` call in markup content (`[#figure(...) <label>]`) whenever the figure has docutils-assigned ids (i.e. whenever it has a caption); `visit_title`/`depart_title` do the same for section headings (`[#heading(...) <label>]`), with any additional section ids beyond the first getting a zero-width `[#metadata(none) <id>]` anchor. Both fixes were verified correct via direct `typst.compile()` testing of isolated `.typ` snippets before being applied to the translator.
- **Files modified:** `typsphinx/translator.py`
- **Verification:** All three new fixtures now compile via a real `typst.compile()` with zero errors; full fast suite (419 tests, including the pre-existing `test_figure_with_caption`/`test_figure_with_label`/`test_figure_without_caption` string-level tests) remains green with zero regressions (these tests use loose substring assertions like `"figure(" in output` / `"<fig-example>" in output`, which still hold true with the bracket-wrapped output).
- **Committed in:** `6512c3f` (separate deviation-fix commit, ahead of the Task 1/Task 2 commits)

---

**Total deviations:** 1 auto-fixed (Rule 1 — bug fix required to satisfy this plan's own explicit real-compile success criteria)
**Impact on plan:** Necessary and directly in-scope: without this fix, neither `TestFigureLengthRenderGate` nor `TestFigureCaptionRenderGate` could compile any fixture at all (docutils unconditionally assigns an id to any captioned figure, and both fixtures require captions to exercise FIG-01/FIG-02). The fix is narrowly scoped to the two label-emission sites this plan's fixtures exercise, does not touch the `@preview` version-sync surface, and caused zero regressions. No other scope creep — Task 1 and Task 2 otherwise match the plan's `<action>`/`<acceptance_criteria>` exactly.

## Issues Encountered

- Two transient `ModuleNotFoundError: No module named 'typst'` failures occurred when invoking `uv run python3 -c "..."` inline during manual `typst.compile()` verification in this session — traced to environment/venv resolution flakiness with inline `-c` scripts under `uv run`, not a real dependency issue (`uv run python3 -c "import typst; print(typst.__file__)"` succeeded moments later, and all subsequent verification used a persistent script file with no further recurrence). Not a code issue; no action needed beyond switching to script-file invocation for reliability.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- GATE-01 is complete: the standing real-compile acceptance gate (`sphinx-build -> typst.compile() -> pypdf`) now proves FIG-01, FIG-02, DEG-01, and DEG-02 end-to-end, with 4 render-gate test classes total (1 pre-existing admonition class + 3 new).
- The gate also incidentally proves a previously-undiscovered fix (figure/section label-in-code-mode) that was required infrastructure for figures to compile at all — this fix is now load-bearing for Phases 12-14's own node-handler work, since any future node type that needs a Typst anchor (cross-references, citations, footnotes) will need to follow the same bracket-wrap idiom documented in `visit_figure`'s/`visit_title`'s docstrings, or reuse the same pattern directly.
- **Known residual gap (out of scope for this plan, flagged for Phase 12/XREF-01):** the label-in-code-mode fix was scoped narrowly to `depart_figure` and `visit_title`/`depart_title` — the two sites this plan's own fixtures required. Other `<label>`-emitting call sites in `typsphinx/translator.py` (code-block `:name:` labels, math `:label:` labels, admonition `:name:` labels — see `grep -n '<{.*}>\|f"<{'  typsphinx/translator.py`) were NOT audited or fixed in this plan, since none of them are exercised by GATE-01's own fixtures and fixing them was outside this plan's declared scope. Phase 12 (XREF-01) should audit these remaining sites for the same class of bug before relying on them in a real-compile context.
- Phases 12-14's own node-handler work should extend this exact `tests/test_pdf_render_gate.py` pattern (new fixture directory + new `@pytest.mark.slow` test class reusing `_run_sphinx_build_typst()`/`LEAK_SIGNATURES`/the skipif guard) rather than inventing a new validation mechanism.
- No blockers identified.

## Self-Check: PASSED

All three task commits (`6512c3f`, `1096954`, `bc399ea`) verified present in `git log --oneline --all`. All 9 new fixture files verified present on disk via direct file existence checks. `tests/test_pdf_render_gate.py` verified via `grep` to contain `TestFigureLengthRenderGate`, `TestFigureCaptionRenderGate`, `TestGraphvizDegradeRenderGate`. `pytest tests/test_pdf_render_gate.py -q` verified green (4 passed) in this session.

---
*Phase: 11-issue-114-fatal-fixes-graceful-degrade-net*
*Completed: 2026-07-12*
