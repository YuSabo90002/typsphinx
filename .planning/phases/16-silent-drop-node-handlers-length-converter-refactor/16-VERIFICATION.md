---
phase: 16-silent-drop-node-handlers-length-converter-refactor
verified: 2026-07-16T13:55:00Z
status: human_needed
score: 11/12 must-haves verified
behavior_unverified: 0
overrides_applied: 0
behavior_unverified_items: []
human_verification:
  - test: "Feed a manpage node whose Text child is empty or whitespace-only (would require a synthetic docutils tree; not reachable through normal rST parsing of the `:manpage:` role) through visit_manpage/depart_manpage and confirm it emits a well-formed emph() call that does not abort typst.compile()."
    expected: "A well-formed (possibly empty) emph({...}) call is emitted; the document still compiles."
    why_human: "16-02-PLAN.md tags this truth `verification: backstop` and states no fixture case exists because rST interpreted-text roles cannot normally be empty. No test, fixture, or direct observation in the codebase exercises this path (grep for an empty/whitespace emphasis case in tests/ returns nothing) — per the honest-verifier protocol, symbol presence/delegation to visit_emphasis is not explicit evidence for a non-inferable (backstop) truth, so this must abstain rather than be marked VERIFIED."
---

# Phase 16: Silent-Drop Node Handlers + Length-Converter Refactor Verification Report

**Phase Goal:** The last two node types the v0.6.0 warning audit confirmed are still silently `unknown_visit`-dropped in the Sphinx corpus (`todo_node` ×10, `manpage` ×10) render their content, and v0.6.0's `visit_image`-local px→pt conversion is generalized into a single shared helper reused at every length-bearing site.
**Verified:** 2026-07-16T13:55:00Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A `.. todo::` body renders inside a gentle-clues `task()` box titled "Todo" in the compiled PDF when `todo_include_todos=True` (ROADMAP SC1, D-01) | VERIFIED | `typsphinx/translator.py:3874-3900` `visit_todo_node`/`depart_todo_node`; `tests/test_pdf_render_gate.py::TestTodoRenderGate::test_todo_pdf_renders_body_and_title` PASSED in a real `sphinx-build → typst.compile() → pypdf` run (`uv run pytest tests/test_pdf_render_gate.py -q` → 24 passed) |
| 2 | Building the same fixture with `todo_include_todos=False` (default) emits neither the todo body nor a `task(` call — internal notes never leak (T-16-01 prohibition, verification: test) | VERIFIED | `test_todo_typ_omits_body_when_todo_include_todos_false` PASSED; `visit_todo_node` gates with `raise nodes.SkipNode` before `_visit_admonition` |
| 3 | The `:manpage:` role's literal page-reference text renders in the compiled PDF in all three contexts — plain paragraph, list item, figure caption (ROADMAP SC2, D-02) | VERIFIED | `typsphinx/translator.py:1035-1064` `visit_manpage`/`depart_manpage` delegate fully to `visit_emphasis`/`depart_emphasis`; `TestManpageRenderGate::test_manpage_pdf_renders_italic_text` PASSED — pypdf-extracted text contains `ls(1)`, `grep(1)`, `tar(1)` |
| 4 | No external manpage URL/link is ever fabricated — `manpages_url` unset renders literal text only, never `link()` (D-02a prohibition, verification: test) | VERIFIED | Same test asserts `"link(" not in typ_source`; fixture's `conf.py` contains no `manpages_url` |
| 5 | Generated `.typ` contains exactly 3 `emph({` wrappers for the 3 `:manpage:` uses, and the real compile succeeds (encoding edge) | VERIFIED | Same test asserts `typ_source.count("emph({") == 3`; real `typst.compile()` (no try/except) succeeds |
| 6 | A manpage node with an empty/whitespace-only Text child emits a well-formed `emph()` call that does not abort compile (backstop truth, D-02) | ⚠️ UNCONFIRMED (insufficient_spec) | No fixture/test exercises this path; 16-02-PLAN.md itself flags it as "confirm only if explicit evidence surfaces" and states rST cannot normally produce it. Routed to human verification — never scored as VERIFIED on delegation/presence alone |
| 7 | Building the todo/manpage fixtures emits no `unknown node type` warning on stderr (TODO-01/MAN-01 warnings eliminated) | VERIFIED | Both render-gate test classes assert `"unknown node type" not in result.stderr`; both pass |
| 8 | Exactly one `_convert_length_to_typst` implementation exists, and every length-bearing site (`visit_image`, `visit_figure`, `depart_table`) obtains lengths only by calling it (ROADMAP SC3, D-03b) | VERIFIED | `grep -c 'def _convert_length_to_typst' typsphinx/translator.py` → 1; call sites at lines 1956 (figure), 2286 (table), 2618/2623 (image); `grep -cE '0\.75\|\* 12'` → 4 (unchanged, all inside the one helper — no duplicated arithmetic) |
| 9 | `figure :figwidth:` px converts at the exact CSS-canonical 0.75 ratio (400px→300pt) and `%` passes through unchanged; unsupported units (figwidth/table width `ex`) drop with exactly one warning each and never leak the raw unit into `.typ` (D-03/D-03b) | VERIFIED | `typsphinx/translator.py:1944-1965` (visit_figure) and `:2273-2317` (depart_table); `TestFigureFigwidthRenderGate::test_figwidth_pdf_wraps_block_and_compiles` and `TestTableWidthRenderGate::test_table_width_pdf_wraps_block_and_compiles` PASSED |
| 10 | Table width wiring covers `.. table::`, `.. csv-table::`, `.. list-table::` through the single `nodes.table` visitor (D-03a — previously-ignored lengths now wired) | VERIFIED | `depart_table` reads `node.get("width")` once, shared by all three directive types via docutils' `Table.set_table_width()`; `TestTableWidthRenderGate` fixture exercises all three directive types in one document and passes |
| 11 | `visit_image` behavior is unchanged (behavior-preserving refactor at the load-bearing v0.6.0 call site) | VERIFIED | `TestFigureLengthRenderGate::test_figure_length_pdf_converts_px_and_drops_unknown_unit` (pre-existing gate) still PASSES unmodified; `visit_image`/`depart_image` untouched by this phase's diff |
| 12 | With multiple width-bearing figures/tables in one document, each `block(width:)` wrapper pairs with exactly its own figure/table call in document order (backstop truth, D-03/ordering) | VERIFIED | Explicit evidence observed directly: `figure_length_render_gate/index.rst` contains 3 width-bearing figures (400px/75%/60% captionless) plus a list-item-nested figure in one document, and `table_width_render_gate/index.rst` contains 3 width-bearing tables (table/list-table/csv-table) in one document — both fixtures `typst.compile()` fatal-free (verified by direct test run), which requires every `block(width:)[...]` bracket pair to be correctly balanced and ordered |

