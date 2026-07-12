---
phase: 13-shared-dispatch-point-changes-topic-line-blocks
plan: 03
subsystem: testing
tags: [sphinx, typst, docutils, pytest, typst-py, pypdf, render-gate]

# Dependency graph
requires:
  - phase: 13-01
    provides: "visit_topic/depart_topic (clue box + box-less contents pass-through), the generalized visit_title buffer-swap, and the Pitfall-1 multi-child-title fix"
  - phase: 13-02
    provides: "visit_line_block/visit_line/depart_line_block/depart_line (verbatim linebreak() + per-depth nested indent)"
provides:
  - "GATE-01 real-compile acceptance fixture covering topic + contents + address/poem line_block + admonition-title regression in one master document (ROADMAP SC#4)"
  - "TestTopicLineBlockRenderGate: three-method real-compile test class proving SC#1 (no outline leak), SC#2 (verbatim line breaks), and SC#3 (multi-child admonition title regression)"
affects: [phase-14-footnotes, phase-15-full-corpus-validation]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Class-scoped GATE-01 fixture (topic_line_block_render_gate_pdf_text): build+compile+extract runs ONCE per test class via tmp_path_factory, shared across multiple thin assertion-only test methods"
    - "pytest -k selector-driven test naming: a test method intentionally omits an underscore between three words (test_admonitiontitleregression_multichild) so a required -k selector resolves via contiguous substring match"

key-files:
  created:
    - tests/fixtures/topic_line_block_render_gate/conf.py
    - tests/fixtures/topic_line_block_render_gate/index.rst
  modified:
    - tests/test_pdf_render_gate.py

key-decisions:
  - "Rendered the 'epigraph' shape as a plain top-level line_block under a titled section (no `.. epigraph::` directive) per 13-RESEARCH.md Pitfall 4 -- sidesteps the pre-existing, unrelated block_quote/attribution fatal/leak bug entirely"
  - "Used a class-scoped fixture (topic_line_block_render_gate_pdf_text) to run sphinx-build/typst.compile()/pypdf-extraction exactly once per class, with three thin test methods each asserting a disjoint slice of the same PDF text -- avoids recompiling three times while still giving each -k selector its own test node"
  - "Named the admonition-regression test method test_admonitiontitleregression_multichild (no underscore between the three words) after discovering empirically that pytest's -k performs a case-insensitive but underscore-literal CONTIGUOUS substring match -- an underscore-separated admonition_title_regression would NOT have matched `-k AdmonitionTitleRegression`"

patterns-established:
  - "GATE-01 class-scoped shared-artifact fixture pattern for future multi-assertion render-gate classes (build once, assert many)"

requirements-completed: [BLK-02, BLK-03]

coverage:
  - id: D1
    description: "GATE-01 combined fixture (topic + contents + address/poem line_block + admonition regression) compiles to a valid PDF via an uncaught typst.compile() -- no TypstCompilationError"
    requirement: "BLK-02"
    verification:
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestTopicLineBlockRenderGate (class-scoped fixture topic_line_block_render_gate_pdf_text)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Topic title and .. contents:: title each appear exactly once in extracted PDF text -- not leaked into Typst's auto-outline"
    requirement: "BLK-02"
    verification:
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestTopicLineBlockRenderGate::test_topic_and_contents_render_no_outline_leak"
        status: pass
    human_judgment: false
  - id: D3
    description: "Address and poem line_block sentinels appear as separate extracted-text lines, never concatenated with no separator"
    requirement: "BLK-03"
    verification:
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestTopicLineBlockRenderGate::test_line_block_address_and_poem_breaks"
        status: pass
    human_judgment: false
  - id: D4
    description: "note/warning/multi-child .. admonition:: Custom *Title* all render correctly (Pitfall-1 regression); LEAK_SIGNATURES negative control holds"
    requirement: "BLK-03"
    verification:
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestTopicLineBlockRenderGate::test_admonitiontitleregression_multichild"
        status: pass
    human_judgment: false

duration: 7min
completed: 2026-07-12
status: complete
---

