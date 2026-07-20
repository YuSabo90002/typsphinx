---
phase: 12-high-volume-independent-node-handlers
plan: 03
subsystem: translator
tags: [typst, sphinx, autodoc, desc-signature, linebreak, render-gate]

# Dependency graph
requires:
  - phase: 12-02
    provides: depart_term bracket-wrap <label> anchor fix and the shared test_pdf_render_gate.py file this plan appends to (file-ownership sequencing only, per D-03 wave note -- DESC group is logically independent of VER-01/XREF-01)
provides:
  - "visit_desc_returns/depart_desc_returns: literal ' -> ' return-arrow injection (DESC-01)"
  - "visit_desc_optional/depart_desc_optional: recursion-safe literal bracket wrap reusing _desc_parameter_has_content (DESC-03)"
  - "visit_desc_inline/depart_desc_inline: transparent pass-through, no strong() wrapper (DESC-04, D-06)"
  - "visit_desc_signature_line/depart_desc_signature_line + _is_first_desc_signature_line state (DESC-02): real Typst linebreak() between genuine multi-line signature lines"
  - "Resolved Open Question 1: `.. cpp:function:: template<typename T> ...` is the confirmed rST construction producing TWO genuine desc_signature_line siblings under one desc_signature"
  - "desc_signature_render_gate fixture + TestDescSignatureRenderGate real-compile acceptance gate"
affects: [13-shared-dispatch-point-changes, 14-footnotes, 15-full-corpus-validation]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Typst stdlib linebreak() as an explicit statement for a genuine visual line break -- a source '\\n' between code-mode statements is proven cosmetic-only (New Pitfall 11); this is the first use of linebreak() in this codebase"
    - "Recursion-safe bracket-wrap via a shared is-first-content flag (_desc_parameter_has_content) -- nested desc_optional is a structural doctree sibling, not something the handler tracks depth for"

key-files:
  created:
    - tests/fixtures/desc_signature_render_gate/conf.py
    - tests/fixtures/desc_signature_render_gate/index.rst
  modified:
    - typsphinx/translator.py
    - tests/test_translator.py
    - tests/test_pdf_render_gate.py

key-decisions:
  - "Resolved Open Question 1 empirically via a live -b pseudoxml doctree dump: `.. cpp:function:: template<typename T> void foo(T t)` produces two genuine desc_signature_line children (templatePrefix line + main declarator line) -- confirmed BEFORE writing the RED test, per Task 2's explicit first-step instruction"
  - "Used uppercase per-line sentinel tokens (DESCLINEONESENTINEL4Q1 as the template parameter name, DESCLINETWOSENTINEL5Q2 as the C++ function name) so the render-gate test can prove via real pypdf extraction that the two lines are NOT concatenated -- following New Pitfall 11's explicit warning against a .typ-source-only '\\n' check"
  - "Placed visit_desc_signature_line/depart_desc_signature_line and _is_first_desc_signature_line's reset immediately adjacent to visit_desc_returns in the desc_signature family region, keeping the existing dummy-strong() delegation in visit_desc_signature untouched apart from the one reset line"

patterns-established:
  - "linebreak() is now the established idiom for any future handler needing a genuine visual line break inside a code-mode {...} block -- never a source '\\n', which is a Typst-grammar-level statement separator only"

requirements-completed: [DESC-01, DESC-02, DESC-03, DESC-04]