**Score:** 11/12 truths verified (1 routed to human verification per the honest-verifier backstop protocol — never silently passed)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `typsphinx/translator.py::visit_todo_node`/`depart_todo_node` | New handler pair, config-gated | ✓ VERIFIED | Lines 3874-3904; gates on `self.config.todo_include_todos` before `_visit_admonition` |
| `typsphinx/translator.py::visit_manpage`/`depart_manpage` | New handler pair, full delegation | ✓ VERIFIED | Lines 1035-1064; body is exactly `self.visit_emphasis(node)` / `self.depart_emphasis(node)` |
| `typsphinx/translator.py::_convert_length_to_typst` wiring | New calls in `visit_figure`/`depart_figure`/`depart_table` | ✓ VERIFIED | Lines 1944-1965 (figure), 2273-2317 (table); single helper at line 3116 |
| `tests/fixtures/todo_render_gate/{conf.py,index.rst}` | New GATE-01 fixture | ✓ VERIFIED | Both files exist; `todo_include_todos = True`, sentinel `TODOBODYSENTINEL9X4` present |
| `tests/fixtures/manpage_render_gate/{conf.py,index.rst,image.png}` | New GATE-01 fixture, 3 contexts | ✓ VERIFIED | All three files exist; index.rst has `:manpage:` in paragraph/list-item/figure-caption |
| `tests/fixtures/table_width_render_gate/{conf.py,index.rst}` | New GATE-01 fixture, 3 directive types | ✓ VERIFIED | Both files exist; `.. table::`/`.. list-table::`/`.. csv-table::` each carry `:width:` |
| `tests/fixtures/figure_length_render_gate/index.rst` | Extended with `:figwidth:` cases | ✓ VERIFIED | Appended 400px/75%/5ex/list-item/captionless sections; pre-existing image `:width:` cases unmodified |
| `tests/test_pdf_render_gate.py::TestTodoRenderGate` | 2 tests | ✓ VERIFIED | Both pass |
| `tests/test_pdf_render_gate.py::TestManpageRenderGate` | 1 test | ✓ VERIFIED | Passes |
| `tests/test_pdf_render_gate.py::TestFigureFigwidthRenderGate` | 2 tests (incl. CR-01 regression) | ✓ VERIFIED | Both pass |
| `tests/test_pdf_render_gate.py::TestTableWidthRenderGate` | 1 test | ✓ VERIFIED | Passes |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `visit_todo_node` | `_visit_admonition(node, "task", custom_title="Todo")` | Direct call, gated by `nodes.SkipNode` | ✓ WIRED | Confirmed in source; gentle-clues `task` clue pinned at 1.3.1, unchanged |
| `self.config.todo_include_todos` | `raise nodes.SkipNode` | Config-gate at top of `visit_todo_node` | ✓ WIRED | Test 2 above proves the gate fires |
| `visit_manpage` | `self.visit_emphasis(node)` | Full delegation | ✓ WIRED | Same for `depart_manpage`/`depart_emphasis`; no bespoke logic added |
| `visit_figure` → `self._convert_length_to_typst(figwidth)` → `block(width:)[#figure(` | figwidth wiring | Convert-once-at-visit, consume-at-depart via `self._figure_block_width` | ✓ WIRED | Verified in source and by passing real-compile test |
| `depart_table` → `self._convert_length_to_typst(width)` → `block(width:)[#table(` | table width wiring | `self.body.append` (not `self.add_text`) | ✓ WIRED | Verified in source and by passing real-compile test |
| `visit_figure`/`in_list_item` separator | `list_item_needs_separator` check before opening the wrapper | CR-01 fix | ✓ WIRED | Present at translator.py:1940-1942; regression test `test_figwidth_figure_as_list_item_non_first_element_compiles` passes |

