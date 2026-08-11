---
phase: 43-table-state-correctness-nested-tables-empty-title-anchors
verified: 2026-08-04T02:20:24Z
status: passed
score: 6/6 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification: false
---

# Phase 43: Table State Correctness — Nested Tables + Empty-Title Anchors Verification Report

**Phase Goal:** A document whose tables nest, or whose table caption renders to nothing, produces
the table the source describes; a nested figure no longer drops the outer caption; and
`_emit_id_anchors`'s docstring names its actual callers.

**Verified:** 2026-08-04T02:20:24Z
**Status:** passed
**Re-verification:** No — initial verification

## Important context this verification accounts for

This phase did **not** land cleanly on the first pass. Plans 43-01 through 43-05 executed and
reported complete, but the phase's own code review (`43-REVIEW.md`) then found a **BLOCKER
(CR-01)**: `visit_legend`/`depart_legend` (added by plan 43-03 for FIG-01) saved
`in_list_item`/`list_item_needs_separator` into flat instance-attribute scalars instead of a real
stack. A figure whose legend itself contains a legend-bearing figure clobbered those scalars,
leaking `in_list_item=True` into every sibling for the rest of the document — silently wrong Typst
output, exit 0, no warning. This is exactly the same defect *class* the phase's own TBL-04/FIG-01
fixes (`_table_state_stack`/`_figure_state_stack`) were written to eliminate, just missed for the
one piece of state `visit_legend`/`depart_legend` touched directly.

Gap-closure plan 43-06 fixed it (`self._legend_list_item_stack: List[Tuple[bool, bool]]`, mirroring
the pre-existing `self._list_item_stack` pattern), added a regression fixture/test exercising
exactly the legend-in-legend shape, and `43-GATE-EVIDENCE-05.md`/`-06.md` were **regenerated**
against the new tip (the originals were superseded, not silently left stale).

This verification re-measured the CR-01 fix independently (see "CR-01 fix scrutiny" below) rather
than accepting `43-06-SUMMARY.md`'s claim, and spot-checked the regenerated SC#4/SC#5 evidence for
the two guards the task specifically flagged (two distinct `typsphinx.__file__` paths; a genuinely
non-empty positive control) — both are present and were freshly re-run against the CR-01-fixed tip,
not carried forward from the superseded run.

## Goal Achievement

### Observable Truths (roadmap Success Criteria 1–6)

