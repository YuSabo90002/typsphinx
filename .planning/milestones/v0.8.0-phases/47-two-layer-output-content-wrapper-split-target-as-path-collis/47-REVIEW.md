---
phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis
reviewed: 2026-08-12T00:00:00Z
depth: standard
scope: "SCOPED re-review of plans 47-13/47-14 only (gap closure for CR-01 and WR-01). Diff range: 80043b3^..HEAD. This report REPLACES the prior 47-REVIEW.md but does NOT re-review the ~200 files from plans 47-01..47-12 -- those findings are not re-verified here except where directly implicated by CR-01/WR-01."
files_reviewed: 12
files_reviewed_list:
  - typsphinx/builder.py
  - tests/test_master_include_set_predicate_gate.py
  - tests/test_builder_output_stem.py
  - tests/test_two_layer_output_gate.py
  - tests/test_corpus_gate.py
  - tests/fixtures/bld03_ghost_entry_xref_gate/conf.py
  - tests/fixtures/bld03_ghost_entry_xref_gate/index.rst
  - tests/fixtures/bld03_ghost_entry_xref_gate/ghost.rst
  - tests/fixtures/bld03_ghost_entry_xref_gate/ghost_child.rst
  - tests/fixtures/bld03_unhashable_docname_gate/conf.py
  - tests/fixtures/bld03_unhashable_docname_gate/index.rst
  - tests/fixtures/entry_title_author_render_gate/conf.py
findings:
  critical: 0
  warning: 1
  info: 0
  total: 1
status: issues_found
---

# Phase 47: Code Review Report (Scoped Re-Review, Plans 47-13/47-14)

**Reviewed:** 2026-08-12T00:00:00Z
**Depth:** standard
**Files Reviewed:** 12
**Diff Range:** `80043b3^..HEAD`
**Status:** issues_found (one new WARNING; both prior findings genuinely closed)

## Scope Note

This is **not** a fresh full-phase review. The original `47-REVIEW.md` covered
plans 47-01..47-12 (~200 files) and raised two findings, CR-01 (BLOCKER) and
WR-01 (Warning). Plans 47-13 and 47-14 were written specifically to close
those two findings. This pass re-reviews only the 12 files those two plans
touched (diff `80043b3^..HEAD`) to verify the closure claims and to catch any
new defects introduced by the gap-closure work itself. The other ~200 files
from 47-01..47-12 were **not** re-read in this pass.

## Disposition of Prior Findings

### CR-01 (Critical/BLOCKER) — CLOSED, verified genuine

**Original finding:** `TypstBuilder._compute_master_included_docnames()`
(builder.py) was a fifth site reading `typst_documents` that answered "is
this entry usable" with a bare `if entry` truthiness test instead of the
named `_is_usable_typst_documents_entry()` predicate, allowing an
under-length entry to (a) phantom-include a toctree subtree that produces no
wrapper file, silently emitting dangling `link(<label>)`s, and (b) crash the
whole build with an uncaught `TypeError: unhashable type: 'list'` for a
non-hashable `entry[0]`.

**Verification performed:**
- Read `typsphinx/builder.py:304-309` directly. The masters list is now
  built as `[entry[0] for entry in typst_documents if
  _is_usable_typst_documents_entry(entry)]` — the bare `if entry` filter is
  gone.
- Confirmed via `git diff 80043b3^..HEAD -- typsphinx/builder.py` that this
  is the only functional change to `_compute_master_included_docnames()`;
  everything else in the diff is docstring/comment-only.
- Grepped all five call sites of `_is_usable_typst_documents_entry(` in
  builder.py (lines 308, 614, 792, 1008, 1440) and confirmed each matches
  the predicate's own docstring enumeration ("all FIVE sites") — no drift
  between the documented consumer list and the wired reality.
- `_is_usable_typst_documents_entry()`'s `isinstance(entry[0], str)` check
  guarantees `entry[0]` is hashable before it ever reaches the BFS's `set`
  membership/`add` operations in `_compute_master_included_docnames()`,
  closing the `TypeError: unhashable type` crash.
