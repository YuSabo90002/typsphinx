---
phase: 39-admonition-taxonomy-rubric-nesting
plan: 06
subsystem: rendering
tags: [typst, translator, rubric, admonition-taxonomy, node-handler]

# Dependency graph
requires:
  - phase: 39-admonition-taxonomy-rubric-nesting (plan 02)
    provides: the recorded D-11/D-13 RED fixtures and hand-derived expected post-fix values (39-GATE-EVIDENCE-02.md)
  - phase: 36-shared-emission-seam-cleanup
    provides: D-01 (deliberate triplication of visit_strong's body across visit_rubric/visit_desc_signature) and D-02 (shared _strong_was_* attribute names) as standing decisions this plan partially unwinds for the rubric only
provides:
  - visit_rubric/depart_rubric own their own _rubric_was_* save/restore slots, independent of visit_strong/depart_strong and visit_desc_signature/depart_desc_signature's shared _strong_was_* names
  - A guard on visit_rubric's leading-separator emission that suppresses the double-count when _emit_id_anchors already supplied the rubric's separator newline
  - Regenerated tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ, confined to the propagated-target-inside-a-list-item region
affects: [39-07, 39-08]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Node-handler save-slot ownership: when two handlers share instance-attribute names by deliberate design (Phase 36 D-02), breaking that sharing for ONE handler is a slot rename scoped strictly to that handler's own visit/depart pair -- never a shared helper or stack."
    - "Measuring a shared emitter's side effect via a body-length delta (len(self.body) before/after a call) to detect whether it emitted anything, rather than re-deriving that fact from node state -- keeps the shared emitter (_emit_id_anchors) completely untouched while letting the caller (visit_rubric) make its own separator decision conditional on the callee's actual output."

key-files:
  created: []
  modified:
    - typsphinx/translator.py
    - tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ

key-decisions:
  - "Renamed only visit_rubric/depart_rubric's three save slots to _rubric_was_* (D-13's fix), leaving visit_strong/depart_strong and visit_desc_signature/depart_desc_signature's shared _strong_was_* names completely untouched -- the rename targets the diverging handler, not the two handlers whose sharing (Phase 36 D-02) stays deliberate."
  - "Detected whether _emit_id_anchors emitted anything via a self.body length delta across the call (rather than re-reading node.get('ids') after the fact, which could not distinguish an id-less node from one whose ids were all skip_ids), then gated BOTH halves of the double-count (the unconditional newline append and the re-armed-flag separator check) on that single boolean -- closing only one half would leave the re-armed list_item_needs_separator flag firing the other newline (D-11)."
  - "Regenerated tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ by building the fixture through -b typst into a temp directory and reading the diff before writing anything, per D-14's transparency requirement -- documented verbatim below."

requirements-completed: [ADM-05]

coverage:
  - id: D1
    description: "A rubric with inline bold markup no longer corrupts the translator's in_list_item state -- every paragraph after it (including the second and third, separated by intervening section headings) keeps its par({...}) wrapper, document-wide."
    requirement: "ADM-05"
    verification:
      - kind: unit
        ref: "tests/test_rubric_strong_nesting_render_gate.py::TestRubricStrongNestingRenderGate::test_paragraph_immediately_after_defect_rubric_loses_par_wrapper"
        status: pass
      - kind: unit
        ref: "tests/test_rubric_strong_nesting_render_gate.py::TestRubricStrongNestingRenderGate::test_second_later_paragraph_still_loses_par_wrapper"
        status: pass
      - kind: unit
        ref: "tests/test_rubric_strong_nesting_render_gate.py::TestRubricStrongNestingRenderGate::test_third_later_paragraph_still_loses_par_wrapper"
        status: pass
    human_judgment: false
  - id: D2
    description: "An anchored rubric (propagated target) emits exactly one separator newline between the anchor and its wrapper open, instead of three; an unanchored rubric is byte-unchanged at both top level and inside a list item."
    requirement: "ADM-05"
    verification:
      - kind: unit
        ref: "tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_propagated_target_rubric_separator_run_is_not_yet_one"
        status: pass
      - kind: unit
        ref: "tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_control_non_propagated_target_rubrics_keep_current_byte_shape"
        status: pass
      - kind: unit
        ref: "tests/test_rubric_propagated_target_render_gate.py::TestRubricPropagatedTargetRenderGate::test_typstpdf_propagated_rubric_and_sweep_anchors_resolve"
        status: pass
    human_judgment: false
  - id: D3
    description: "visit_strong, depart_strong, visit_desc_signature and depart_desc_signature are byte-unchanged; the deliberate triplication (Phase 36 D-01) and the shared _strong_was_* names between those two handlers (D-02) stand untouched."
    requirement: "ADM-05"
    verification:
      - kind: unit
        ref: "git diff -U0 typsphinx/translator.py (whole plan): every hunk header above line 5700"
        status: pass
      - kind: unit
        ref: "tests/test_signature_typography_gate.py (all 15 tests)"
        status: pass
      - kind: unit
        ref: "tests/test_desc_signature_anchor_render_gate.py, tests/test_desc_signature_concat_render_gate.py"
        status: pass
    human_judgment: false
  - id: D4
    description: "tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ is regenerated from a diff that was read and attributed line by line, confined to the propagated-target-inside-a-list-item region; D-14's full rubric census is re-run and every result recorded as confirmed, not assumed."
    requirement: "ADM-05"
    verification:
      - kind: unit
        ref: "tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_emitted_typ_is_byte_identical_to_golden"
        status: pass
      - kind: unit
        ref: "tests/test_rubric_indent_invariance.py (all 7 tests, ADM-05's own guard)"
        status: pass
      - kind: unit
        ref: "tests/test_translator.py::test_rubric_rendering"
        status: pass
      - kind: other
        ref: "uv run pytest -m \"not slow\" -- 735 passed, 29 deselected, 0 failed; uv run pytest (whole suite) -- 763 passed, 1 skipped (env-gated, unrelated), 0 failed"
        status: pass
    human_judgment: false

duration: 40min
completed: 2026-08-02
status: complete
---

# Phase 39 Plan 06: Rubric State-Bookkeeping and Separator-Double-Count Fix Summary

**Renamed `visit_rubric`/`depart_rubric`'s shared `_strong_was_*` save slots to rubric-owned `_rubric_was_*` names and guarded the leading-separator emission so an anchored rubric no longer triple-counts a newline `_emit_id_anchors` already supplied, flipping all four D-11/D-13 REDs GREEN with zero regressions.**

## Performance

- **Duration:** ~40 min
- **Completed:** 2026-08-02T02:42:01Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments

- **D-13 (document-wide `par()` drop, GATE-01 classic RED) fixed:** `visit_rubric`/`depart_rubric` now save and restore their three pieces of list-item/paragraph state under `_rubric_was_in_paragraph`, `_rubric_was_in_list_item`, and `_rubric_was_list_item_needs_separator` -- names no longer shared with `visit_strong`/`depart_strong` or `visit_desc_signature`/`depart_desc_signature`. A nested inline `strong` child firing while a rubric's state is saved can no longer have `depart_strong`'s own `delattr` calls delete the keys `depart_rubric` still needs, so `self.in_list_item` is correctly restored and every subsequent paragraph in the document keeps its `par({...})` wrapper.
- **D-11 (double-blank-line wart) fixed:** `visit_rubric` now measures whether `_emit_id_anchors` actually emitted anything for this node (via a `self.body` length delta across the call) and suppresses both its own unconditional leading newline and its list-item separator check when it did. A rubric anchoring a propagated target inside a list item now emits exactly one separator newline between the anchor and its `strong({` wrapper open, instead of three. `_emit_id_anchors` itself is byte-unchanged.
- **Golden file regenerated by hand-derivation:** `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` was rebuilt from a real `-b typst` compile of the fixture, diffed against the previously-committed golden, and the diff read line-by-line before writing -- confirmed confined to exactly the expected region (see "Golden Diff, Read and Attributed" below).
- **D-14's full rubric-touching census re-run and confirmed green**, including the three modules `39-RESEARCH.md` predicted would be unaffected (see table below).

## Task Commits

Each task was committed atomically:

1. **Task 1: Give the rubric handlers their own save slots** - `db70c2a` (fix)
2. **Task 2: Stop the rubric double-counting the id-anchor separator** - `5a45b20` (fix)
3. **Task 3: Regenerate the golden file by hand-derivation and re-run the whole rubric census** - `d5205d4` (test)

_Note: no separate plan-metadata commit is created in worktree-isolation mode -- STATE.md/ROADMAP.md are updated by the orchestrator after merge; this SUMMARY.md is committed by the harness's post-return commit step._

## Files Created/Modified

- `typsphinx/translator.py` - `visit_rubric`/`depart_rubric`: renamed their three save/restore attribute names from the shared `_strong_was_*` prefix to a rubric-owned `_rubric_was_*` prefix (Task 1); added a `body`-length-delta measurement of `_emit_id_anchors`'s own emission and guarded the unconditional leading newline plus the list-item separator check on it (Task 2); both handlers' docstrings rewritten to describe the actual (now-diverged) state instead of the deferred-repair note (Task 1 + Task 2).
- `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` - regenerated; the only change is two blank lines removed between the propagated-target anchor and the rubric's `strong({` wrapper open, inside the list item (Task 3).

## Decisions Made

- **Slot rename scoped to the rubric alone, not the strong handler.** `39-RESEARCH.md`'s Pitfall 1 table evaluated renaming `visit_strong`'s slots instead and rejected it for pointing the change at the wrong owner (`visit_strong` is the older, more-widely-relied-upon handler; the rubric is the one Phase 36's own docstrings already named as the future point of divergence). This plan renamed only the rubric's slots, leaving `visit_strong`/`depart_strong` and `visit_desc_signature`/`depart_desc_signature`'s shared `_strong_was_*` names completely untouched -- verified by `git diff -U0 typsphinx/translator.py` showing every hunk header above line 5700 across all three of this plan's commits.
- **Anchoring detection via body-length delta, not a second read of `node.get("ids")`.** Re-checking `node.get("ids")` after `_emit_id_anchors` returns cannot distinguish "this node had ids but they were all in `skip_ids`" (a real, if currently-unused-by-`visit_rubric`, case) from "this node genuinely emitted an anchor". Measuring `len(self.body)` before and after the call captures the emitter's ACTUAL output, which is what the separator decision needs to be correct against -- and keeps `_emit_id_anchors` itself unmodified (confirmed via `git diff -U0` showing no hunk in the 380-470 line range across the whole plan).
- **Both halves of the double-count closed together, not separately.** The plan's own action block warns that closing only the unconditional append leaves the re-armed `list_item_needs_separator` flag firing the second newline on its own. Both the unconditional `self.body.append("\n")` and the `if ... self.list_item_needs_separator: self.add_text("\n")` branch were gated on the same `not anchors_were_emitted` boolean in the same commit (Task 2), so there is no intermediate state where only one half is fixed.
- **Golden file regenerated by build-and-diff, not by copying failing pytest output.** Per D-14 (`must_haves.prohibitions`), the golden was rebuilt via a direct `sphinx-build -b typst` invocation into a scratch directory, `diff`ed against the committed file, and the diff read and attributed BEFORE writing -- not derived from `test_emitted_typ_is_byte_identical_to_golden`'s own failure-mode unified diff (which was consulted only afterward, to confirm the written file makes that test pass).

## Golden Diff, Read and Attributed

Full diff of the regenerated `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` against the pre-plan committed version:

```diff
@@ -73,8 +73,6 @@ text("First bullet text.")


 [#metadata(none) <index:decoupling-rubric-in-list-target>]
-
-
 strong({text("A Rubric In A List Item")})

 linebreak()
```

**Attribution:** this is the ONLY changed region in the entire fixture. It is the "A rubric carrying a propagated target, inside a list item" section named in the fixture's own body text a few lines above. Before this plan, the run of newlines between the anchor's closing `]` and the rubric's `strong({` wrapper open was 3 (the anchor's own trailing `"\n"`, `visit_rubric`'s unconditional `"\n"` append, and the separator check firing a second time against the flag `_emit_id_anchors`'s tail had just re-armed) -- exactly what plan 39-02's `39-GATE-EVIDENCE-02.md` hand-derived and recorded RED (`assert 3 == 1`). Task 2's guard (commit `5a45b20`) suppresses both the unconditional append and the separator-check newline whenever `_emit_id_anchors` already emitted something for the node, so only the anchor's own trailing newline remains -- a run of exactly 1, matching the hand-derivation and closing the two removed blank lines shown above. No other line, section, or fixture region changed: the top-level "A rubric at true end-of-document" rubric, the markup-free "Options" rubric, both signature blocks, and the plain-bold-markup control paragraph are all byte-identical to the pre-plan golden, confirming neither the D-13 slot rename nor the D-11 guard reached beyond their own two handlers.

## D-14 Rubric Census (re-run, confirmed not assumed)

| Module / assertion | Predicted by 39-RESEARCH.md | Result |
|---|---|---|
| `tests/test_desc_rubric_decoupling_render_gate.py` (5 tests, incl. golden byte-identity + D-11 newline-run assertion) | Affected (this plan's own gate) | **confirmed-green** (5/5 passed) |
| `tests/test_rubric_option_concat_render_gate.py` | Predicted unaffected (markup-free rubric, zero different bytes) | **confirmed-green** (1/1 passed, byte shape unchanged) |
| `tests/test_rubric_propagated_target_render_gate.py` | Affected (top-level anchored rubric, same D-11 wart class) | **confirmed-green** (1/1 passed; separator shape change is the same wart being closed, not a regression -- no assertion in this module needed re-deriving, since it asserts PDF/link resolution rather than an exact newline count) |
| `tests/test_signature_typography_multi_signature_page_count_gate.py` | Predicted unaffected (no rubric in that fixture) | **confirmed-green** (1/1 passed) |
| `tests/test_translator.py::test_rubric_rendering` | Predicted unaffected (unit-level, markup-free rubric) | **confirmed-green** (1/1 passed) |
| `tests/test_rubric_strong_nesting_render_gate.py` (this phase's classic GATE-01 RED, 6 tests) | Affected (D-13's own gate) | **confirmed-green** (6/6 passed, including all 3 previously-RED assertions and 3 controls) |
| `tests/test_rubric_indent_invariance.py` (ADM-05's own indentation guard, 7 tests) | Must stay green -- proves the state-bookkeeping change didn't regress indentation | **confirmed-green** (7/7 passed) |
| `tests/test_desc_signature_anchor_render_gate.py`, `tests/test_desc_signature_concat_render_gate.py`, `tests/test_signature_typography_gate.py` | Predicted unaffected (Phase 37's signature emission; visit_desc_signature untouched) | **confirmed-green** (2/2, 2/2, 15/15 passed respectively) |
| Full suite (`uv run pytest -m "not slow"`) | -- | **confirmed-green**: 735 passed, 29 deselected, 0 failed |
| Full suite (`uv run pytest`, no marker filter) | -- | **confirmed-green**: 763 passed, 1 skipped (the pre-existing env-gated `tests/test_corpus_gate.py` SC#3 measurement test, unrelated to this plan and unrelated to rubrics), 0 failed -- against the recorded baseline of 4 failed / 758 passed / 2 skipped, all 4 REDs are now GREEN with zero new failures |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking, non-package] Task 1's acceptance criteria named a non-existent test file**
- **Found during:** Task 1 (verification step)
- **Issue:** The plan's Task 1 `<verify>`/acceptance criteria reference `tests/test_desc_signature_render_gate.py`, which does not exist in the repository (confirmed via `pytest --collect-only` erroring `file or directory not found`). The closest existing modules covering the same intent ("confirming Phase 37's signature emission is unmoved") are `tests/test_desc_signature_anchor_render_gate.py` and `tests/test_desc_signature_concat_render_gate.py`.
- **Fix:** Ran Task 1's verification against the two existing signature-emission modules instead of the non-existent filename; both pass (4/4 tests), confirming `visit_desc_signature`/`depart_desc_signature` are unaffected.
- **Files modified:** none (verification-only substitution; no source or test file was renamed or created).
- **Verification:** `uv run pytest tests/test_rubric_strong_nesting_render_gate.py tests/test_rubric_option_concat_render_gate.py tests/test_desc_signature_anchor_render_gate.py tests/test_desc_signature_concat_render_gate.py tests/test_signature_typography_gate.py -v` -- 25/25 passed.
- **Committed in:** not applicable (no code change; documented here as a plan-accuracy note only).

---

**Total deviations:** 1 auto-fixed (1 non-package blocking substitution, Rule 3)
**Impact on plan:** Zero impact on scope or correctness -- the substituted test files cover exactly the same Phase 37 signature-emission-unmoved property the plan intended to verify. No source code change was affected by this deviation.

## Issues Encountered

None beyond the deviation documented above. The NixOS-sandbox `ruff`/`uv` ELF-binary hazard (documented in project memory) was handled per the standard worktree-provisioning steps: `uv sync --extra dev` succeeded directly; the worktree's generic-linux `ruff` wheel could not exec under the NixOS stub loader, so `.venv/bin/ruff` was symlinked to the main checkout's already-working `.venv/bin/ruff` binary (both are the same pinned version, `0.15.20`, per `uv.lock`) before running any lint command.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Both D-11 and D-13 rubric defects are closed; the phase's rubric half is coherent end-to-end: the classic GATE-01 RED (D-13) is green, the ADM-05 indentation invariance guard (D-12) is still green, and the D-11 wart named in both handlers' own docstrings is closed.
- `visit_strong`/`depart_strong` and `visit_desc_signature`/`depart_desc_signature` are byte-unchanged; Phase 36's D-01/D-02 decisions and Phase 37's signature emission contract are undisturbed.
- No blockers for the remaining Phase 39 plans (39-07, 39-08).

---
*Phase: 39-admonition-taxonomy-rubric-nesting*
*Completed: 2026-08-02*
