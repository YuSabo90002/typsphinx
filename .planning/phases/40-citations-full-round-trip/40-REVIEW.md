---
phase: 40-citations-full-round-trip
reviewed: 2026-08-02T10:46:43Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - typsphinx/translator.py
  - tests/test_citation_render_gate.py
  - tests/fixtures/citation_render_gate/conf.py
  - tests/fixtures/citation_render_gate/index.rst
  - tests/fixtures/citation_render_gate/second.rst
  - examples/charged-ieee/approach1/source/index.rst
  - examples/charged-ieee/approach2/source/index.rst
findings:
  critical: 0
  warning: 3
  info: 1
  total: 4
status: issues_found
---

# Phase 40: Code Review Report

**Reviewed:** 2026-08-02T10:46:43Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

Phase 40 adds `visit_citation` / `depart_citation` / `visit_label`, a run-adjacency helper
(`_citation_run_neighbour`), a same-document backref lookup (`_find_citing_reference` /
`_citing_reference_has_own_anchor`), and a new D-14 own-anchor guard added to the existing
`visit_reference`/`depart_reference` pair, in `typsphinx/translator.py`. The other six files in
scope are a new render-gate test module, its four fixtures, and two example `.rst` files
deliberately restored byte-for-byte to a prior git blob (confirmed via `git hash-object`, matches
`82831eb092b9f52cba8b1247b95f7e148f499bb2` for both — not reviewed for content per the phase's
D-11/D-12 decision).

Verification performed beyond static reading: ran the full non-slow test suite (755 passed, 0
failed), ran `ruff check`/`mypy` on `translator.py` (clean), and ran a real `sphinx-build -b typst`
and `-b typstpdf` over the fixture directly, inspecting the emitted `.typ` and the resolved doctree
(`env.get_and_resolve_doctree`) to confirm bracket/paren balance and label/link target agreement by
hand for every construct in the fixture (single/multi backref, cross-document, duplicate key,
uncited entry, run vs. run-break, list-item nesting, concat-context nesting). All of that checked
out — no dangling label, no unbalanced bracket, no double-escaping route was found in the paths the
fixture actually exercises.

The findings below are about paths the fixture does **not** exercise: two places where the new
code's own "graceful degradation" contract is inconsistently applied, so a citing-site topology the
fixture doesn't construct could still reach a genuine Typst compile-fatal (dangling label) instead
of degrading. Both are structurally provable from the code; neither was reproduced against a real
Sphinx build in the time available for this review, so both are filed as WARNING rather than
BLOCKER — but they sit exactly in the "dangling/cross-document link()" hazard class the phase's own
design documentation calls out as compile-fatal, not cosmetic, and are worth closing before the
next citation-heavy corpus is thrown at this feature.

## Warnings

### WR-01: `_find_citing_reference` returning `None` is treated as "eligible" instead of "skip", unlike its sibling check

**File:** `typsphinx/translator.py:2856-2862`

**Issue:** In `visit_citation`'s backref loop:

```python
for refid in node.get("backrefs") or []:
    ref_node = self._find_citing_reference(refid)
    if ref_node is not None and not self._citing_reference_has_own_anchor(
        ref_node
    ):
        continue
    backref_targets.append(self._namespace_label(docname, refid))
```

When `_find_citing_reference(refid)` returns `None` (no `nodes.reference` in the current document
tree carries `refid` in its own `ids`), the `if` condition short-circuits to `False` (`ref_node is
not None` is `False`), so the loop does **not** `continue` — it falls through and appends
`_namespace_label(docname, refid)` to `backref_targets` anyway. That target is later emitted as
`link(<docname:refid>, [N])` in the citation's back-reference marker group
(`typsphinx/translator.py:2895-2903`).

