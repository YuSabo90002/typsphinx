---
phase: 48-compile-time-cross-reference-guard
reviewed: 2026-08-12T06:52:02Z
depth: standard
files_reviewed: 19
files_reviewed_list:
  - typsphinx/translator.py
  - typsphinx/builder.py
  - tests/test_label_existence_guard_unit.py
  - tests/test_xref_compile_time_guard_render_gate.py
  - tests/test_citation_caption_dangling_label_gate.py
  - tests/test_citation_degradation_gate.py
  - tests/test_citation_render_gate.py
  - tests/test_master_include_set_predicate_gate.py
  - tests/test_translator.py
  - tests/test_xref_orphan_degrade_render_gate.py
  - tests/fixtures/xref_per_master_guard_gate/conf.py
  - tests/fixtures/xref_per_master_guard_gate/index.rst
  - tests/fixtures/xref_per_master_guard_gate/bravo.rst
  - tests/fixtures/xref_per_master_guard_gate/target.rst
  - tests/fixtures/citation_caption_dangling_label_gate/conf.py
  - tests/fixtures/citation_caption_dangling_label_gate/index.rst
  - tests/fixtures/xref_label_collision_guard_gate/conf.py
  - tests/fixtures/xref_label_collision_guard_gate/index.rst
  - tests/fixtures/xref_label_collision_guard_gate/a/b.rst
  - tests/fixtures/xref_label_collision_guard_gate/a_u2f_b.rst
findings:
  critical: 0
  warning: 2
  info: 2
  total: 4
status: issues_found
---

# Phase 48: Code Review Report

**Reviewed:** 2026-08-12T06:52:02Z
**Depth:** standard
**Files Reviewed:** 19
**Status:** issues_found

## Summary

Phase 48 replaces a build-time Python "is this docname in the master's toctree
closure" union with a Typst compile-time guard (`context { ... query(<label>)
... }`) around every cross-document reference, plus the matching deletion of
`TypstBuilder.master_included_docnames` / `_compute_master_included_docnames()`
and the `_ReferenceAnchorDecision.degrade_xref_to_text` field. I anchored on
`git diff db72a33..HEAD -- typsphinx/translator.py typsphinx/builder.py` and
the phase's own test/fixture set, then went further: I ran the full changed
test surface (unit + real `-b typstpdf` + `typst.compile()` gates, 174 tests
total across the reviewed modules, all green), and independently probed two
scenarios the existing suite does not cover directly — (a) a guarded
cross-document reference immediately followed by a `nodes.target` sibling
(`next_is_target=True`, which opens a second markup bracket around the guard),
and (b) two independently-guarded cross-document references inside the same
paragraph. Both compiled correctly via a hand-built doctree run through real
`typst.compile()` (not part of the shipped test suite — recommend adding
these as permanent regression coverage; see WR-01 below).

I did not find a defect in the guard's own emission logic, brace balancing,
or the `_reference_guard_close`/`_pending_xref_guard_close` slot lifecycle
(single-scalar-slot reentrancy is sound because a `reference` node cannot
nest inside another `reference` node, and `SkipNode` raised by a *child*
node never skips the parent's own `depart_reference` call). Label text
flowing into the guard's `<label>` / `query(<label>)` interpolation is
already constrained to `[A-Za-z0-9_.:-]` by the pre-existing, unmodified
`_sanitize_label`, so there is no injection surface in the new emission
sites. `master_included_docnames` / `_compute_master_included_docnames` are
fully gone with no dangling references anywhere in `typsphinx/` (verified by
both the shipped `TestSingleDerivationPointStructural` gate and an
independent grep).

The two WARNINGs below are both about things the phase's own authors
already identified and accepted (documented in fixture comments / module
docstrings) rather than things I discovered fresh — I am still surfacing
them per the adversarial-review brief, because "known and accepted" is a
different bar than "not a real correctness or coverage gap."

## Warnings

### WR-01: `next_is_target` + cross-document guarded reference has no test coverage

**File:** `typsphinx/translator.py:5169-5173` (guard open), `typsphinx/translator.py:5096-5101` (the `next_is_target` bracket that wraps it), `typsphinx/translator.py:4317-4354` (`visit_target`'s consuming half)

**Issue:** When a cross-document reference's `xref` resolves (guarded path) *and* its immediate next sibling is a `nodes.target` (`next_is_target=True`), the guard's `context { ... }` expression is opened *inside* the markup bracket `next_is_target` itself opens, and `visit_target` later closes that bracket with `#label("...")]` directly abutting the guard's closing `}` (no separator). This composition is not exercised by any test in `tests/test_xref_compile_time_guard_render_gate.py`, `tests/test_label_existence_guard_unit.py`, or `tests/test_citation_degradation_gate.py` — every guarded-reference fixture/case in the suite has an empty or non-target-following sibling. I independently built this exact doctree shape and compiled it through real `typst.compile()`; it compiled successfully (`context {...}#label("index:my-target")]` is valid), so this is **not a live defect**, but it is an untested composition of two independently-designed mechanisms (D-14's own-anchor bracket / the target-attachment bracket, and D-07's guard) that happened to work by inspection rather than by an asserted contract. A future change to either mechanism's bracket/brace shape could silently break this combination with no gate to catch it.