coverage:
  - id: D1
    description: "visit_desc_returns/depart_desc_returns emit a literal ' -> ' arrow before the return type; resolved return-type xref children stream through the unmodified visit_reference refid branch with zero extra code"
    requirement: "DESC-01"
    verification:
      - kind: unit
        ref: "grep -q \"def visit_desc_returns\" typsphinx/translator.py; pytest -m \"not slow\" -q (no regression in existing desc/signature tests)"
        status: pass
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestDescSignatureRenderGate -- asserts '-> int' in extracted PDF text"
        status: pass
    human_judgment: false
  - id: D2
    description: "visit_desc_signature_line/depart_desc_signature_line emit a real Typst linebreak() between genuine multi-line signature lines (never a source '\\n', proven cosmetic-only); _is_first_desc_signature_line is the phase's one new state variable, reset per visit_desc_signature"
    requirement: "DESC-02"
    verification:
      - kind: unit
        ref: "tests/test_translator.py::test_desc_signature_line_multiline_emits_one_linebreak (RED before implementation, GREEN after) + test_desc_signature_line_single_line_emits_no_linebreak + test_desc_signature_line_resets_per_signature"
        status: pass
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestDescSignatureRenderGate -- real pypdf extraction proves DESCLINEONESENTINEL4Q1 and DESCLINETWOSENTINEL5Q2 are present and NOT concatenated with no separator"
        status: pass
    human_judgment: false
  - id: D3
    description: "visit_desc_optional/depart_desc_optional literal-bracket-wrap trailing optional parameter groups, reusing _desc_parameter_has_content (zero new state); recursion-safe by construction for nested desc_optional (printf(fmt[, args[, more]]))"
    requirement: "DESC-03"
    verification:
      - kind: unit
        ref: "grep -q \"def visit_desc_optional\" typsphinx/translator.py; pytest -m \"not slow\" -q"
        status: pass
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestDescSignatureRenderGate -- typst.compile() with NO try/except (a bracket mismatch would abort the whole compile) + asserts 'printf(fmt, [args, [more]])' in extracted PDF text"
        status: pass
    human_judgment: false
  - id: D4
    description: "visit_desc_inline/depart_desc_inline are a pure pass-through (never delegates to visit_strong the way visit_desc_signature does), resolving D-06 via node-type dispatch alone"
    requirement: "DESC-04"
    verification:
      - kind: unit
        ref: "grep -q \"def visit_desc_inline\" typsphinx/translator.py; manual read confirms no visit_strong call inside visit_desc_inline"
        status: pass
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestDescSignatureRenderGate -- asserts DescInlineExprToken present and no LEAK_SIGNATURES token (no strong()-wrapper leak)"
        status: pass
    human_judgment: false
  - id: D5
    description: "desc_signature_render_gate fixture covers all four DESC cases; TestDescSignatureRenderGate proves all four render correctly through a real sphinx-build -> typst.compile() -> pypdf round-trip, extending the GATE-01 standing bar"
    requirement: "DESC-01, DESC-02, DESC-03, DESC-04"
    verification:
      - kind: integration
        ref: "pytest tests/test_pdf_render_gate.py::TestDescSignatureRenderGate -q (1 passed) + pytest tests/test_pdf_render_gate.py -q (7 passed, all render-gate classes)"
        status: pass
    human_judgment: false

duration: 4min
completed: 2026-07-12
status: complete
---

# Phase 12 Plan 03: Desc Signature Sub-Part Handlers (DESC-01..04) Summary

**Landed the four autodoc signature sub-part handlers -- `desc_returns` (return arrow), `desc_signature_line` (genuine `linebreak()`, resolving Open Question 1 empirically), `desc_optional` (recursion-safe nested brackets), and `desc_inline` (transparent pass-through, D-06) -- plus a real-compile GATE-01 fixture proving all four via `pypdf` text-extraction.**

## Performance

- **Duration:** 4 min
- **Started:** 2026-07-12T11:09:46+09:00 (first task commit)
- **Completed:** 2026-07-12T11:13:18+09:00 (last task commit)
- **Tasks:** 3
- **Files modified:** 5 (2 modified in Task 1/2 overlap counted once, 1 test file modified, 2 fixture files created)

## Accomplishments

