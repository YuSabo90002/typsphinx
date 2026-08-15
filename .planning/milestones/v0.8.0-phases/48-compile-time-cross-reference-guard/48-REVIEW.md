---
phase: 48-compile-time-cross-reference-guard
reviewed: 2026-08-14T04:52:07Z
depth: standard
files_reviewed: 9
files_reviewed_list:
  - typsphinx/translator.py
  - tests/test_whole_document_xref_unit.py
  - tests/test_xref_whole_document_guard_render_gate.py
  - tests/test_desc_rubric_decoupling_render_gate.py
  - tests/fixtures/xref_whole_document_guard_gate/conf.py
  - tests/fixtures/xref_whole_document_guard_gate/index.rst
  - tests/fixtures/xref_whole_document_guard_gate/included.rst
  - tests/fixtures/xref_whole_document_guard_gate/orphan.rst
  - tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ
findings:
  critical: 1
  warning: 1
  info: 0
  total: 2
status: resolved
resolved_in: d3f29605
resolved_by: orchestrator
---

# Phase 48: Code Review Report

**Reviewed:** 2026-08-14T04:52:07Z
**Depth:** standard
**Files Reviewed:** 9
**Status:** issues_found

## Summary

This review covers `2bbbc6d3..HEAD` — the G-48-4 / XREF-03 gap-closure work
(plans 48-05/06/07) that fixes the dead-link whole-document `:doc:` reference
bug, not yet reviewed at the previous checkpoint.

The core mechanism is sound: the self-anchor token
(`_WHOLE_DOCUMENT_SELF_ANCHOR_TOKEN = "__tsx-doc__"`), its emission in
`visit_document`, and the guarded reference emission in `visit_reference`
correctly reuse the single existing `_label_existence_guard` derivation point
— no second guard-string or label helper was introduced. I independently
verified the label-collision-safety claims in the new module-level comment
(lines 32-44) against the actually-installed Sphinx 9.1.0 / docutils source:
docutils' `make_id` never emits an underscore even when the input already has
one, and Sphinx's own `_make_id`/`make_id` (used by the python/javascript
domains with an empty `prefix`) only ever feeds a dotted Python-identifier
string through, which structurally excludes `-`. Both claims hold; the
`docname:__tsx-doc__` label cannot collide with a real anchor produced
elsewhere in the translator. `golden.typ`'s one-line diff matches the
self-anchor's documented emission form exactly, and the render-gate/unit
tests are genuine, non-weakened, non-xfail assertions that exercise the real
whole-document path (verified by running all 22 new/changed tests locally —
all pass).