- Ran the two new real-`sphinx-build` subprocess gates
  (`tests/test_master_include_set_predicate_gate.py`,
  `TestGhostEntryXrefRenderGate` / `TestUnhashableDocnameRenderGate`) plus
  their unit-level companions and the two invariance guards
  (`TestMasterIncludeSetInvarianceGuards`) — all 8 tests pass against the
  current tree (`pytest tests/test_master_include_set_predicate_gate.py -q`
  → 8 passed).
- Confirmed the two fixtures (`bld03_ghost_entry_xref_gate`,
  `bld03_unhashable_docname_gate`) are load-bearing and shaped exactly as
  each fixture's own header comment claims (under-length `("ghost",)` entry
  with a real `:orphan:` toctree child; non-hashable `(["weird"], ...)`
  first entry alongside a well-formed second entry).

**Conclusion: CR-01 is genuinely closed.** No bare-truthiness filter remains
anywhere in builder.py; all five predicate-consuming sites are wired
identically.

### WR-01 (Warning) — CLOSED, verified genuine

**Original finding:** `TypstBuilder._resolve_output_stem()` was fully
implemented, documented, and tested dead code with zero real production
call sites — a green test suite exercising it reported false confidence in
a route no real build path ever reached.

**Verification performed:**
- `git diff 80043b3^..HEAD -- typsphinx/builder.py` shows the entire
  `_resolve_output_stem()` method body deleted (was previously between the
  old `_compute_master_included_docnames()` and `_resolve_target_stem()`
  definitions).
- `grep -rn "_resolve_output_stem" typsphinx/` (excluding `.planning/`)
  returns zero hits in any `.py` source file under `typsphinx/`.