This is the one path in `visit_citation`'s backref handling that is **not** symmetric with the
`_citing_reference_has_own_anchor(ref_node) is False` case immediately next to it, which is
explicitly skipped because "the definition's back-reference marker has [no target]" would otherwise
target a label that was never attached (the method's own docstring, and the class-level
`visit_citation` docstring: "A backref whose citing site's own anchor Task 1 declined to emit … is
skipped"). A `None` result from `_find_citing_reference` is a *stronger* signal that no D-14 anchor
exists for `refid` — the citing site could not even be located — yet it fails **open** rather than
closed. If `refid` genuinely has no live `nodes.reference` anywhere in the document (which
`_find_citing_reference`'s own docstring says is the exact scenario it was written to distinguish
from a *stale* `document.ids[refid]` pointer — implying the stale case is real, and the "not even in
`findall`" case is not ruled out for future citing-site topologies), the emitted
`link(<docname:refid>, …)` targets a label nothing ever attaches, which is a Typst compile
**fatal** ("label `<…>` does not exist in the document"), not a cosmetic defect — exactly the
"dangling…case" this project's own review guidance calls out.

The current fixture never reaches this branch (verified empirically: every `backrefs` id in the
fixture's resolved doctree matches exactly one `reference` node's sole `ids` entry, so
`_find_citing_reference` never returns `None` there), so this is not proven to fire against today's
corpus — filed as WARNING, not BLOCKER, on that basis.

**Fix:** Treat "not found" the same as "found but ineligible" — skip it:

```python
for refid in node.get("backrefs") or []:
    ref_node = self._find_citing_reference(refid)
    if ref_node is None or not self._citing_reference_has_own_anchor(ref_node):
        continue
    backref_targets.append(self._namespace_label(docname, refid))
```

### WR-02: `_citation_run_neighbour` skips `comment`/`system_message` siblings but not an ids-less `nodes.target`, which also emits nothing

**File:** `typsphinx/translator.py:2644-2683`

**Issue:** `_citation_run_neighbour`'s whole purpose (per its own docstring) is to scan through
sibling nodes that "emit NOTHING" so they don't spuriously break a D-05 citation run. It special-
cases exactly two node types:

```python
if isinstance(sibling, (nodes.comment, nodes.system_message)):
    i += offset
    continue
return isinstance(sibling, nodes.citation)
```

But `visit_target` (`typsphinx/translator.py:3524-3557`, the "original behavior" branch used when a
target is *not* immediately preceded by a reference) emits **nothing** — no `add_text` call at all —
when `node.get("ids")` is falsy, before raising `SkipNode`. An ids-less `nodes.target` sibling
between two citation definitions is therefore structurally identical to a comment for run-adjacency
purposes (it contributes zero bytes to the emitted `.typ`), yet `_citation_run_neighbour` treats it
as a "real" sibling: `isinstance(sibling, nodes.citation)` is `False` for a target, so the run is
reported broken, splitting what should be one `grid(...)` into two independently-aligned grids with
no error and no visible defect in most renders (D-06's own two-grid case looks identical, so this
degrades silently into a cosmetic misalignment rather than a compile fatal — lower severity than
WR-01, but the same category of gap in an abstraction whose whole job is "don't let something that
emits nothing break the run").

This is a narrow case — an anonymous/nameless explicit target directly between two citation
definitions is unusual RST — and is not exercised by the fixture. Filed as a completeness gap in the
helper, not a proven defect against the shipped corpus.

**Fix:** Extend the skip condition to also treat an ids-less target as non-breaking:

```python
if isinstance(sibling, (nodes.comment, nodes.system_message)) or (
    isinstance(sibling, nodes.target) and not sibling.get("ids")
):
    i += offset
    continue
```

### WR-03: D-14 eligibility logic is duplicated across two functions with an unenforced invariant between them

**File:** `typsphinx/translator.py:4225-4231` (visit_reference) and `typsphinx/translator.py:2712-2740` (`_citing_reference_has_own_anchor`)

**Issue:** `visit_reference` decides whether a reference gets its own D-14 anchor via three
conditions: `node.get("ids") and opens_wrapper and not next_is_target`.
`_citing_reference_has_own_anchor`, called later from `visit_citation` to decide whether a backref
marker should be skipped, re-derives the *same* answer but checks only the third condition
(whether the immediately-following sibling is a `nodes.target`):

```python
def _citing_reference_has_own_anchor(self, ref_node: nodes.reference) -> bool:
    parent = ref_node.parent
    if parent is None:
        return True
    index = parent.index(ref_node)
    if index + 1 < len(parent.children) and isinstance(
        parent.children[index + 1], nodes.target
    ):
        return False
    return True
```

It implicitly assumes `node.get("ids")` and `opens_wrapper` are always `True` for any reference node
reachable via a citation's `backrefs` list (true today, per the docstring's own claim that "only
citation-derived references carry a populated `ids`", verified empirically against this fixture).
If that invariant is ever violated in a future Sphinx/docutils version — e.g. a citation-derived
reference that legitimately degrades to `opens_wrapper=False` (the existing `degrade_xref_to_text`
path already proves `opens_wrapper` can be `False` for *some* references with populated `refuri`) —
`_citing_reference_has_own_anchor` would report `True` (anchor exists) for a reference that
`visit_reference` never actually anchored, reproducing WR-01's dangling-label hazard through a
different route.

**Fix:** Either derive both answers from one shared predicate, or have
`_citing_reference_has_own_anchor` accept/consult the same `opens_wrapper`-equivalent state (e.g. by
checking `ref_node.get("ids")` and the reference's `refuri`/`refid` emptiness directly) rather than
only the `next_is_target` half of the condition, so the two call sites cannot silently drift apart.

## Info

### IN-01: `_find_citing_reference` is a full-document linear scan invoked once per backref, per citation

**File:** `typsphinx/translator.py:2685-2710`

**Issue:** `_find_citing_reference` calls `self.document.findall(nodes.reference)` and scans every
reference node in the document for each `refid` in each citation's `backrefs` list — O(citations ×
backrefs × references) in the worst case. This is a real inefficiency but is explicitly out of scope
for this review (performance is not a v1 concern per review instructions); noted only because a
document with many citations and many backrefs could make this a noticeably slow build step. No
action required for this phase.

---

_Reviewed: 2026-08-02T10:46:43Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
