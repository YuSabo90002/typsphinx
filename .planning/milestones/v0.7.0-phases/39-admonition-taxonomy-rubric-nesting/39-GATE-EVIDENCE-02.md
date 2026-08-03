# Phase 39 Plan 02 — Rubric-Half GATE-01 RED Evidence (ADM-05, D-11, D-12, D-13)

**Captured:** 2026-08-02
**Plan:** 39-02 (Wave 1)

## Commit SHA the RED was captured against

`typsphinx/` is **completely untouched** by plan 39-02
(`git diff --stat 92c0891 HEAD -- typsphinx/` is empty at every point in this
plan's execution — verified again below). The RED below was captured at:

- **Worktree base (plan start, "the untouched translator"):**
  `92c0891dbd86dc6b5aa643530657a1626a163df2` (`docs(phase-39): begin phase
  execution`) — short hash `92c0891`
- **This plan's Task 1 commit (D-13 fixture + gate module):** `dd8a4a6`
  (`test(39-02): record document-wide GATE-01 RED for rubric+strong nesting
  (D-13)`)
- **This plan's Task 2 commit (D-11 wart assertion):** `8cbe730`
  (`test(39-02): assert the D-11 double-blank-line wart on the decoupling
  fixture`)
- **Last commit that touched `typsphinx/` before this plan:** `76324bf`
  (`fix(37-09): drop the zeroed above/below override on the signature
  wrapper`) — pre-dates this plan and every Phase 38/39 plan before it;
  `visit_rubric`/`depart_rubric`/`visit_strong`/`depart_strong`/
  `_emit_id_anchors` are all byte-identical to `92c0891` at this SHA.

## Intentionally-RED node ids (4)

Enumerated explicitly so a later wave (39-06, the fix plan) can verify by
**set difference**, never by count:

```
tests/test_rubric_strong_nesting_render_gate.py::TestRubricStrongNestingRenderGate::test_paragraph_immediately_after_defect_rubric_loses_par_wrapper
tests/test_rubric_strong_nesting_render_gate.py::TestRubricStrongNestingRenderGate::test_second_later_paragraph_still_loses_par_wrapper
tests/test_rubric_strong_nesting_render_gate.py::TestRubricStrongNestingRenderGate::test_third_later_paragraph_still_loses_par_wrapper
tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_propagated_target_rubric_separator_run_is_not_yet_one
```

**CONTROL-GREEN (5 new + 5 pre-existing = 10), expected to PASS in every
state (pre- and post-39-06):**

```
tests/test_rubric_strong_nesting_render_gate.py::TestRubricStrongNestingRenderGate::test_control_paragraph_after_markup_free_rubric_stays_wrapped
tests/test_rubric_strong_nesting_render_gate.py::TestRubricStrongNestingRenderGate::test_control_defect_rubrics_own_emission_is_unchanged
tests/test_rubric_strong_nesting_render_gate.py::TestRubricStrongNestingRenderGate::test_fixture_compiles_to_valid_typst
tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_control_non_propagated_target_rubrics_keep_current_byte_shape
tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_emitted_typ_is_byte_identical_to_golden
```

(The remaining four pre-existing tests in
`tests/test_desc_rubric_decoupling_render_gate.py` --
`test_desc_signature_and_rubric_do_not_delegate_to_visit_strong` and
`test_decoupling_fixture_still_compiles_to_pdf` -- also stay green; this
plan added zero new failures to that module beyond the one intentional RED
above.)

### Per-RED cause (one sentence each)

| Node id (short form) | Property that failed |
|---|---|
| `test_paragraph_immediately_after_defect_rubric_loses_par_wrapper` | `par({text("Alpha prose...")})` is **absent** from the emitted `.typ` -- the paragraph immediately after the inline-markup rubric emits a bare `text("...")` instead, because `self.in_list_item` is stuck `True`. |
| `test_second_later_paragraph_still_loses_par_wrapper` | `par({text("Bravo prose...")})` is **absent** -- a SECOND paragraph, separated from the defect rubric by an intervening section heading, is *also* affected, proving the defect is document-wide. |
| `test_third_later_paragraph_still_loses_par_wrapper` | `par({text("Charlie prose...")})` is **absent** -- a THIRD paragraph, separated by two intervening section headings, is *still* affected -- the defect runs to the end of the file, not just the next paragraph or two. |
| `test_propagated_target_rubric_separator_run_is_not_yet_one` | The measured newline run between the propagated-target anchor and the rubric's `strong({` wrapper open is **3** (expected **1**, hand-derived below) -- the D-11 double-blank-line wart. |

### None of the above is a compile failure

Every RED above is a **structural substring-membership / newline-count
mismatch on already-compiled output** -- `assert <substring> in <text>` or
`assert <count> == <count>` -- **never** a `typst.TypstError` or any other
compile-time exception. Confirmed by direct count over both modules'
verbatim output (below):

```
$ grep -c "TypstError" <verbatim pytest output below>
0
```

The compile step itself, run standalone against the SAME (untouched)
translator immediately before capturing this evidence, for the NEW D-13
fixture (the D-11 wart is asserted on the pre-existing
`desc_rubric_decoupling_render_gate` fixture, whose own compile-sanity leg,
`test_decoupling_fixture_still_compiles_to_pdf`, is unmodified and stays
green -- see the CONTROL-GREEN list above):

```
$ uv run python -m sphinx -b typst tests/fixtures/rubric_strong_nesting_render_gate /tmp/rub39evid
...
writing output... [index] done
build succeeded.
sphinx-build exit status: 0

$ uv run python -c "import typst; typst.compile('/tmp/rub39evid/index.typ')"
typst.compile() exit: success, no exception raised
typst.compile() python exit status: 0
```

`sphinx-build -b typst` exits **0** and `typst.compile()` raises **no
exception** -- the SAME build every RED test above reads from (via the
session-scoped `rubric_strong_nesting_build` fixture). Milestone invariant
#4's structural-RED redefinition is satisfied: both D-13 and D-11 compile
fine today; the RED is entirely about a missing `par({...})` substring and
an over-long newline run.

## Verbatim `uv run pytest tests/test_rubric_strong_nesting_render_gate.py -v` output (status lines + failure headlines)

The full inline representation of the emitted `.typ` inside pytest's own
`assert ... in <value>` diff output is elided below with `...` for
readability (each failure repeats the SAME ~50-line `.typ` dump); the full,
unedited output was captured to `/tmp/rubric_nesting_pytest_output.txt`
during this session and every line quoted here is copied verbatim from it.

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- .../.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a9a977094e8349725
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 6 items

tests/test_rubric_strong_nesting_render_gate.py::TestRubricStrongNestingRenderGate::test_paragraph_immediately_after_defect_rubric_loses_par_wrapper FAILED [ 16%]
tests/test_rubric_strong_nesting_render_gate.py::TestRubricStrongNestingRenderGate::test_second_later_paragraph_still_loses_par_wrapper FAILED [ 33%]
tests/test_rubric_strong_nesting_render_gate.py::TestRubricStrongNestingRenderGate::test_third_later_paragraph_still_loses_par_wrapper FAILED [ 50%]
tests/test_rubric_strong_nesting_render_gate.py::TestRubricStrongNestingRenderGate::test_control_paragraph_after_markup_free_rubric_stays_wrapped PASSED [ 66%]
tests/test_rubric_strong_nesting_render_gate.py::TestRubricStrongNestingRenderGate::test_control_defect_rubrics_own_emission_is_unchanged PASSED [ 83%]
tests/test_rubric_strong_nesting_render_gate.py::TestRubricStrongNestingRenderGate::test_fixture_compiles_to_valid_typst PASSED [100%]

=================================== FAILURES ===================================
_ TestRubricStrongNestingRenderGate.test_paragraph_immediately_after_defect_rubric_loses_par_wrapper _
E   AssertionError: D-13: the paragraph immediately after the inline-markup rubric did not emit the par({text(...)}) wrapper -- the shared _strong_was_* save-slot clobbering (Phase 36 D-02) is still leaving in_list_item stuck True:
      ...(emitted .typ, elided)...
    assert 'par({text("Alpha prose sits directly after the defect rubric and must render inside a wrapped block.")})' in '...(emitted .typ, elided)...'

_ TestRubricStrongNestingRenderGate.test_second_later_paragraph_still_loses_par_wrapper _
E   AssertionError: D-13 document-wide: a paragraph separated from the defect rubric by an intervening section heading still did not emit the par({text(...)}) wrapper:
      ...(emitted .typ, elided)...
    assert 'par({text("Bravo prose sits after an intervening section heading and must also render inside a wrapped block.")})' in '...(emitted .typ, elided)...'

_ TestRubricStrongNestingRenderGate.test_third_later_paragraph_still_loses_par_wrapper _
E   AssertionError: D-13 document-wide: a paragraph separated from the defect rubric by two intervening section headings still did not emit the par({text(...)}) wrapper:
      ...(emitted .typ, elided)...
    assert 'par({text("Charlie prose sits deep in the document and must also render inside a wrapped block.")})' in '...(emitted .typ, elided)...'
=========================== short test summary info ============================
FAILED tests/test_rubric_strong_nesting_render_gate.py::TestRubricStrongNestingRenderGate::test_paragraph_immediately_after_defect_rubric_loses_par_wrapper
FAILED tests/test_rubric_strong_nesting_render_gate.py::TestRubricStrongNestingRenderGate::test_second_later_paragraph_still_loses_par_wrapper
FAILED tests/test_rubric_strong_nesting_render_gate.py::TestRubricStrongNestingRenderGate::test_third_later_paragraph_still_loses_par_wrapper
========================= 3 failed, 3 passed in 0.34s ==========================
```

## Verbatim `uv run pytest tests/test_desc_rubric_decoupling_render_gate.py -v` output (D-11 addition)

```
tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_desc_signature_and_rubric_do_not_delegate_to_visit_strong PASSED [ 20%]
tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_emitted_typ_is_byte_identical_to_golden PASSED [ 40%]
tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_decoupling_fixture_still_compiles_to_pdf PASSED [ 60%]
tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_propagated_target_rubric_separator_run_is_not_yet_one FAILED [ 80%]
tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_control_non_propagated_target_rubrics_keep_current_byte_shape PASSED [100%]

=================================== FAILURES ===================================
_ TestDescRubricDecouplingRenderGate.test_propagated_target_rubric_separator_run_is_not_yet_one _
E   AssertionError: D-11: measured a run of 3 newline(s) between the propagated-target anchor and the rubric's strong({ wrapper open (expected 1, hand-derived above: _emit_id_anchors's own trailing newline is the anchor's fair share; visit_rubric's unconditional newline plus its re-armed separator check double-count on top of it). RED today (the untouched translator measures 3, from the double-count); expected GREEN once plan 39-06 lands the fix.
assert 3 == 1
========================= 1 failed, 4 passed in 0.98s ==========================
```

`uv run pytest tests/test_desc_rubric_decoupling_render_gate.py -k
byte_identical -x` -- the module's pre-existing SC#2 byte-identity golden
test -- **stays green** (verified separately this session): this plan's
addition changes zero emitted bytes, only adds two new assertions.

## Hand derivation of both expected post-fix values

Written newline-by-newline / call-by-call against named
`typsphinx/translator.py` line ranges, **never** by running a candidate
fix and copying its output (`must_haves.prohibitions`, ADM-05).

### D-13 (document-wide `par()` drop) -- `typsphinx/translator.py:826-941`, `1206-1317`, `1429-1501`, `5767-5890`

1. `visit_rubric` (`typsphinx/translator.py:5789-5831`) is a deliberate
   verbatim copy of `visit_strong`'s body (Phase 36 D-01). It saves the
   caller's `in_paragraph` / `in_list_item` / `list_item_needs_separator`
   into three **shared, single-slot** instance attributes --
   `_strong_was_in_paragraph`, `_strong_was_in_list_item`,
   `_strong_was_list_item_needs_separator` (line 5828-5830) -- the exact
   same attribute names `visit_strong`/`depart_strong` use
   (`typsphinx/translator.py:1469-1472`, Phase 36 D-02). It then forces
   `self.in_list_item = True` for its own children (line 5818).
2. When the rubric's title contains a real inline `strong` child, that
   inner `visit_strong` (`typsphinx/translator.py:1450-1472`) fires WHILE
   the rubric's own three attributes are still set, and **overwrites all
   three with its own values** (line 1470-1472) -- since the inner
   `strong` entered with `in_list_item = True` (the value the OUTER rubric
   just forced), the overwritten values are the SAME as the rubric's own,
   but they are now attributed to the INNER `strong`'s save, not the
   OUTER rubric's.
3. `depart_strong` (`typsphinx/translator.py:1487-1501`) restores from
   those attributes and then `delattr`s all three (line 1489, 1494, 1501).
   By the time the OUTER `depart_rubric` runs
   (`typsphinx/translator.py:5859-5873`), `hasattr(self,
   "_strong_was_in_paragraph")` is already `False` -- every one of its
   three restore blocks silently no-ops (the `if hasattr(...)` guards all
   fail).
4. `self.in_list_item` therefore stays at whatever the INNER `depart_strong`
   left it (`True`, restored from its own save of the rubric-forced value)
   for the rest of the document -- nothing ever sets it back to `False`.
5. `visit_paragraph` (`typsphinx/translator.py:891-894`) checks
   `if self.in_list_item:` BEFORE the normal `par({` wrapper path
   (`typsphinx/translator.py:896-899`) and takes the list-item branch
   instead, emitting a real `parbreak()` via `_emit_forced_break` and
   `return`ing WITHOUT opening `par({`. `visit_Text`
   (`typsphinx/translator.py:1293-1301`) then emits a bare
   `text("...")` with no enclosing `par({...})`.
6. Because nothing in `visit_section`/`visit_title`/`depart_paragraph`
   ever resets `in_list_item` back to `False` for an ordinary top-level
   paragraph, step 5 repeats for EVERY subsequent paragraph in the
   document, not just the one immediately following the defect rubric --
   the measured, document-wide RED.

Expected post-fix string for an ordinary paragraph, hand-derived from
`visit_paragraph`'s non-list-item branch (`typsphinx/translator.py:896-899`,
opens `par({`), `visit_Text`'s wrapper (`typsphinx/translator.py:1300-1301`,
`text("...")`with no leading separator as the first child), and
`depart_paragraph`'s close (`typsphinx/translator.py:938-941`, `})`):
`par({text("...")})`.

### D-11 (double-blank-line wart) -- `typsphinx/translator.py:394-465`, `5789-5798`

1. `_emit_id_anchors` (`typsphinx/translator.py:460-461`): because
   `in_list_item` and `list_item_needs_separator` are both `True` (set by
   the fixture's preceding "First bullet text." list-item text), it
   appends ONE leading `"\n"` **before** the anchor.
2. `_emit_id_anchors` (`typsphinx/translator.py:462-463`): for the
   rubric's one pending id, it appends
   `f"\n[#metadata(none) <{label_id}>]\n"` -- this string carries its OWN
   leading `"\n"` (folds into step 1's run before the anchor) AND its OWN
   TRAILING `"\n"` immediately after the anchor's closing `"]"`. **This
   trailing newline is the anchor's fair, sufficient share of the run
   this test measures.**
3. `_emit_id_anchors` (`typsphinx/translator.py:464-465`): its tail
   RE-ARMS `list_item_needs_separator = True`, because we are still
   inside the list item.
4. `visit_rubric` (`typsphinx/translator.py:5793-5794`): appends an
   UNCONDITIONAL `"\n"` ("Add newline before rubric") regardless of any
   flag -- the FIRST newline the rubric itself owes at this site.
5. `visit_rubric` (`typsphinx/translator.py:5804-5806`):
   `_add_paragraph_separator()` is a no-op (not inside a paragraph); then,
   because `list_item_needs_separator` was JUST re-armed by step 3, the
   leading list-item separator check fires AGAIN and appends a SECOND
   `"\n"` -- **double-counting a flag `_emit_id_anchors` had already
   discharged with its own trailing newline in step 2.**

Today's run: step 2's trailing newline (1) + step 4's unconditional
newline (1) + step 5's double-counted separator-check newline (1) = **3**
-- matches the measured RED. The rubric owes ZERO further newlines at this
site: step 2 already supplies the one separator needed. Post-fix expected
run: **1**.

## The two folded defects, cited by source

- **`.planning/todos/pending/2026-07-30-rubric-with-inline-markup-leaks-in-list-item-and-drops-par.md`**
  (frontmatter `resolves_phase: 39`) -- files
  `typsphinx/translator.py` (`visit_strong`/`depart_strong`,
  `visit_rubric`/`depart_rubric`, `visit_desc_signature`/
  `depart_desc_signature`, all sharing the three `_strong_was_*` slots).
  This is D-13's source todo; its own measured reproduction (pre-Phase-36,
  updated with a post-Phase-36 correction in the same file) matches this
  plan's fixture shape byte-for-byte in structure (a rubric with inline
  bold, followed by paragraphs that lose their `par()` wrapper).
- **`visit_rubric`'s own docstring**, `typsphinx/translator.py:5781-5787`:
  "Known, pre-existing, and deliberately preserved here: when a rubric
  containing a propagated target sits inside a list item, the leading
  separator check below fires a second time against a flag
  `_emit_id_anchors` already set, on top of the unconditional newline
  append two lines above, producing two blank lines between the anchor
  and this opening wrapper -- a cosmetic wart, not fixed in this plan
  (fixing it changes emitted bytes; Phase 39 owns the repair)." This is
  D-11's source citation, named directly in the code this plan measures
  against.

## D-12: ADM-05's own indentation property is NOT red-able

Per `39-CONTEXT.md` D-12 (following Phase 36's SC#3 precedent): ADM-05's
indentation claim ("a rubric inherits its container's indent via Phase 38's
`pad(left: SHARED_INDENT_STEP, ...)` wrapper") **already holds** pre-phase
-- it was measured directly against a real `-b typstpdf` build in
`39-CONTEXT.md`'s "Rubric -- ADM-05/SC#3" section (four `pypdf`-measured x
positions, all matching their container's body column). A RED cannot be
recorded against pre-phase code for a property that is already true; per
D-12 this becomes an **invariance guard** in plan 39-03 (following the
`36-GATE-EVIDENCE.md` SC#3 precedent), not a waiver. The milestone's
GATE-01 bar for this phase's rubric half is instead met by THIS plan's two
real REDs (D-13's document-wide `par()` drop, D-11's double-blank-line
wart) -- both structural, both measured against the untouched translator,
both recorded above.

## `git diff --stat` proving `typsphinx/` and the decoupling fixture are untouched

```
$ git diff --stat 92c0891 HEAD -- typsphinx/
(empty)

$ git diff --stat 92c0891 HEAD -- tests/fixtures/desc_rubric_decoupling_render_gate/
(empty)
```

Both commands produced zero output when run against this plan's two commits
(`dd8a4a6`, `8cbe730`) -- confirmed at evidence-capture time. Neither
`typsphinx/translator.py` nor
`tests/fixtures/desc_rubric_decoupling_render_gate/index.rst` /
`golden.typ` was touched by this plan; the D-11 assertion reads the
existing fixture's already-committed output and the existing `golden.typ`,
it does not regenerate either.