- Every remaining hit of the string `_resolve_output_stem` project-wide is
  inside test docstrings/comments, and every one of them is explicitly
  past-tense / historical ("was deleted in Phase 47 Plan 14", "the FILE
  name is historical and no longer names the resolver these tests
  exercise") — none present it as a live mechanism.
- `tests/test_builder_output_stem.py` was retargeted onto
  `_resolve_target_stem(docname, target)` (given the target value directly)
  and `_wrapper_output_relpath(entry)` (the two resolvers production code
  actually calls). Diffed every retargeted assertion against its
  pre-deletion counterpart (`git diff 80043b3^..HEAD --
  tests/test_builder_output_stem.py`): every survived assertion keeps the
  **same expected return value**, only the call shape changed (config-list
  setup replaced by a direct target-value argument). No expected value was
  altered to match new/different behavior — this is a faithful retarget,
  not a laundered behavior change.
- The three assertions the module's own docstring says did NOT survive
  (unlisted-docname fallback, missing-config fallback, short-tuple
  fallback) are each accounted for by name with a stated reason and a
  named surviving-coverage location; none of the three reasons is "it
  would be work to port" — the short-tuple one in particular is correctly
  identified as asserting a contract BLD-03 (47-11) deliberately reversed,
  so porting it verbatim would have re-introduced the defect 47-11 closed.
- Ran `tests/test_builder_output_stem.py` (25 tests) and
  `tests/test_two_layer_output_gate.py` (12 tests) — all pass.

**Conclusion: WR-01 is genuinely closed.** The dead code is gone, and no
docstring, comment, or test body treats it as live.

## New Findings (This Pass)

### WR-02: Stale module docstring in `test_master_include_set_predicate_gate.py` claims RED evidence is recorded via `xfail(strict=True)`, but every `xfail` marker was removed when the fix landed

**File:** `tests/test_master_include_set_predicate_gate.py:27-31`

**Issue:** The module docstring states:

> Structured like `tests/test_collision_predicate_completeness_gate.py` ...
> but recording the pre-fix RED as `xfail(strict=True)`: six of the eight
> tests below fail on the unfixed tree; two are invariance guards that
> already pass and must keep passing.

This was true of the file as committed in `80043b3` (the RED-recording
commit for plan 47-13), which had six `@pytest.mark.xfail(strict=True, ...)`
decorators. The very next commit, `e422bfb` (the fix commit for plan
47-13), removes all six `xfail` decorators — correctly, since the tests now
pass against the fixed tree — but leaves this docstring paragraph
unedited. `grep -n xfail tests/test_master_include_set_predicate_gate.py`
against the current tree confirms zero `@pytest.mark.xfail` decorators
remain anywhere in the file; every remaining occurrence of the word
`xfail` is inside prose.

A related, milder instance of the same staleness sits in two class
docstrings (`TestGhostEntryIncludeSetUnit` and
`TestUnhashableDocnameIncludeSetUnit`, lines ~161-162 and ~256-257): both
say the `TypstBuilder` import is placed inside the test body "so a
signature change lands as an xfail rather than a module-level collection
error" — a rationale that no longer applies now that neither test carries
an `xfail` marker (a signature change now surfaces as an ordinary test
failure or a collection error either way, since nothing in the file
converts a failure into an expected one anymore).

This is not a functional defect — the 8 tests all pass today, and the fix
itself (verified above) is correct — but a future maintainer reading this
docstring while triaging a failure in this module would reasonably expect
to find `xfail(strict=True)` markers recording the historical RED baseline,
search for them, and be confused when they are absent. The actual verbatim
pre-fix transcripts still live in `47-GAP2-RED-EVIDENCE.md` per the same
docstring's next sentence, which remains accurate — only the "recording ...
as `xfail(strict=True)`" claim about *this file's own contents* is now
false.

**Fix:** Update the docstring paragraph to past tense, e.g.:

```python
"""
Structured like ``tests/test_collision_predicate_completeness_gate.py`` (one
fixture-directory constant per scenario, one ``_run_sphinx_build`` helper
duplicated per this repo's own convention). The pre-fix RED was originally
recorded as ``xfail(strict=True)`` on six of the eight tests below (the
other two are invariance guards that already passed and had to keep
passing); those ``xfail`` markers were removed once the fix landed and all
eight tests pass unconditionally. The verbatim pre-fix transcripts each
former xfail's ``reason=`` paraphrased are recorded in full in
``47-GAP2-RED-EVIDENCE.md``.
"""
```

and similarly adjust the two class docstrings' "lands as an xfail" phrasing
to past tense (e.g. "so a signature change lands as an ordinary failure
inside the test body rather than a module-level collection error" if that
rationale is still the intended justification for the in-body import, or
simply drop the now-inapplicable xfail clause).

## Summary

Both findings the scoped re-review was dispatched to verify — CR-01
(BLOCKER) and WR-01 (Warning) from the prior full-phase review — are
genuinely closed by plans 47-13 and 47-14 respectively, confirmed by direct
code reading, `git diff` against the pre-fix commit, a full grep sweep for
stray references to the deleted function, and by running every test in the
12 files in scope (all pass; `mypy typsphinx/` and `black --check` both
clean on the scoped files). No test assertion was retargeted by silently
changing its expected value to match new behavior — every retarget in
`test_builder_output_stem.py` preserves the original expected return value
and only changes the call shape.

One new, narrowly-scoped documentation-staleness issue (WR-02) was found in
the new gap-closure test file itself: a module docstring describes an
`xfail(strict=True)` RED-recording mechanism that was removed in the very
next commit and never updated to say so. This does not affect correctness
or test reliability — it is a maintainability/clarity issue in test
documentation.

## Warnings

### WR-02: Stale module docstring describes removed `xfail` markers as present

**File:** `tests/test_master_include_set_predicate_gate.py:27-31` (plus
related staleness at lines ~161-162, ~256-257)
**Issue:** See "New Findings" section above for full detail. The docstring
claims RED-phase evidence is "recorded ... as `xfail(strict=True)`" in this
file, but the fix commit removed all six `xfail` decorators without
updating this claim.
**Fix:** Rephrase to past tense, describing the `xfail` markers as having
existed during RED and having been removed once the fix landed (see
suggested replacement text above).

---

_Reviewed: 2026-08-12T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
_Scope: plans 47-13/47-14 gap closure only (diff 80043b3^..HEAD), 12 files_