# Phase 13 Plan 03: Combined GATE-01 topic/line_block/admonition real-compile fixture Summary

**New `topic_line_block_render_gate` fixture + `TestTopicLineBlockRenderGate` class prove, via an uncaught real `typst.compile()`, that topic titles and `.. contents::` never leak into Typst's auto-outline (count==1), address/poem `line_block`s produce genuine `linebreak()`s (never source-`\n`-only concatenation), and the pre-existing multi-child admonition-title path (Pitfall 1) still renders correctly.**

## Performance

- **Duration:** ~7 min
- **Started:** 2026-07-12T13:29Z (following 13-02 completion)
- **Completed:** 2026-07-12T13:34Z
- **Tasks:** 2 completed
- **Files modified:** 3 (2 new fixture files, 1 test file)

## Accomplishments
- Created `tests/fixtures/topic_line_block_render_gate/{conf.py,index.rst}` — a combined master-document Sphinx project exercising a multi-child-title `.. topic::`, a `.. contents::` local TOC, a flat "Address" `line_block`, a one-level-nested "Poem" `line_block`, and a `.. note::`/`.. warning::`/multi-child `.. admonition::` regression block — deliberately excluding `.. epigraph::` per Pitfall 4.
- Added `TestTopicLineBlockRenderGate` to `tests/test_pdf_render_gate.py` with a class-scoped `topic_line_block_render_gate_pdf_text` fixture (build + uncaught `typst.compile()` + `pypdf` text-extraction run once) and three thin test methods, each asserting a disjoint slice of GATE-01's SC#1/SC#2/SC#3 requirements.
- Verified all three plan-mandated `-k` selectors (`Topic`, `LineBlock`, `AdmonitionTitleRegression`) each resolve to and pass ≥1 test node.
- Verified the full `tests/test_pdf_render_gate.py` suite (11 tests) and the full non-integration suite (393 tests) are green — no regression to any sibling GATE-01 class or prior-phase unit tests.

## Task Commits

Each task was committed atomically:

1. **Task 1: Create the combined topic_line_block_render_gate fixture project** - `42835af` (test)
2. **Task 2: Add TestTopicLineBlockRenderGate real-compile class to test_pdf_render_gate.py** - `aa0b810` (test)

**Plan metadata:** (this commit, docs)

## Files Created/Modified
- `tests/fixtures/topic_line_block_render_gate/conf.py` - Minimal master-document Sphinx project config (`typst_documents` set so the writer emits the full template with the `gentle-clues` import)
- `tests/fixtures/topic_line_block_render_gate/index.rst` - Combined RST fixture: multi-child-title topic, `.. contents::`, flat + nested `line_block`s, note/warning/multi-child-admonition regression block
- `tests/test_pdf_render_gate.py` - Added `topic_line_block_render_gate_dir` fixture, a class-scoped `topic_line_block_render_gate_pdf_text` build+compile+extract fixture, and `TestTopicLineBlockRenderGate` (3 test methods + 7 module-level sentinel constants)

