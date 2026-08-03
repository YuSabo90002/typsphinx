---
phase: 38-structural-indentation-info-fields
plan: 01
subsystem: testing
tags: [sphinx, typst, pypdf, render-gate, tdd-red]

# Dependency graph
requires:
  - phase: 37-signature-typography-the-desc-family
    provides: "block(sticky: true, par(hanging-indent: 2.5em, {...})) signature wrapper, SHARED_INDENT_STEP constant, desc_signature id-anchor stability (D-14) this plan's structural markers depend on"
provides:
  - "tests/fixtures/desc_content_indent_render_gate/ -- one fixture exercising IND-01..IND-05, FLD-01, D-04, D-11 in a single -b typst build"
  - "tests/test_desc_content_indent_render_gate.py -- 13 hand-derived structural/column assertions, recorded RED against the untouched translator (6 RED, 7 GREEN-as-control)"
  - "38-GATE-EVIDENCE-01.md -- verbatim RED, SC#4 discovery grep, pre-phase column baseline, pypdf layout-mode-vs-visitor_text side-by-side comparison"
  - "Discovery: depart_desc_signature (Phase 37) and the field_list family's five self.body.append(...) sites (38-EMISSION-CONTRACT.md section 3.1) both independently abort the Typst compile for a desc/field_list inside a table cell -- pre-existing, out-of-scope for this plan"
affects: [38-05, 38-06, 38-08]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Page-index-agnostic left-edge measurement: _find_page_and_column searches ALL pages for a marker by content, not a hard-coded page index, so the assertion survives the fixture's page count changing once the pad() wrapper adds vertical space"
    - "Session-scoped .typ-only fixture split from a session-scoped compiled-PDF fixture, so purely structural tests never require typst/pypdf to be installed"

key-files:
  created:
    - tests/fixtures/desc_content_indent_render_gate/conf.py
    - tests/fixtures/desc_content_indent_render_gate/index.rst
    - tests/test_desc_content_indent_render_gate.py
    - .planning/phases/38-structural-indentation-info-fields/38-GATE-EVIDENCE-01.md
  modified: []

key-decisions:
  - "Table-Cell CONTROL construct changed from a desc/field_list-in-table-cell falsifier to plain, desc-free content, because BOTH candidate shapes independently abort the Typst compile today via pre-existing, out-of-scope self.body.append bugs (depart_desc_signature, Phase 37; the field_list family, 38-EMISSION-CONTRACT.md section 3.1) -- recorded as a discovery in 38-GATE-EVIDENCE-01.md rather than silently worked around or fixed outside this plan's typsphinx/-untouched scope."
  - "IND-03, IND-05 and the D-11/SIG-09 page-boundary assertion come out GREEN pre-phase (0 == 0, nothing is indented yet) rather than RED as the plan's acceptance criteria anticipated -- reclassified as non-regression controls per the plan's own Task 3 instruction, with the reason each must still hold post-phase recorded in the evidence file."
  - "Page-boundary construct (D-11/SIG-09) uses a genuinely long (30-sentence) body paragraph rather than precise filler-paragraph tuning, so the page crossing is robust rather than incidentally dependent on exact page arithmetic."

requirements-completed: [IND-01, IND-02, IND-03, IND-04, IND-05, FLD-01]

coverage:
  - id: D1
    description: "One fixture Sphinx project exercising every IND-01..IND-05/FLD-01 doctree shape (three-level nest, resumed body, sibling top-level desc, nested field list, body-less CONTROL, list-item CONTROL, table-cell CONTROL, page-boundary case, no-desc CONTROL, block quote) in one -b typst build that compiles"
    requirement: "IND-01"
    verification:
      - kind: integration
        ref: "tests/test_desc_content_indent_render_gate.py -- full module run"
        status: pass
    human_judgment: false
  - id: D2
    description: "Gate module with 13 hand-derived structural/column assertions, RED against the untouched translator where the contract predicts a defect, GREEN where it predicts none"
    requirement: "FLD-01"
    verification:
      - kind: unit
        ref: "tests/test_desc_content_indent_render_gate.py::TestDescContentIndentStructuralGate and ::TestDescContentIndentPdfGate (13 node ids)"
        status: pass
    human_judgment: false
  - id: D3
    description: "38-GATE-EVIDENCE-01.md recording the verbatim RED, the SC#4 discovery grep, the pre-phase column baseline, and the layout-mode-vs-visitor_text comparison"
    verification:
      - kind: other
        ref: "test -s .planning/phases/38-structural-indentation-info-fields/38-GATE-EVIDENCE-01.md"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-08-01
status: complete
---

# Phase 38 Plan 01: Structural Indentation Nesting Fixture + Gate Module Summary