**Fix:** Add a case to `tests/test_label_existence_guard_unit.py` (or a small addition to `tests/test_xref_compile_time_guard_render_gate.py`'s fixture) that builds a citing reference whose `refuri` resolves cross-document *and* is immediately followed by a `nodes.target`, and assert it compiles via `typst.compile()` with the target's own label still correctly attached outside the guard's context block — mirroring the probe:
```python
ref = docutils_nodes.reference(refuri="second.typ#anchor-x")
ref += docutils_nodes.Text("Cross Doc Text")
tgt = docutils_nodes.target()
tgt["ids"] = ["my-target"]
para += ref
para += tgt
```

### WR-02: The label-namespace-collision false negative is a real (if narrow) regression versus the pre-Phase-48 mechanism

**File:** `typsphinx/translator.py:343-417` (`_label_existence_guard`), characterized by `tests/fixtures/xref_label_collision_guard_gate/` and `tests/test_xref_compile_time_guard_render_gate.py::test_label_collision_guard_links_to_decoy`

**Issue:** The guard's `query(<label>)` decides reachability by *sanitized label string identity*, not by the actual target docname. `_sanitize_label` maps `/` to the literal token `_u2f_`, so a nested docname `a/b` and an unrelated flat docname `a_u2f_b` share one label namespace after sanitization. Pre-Phase-48, the build-time union checked membership on the **raw, unsanitized** target docname (`xref[0] not in master_included_docnames`), so this exact collision degraded correctly to plain text (the raw docname `"a/b"` was genuinely absent from the set). Post-Phase-48, the same collision instead produces a **working link to the wrong document/section** — a decoy's heading — with no warning and no visual difference from a correct link. This is documented and deliberately accepted in the fixture's own `conf.py` comment and exercised (not merely asserted-away) by `test_label_collision_guard_links_to_decoy`, so it is a known, characterized trade-off rather than an oversight. I'm still flagging it as a WARNING because "silently links to the wrong content" is a materially worse failure mode for a reader than the prior "silently degrades to plain text," and the narrowing condition (a docname literally shaped like another docname's `/`-to-`_u2f_` sanitization) is exactly the kind of thing a project restructure (splitting a flat doc into a subdirectory) could trigger without anyone noticing.

**Fix:** No code fix is being requested here (the trade-off is already deliberate and load-bearing for this phase's design) — recommend only surfacing this in user-facing documentation (e.g. a note near `typst_documents`/nested-docname guidance) so a project that reorganizes docs into subdirectories is warned about the collision class, rather than leaving it discoverable only via this test fixture's internal comments.

## Info

### IN-01: Stale invariant comment in `visit_target`'s reference-with-target branch

**File:** `typsphinx/translator.py:4336-4338`

**Issue:** The comment reads: `"the preceding content is always the closing ')' of the reference's link(...) call"`. This was true before Phase 48. Since Phase 48, when the preceding reference took the guarded cross-document path, the actual preceding character is the guard's closing `}` (from `_label_existence_guard`'s `close_str`), not `)`. The comment's *reasoning* (`'#' unambiguously starts a new markup-embedded expression with no separator needed`) still holds regardless of which closing character precedes it, so this is not a functional bug — just a factual claim in a comment that is no longer universally true and could mislead a future editor auditing this fragile juxtaposition logic.

**Fix:** Update the comment to say "closing token" (or enumerate `)`/`}`) rather than asserting it is always `)`.

### IN-02: `visit_pending_xref`'s guard uses a fixed `"#"` prefix regardless of `_in_markup_mode`

**File:** `typsphinx/translator.py:4441-4457`

**Issue:** Unlike `visit_reference` (which computes `prefix = "#" if self._in_markup_mode else ""`), `visit_pending_xref` passes a hardcoded `prefix="#"` to `_label_existence_guard()`. This is called out explicitly in the added comment as a pre-existing behavior carried forward unchanged (this handler is unreachable in the normal Sphinx pipeline per the same docstring's D-04 note), so it is not a new defect introduced by this phase. Flagging only for completeness: if research assumption A2 (`48-RESEARCH.md`, "no third-party extension observed emitting a fresh `pending_xref` after `ReferencesResolver` runs") ever turns out to be false, this fixed prefix could mismatch the surrounding mode and emit invalid Typst syntax with no test coverage to catch it, since there is (by design) no reachable path to exercise it.

**Fix:** None required now — this is an accepted, documented risk on an already-unreachable defence-in-depth path. If a future Sphinx/extension interaction is ever found to reach this handler, revisit the fixed prefix at that time.

---

_Reviewed: 2026-08-12T06:52:02Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