| # | Truth (roadmap SC) | Status | Evidence |
|---|---|---|---|
| 1 | SC#1 (TBL-04) — a table nested inside another table's cell no longer clobbers the enclosing table's cells, column count, column widths and caption; the fix generalizes over shape and depth | ✓ VERIFIED | `_push_table_state`/`_pop_table_state` (translator.py:3349-3417) implement a real stack, guarded pop (`if not self._table_state_stack: return`). Independently ran `tests/test_nested_table_render_gate.py` (7 tests: list-in-list, grid-in-list, list-in-grid, 3-level nest, header-cell nest, adjacency/empty/siblings, top-level control) — all 7 **PASS** in this session. `43-GATE-EVIDENCE-01.md` records a real RED (unfixed translator, base `7bdaf40`) before the fix. |
| 2 | SC#2 (TBL-05) — a captioned table whose title renders to an empty/whitespace string still emits its id anchors (rendering stays gated on `self.table_caption` truthiness; anchoring gated on the structural `_table_is_captioned`, per D-05's LaTeX-matching split) | ✓ VERIFIED | `depart_table` (translator.py:3609-3820): `structural_is_captioned = self._table_is_captioned` drives the anchor call independently of `was_captioned` (the rendering/figure-wrap gate). Ran `tests/test_table_empty_caption_anchor_render_gate.py` — both tests **PASS**, including the assertion that a real captioned table later in the same doc still renders `Table 1: TECREALCAP` (not shifted to `Table 2`). `43-GATE-EVIDENCE-04.md` records a real pre-fix `TypstError: label ... does not exist` RED (exit 2, zero PDF) via a Sphinx-driven doctree probe confirming the `raw`-node/`astext()` divergence (D-07). |
| 3 | SC#3 (QUA-01) — `_emit_id_anchors`'s docstring names its actual callers, no surviving claim that `depart_figure` is the sole `skip_ids` user | ✓ VERIFIED | Read `_emit_id_anchors`'s docstring (translator.py:545-628): "There are two such callers, `depart_figure` and `depart_table` (Phase 25)..." — no "sole"/"only" claim remains (`grep` for those terms near `skip_ids`/`_emit_id_anchors` returns nothing). Independently re-grepped: 21 total `_emit_id_anchors` call sites, 2 pass `skip_ids` — matches D-08's measured count exactly. |
| 4 | SC#4 — no collateral change to existing output: full pytest suite, black/ruff/mypy, and the full-corpus `-b typstpdf` gate are green; documents with no nested table/figure/empty-titled caption emit byte-identical `.typ` across the whole phase's change (through the CR-01 gap closure) | ✓ VERIFIED | Independently ran `uv run python -m pytest -q` → **837 passed, 1 skipped** (matches orchestrator's figure exactly); `black --check .`, `ruff check .`, `mypy typsphinx/` all green. Independently ran `tox -e docs-pdf` (this project's own doc corpus, `-b typstpdf`) → **"build succeeded, 2 warnings"**, PDF generated; the 2 warnings are pre-existing `visit_toctree` docstring formatting issues, confirmed **not** touched by this phase's diff (absent from `git diff 7bdaf40..61296f9 -- typsphinx/`). `43-GATE-EVIDENCE-05.md` was regenerated against the CR-01-fixed tip with both required guards present and freshly re-run: two distinct `typsphinx.__file__` paths (§3, resolving into two separate `git archive` exports, not the main checkout) and a genuinely non-empty positive control (§5, the `nested_table_render_gate` diff, which the file explicitly distinguishes from `nested_figure_render_gate` — a "measured divergence from the premise" the evidence author caught and corrected rather than silently complying with a wrong assumption). Independently confirmed the production diff is isolated: `git diff --stat 7bdaf40..61296f9 -- typsphinx/ pyproject.toml uv.lock` → only `typsphinx/translator.py`, `518 insertions(+), 53 deletions(-)` — matches both the evidence file's and the orchestrator's figures exactly. |
| 5 | SC#5 — the milestone branch reached `origin` during this phase (not at the release PR), and a COMPLETED CI run including both Windows lanes ran against it | ✓ VERIFIED | Independently ran `git ls-remote --heads origin gsd/v0.7.1-bug-fix-round` → `1a3b3c85ea4dbbdefade23ef43f0a9e758a93e52`. Independently ran `gh run view 30870536482 --json status,conclusion,headSha` → `{"conclusion":"success","headSha":"1a3b3c8...","status":"completed"}` — same SHA. Confirmed `4ea6400` (the CR-01 fix) is an ancestor of `1a3b3c8`, and that no `typsphinx/`, `pyproject.toml`, or `uv.lock` changes landed between `1a3b3c8` and the current tip `61296f9` (`git diff --stat` empty) — so the completed CI run genuinely covers the code at the phase's actual current tip. `43-GATE-EVIDENCE-06.md` independently confirms all 12 lanes `success` including both named Windows lanes (`Test Python 3.12 on windows-latest`, `Test Python 3.13 on windows-latest`) and documents a real, useful finding: `ci.yml`'s `on.push` only fires for `main`/`develop`, so the milestone branch's CI had to be triggered via `workflow_dispatch` explicitly — this correction is recorded transparently, not glossed over. |
| 6 | SC#6 (FIG-01) — a figure nested inside another figure's legend compiles with both figures' captions/ids/state surviving; no `unknown node type: <legend>` warning | ✓ VERIFIED | `visit_legend`/`depart_legend` (translator.py:2714-2789) exist and handle the docutils `legend` node. `_push_figure_state`/`_pop_figure_state` (translator.py:3419-3472) implement a guarded stack for the figure scalar set. Independently ran `tests/test_nested_figure_render_gate.py` — all 7 tests **PASS**, including `test_legend_in_legend_does_not_leak_list_item_state` (the CR-01 regression gate added by 43-06, asserting the trailing paragraph after a legend-in-legend figure renders via the normal `par({...})` path, not the leaked `parbreak()` form). `43-GATE-EVIDENCE-03.md` records the original FIG-01 RED/GREEN; `43-GATE-EVIDENCE-07.md` independently re-reproduces the CR-01 RED (`git diff <base> <red-sha> -- typsphinx/` empty, confirming the test-first fixture landed before any code change) and records a depth-general 3-level-nest scratch-build proof (not merely the 2-level shape the reviewer found). |