However, the routing predicate `_whole_document_reference_eligible`
(translator.py:3084-3136) has a real blast-radius gap beyond the deliberately
accepted `genindex`/`py-modindex`/`search` policy carve-out: it gates purely
on `target_docname in env.found_docs`, with **no check that the reference was
actually Sphinx-resolved** (`node.get("internal")`). I reproduced, with a
real `sphinx-build -b typstpdf` run (not just a synthetic unit-node probe),
a case where a hand-written relative rST link to a genuine external file
(e.g. a downloadable `report.pdf` asset) is silently hijacked into a
compile-time-guarded jump to an unrelated document's self-anchor, solely
because a real Sphinx document happens to share the same relative path stem.
This is exactly the failure mode the review's own focus asked to be checked
for point 2 ("a hand-written relative rST link to a genuine `.pdf` file asset
must keep working") — it does not always keep working. See CR-01 below.

## Critical Issues

### CR-01: Whole-document guard hijacks hand-written links to real asset files that share a path with a real document

**File:** `typsphinx/translator.py:3084-3136` (`_whole_document_reference_eligible`), consumed at `typsphinx/translator.py:3208-3213` (`_reference_anchor_decision`)

**Issue:** `_whole_document_reference_eligible` decides whether a no-fragment
local refuri gets routed through the D-07 compile-time guard using *only*
`target_docname in env.found_docs` — it deliberately ignores whether the
reference node was actually produced by Sphinx's own resolver
(`node.get("internal")`, present in the function signature but explicitly
unused per its own docstring, lines 3122-3126). `_resolve_xref_docname`
(translator.py:4886-4936) is likewise unconditional: it resolves *any* local,
no-fragment refuri ending in the builder's `out_suffix`, regardless of
whether Sphinx ever resolved it as a document reference — including a
plain, hand-authored docutils hyperlink to an unrelated file.

Combined, these two facts mean a bare rST hyperlink to a real, non-document
file (e.g. a downloadable PDF data sheet, common in real doc trees for the
`typstpdf` builder where `out_suffix == ".pdf"`, per `builder.py:1245`)
silently gets its destination rewritten to a whole-document self-anchor jump
whenever a real Sphinx document happens to resolve to the same relative
path stem — with zero warning, and a build that still exits 0.

Reproduced end-to-end with a real `sphinx-build -b typstpdf` run (not just a
unit-level node stub): a project with `report.rst` (a real, toctree-included
document) and, in `index.rst`, a hand-written link `` `real PDF asset
<report.pdf>`_`` (intended to open an actual shipped `report.pdf` asset, not
the `report` document) emits:

```
text("real PDF asset")}]; if query(<report:__tsx-doc__>).len() > 0 { link(<report:__tsx-doc__>, __tsx_body) } else { __tsx_body } }
```

instead of the correct `link("report.pdf", ...)`. The link's destination
silently changes from "open the shipped asset file" to "jump to the `report`
document's own heading" — a materially different, wrong destination, emitted
with no diagnostic. Before this phase's fix, the same no-fragment refuri
always resolved to `None` in `_resolve_xref_docname`, so this exact
collision surface did not exist for the no-fragment case (only the
already-shipped anchored-refuri form could theoretically collide, and that
path is explicitly unaffected/pre-existing — D-06). This phase's change
therefore *expands* the collision surface without adding the
`node.get("internal")` check its own test module's docstring
(`tests/test_whole_document_xref_unit.py:12-22`) claims exists.

Minimal repro (also confirmed against the real `TypstTranslator`, not a
mock):

```python
builder = _StubBuilder(current_docname="index", found_docs={"report"})
translator = TypstTranslator(_make_document(), builder)
ref = docutils_nodes.reference("", "", internal=False)  # hand-authored, NOT Sphinx-resolved
ref["refuri"] = "report.pdf"
decision = translator._reference_anchor_decision(ref)
assert decision.xref is None  # FAILS: decision.xref == ('report', '')
```

**Fix:** Gate `_whole_document_reference_eligible` on `node.get("internal")`
in addition to the `found_docs` membership test, so only references Sphinx
itself resolved (`:doc:`, `:ref:`, toctree-generated) are eligible for the
whole-document guard — matching what the test module's own docstring already
(incorrectly) claims the implementation does:

```python
def _whole_document_reference_eligible(
    self, node: nodes.reference, target_docname: str
) -> bool:
    if not node.get("internal"):
        return False
    return target_docname in getattr(
        getattr(self.builder, "env", None), "found_docs", ()
    )
```

Add a regression test (real-build or node-level) covering exactly the
divergent case that is currently untested: a non-internal reference whose
resolved path *does* land in `found_docs` — see WR-01 below, this is the
missing test that would have caught CR-01.

## Warnings

### WR-01: Test module's own docstring misdescribes the implemented policy, and no test exercises the one case that would distinguish the two descriptions

**File:** `tests/test_whole_document_xref_unit.py:12-22, 195-277`

**Issue:** The module docstring states the policy predicate "additionally
gates whether that resolved pair is exposed through its own `.xref` field on
`node.get("internal")` being truthy AND the target docname being a member of
`env.found_docs`" (lines 18-22). This is not what `_whole_document_reference_
eligible` implements (see CR-01) — the actual code never reads
`node.get("internal")`. `_whole_document_reference_eligible`'s own docstring
(translator.py:3106-3114) is more precise and confirms the `internal` flag is
deliberately never consulted under option-a.

None of the four tests in `TestReferenceAnchorDecisionWholeDocumentPolicy`
distinguishes the two descriptions, because every scenario pairs
`internal=False` with an *empty* `found_docs` set, or `internal=True` with a
matching `found_docs` entry — the discriminating combination
(`internal=False` with the target present in `found_docs`, which is exactly
CR-01's repro) is never constructed. `test_non_internal_reference_onto_
unknown_target_not_guarded` (lines 221-237) sounds like it covers this but
its `found_docs=set()` makes the assertion pass for a reason unrelated to the
`internal` flag at all.

**Fix:** Add the missing discriminating test (asserting `decision.xref is
None` for a non-internal reference onto a *known* target) once CR-01's fix
lands, and correct the module docstring's lines 18-22 to describe the actual
`found_docs`-only policy (or, if the `internal` check is added per CR-01,
leave the docstring as originally written and this finding is resolved by
the same fix).

---

_Reviewed: 2026-08-14T04:52:07Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

---

## Resolution (orchestrator, 2026-08-14)

Both findings were independently re-measured by the orchestrator before acting — a
reviewer's Critical is a claim to verify, not a verdict to apply — and both were
**confirmed**. Both are now **fixed** in commit `d3f29605`.

### CR-01 — CONFIRMED and FIXED

Reproduced on a minimal `sphinx-build -b typstpdf` project built by the orchestrator
(`index.rst` carrying a hand-written ``` `the report <report.pdf>`_ ``` link, alongside a
real `report.rst` and a real `report.pdf` asset):

```typst
// before — the asset link is hijacked onto the document's self-anchor
[#{ let __tsx_body = ...; if query(<report:__tsx-doc__>).len() > 0 { link(<report:__tsx-doc__>, __tsx_body) } else { __tsx_body } }]

// after — the asset link is preserved
[#link("report.pdf", text("the report"))#label("index:the-report")]
```

**Classified as a defect against the pre-declared spec, not as the owner's policy choice.**
Two independent records fix the intended behaviour:

1. The plan 48-05 blocking checkpoint presented `internal` as "a measured discriminator
   available to both" options and stated plainly that "**both options preserve such asset
   links untouched**"; option-a's own listed pro was "zero risk to any relative link to a
   genuine file asset". The owner selected option-a with that guarantee attached.
2. Plan 48-06's unit gate — written *before* any emitter existed — specified the policy in
   its "Design split" docstring as `node.get("internal")` truthy **AND** `found_docs`
   membership.

Plan 48-07's implementation dropped the first conjunct and its docstring mis-recorded the
`internal` test as belonging to the rejected option-b. Pre-fix, `_resolve_xref_docname`
returned `None` for any no-fragment refuri, so asset links took the external-reference
branch correctly — confirming this as a regression introduced by 48-07, not a pre-existing
gap.

**The restored conjunct changes nothing else, verified by re-measurement rather than
reasoning alone.** A clean `rm -rf docs/_build && tox -e docs-pdf` rebuild followed by the
plan's own enumeration snippet gives:

| | Pre-declared expectation (§6) | Post-fix measurement |
|---|---|---|
| URI actions ending in `out_suffix` | 5 | **5** |
| Sub-population A (resolves onto a real docname) | 0 targets / 0 annotations | **0 / 0** |
| Sub-population B (Sphinx-generated pages, by policy) | 5 targets / 5 annotations | **5 / 5** |

All 35 sub-population-A annotations that plan 48-07 closed remain closed — they were all
Sphinx-internal `:doc:` references, so the `internal` conjunct excludes none of them.

### WR-01 — CONFIRMED and FIXED

The three pre-existing policy tests could not isolate the `internal` conjunct: one fails
**both** conjuncts simultaneously (so it passes even when `internal` is never read), and one
isolates only `found_docs`. Added
`test_non_internal_reference_onto_known_document_not_guarded`, the single discriminating
combination (non-internal reference whose target **is** in `found_docs`), and verified it
**RED without the fix / GREEN with it** rather than only observing it pass.

### Gates after the fix

`1080 passed, 5 skipped, 0 xfailed` (baseline 1079 + the one new regression test);
`ruff check .`, `black --check .`, `mypy typsphinx/` all clean.
