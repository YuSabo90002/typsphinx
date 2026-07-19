---
phase: 18-fidelity-fixes-regression-gate-close
plan: 01
subsystem: rendering
tags: [typst, docutils, sphinx, translator, pdf, colwidth, fr-columns, zwsp]

# Dependency graph
requires:
  - phase: 17-rendering-fidelity-audit
    provides: "FID-01a (F12 wide-table overflow) as the sole high-severity fix backlog item, with a minimal-repro pointer (extdev/deprecated grid table)"
provides:
  - "depart_table emits columns: (Nfr, Mfr, ...) built from docutils colspec['colwidth'] instead of columns: <integer>"
  - "visit_colspec captures colwidth into self.table_colwidths instead of discarding it via SkipNode alone"
  - "visit_literal injects U+200B zero-width space after '.'/'_' in in-table raw() content, gated on self.in_table"
  - "A new real-compile GATE-01 fixture (tests/test_wide_table_render_gate.py) proving the collision-absence regression, RED-verified pre-fix and GREEN-verified post-fix"
affects: [18-02-gate-close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "fr-weighted Typst table columns sourced from docutils colwidth (no GCD/percentage normalization -- raw ints used directly as fr weights)"
    - "in-table-gated ZWSP (chr(0x200B)) injection at natural break points ('.'/'_') as the durable workaround for Typst's lack of overlong-word wrapping (typst/typst#674)"

key-files:
  created:
    - tests/test_wide_table_render_gate.py
    - tests/fixtures/wide_table_render_gate/conf.py
    - tests/fixtures/wide_table_render_gate/index.rst
  modified:
    - typsphinx/translator.py
    - tests/test_table_in_list_item_render_gate.py

key-decisions:
  - "D-01/D-02 implemented exactly as locked: fr-columns applied uniformly to every table, sourced from raw colwidth ints with an equal-1fr fallback for missing/zero/length-mismatched data."
  - "D-03 unchanged: visit_tabular_col_spec stays raise nodes.SkipNode -- tabularcolumns is LaTeX-only and the HTML fidelity authority ignores it."
  - "Fixture collision-assertion redesigned during Task 1 (Claude's discretion per 18-RESEARCH.md): the plan/research's literal 'TARGET_SENTINEL + DEPRECATED_SENTINEL' concatenation check never matches this fixture's actual content shape (the sentinel is followed by a '_long_path' suffix before the cell boundary), so the working collision-absence proof checks the cell's actual tail boundary ('_long_path' + '8.7') instead -- verified this is the exact zero-separator signature that reproduces pre-fix and disappears post-fix."

requirements-completed: [FID-01, FID-01a]

coverage:
  - id: D1
    description: "fr-columns emitted from colwidth (visit_colspec capture + depart_table _build_columns_fr_arg emission at both sites), with equal-1fr fallback for missing/zero/length-mismatched colwidth"
    requirement: "FID-01a"
    verification:
      - kind: unit
        ref: "tests/test_translator.py::test_table_conversion"
        status: pass
    human_judgment: false
  - id: D2
    description: "In-table inline-literal content gets U+200B injected after '.'/'_' (visit_literal, gated on self.in_table); prose/code-block literals stay byte-unchanged"
    requirement: "FID-01a"
    verification:
      - kind: integration
        ref: "tests/test_wide_table_render_gate.py::TestWideTableRenderGate::test_wide_table_pdf_has_no_column_collision"
        status: pass
    human_judgment: false
  - id: D3
    description: "Real-compile FID-01a regression gate (RED pre-fix at the collision-absence assertion, GREEN post-fix) via sphinx-build -b typstpdf + pypdf text-extraction"
    requirement: "FID-01a"
    verification:
      - kind: integration
        ref: "tests/test_wide_table_render_gate.py::TestWideTableRenderGate::test_wide_table_pdf_has_no_column_collision"
        status: pass
    human_judgment: false
  - id: D4
    description: "Stale byte-exact columns: 2 assertion in test_table_in_list_item_render_gate.py updated to columns: (50fr, 50fr); full offline suite green"
    verification:
      - kind: unit
        ref: "tests/test_table_in_list_item_render_gate.py::TestTableInListItemRenderGate::test_typstpdf_separates_table_in_list_item_and_produces_pdf"
        status: pass
      - kind: unit
        ref: "pytest -m 'not slow' -q (477 passed, 23 deselected)"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-07-19
status: complete
---

# Phase 18 Plan 01: FID-01a Wide-Table Fix Summary

**depart_table now emits fr-weighted `columns: (Nfr, ...)` from docutils colwidth, and visit_literal injects U+200B after `.`/`_` in in-table raw() content, closing the audit's sole high-severity wide-table collision bug.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-07-19T13:48:00Z
- **Completed:** 2026-07-19T13:54:37Z
- **Tasks:** 3
- **Files modified:** 5 (2 new fixture files, 1 new test file, 1 translator.py edit, 1 stale-assertion update)

## Accomplishments

- `visit_colspec` now captures `colwidth` into a new `self.table_colwidths` per-table accumulator (init in `visit_table`/`__init__`, reset in `depart_table`) instead of discarding it via bare `SkipNode`.
- New `_build_columns_fr_arg()` helper builds a Typst `(Nfr, Mfr, ...)` tuple from the captured widths, with an equal-`1fr`-per-column fallback when data is missing, all-zero, or length-mismatched — never an empty `columns: ()` or a non-positive weight.
- `depart_table`'s two `columns: {colcount}` emission sites (the LEN-01 `block(width:...)`-wrapped branch and the unwrapped branch) both now call `_build_columns_fr_arg()`.
- `visit_literal` injects `chr(0x200B)` (zero-width space) after every `.` and `_` in `raw()` content when `self.in_table` is true — the second, necessary half of the fix (fr-columns alone do not wrap an unbroken dotted/underscored token; verified empirically in 18-RESEARCH.md's "Critical Finding").
- A new real-compile fixture (`tests/test_wide_table_render_gate.py` + `tests/fixtures/wide_table_render_gate/`) proves the fix via `sphinx-build -b typstpdf` → `pypdf` text-extraction, asserting the absence of the audit's exact cross-column glyph-collision signature. Confirmed RED on the pre-fix translator (failed at the collision-absence assertion), confirmed GREEN after both fix halves landed.
- The one stale byte-exact `columns: 2` assertion in `tests/test_table_in_list_item_render_gate.py` updated to `columns: (50fr, 50fr)`.
- Full offline suite (`pytest -m "not slow" -q`): 477 passed, 23 deselected. `black --check .`, `ruff check .`, `mypy typsphinx/` all clean.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add the RED wide-table render-gate fixture + failing acceptance test** - `c55bab8` (test)
2. **Task 2: Implement the two-part FID-01a fix in translator.py** - `a86536e` (feat)
3. **Task 3: Update the stale byte-exact columns assertion** - `6b0ab2b` (test)

_Note: no TDD-mode multi-commit cycle was used (this plan is `tdd_mode: false` per config); each task is a single atomic commit._

## Files Created/Modified

- `tests/fixtures/wide_table_render_gate/conf.py` - Minimal Sphinx project declaring `index` as a typst master document
- `tests/fixtures/wide_table_render_gate/index.rst` - Wide `list-table` with double-backtick inline-literal cells carrying collision sentinels, mirroring `extdev/deprecated`'s repro shape
- `tests/test_wide_table_render_gate.py` - Real-compile GATE-01 acceptance gate for FID-01a; DESC-02-style collision-absence idiom
- `typsphinx/translator.py` - `visit_colspec` colwidth capture, `self.table_colwidths` accumulator, `_build_columns_fr_arg()` helper, fr-column emission at both `depart_table` sites, in-table-gated ZWSP injection in `visit_literal`
- `tests/test_table_in_list_item_render_gate.py` - Updated stale `columns: 2` → `columns: (50fr, 50fr)` byte-exact assertion

## Decisions Made

- **Fixture collision-assertion redesign (Task 1, Claude's discretion per 18-RESEARCH.md "Regression-fixture proof design").** The plan/research's literal `WIDE_TABLE_TARGET_SENTINEL + WIDE_TABLE_DEPRECATED_SENTINEL` concatenation check can never match this fixture's actual content (the rst embeds the sentinel followed by a `_long_path` suffix before the cell boundary, per the research doc's own verified fixture content — `sentinel_long_path` then `8.7`). Verified empirically this session (direct `pypdf` extraction on the pre-fix translator) that the real zero-separator collision boundary is `"_long_path" + "8.7"`, not `"SENTINEL" + "8.7"`. Redesigned the assertion to check this actual tail-boundary substring — confirmed it correctly reproduces RED pre-fix (failed exactly at this assertion, not earlier/later) and GREEN post-fix. This is the "regression-fixture proof design" explicitly left to researcher/planner/executor discretion in 18-CONTEXT.md; no architectural change, no user decision needed (Rule 1 — the original design was a genuine bug that would have made the test a false-negative).
- D-01/D-02/D-03 implemented exactly as locked in 18-CONTEXT.md — no deviations from the locked decisions themselves.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed the wide-table fixture's collision-absence assertion to actually detect the collision**
- **Found during:** Task 1 (RED-proof verification)
- **Issue:** The plan/research-specified assertion `WIDE_TABLE_TARGET_SENTINEL + WIDE_TABLE_DEPRECATED_SENTINEL not in full_text` never fails against the pre-fix translator, because the fixture's actual rst content (also per research's own verified example) places a `_long_path` suffix between the sentinel and the cell boundary — so the concatenated string never appears in the extracted text regardless of whether the bug is present. Running the test against the unfixed translator showed it passing this assertion and failing instead at an unrelated later structural check, which is NOT the required RED-first failure mode (the plan's acceptance criteria explicitly require failure "at the collision-absence assertion... not at compile/collect time").
- **Fix:** Replaced the assertion with a check on the actual observed zero-separator boundary text (`WIDE_TABLE_TARGET_TAIL + WIDE_TABLE_DEPRECATED_SENTINEL`, i.e. `"_long_path8.7"`), derived by directly inspecting the pre-fix translator's real extracted PDF text this session. Verified this correctly fails RED pre-fix (at the intended assertion) and passes GREEN post-fix.
- **Files modified:** tests/test_wide_table_render_gate.py
- **Verification:** Ran the fixture against the pre-fix translator (failed at the collision assertion, confirmed by traceback line number); ran again post-fix (passed).
- **Committed in:** c55bab8 (Task 1 commit; the corrected version, no separate fix-up commit needed since this was caught before the initial commit)

---

**Total deviations:** 1 auto-fixed (1 bug fix, discovered and corrected before the Task 1 commit)
**Impact on plan:** Necessary for the fixture to actually serve as a valid regression proof (SC#1's core requirement). No scope creep — the fixture's intent (collision-absence proof at this exact cell boundary) is unchanged, only the concrete string comparison was corrected to match the fixture's real content shape.

## Issues Encountered

None beyond the deviation documented above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- FID-01a is fixed and proven with a real-compile regression fixture; `test_translator.py::test_table_conversion` and `test_table_in_list_item_render_gate.py` both green; full offline suite (477 tests) green; lint/format/type gates all clean.
- No new runtime dependency added; `visit_tabular_col_spec` unchanged (D-03); `writer.py`/`template_engine.py`/`templates/base.typ` `@preview` version-sync surface untouched (SC#4 — will be re-confirmed at 18-02's gate close).
- Plan 18-02 (GATE-03 corpus close) can now proceed: re-run `tests/test_corpus_gate.py::TestCorpusRenderGate -m slow` against the full ~684-page corpus to confirm the fr-columns change (applied to every table, D-02) does not introduce a NEW fatal error corpus-wide, and that the `unknown_visit` catalogue stays empty of `todo_node`/`manpage`.
- Known residual risk (documented in 18-RESEARCH.md Assumption A2, explicitly out of Phase 18's locked scope): a corpus table OTHER than `extdev/deprecated` with similarly unbroken long literal content could still collide after this fix — GATE-03's corpus re-run only catches fatal-error regressions, not a new silent collision instance. Any such finding would be a future-audit candidate, not a Phase 18 regression.

## Self-Check: PASSED

All created/modified files confirmed present on disk; all 4 commits
(`c55bab8`, `a86536e`, `6b0ab2b`, `1bed215`) confirmed present in `git log`.

---
*Phase: 18-fidelity-fixes-regression-gate-close*
*Completed: 2026-07-19*