**Score:** 6/6 truths verified (0 present-but-behavior-unverified)

### CR-01 fix scrutiny (the class-of-defect question this verification was asked to answer)

The task asked whether the same defect class — a flat scalar clobbered by re-entrant nesting,
where a real stack is needed — survives anywhere else in the table/figure/legend state machinery
this phase touched. Checked directly:

- `_table_state_stack` / `_push_table_state` / `_pop_table_state` (translator.py:3349-3417): real
  list-of-dict stack, guarded pop (`if not self._table_state_stack: return`), covers the full
  scalar set including the TBL-05 `_table_is_captioned` addition. No unguarded `.pop()`/`[-1]`.
- `_figure_state_stack` / `_push_figure_state` / `_pop_figure_state` (translator.py:3419-3472):
  same pattern, guarded pop, covers all six figure-neighborhood scalars including
  `_saved_body_for_figure_caption`.
- `_legend_list_item_stack` (translator.py:2757-2789, the CR-01 fix): real
  `List[Tuple[bool, bool]]` stack, guarded pop with an explicit `False, False` fallback.
- Grepped the whole file for `.pop()`/`[-1]` on these three new stacks — every occurrence is inside
  a preceding truthiness guard (translator.py:2785, 3404, 3466).
- The figure caption save/restore (`_caption_was_in_paragraph`/`_caption_was_paragraph_has_content`,
  translator.py:2674-2712) is a flat scalar too, but cannot exhibit CR-01's re-entrancy: a figure's
  `caption` child is always fully visited-and-departed before its `legend` sibling begins, so there
  is no window in which a nested figure's own caption processing could run while the outer caption's
  save is still live. Confirmed by reading `visit_figure`'s child-dispatch order.
- Other pre-existing flat "was_in_list_item" scalars in the file (`_emph_was_in_list_item`,
  `_strong_was_in_list_item`, `_title_was_in_list_item`, `_rubric_was_in_list_item`) were **not**
  touched by this phase's diff (confirmed via `git diff 7bdaf40..61296f9` — zero hits for any of
  those four names) and are pre-existing code outside this phase's stated scope (emphasis/
  strong/title/rubric do not nest within themselves in ordinary docutils trees the way a legend
  can contain a legend-bearing figure). Not a phase-43 gap; flagged here only because the task asked
  the question directly, and is out of scope for this phase per `43-CONTEXT.md`'s Deferred Ideas
  ("if measurement turns up the same clobber shape in a third container, file a todo").