- Added `visit_desc_returns`/`depart_desc_returns`: emits a literal `text(" -> ")` arrow before a signature's return-type annotation (DESC-01). Resolved return-type xref children already stream through the existing, unmodified `visit_reference` refid branch -- zero extra code needed for that case.
- Added `visit_desc_optional`/`depart_desc_optional`: literal-bracket-wraps trailing optional parameter groups (`printf(fmt[, args[, more]])`), reusing the existing `_desc_parameter_has_content` flag with zero new state (DESC-03). Recursion-safe by construction: a nested `desc_optional` is a structural doctree sibling, so the identical handler fires again producing correctly nested brackets -- no depth counter added.
- Added `visit_desc_inline`/`depart_desc_inline`: a pure pass-through pair (DESC-04). Confirmed by direct inspection that neither method delegates to `visit_strong` the way `visit_desc_signature` does -- resolving D-06 (the strong()-suppression predicate is simply "which node class Sphinx dispatches to," not a parent-inspection hack).
- Resolved the phase's one open item (Open Question 1 / Assumption A1) empirically via a live `-b pseudoxml` doctree dump **before** writing the RED test: `.. cpp:function:: template<typename T> void foo(T t)` produces TWO genuine `desc_signature_line` siblings under one `desc_signature` (the C++ domain's templatePrefix line, then the main declarator line) -- confirming the construction 12-RESEARCH.md flagged as unconfirmed.
- Followed the TDD gate for Task 2 (`tdd="true"`): wrote `test_desc_signature_line_multiline_emits_one_linebreak` first (confirmed genuinely RED -- `assert 0 == 1` -- since no handler existed), then implemented `_is_first_desc_signature_line` (the phase's one D-05-sanctioned new state variable), the `visit_desc_signature` reset line, and `visit_desc_signature_line`/`depart_desc_signature_line` emitting Typst's stdlib `linebreak()` (first use in this codebase) -- confirmed GREEN. No REFACTOR commit needed (the GREEN implementation was already minimal and clean).
- Added the `desc_signature_render_gate` fixture (all four DESC cases: return-annotated `.. py:function::`, the confirmed multi-line `.. cpp:function:: template<...>`, the nested-optional `printf(fmt[, args[, more]])`, and an inline `:cpp:expr:` fragment) and `TestDescSignatureRenderGate` -- a real `sphinx-build -> typst.compile() -> pypdf` round-trip with an **uncaught** `typst.compile()` call (a bracket mismatch in the DESC-03 nested case would abort the whole compile, per Pitfall 1). The DESC-02 assertion is a genuine real-extraction proof (per New Pitfall 11): it asserts both per-line sentinel tokens are present AND that their concatenation (no-separator form) is absent from the extracted text -- proving the emitted `linebreak()` produced a real visual break, not a cosmetic source `\n`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add desc_returns, desc_optional, desc_inline handlers (DESC-01/03/04, D-05/D-06)** - `040e9c1` (feat)
2. **Task 2 RED: add failing test for desc_signature_line linebreak() (DESC-02)** - `0f28b73` (test)
2. **Task 2 GREEN: implement desc_signature_line linebreak() (DESC-02)** - `90d1142` (feat)
3. **Task 3: Create desc_signature_render_gate fixture + TestDescSignatureRenderGate (DESC-01…04, GATE-01, SC#3/SC#5)** - `8a94ed8` (test)

_Note: no separate plan-metadata commit -- orchestrator owns STATE.md/ROADMAP.md writes after all worktree agents in the wave complete; this SUMMARY.md itself is committed as part of the parallel-executor protocol._

## TDD Gate Compliance

Task 2 (`tdd="true"`) followed the full RED/GREEN cycle:
- RED gate: `0f28b73` (`test(12-03): add failing test for desc_signature_line linebreak() (DESC-02)`) -- confirmed genuinely failing (`assert 0 == 1`) before any implementation, per the fail-fast rule.
- GREEN gate: `90d1142` (`feat(12-03): implement desc_signature_line linebreak() (DESC-02)`) -- confirmed all 3 new unit tests pass after implementation.
- No REFACTOR commit: the GREEN implementation required no cleanup (minimal diff, no duplication introduced).

## Files Created/Modified

- `typsphinx/translator.py` - Added `visit_desc_returns`/`depart_desc_returns`, `visit_desc_optional`/`depart_desc_optional`, `visit_desc_inline`/`depart_desc_inline`, `visit_desc_signature_line`/`depart_desc_signature_line`; added `_is_first_desc_signature_line` state var in `__init__`; added one reset line in `visit_desc_signature`
- `tests/test_translator.py` - 3 new unit tests: `test_desc_signature_line_multiline_emits_one_linebreak`, `test_desc_signature_line_single_line_emits_no_linebreak`, `test_desc_signature_line_resets_per_signature`
- `tests/fixtures/desc_signature_render_gate/conf.py` - Minimal Sphinx config (project/author/release, `extensions = ["typsphinx"]`, `typst_documents` master tuple for "index")
- `tests/fixtures/desc_signature_render_gate/index.rst` - All four DESC cases with distinctive sentinel tokens for the multi-line case
- `tests/test_pdf_render_gate.py` - New `desc_signature_render_gate_dir` fixture and `TestDescSignatureRenderGate` class

## Decisions Made

- Resolved Open Question 1 empirically via a live `-b pseudoxml` doctree dump BEFORE writing the RED test (per Task 2's explicit first-implementation-step instruction), confirming `.. cpp:function:: template<typename T> ...` as the working multi-line construction syntax -- this feeds directly into both the unit test's realism and the Task 3 fixture's actual rST content.
- Chose uppercase, code-like per-line sentinel tokens (`DESCLINEONESENTINEL4Q1` as a template parameter identifier, `DESCLINETWOSENTINEL5Q2` as the C++ function name) rather than natural-language sentinels, since both slots require valid C++ identifiers -- verified both compile cleanly via a real `typst.compile()` + `pypdf` round-trip in a scratch fixture before finalizing.
- Kept `visit_desc_optional`/`depart_desc_optional` adjacent to `depart_desc_parameter` (same `desc_parameter`-family region) rather than near `visit_desc_returns`, matching 12-PATTERNS.md's grouping and the existing file's locality convention for related state-sharing handlers.

## Deviations from Plan

None - plan executed exactly as written. All three tasks' acceptance criteria were met without needing any Rule 1-4 deviation: no bugs found in adjacent code, no missing critical functionality discovered, no blocking issues, no architectural changes needed.

## Issues Encountered

- `pytest -m "not slow" -q` shows the same 45 pre-existing environmental failures documented in `deferred-items.md` (Plan 12-01) -- `subprocess.run([sys.executable, "-m", "sphinx", ...])`-adjacent `["uv", "run", ...]`-based integration tests hitting the NixOS dynamic-linking PATH-shadowing hazard in `tests/test_integration_{advanced,basic,multi_doc,nested_toctree}.py`. Confirmed unrelated: none of the 4 failing files were touched by this plan; 377 tests pass (374 baseline + 3 new unit tests), and the full `test_pdf_render_gate.py` suite (7 classes, including this plan's new `TestDescSignatureRenderGate`) is entirely green.
- No other issues -- Open Question 1 resolved cleanly on the first attempted construction (`template<typename T> ...`), matching 12-RESEARCH.md's own recommendation.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The GATE-01 standing bar is extended: 7 render-gate classes now pass in `tests/test_pdf_render_gate.py`, including this plan's `TestDescSignatureRenderGate` proving all four DESC handlers render correctly in a real compile.
- All four DESC-01..04 requirements are complete; the `desc_*` visitor family in `typsphinx/translator.py` now covers `desc_returns`, `desc_signature_line`, `desc_optional`, and `desc_inline` in addition to the pre-existing `desc_signature`/`desc_content`/`desc_parameterlist`/`desc_parameter`/`desc_annotation`/`desc_addname`/`desc_name`/`desc_sig_*` handlers.
- `typsphinx/translator.py` and `tests/test_pdf_render_gate.py` were both files-modified in this plan and in 12-01/12-02 (file-ownership sequencing, D-03 wave note) -- no logical dependency, but all three plans' diffs to these shared files now land together on this wave's branch.
- No blockers for Phase 13 (shared `visit_title` generalization for topic + line/line_block) -- this plan's changes are isolated to the `desc_*` family and do not touch `visit_title`/`visit_figure`/`visit_reference`.

---
*Phase: 12-high-volume-independent-node-handlers*
*Completed: 2026-07-12*

## Self-Check: PASSED

All claimed files exist (`typsphinx/translator.py`, `tests/test_translator.py`, `tests/fixtures/desc_signature_render_gate/conf.py`, `tests/fixtures/desc_signature_render_gate/index.rst`, `tests/test_pdf_render_gate.py`, this `12-03-SUMMARY.md`) and all 4 task commit hashes (`040e9c1`, `0f28b73`, `90d1142`, `8a94ed8`) are present in git log.
