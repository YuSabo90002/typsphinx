---
phase: 34-inline-math-after-text-separator-fix
reviewed: 2026-07-28T00:00:00Z
depth: standard
files_reviewed: 4
files_reviewed_list:
  - typsphinx/translator.py
  - tests/test_inline_math_after_text_render_gate.py
  - tests/fixtures/inline_math_after_text_render_gate/conf.py
  - tests/fixtures/inline_math_after_text_render_gate/index.rst
findings:
  critical: 0
  warning: 4
  info: 0
  total: 4
status: issues_found
---

# Phase 34: Code Review Report

**Reviewed:** 2026-07-28
**Depth:** standard
**Files Reviewed:** 4
**Status:** issues_found

## Summary

Reviewed the phase's diff to `typsphinx/translator.py` (`visit_math` /
`visit_math_block` only — confirmed via `git diff 568121f..HEAD --
typsphinx/translator.py`) plus the three new gate-test files in full.

`visit_math`'s new code is a byte-for-byte faithful port of the
`visit_literal` separator idiom (paragraph separator → concat-context-or-
list-item separator → content → concat-content-marking-or-list-item-flag),
and I could find no defect in it. `visit_math_block`'s new code correctly
omits the concat-context half of the protocol (block math structurally
cannot be a sibling inside any of the five code-mode concat contexts) and
correctly places its leading list-item-separator check *after*
`_emit_id_anchors(node)` (verified: placing it before would starve the
anchor→math gap of a separator).

I did not stop at reading the diff — I empirically validated the fix by:
1. Swapping in the pre-fix (`568121f`) translator and re-running the gate
   tests: both go RED with the exact documented `TypstError: expected
   semicolon or line break`, confirming the tests are a real, meaningful
   regression gate (not vacuously green either way). Restored the fixed
   file afterward (`git status` clean).
2. Running the existing math test suites (`test_math_fallback.py`,
   `test_math_mitex.py`, `test_math_native.py`, 23 tests) — all still pass,
   no regression.
3. Building the fixture directly and inspecting the raw emitted `.typ` to
   independently confirm every construct's exact separator shape.
4. Constructing an additional ad hoc fixture (a `.. math:: :label:`
   equation inside a bullet list item — the specific interaction the
   scope hint flagged between `_emit_id_anchors`'s bookkeeping and
   `visit_math_block`'s new list-item bookkeeping) and confirming it
   compiles successfully.
5. `ruff check`, `black --check`, and `mypy` all pass clean on the changed
   files.

No BLOCKER-level defect was found: the fix does not introduce incorrect
behavior, a security issue, or a crash, and the `raise nodes.SkipNode`
control flow does not skip any of the new bookkeeping (it runs before the
raise in both methods). All findings below are WARNING-level: one is a
confirmed redundant/cosmetic double-separator emission introduced by the
diff, and three are test-coverage gaps in the new gate-test file that
leave parts of the fixture (and one build path) unverified by an exact
assertion — including the exact interaction (labeled equation in a list
item) that made items 1 and 2 above worth doing in the first place.

## Warnings

### WR-01: `visit_math_block`'s new list-item bookkeeping doubles up with its own pre-existing unconditional `"\n\n"`, emitting redundant blank lines

**File:** `typsphinx/translator.py:4079-4088`
**Issue:** The pre-existing (unchanged) line `self.add_text("\n\n")` at
line 4079 unconditionally emits two newlines after every block-math
expression, in *every* context (top-level and inside a list item alike) —
so any following sibling in a list item already has guaranteed separating
whitespace before it, regardless of `list_item_needs_separator`. The new
code added by this diff (lines 4081-4088) additionally sets
`self.list_item_needs_separator = True` when `self.in_list_item`. Since the
*next* sibling's own visitor (e.g. `visit_paragraph`'s
`_emit_forced_break`, or `visit_bullet_list`) independently consults that
same flag and emits its *own* leading `"\n"` when it is `True`, the two
mechanisms stack: the flag set here is never actually needed for
correctness (the unconditional `"\n\n"` already prevents any juxtaposition
"expected comma"/"expected semicolon" fatal), yet it still fires an extra,
unnecessary separator downstream.

Confirmed empirically by building the phase's own fixture — Construct E
(`* Text before block math.` / `.. math::` / `Text after block math.`)
emits:
```
text("Text before block math.")
mitex(`E = m c^2`)


parbreak()

text("Text after block math.")
```
i.e. **two** blank lines between the `mitex(...)` call and the following
`parbreak()`, versus exactly one blank line everywhere else in the same
document that a block-level construct is followed by a paragraph. This is
inert in Typst code mode (extra whitespace between statements has no
compiled/visual effect — the actual paragraph break is `parbreak()`
itself), so it is not a functional regression, but it is dead/redundant
work that diverges from every other block-level visitor in this file
(none of which pairs a hardcoded unconditional separator with the
`list_item_needs_separator` flag at the same call site) and will keep
compounding (extra blank line per math_block) as an unexplained artifact
in future diffs' emitted-`.typ` diffs.
**Fix:** Either drop the new `if self.in_list_item: self.list_item_needs_separator = True` block (lines 4081-4088) since the existing unconditional `"\n\n"` already guarantees separation from any following sibling, or — if the flag is being set defensively for some future codepath that does *not* itself unconditionally add whitespace — gate the pre-existing `"\n\n"` to only fire when *not* `self.in_list_item`, so exactly one of the two mechanisms is responsible for separation in each context (mirroring how `depart_paragraph` relies solely on the flag inside list items, with no hardcoded trailing text of its own).