No further instance of the CR-01 pattern was found within the code this phase touched.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `typsphinx/translator.py` | `_table_state_stack`, `_figure_state_stack`, `_legend_list_item_stack`, `_table_is_captioned`, `visit_legend`/`depart_legend` | ✓ VERIFIED | All present, wired, exercised by passing tests (see truths table). Sole production file changed this phase (+518/-53, confirmed via `git diff --stat`). |
| `tests/fixtures/nested_table_render_gate/` + `tests/test_nested_table_render_gate.py` | TBL-04 regression corpus + gate | ✓ VERIFIED | 7 tests, all pass against current tree. |
| `tests/fixtures/nested_figure_render_gate/` + `tests/test_nested_figure_render_gate.py` | FIG-01 regression corpus + gate, including CR-01's Section 5 | ✓ VERIFIED | 7 tests, all pass, including the CR-01 regression test. |
| `tests/fixtures/table_empty_caption_anchor_render_gate/` + `tests/test_table_empty_caption_anchor_render_gate.py` | TBL-05 regression corpus + gate | ✓ VERIFIED | 2 tests, both pass. |
| `.planning/.../43-GATE-EVIDENCE-01.md` through `-07.md` | Recorded RED-before-fix evidence, one per criterion/gap | ✓ VERIFIED (spot-checked) | All 7 present; `-05.md`/`-06.md` are the regenerated (post-CR-01) versions with an explicit "why this file was regenerated" section; commits cited in all seven files verified present via `git cat-file -e`. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `visit_table` | `depart_table` | `_push_table_state`/`_pop_table_state`, `_table_is_captioned` snapshot | ✓ WIRED | Push occurs when `self.in_table` already True (nested case); `was_nested` read before pop; nested markup routed into the restored enclosing cell buffer, not `self.body`. |
| `visit_figure` | `depart_figure` | `_push_figure_state`/`_pop_figure_state` | ✓ WIRED | Same shape as the table stack; symmetric push/pop confirmed by reading both methods. |
| `visit_legend` | `depart_legend` | `_legend_list_item_stack` | ✓ WIRED | The CR-01 fix; confirmed the stack is declared in `__init__` alongside `_list_item_stack`, pushed on visit, popped (guarded) on depart. |
| `visit_table` (structural pre-check) | `depart_table` (anchor call) | `_table_is_captioned` read at depart as `structural_is_captioned`, independent of `was_captioned` (rendering gate) | ✓ WIRED | Confirmed the two gates are genuinely independent by reading the depart_table code: `structural_is_captioned` drives the anchor call, `was_captioned` drives only whether `ids[0]` is skipped as already self-anchored. |

### Behavioral Spot-Checks (run directly in this session, not transcribed from evidence files)

| Behavior | Command | Result | Status |
|---|---|---|---|
| Full test suite | `uv run python -m pytest -q` | 837 passed, 1 skipped | ✓ PASS |
| New gate tests (16 total across 3 files) | `uv run python -m pytest -q tests/test_nested_table_render_gate.py tests/test_nested_figure_render_gate.py tests/test_table_empty_caption_anchor_render_gate.py -v` | 16/16 passed, incl. the CR-01 regression test | ✓ PASS |
| Format/lint/types | `black --check .` / `ruff check .` / `mypy typsphinx/` | all green | ✓ PASS |
| Full-corpus PDF compile (`-b typstpdf`) | `uv run tox -e docs-pdf` | "build succeeded, 2 warnings" (2 pre-existing, unrelated `visit_toctree` docstring warnings) | ✓ PASS |
| Milestone branch on origin | `git ls-remote --heads origin gsd/v0.7.1-bug-fix-round` | `1a3b3c85ea4dbbdefade23ef43f0a9e758a93e52` | ✓ PASS |
| CI run against that tip | `gh run view 30870536482 --json status,conclusion,headSha` | completed/success, headSha matches | ✓ PASS |
| Production diff isolation | `git diff --stat 7bdaf40..61296f9 -- typsphinx/ pyproject.toml uv.lock` | `translator.py` only, `518+/53-` | ✓ PASS |
| All cited commits exist | `git cat-file -e <sha>` for 23 commits cited across SUMMARYs/evidence | all present | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|---|---|---|---|---|
| TBL-04 | 43-01 | Nested-table container state | ✓ SATISFIED | Stack + guarded pop present and wired; 7/7 gate tests pass; RED recorded pre-fix. |
| TBL-05 | 43-04 | Id anchoring independent of rendered-caption truthiness | ✓ SATISFIED | `structural_is_captioned` split present and wired; 2/2 gate tests pass, including the non-shifted-numbering assertion; RED recorded pre-fix (`TypstError`, exit 2). |
| FIG-01 | 43-03, 43-06 (gap closure) | `legend` handler + figure-state stack; legend-in-legend leak closed | ✓ SATISFIED | Handler present; both stacks (`_figure_state_stack`, `_legend_list_item_stack`) present and guarded; 7/7 gate tests pass, including the CR-01 regression test; RED recorded twice (original FIG-01, then the CR-01 gap). |
| QUA-01 | 43-04 | `_emit_id_anchors` docstring names actual callers | ✓ SATISFIED | Docstring names `depart_figure` and `depart_table`; no "sole"/"only" claim remains; re-grepped call-site count (21 total, 2 with `skip_ids`) matches D-08's stated measurement. |