## Decisions Made
- Used a class-scoped fixture (`tmp_path_factory`-backed, not depending on the function-scoped `fixtures_dir`/`topic_line_block_render_gate_dir` to avoid a pytest `ScopeMismatch`) so `sphinx-build`/`typst.compile()`/`pypdf`-extraction run exactly once per class rather than once per test method, per the plan's explicit preference.
- Discovered empirically that pytest's `-k` selector performs a case-insensitive but underscore-literal CONTIGUOUS substring match against the full test node id. The `Topic`/`LineBlock` selectors already matched trivially because the enclosing class name `TestTopicLineBlockRenderGate` contains those substrings verbatim, but the plan-suggested method name `test_admonition_title_regression_multichild` would NOT have matched `-k AdmonitionTitleRegression` (the underscores break contiguity). Renamed the method to `test_admonitiontitleregression_multichild` (no underscore between the three key words) to satisfy the selector exactly as the plan's acceptance criteria require, and documented the reasoning in the method's own docstring for future maintainers.
- Reused the RESEARCH-verified fixture combination and sentinel names near-verbatim (`TOPICBODYSENTINEL`, `ADDRESSLINEONE`/`TWO`, `POEMLINEONE`/`POEMNESTEDONE`/`POEMNESTEDTWO`/`POEMLINETHREE`, `ADMONITIONNOTESENTINEL`/`ADMONITIONWARNINGSENTINEL`/`ADMONITIONCUSTOMSENTINEL`) rather than inventing new ones, per the plan's explicit instruction.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Renamed the AdmonitionTitleRegression test method to satisfy its own `-k` selector**
- **Found during:** Task 2, verifying `pytest tests/test_pdf_render_gate.py -k AdmonitionTitleRegression -x` (an explicit acceptance criterion)
- **Issue:** The plan's suggested method name `test_admonition_title_regression_multichild` (underscore-separated) does not literally contain the contiguous substring `AdmonitionTitleRegression`; pytest's `-k` matches contiguous substrings case-insensitively, but underscores are literal characters that break contiguity. Running `-k AdmonitionTitleRegression` against the as-planned name selected 0 tests, failing the plan's own acceptance criterion.
- **Fix:** Renamed the method to `test_admonitiontitleregression_multichild` (no underscore between "admonition"/"title"/"regression") and added a docstring note explaining why, so the selector matches verbatim.
- **Files modified:** tests/test_pdf_render_gate.py
- **Verification:** `pytest tests/test_pdf_render_gate.py -k AdmonitionTitleRegression --collect-only -q` now selects 1 test; `pytest tests/test_pdf_render_gate.py -k "Topic or LineBlock or AdmonitionTitleRegression" -x` passes all 3.
- **Committed in:** aa0b810 (Task 2 commit)

**2. [Rule 3 - Blocking] Ran `black` (unstaged formatting) to fix a CI-parity failure**
- **Found during:** post-Task-2 verification, `uv run black --check .`
- **Issue:** `black --check .` reported `tests/test_pdf_render_gate.py` would be reformatted (the newly added multi-line string-literal assert calls needed black's canonical wrapping).
- **Fix:** Ran `uv run black tests/test_pdf_render_gate.py` (formatting only, no logic change) before committing Task 2.
- **Files modified:** tests/test_pdf_render_gate.py
- **Verification:** `uv run black --check tests/test_pdf_render_gate.py` passes; `pytest tests/test_pdf_render_gate.py -q` still 11/11 green after reformatting.
- **Committed in:** aa0b810 (Task 2 commit, formatting included in the same commit since black ran before the commit was made)

---

**Total deviations:** 2 auto-fixed (1 bug fix to satisfy a plan acceptance criterion, 1 blocking CI-parity formatting fix)
**Impact on plan:** Both deviations were necessary to satisfy the plan's own explicit, stated acceptance criteria (the `-k AdmonitionTitleRegression` selector requirement and CI-parity `black --check .`). No scope creep — no production (`typsphinx/`) code was touched by this plan.

## Issues Encountered
None beyond the deviation above (pytest `-k` matching semantics were not spelled out in the plan/research and had to be verified empirically during Task 2).

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness

Phase 13 is now complete: all three plans (13-01 topic/visit_title, 13-02 line/line_block, 13-03 this combined GATE-01 fixture) are landed. `pytest --cov=typsphinx --cov-report=term-missing` (minus the four environmentally-false-failing integration files) is green at 393 passed. Both phase requirements (BLK-02, BLK-03) are fully implemented and empirically real-compile-verified. Phase 14 (footnotes) and Phase 15 (full-corpus validation) can proceed without any carried-forward blockers from this phase.

---
*Phase: 13-shared-dispatch-point-changes-topic-line-blocks*
*Completed: 2026-07-12*

## Self-Check: PASSED

- FOUND: tests/fixtures/topic_line_block_render_gate/conf.py
- FOUND: tests/fixtures/topic_line_block_render_gate/index.rst
- FOUND: commit 42835af
- FOUND: commit aa0b810