**One `desc_content_indent_render_gate` fixture and a 13-assertion pypdf layout-mode gate module recorded RED (6) / GREEN-as-control (7) against the untouched translator, with two pre-existing out-of-scope `self.body.append` table-cell bugs discovered and documented.**

## Performance

- **Duration:** ~55 min
- **Started:** 2026-08-01T20:00:00+09:00 (approx.)
- **Completed:** 2026-08-01T20:45:05+09:00
- **Tasks:** 3
- **Files created:** 4

## Accomplishments

- Built one Sphinx fixture project (`tests/fixtures/desc_content_indent_render_gate/`) exercising a three-level `py:class::`/`py:method::`/`py:attribute::` nest with a field list, a resumed class body, a sibling top-level function, a body-less confval CONTROL, a list-item desc CONTROL, a table-cell CONTROL, a page-boundary class whose body genuinely spans two compiled pages, a no-desc/no-field-list CONTROL, and a block quote CONTROL — all in one `-b typst` build that compiles to a 10-page PDF.
- Wrote `tests/test_desc_content_indent_render_gate.py`: 13 test functions, one per IND-01..IND-05/FLD-01/D-04/D-11 property, every expected token and column comparison hand-derived from `38-EMISSION-CONTRACT.md`. Result against the untouched translator: 6 failed (structural token/count/column mismatches, never a `TypstError`), 7 passed (genuine non-regression controls).
- Recorded `38-GATE-EVIDENCE-01.md`: verbatim pytest output, per-RED cause sentences, an explicit compile-exit-status statement, the SC#4 repo-wide grep re-run at discovery time (still exactly one `em`-literal), a full pre-phase left-edge column baseline table, and a side-by-side `pypdf` layout-mode-vs-`visitor_text` comparison on a genuinely non-zero-indent marker line.
- Discovered and documented two pre-existing, out-of-scope defects: `depart_desc_signature`'s two `self.body.append(...)` calls (Phase 37) and the `field_list` family's five `self.body.append(...)` sites (`38-EMISSION-CONTRACT.md` section 3.1) both independently abort the Typst compile for a desc or field list inside a table cell — confirmed with minimal repros, neither fixed (out of this plan's `typsphinx/`-untouched scope), both recorded for the plan that owns each fix.

## Task Commits

Each task was committed atomically:

1. **Task 1: Build the IND/FLD-01 nesting fixture** - `41dca3f` (test)
2. **Task 2: Write the IND/FLD-01 gate module with hand-derived expectations** - `d4251e7` (test)
3. **Task 3: Record the verbatim RED and the SC#4 discovery grep** - `31749d2` (docs)

## Files Created/Modified

- `tests/fixtures/desc_content_indent_render_gate/conf.py` - Fixture Sphinx config; `typst_documents` master-doc entry; `typst_elements.fontsize=18pt` to make the page-boundary construct's page count reproducible.
- `tests/fixtures/desc_content_indent_render_gate/index.rst` - The ten-construct fixture source (three-level nest, resumed body, sibling desc, bodyless CONTROL, list-item CONTROL, table-cell CONTROL, page-boundary case, no-desc CONTROL, block quote).
- `tests/test_desc_content_indent_render_gate.py` - The gate module: `_layout_lines`/`_leading_columns`/`_find_page_and_column` helpers, `TestDescContentIndentStructuralGate` (7 tests, .typ-text only), `TestDescContentIndentPdfGate` (6 tests, compiled-PDF column comparisons, `skipif`-gated on `typst`/`pypdf`).
- `.planning/phases/38-structural-indentation-info-fields/38-GATE-EVIDENCE-01.md` - RED/CONTROL evidence, SC#4 grep, column baseline, extraction-technique comparison, discovery notes.

## Decisions Made

- **Table-Cell CONTROL redesigned from a desc/field_list falsifier to plain content.** Investigation (two minimal repros, documented in the evidence file) proved ANY `desc` — regardless of id, parameters, or body — and ANY `field_list` inside a `list-table` cell aborts the Typst compile today, via two separate pre-existing `self.body.append(...)` bugs neither in this plan's scope to fix (`typsphinx/` stays untouched by this plan). Since Task 1's acceptance criteria requires the whole fixture to compile, the construct was changed to plain, desc-free table content, with the original falsifier's purpose deferred to whichever later plan fixes the underlying sites.
- **IND-03, IND-05, and the D-11/SIG-09 page-boundary assertion are non-regression controls, not RED assertions**, against the real untouched translator (all evaluate `0 == 0`, since nothing carries any indent yet). This differs from the plan's own acceptance-criteria wording, which anticipated all five (IND-01/02/03/05, FLD-01) failing; the plan's Task 3 explicitly authorizes and requires exactly this reclassification when it is discovered rather than assumed, and it is fully recorded in the evidence file with the reason each must still hold post-phase.
- **Page-boundary body made genuinely long (30 filler sentences)** rather than tuned to a precise byte offset, so the page-crossing property (D-11/SIG-09) is robust to minor future content changes rather than fragile against exact page arithmetic.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed a docutils comment silently swallowing the following block quote**
- **Found during:** Task 1 (fixture construction)
- **Issue:** A `..` docutils comment immediately followed by a more-indented block (no intervening visible paragraph) is parsed by docutils as comment continuation, silently dropping the following content — the block quote construct emitted zero bytes.
- **Fix:** Added an intro paragraph before the block quote, matching the pattern already used by every other construct in the fixture.
- **Files modified:** `tests/fixtures/desc_content_indent_render_gate/index.rst`
- **Verification:** Rebuilt and confirmed `quote(block: true, {` now appears in the emitted `.typ` and the block-quote sentinel reaches the compiled PDF.
- **Committed in:** `41dca3f` (Task 1 commit)

**2. [Rule 3 - Blocking, scope-bounded] Table-cell desc/field-list construct replaced with plain content**
- **Found during:** Task 1 (fixture construction)
- **Issue:** A `desc` (any shape) or a `field_list` inside a `list-table` cell aborts the entire Typst compile via `depart_desc_signature`'s (Phase 37) and the `field_list` family's (38-EMISSION-CONTRACT.md section 3.1) pre-existing `self.body.append(...)` bugs — blocking Task 1's "the emitted index.typ compiles" acceptance criterion.
- **Fix:** Per the SCOPE BOUNDARY guidance (this defect is not caused by this plan's own changes, and fixing `typsphinx/` is out of this plan's explicit scope), the Table-Cell CONTROL construct was changed to plain, desc-free table content rather than fixing the underlying source. The finding is fully documented in the fixture's own comments and in `38-GATE-EVIDENCE-01.md` rather than silently worked around.
- **Files modified:** `tests/fixtures/desc_content_indent_render_gate/index.rst`, `conf.py`
- **Verification:** Fixture now compiles end-to-end (10-page PDF); the discovery is recorded for the plan (38-06) that owns the `field_list` family's fix.
- **Committed in:** `41dca3f` (Task 1 commit)

---

**Total deviations:** 2 auto-fixed (1 bug, 1 scope-bounded workaround with full discovery documentation)
**Impact on plan:** Both were necessary for Task 1's fixture to compile at all; no scope creep — `typsphinx/` remains completely untouched by this plan (`git diff --stat` against the worktree base is empty for that directory).

## Issues Encountered

- Two real, pre-existing `self.body.append(...)` bugs (one Phase 37, one Phase 38-scoped-but-later-plan-owned) made "a desc/field_list inside a table cell" unbuildable as originally specified — resolved by redesigning the construct and recording the discovery, per above.
- A `pypdf` bisection was needed to isolate the exact cause of the initial compile failure (binary search on truncated `.typ` prefixes, then a heading-boundary-safe truncation, then a minimal standalone repro) — documented inline in the fixture's own comments so the reasoning is not lost.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The fixture and gate module are ready for plan 38-05 (which implements `visit_desc_content`/`depart_desc_content`'s `pad()` wrapper) and plan 38-06 (which implements `visit_field_list`'s pad step and fixes the field_list family's `self.body.append` sites) to flip the 6 RED node ids GREEN, while the 7 CONTROL node ids must stay GREEN.
- A follow-up item for 38-06 (or later): once the field_list family's five `self.body.append` sites are fixed, this fixture's Table-Cell CONTROL section can be extended with the originally-intended desc/field-list-in-table-cell falsifier — the finding and the exact blocking mechanism are fully recorded in `38-GATE-EVIDENCE-01.md`.
- `depart_desc_signature`'s table-cell bug (Phase 37, `typsphinx/translator.py:5051,5053`) remains open and out of this milestone's assigned scope; noted here so it is not lost if a future phase touches that handler.

---
*Phase: 38-structural-indentation-info-fields*
*Completed: 2026-08-01*

## Self-Check: PASSED

All created files verified present:
- FOUND: tests/fixtures/desc_content_indent_render_gate/conf.py
- FOUND: tests/fixtures/desc_content_indent_render_gate/index.rst
- FOUND: tests/test_desc_content_indent_render_gate.py
- FOUND: .planning/phases/38-structural-indentation-info-fields/38-GATE-EVIDENCE-01.md
- FOUND: .planning/phases/38-structural-indentation-info-fields/38-01-SUMMARY.md

All task commits verified present in git log:
- FOUND: 41dca3f (Task 1)
- FOUND: d4251e7 (Task 2)
- FOUND: 31749d2 (Task 3)