No orphaned requirements — all four IDs declared in the phase (`TBL-04, TBL-05, FIG-01, QUA-01`) are
claimed by at least one plan's `requirements` field and are all mapped in `.planning/REQUIREMENTS.md`
(§ Tables / Figures / Code quality). Note: `REQUIREMENTS.md`'s checkboxes for TBL-05 and QUA-01
(and ROADMAP.md's Phase 43 checkbox) are still unchecked at the time of this verification — this is
expected, not a gap: that bookkeeping flip is a phase-completion step that has not yet run, and this
verification report is the artifact that step consumes.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `.planning/.../43-GATE-EVIDENCE-06.md` | §7 summary table | The SC-number-to-requirement mapping table mislabels three rows: it maps SC#2→FIG-01, SC#3→TBL-05, SC#6→QUA-01, but ROADMAP.md's actual numbering is SC#2=TBL-05, SC#3=QUA-01, SC#6=FIG-01. Every individual plan (`43-01-PLAN.md`, `43-03-PLAN.md`, `43-04-PLAN.md`) and every other evidence file (`43-GATE-EVIDENCE-03.md`, `43-01-PLAN.md`'s own truths) use the *correct* numbering — this mislabeling is confined to one summary table inside `43-GATE-EVIDENCE-06.md`. | ℹ️ Info | Documentation-only; does not affect which evidence file discharges which requirement (the "Discharged by" column still points at the right file), and does not affect code correctness. Worth a one-line fix before this table is relied on by a future phase, but not a blocker — flagging for the record per the adversarial-verification instruction to report even small found issues plainly. |

No debt markers (`TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER`) were introduced by this phase's
diff (checked the full `git diff 7bdaf40..61296f9 -- typsphinx/translator.py` added-lines set; the
one incidental match, "empty first-comment **placeholder**", is prose inside a docstring explaining
docutils' own behavior, not a debt marker).

### Human Verification Required

None. Every truth in this phase is either a structural/documentation fact (SC#3), a build-and-test
result independently reproduced in this session (SC#1, SC#2, SC#4, SC#6), or a live API/git-state
check independently reproduced in this session (SC#5). No item required visual judgment, real-time
behavior, or an external service this verifier could not query directly.

### Gaps Summary

None. All six roadmap Success Criteria for Phase 43 are met, all four requirement IDs (TBL-04,
TBL-05, FIG-01, QUA-01) are satisfied, the phase's own code-review BLOCKER (CR-01) was genuinely
fixed — re-reproduced independently in this session via the passing `test_legend_in_legend_does_not_leak_list_item_state`
test and a fresh reading of the stack-based fix — and no instance of the same defect class survives
elsewhere in the table/figure/legend code this phase touched. The one finding (SC-number mislabeling
in one evidence-file summary table) is informational only and does not block phase completion.

---

_Verified: 2026-08-04T02:20:24Z_
_Verifier: Claude (gsd-verifier)_