### Behavioral Spot-Checks / Real-Compile Gates

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full render-gate suite (24 tests, includes all 4 new/extended Phase 16 classes) | `uv run python -m pytest tests/test_pdf_render_gate.py -q` | `24 passed in 5.75s`, 0 skipped | ✓ PASS |
| Corpus GATE-03: `unknown_visit` catalogue is empty against the real cloned Sphinx `doc/` corpus | `uv run python -m pytest tests/test_corpus_gate.py -q` | `4 passed, 1 skipped` (the 1 skip is the unrelated, intentionally env-gated SC#3 report test) | ✓ PASS |
| Full project test suite | `uv run python -m pytest -q` | `498 passed, 1 skipped in 40.76s` | ✓ PASS |
| Format | `uv run black --check .` | `All done! 122 files would be left unchanged.` (exit 0) | ✓ PASS |
| Lint | `uv run ruff check .` | `All checks passed!` (exit 0) | ✓ PASS |
| Types | `uv run mypy typsphinx/` | `Success: no issues found in 6 source files` (exit 0) | ✓ PASS |
| Single-converter invariant | `grep -c 'def _convert_length_to_typst' typsphinx/translator.py` | `1` | ✓ PASS |
| No duplicated conversion arithmetic | `grep -cE '0\.75\|\* 12' typsphinx/translator.py` | `4` (matches plan's pre-committed expectation — all inside the one helper) | ✓ PASS |

### Post-Execution Events (verified independently, not taken on SUMMARY claim)

- **`tests/test_corpus_gate.py` assertion flip (commit `bc664b1`):** confirmed present in git log; the flipped assertion (`assert not catalogue`) is live in the file at lines 349-358 and was re-run against the real corpus in this verification pass (PASSED, not skipped).
- **16-REVIEW.md CR-01 (missing in-list-item separator in `visit_figure`) fixed in `ef17c69`:** confirmed present in git log; fix confirmed in source at `translator.py:1930-1942`; regression test `test_figwidth_figure_as_list_item_non_first_element_compiles` confirmed present and PASSING.
- **16-REVIEW.md WR-01 (no coverage for captionless figwidth branch) fixed in `0286b79`:** confirmed present in git log; the captionless `:figwidth: 60%` fixture section confirmed present in `figure_length_render_gate/index.rst`; the no-label branch (`depart_figure` line 1992-1996) confirmed in source.
- **WR-02 (todo handler type-hint looseness):** confirmed no action taken (`node: nodes.Element`, not the precise `todo_node` type) — matches 16-REVIEW-FIX.md's stated "no action required" disposition; not a functional gap.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| TODO-01 | 16-01-PLAN.md | `.. todo::` renders body, warning eliminated | ✓ SATISFIED | Truths 1, 2, 7 above; `TestTodoRenderGate` (2/2 passing) |
| MAN-01 | 16-02-PLAN.md | `:manpage:` renders literal text, warning eliminated | ✓ SATISFIED (with 1 human-review flag on a documented backstop edge case) | Truths 3, 4, 5, 7 above; `TestManpageRenderGate` (1/1 passing); truth 6 is an explicitly-flagged, plan-declared unconfirmable edge case, not a gap in the requirement's core behavior |
| LEN-01 | 16-03-PLAN.md | Single shared length converter, wired at every length-bearing site | ✓ SATISFIED | Truths 8, 9, 10, 11, 12 above; `TestFigureFigwidthRenderGate` + `TestTableWidthRenderGate` + pre-existing `TestFigureLengthRenderGate` all passing |

No orphaned requirements: REQUIREMENTS.md maps exactly TODO-01, MAN-01, LEN-01 to Phase 16 (lines 60-62), and all three appear in a plan's `requirements:` frontmatter field (16-01, 16-02, 16-03 respectively).

### Anti-Patterns Found

None. Scanned all files modified in this phase (`typsphinx/translator.py`, `tests/test_pdf_render_gate.py`, `tests/test_corpus_gate.py`, and all new/extended fixture files) for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER`/empty-implementation patterns. The only matches were the literal substring "TODO" inside the requirement ID `TODO-01` (a naming coincidence, not a debt marker) — confirmed by word-boundary re-check excluding `TODO-01` occurrences, which returned zero matches.

### Human Verification Required

### 1. Empty/whitespace-only manpage Text child

**Test:** Construct (or synthesize via a docutils tree fixture) a `manpage` node whose sole Text child is empty or whitespace-only, and run it through `visit_manpage`/`depart_manpage` → `typst.compile()`.
**Expected:** A well-formed (possibly empty) `emph({...})` call is emitted; the document compiles without aborting.
**Why human:** 16-02-PLAN.md explicitly tags this truth `verification: backstop` and states no fixture case exists because rST's `:manpage:` interpreted-text role cannot normally produce an empty child through standard parsing — "confirm only if explicit evidence surfaces." No test, fixture, or direct observation in the codebase exercises this path. Per the honest-verifier protocol (non-inferable truths require a wired held-out test or directly-observed behavior — symbol presence/delegation is not sufficient evidence), this must be routed to human review rather than marked VERIFIED on the strength of `visit_manpage`'s delegation to `visit_emphasis` alone. This is a low-risk, plan-acknowledged edge case, not a sign of missing core functionality — TODO-01/MAN-01/LEN-01's primary behaviors are all independently, behaviorally verified above.

### Gaps Summary

No blocking gaps. All three requirement IDs (TODO-01, MAN-01, LEN-01) are behaviorally verified through real `sphinx-build → typst.compile() → pypdf` round trips (24/24 render-gate tests passing, including the two post-review regression tests for CR-01 and WR-01), the full project test suite is green (498 passed, 1 unrelated skip), lint/type/format are clean, and the corpus-level GATE-03 steady state (empty `unknown_visit` catalogue) is independently re-confirmed against the real Sphinx corpus in this verification pass. The single open item is a plan-declared, low-probability backstop edge case (an empty/whitespace `:manpage:` body, which standard rST parsing cannot produce) that has no test coverage and therefore cannot be marked VERIFIED under the honest-verifier protocol — it is surfaced for a human decision (accept as out-of-scope / add a synthetic-tree regression test) rather than silently passed or treated as a blocking failure.

---

_Verified: 2026-07-16T13:55:00Z_
_Verifier: Claude (gsd-verifier)_