### WR-02: The labeled-equation + list-item interaction that motivates the `_emit_id_anchors` ordering comment has no regression test

**File:** `typsphinx/translator.py:4046-4055`; `tests/fixtures/inline_math_after_text_render_gate/index.rst:34-42`
**Issue:** The new comment at lines 4046-4055 explicitly reasons about a
subtle ordering constraint: `_emit_id_anchors(node)` (called first, at
line 4044) has its own separator bookkeeping, and the new list-item-
separator check at lines 4054-4055 must run *after* it "or a guard placed
before it would double-separate" (actually: would *under*-separate the
anchor from the following math content — see analysis in Summary). This
is the single most subtle piece of reasoning in the whole diff, and it is
exactly the kind of interaction that regresses silently when someone
later reorders code. Yet Construct E in the fixture
(`tests/fixtures/inline_math_after_text_render_gate/index.rst:34-42`) uses
an *unlabeled* `.. math::` block — no `:label:` option — so
`_emit_id_anchors` is a no-op for it (`ids` is empty, the method returns
before touching any bookkeeping at all, per its own docstring). I manually
verified (ad hoc fixture, not committed to the test suite) that a labeled
equation inside a list item does compile correctly with the current code,
but the shipped gate suite does not lock this in: a future refactor that
reintroduces the ordering bug this comment warns against would not be
caught by any test in this phase.
**Fix:** Add a construct to the fixture (or a follow-up test) with `.. math:: ... :label: some-label` inside a list item, and assert the exact shape, e.g. that the anchor and the `mitex(...)`/`$...$` call are each on their own newline-separated line with no juxtaposition (`>]mitex(` / `>]$` absent), mirroring the existing juxtaposition guards.

### WR-03: Construct F (list item whose sole content is inline math) has no dedicated assertion

**File:** `tests/fixtures/inline_math_after_text_render_gate/index.rst:44-47`; `tests/test_inline_math_after_text_render_gate.py`
**Issue:** The fixture's own comment calls Construct F ("`* :math:`a+b`" — a
list item whose sole content is inline math) "the single-element edge",
i.e. the boundary case where math is the *first and only* expression in
the list item (`list_item_needs_separator` is `False` on entry, so no
separator/operator of any kind should be emitted before it). No assertion
in `tests/test_inline_math_after_text_render_gate.py` references `a+b` or
otherwise checks this construct's exact rendering — it is only covered
indirectly by the overall `returncode == 0` check and the generic
juxtaposition/stray-operator guards (`)mi(`, `{ + `, `( + `), none of which
would fail if, say, an extraneous leading `"\n"` were emitted before a
sole-content math node in a list item (a leading `"\n"` inside `list({...
})` is syntactically harmless, so it would not trip any existing guard,
yet it would be a state-tracking bug — the `list_item_needs_separator`
reset in `visit_list_item` not actually taking effect for this path).
**Fix:** Add an exact-string assertion for Construct F, e.g. `assert 'list({\nparbreak()\n\nmi(`a+b`)' in typ_text` (mitex path) confirming no separator precedes the sole math expression.

### WR-04: The native-math-path test has no equivalent assertion for Construct E (display math block)

**File:** `tests/test_inline_math_after_text_render_gate.py:261-345`
**Issue:** `test_typstpdf_separates_inline_math_mitex_path` has a dedicated
exact-string assertion (assertion 7, `'text("Text before block math.")\nmitex(...)'`)
proving `visit_math_block`'s list-item separator fix on the mitex path.
`test_typstpdf_separates_inline_math_native_path` — which rebuilds the
*same* fixture with `-D typst_use_mitex=0` and therefore exercises the
exact same `visit_math_block` code path with `is_typst_native or not
use_mitex` taking the native branch — has no equivalent assertion for
Construct E at all (it only asserts Constructs B and D). Since this is the
one method (`visit_math_block`) where the concat-context half of the
protocol is deliberately *not* exercised, and the diff explicitly changes
behavior on both the mitex and native branches identically, the native
build path's separator correctness for display math in a list item is
unverified by any exact assertion in this phase's own test file (build
success and the generic `)$` juxtaposition guard are the only checks that
would catch a regression there, and — per WR-03's reasoning — a spurious
extra separator would not trip either of them).
**Fix:** Add the native-path equivalent of assertion 7, e.g. `assert 'text("Text before block math.")\n$ E = m c^2 $' in typ_text`, to `test_typstpdf_separates_inline_math_native_path`.

---

_Reviewed: 2026-07-28_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
