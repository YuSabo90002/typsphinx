---
phase: 21-residual-fidelity-fixes-clusters-c-d-e-f
reviewed: 2026-07-20T14:08:00Z
depth: deep
files_reviewed: 2
files_reviewed_list:
  - typsphinx/translator.py
  - typsphinx/templates/base.typ
findings:
  critical: 0
  warning: 3
  info: 1
  total: 4
status: issues_found
---

# Phase 21: Code Review Report

**Reviewed:** 2026-07-20T14:08:00Z
**Depth:** deep
**Files Reviewed:** 2
**Status:** issues_found (advisory — no blockers)

## Summary

Reviewed the diff `88ca7c6..HEAD` for `typsphinx/translator.py` (five
node-handler edits: FID-10 ZWSP, FID-12 markup-aware wrapper brace, FID-11
soft-newline collapse, FID-14 abbr-title suppression, FID-13 boundary
newline drop) and `typsphinx/templates/base.typ` (one `#show link:` rule).

Traced every guard/predicate against its surrounding control flow (not just
the touched lines): the `visit_literal_block` FID-12 `wrapper_prefix`
predicate is provably identical in shape to the pre-existing
`in_markup_context` predicate a few lines below it (both gate on
`in_captioned_code_block and code_block_caption`, with FID-12's `not
in_list_item` inverted correctly relative to where it's applied), the
FID-13 `visit_target` fix's "preceding content always ends in `)`" claim
holds for every reachable code path (the emitted content immediately before
a `[...#label(...)]` markup block is always a closing paren, whether from
`link(...)` or a nested `#text("...")` call), and the FID-11 blanket
`"\n" -> " "` replace in `visit_Text` is scoped correctly relative to
`in_literal_block` (early-returns above it) and `line`/`line_block` content
(each `line` node is a separate docutils node with its own Text child — no
embedded `\n` reaches `visit_Text` from that path). `@preview` package
version strings in `base.typ` are unchanged and remain byte-identical
across `writer.py` / `template_engine.py` / `base.typ` (verified via grep).
The full existing test suite (521 tests) plus the six new/updated
render-gate test modules for this phase all pass, and `black`/`ruff`/`mypy`
are clean on `translator.py`.

No blocking defects found. Three warnings flag heuristics whose match
condition is broader (FID-10) or narrower-but-fragile (FID-14) than the
specific bug they were introduced to fix, with plausible (if narrow)
false-positive/false-fidelity inputs that are not covered by the new
render-gate tests. One info item notes a debuggability gap.

## Warnings

### WR-01: FID-10's leading-ZWSP guard fires on any inline literal in the no-break-before class, not just colon-leading role tokens — silently injects an invisible character into unrelated code snippets

**File:** `typsphinx/translator.py:1255-1275`
**Issue:** The diagnosed bug (21-RESEARCH.md Pattern 1) is specifically about colon-leading Sphinx role tokens like `` :cpp:any: `` overflowing the page margin. The fix as implemented is not scoped to that case — it fires for *any* non-table inline `literal` node whose first character is in `":;,)]}!?"`, regardless of whether the content originated from a role cross-reference or is ordinary user-authored inline code. For example, an author writing `` `):` `` or `` `?)` `` or `` `!` `` as a plain inline code snippet (a real, plausible occurrence in code documentation — e.g. documenting a closing-paren-plus-colon Python idiom, or a shell `!` history-expansion literal) will silently get a U+200B zero-width space prepended to the `raw(...)` string content. This is invisible in the rendered PDF, but it corrupts the text a reader would extract via copy-paste or `pdftotext` (an extra invisible codepoint before the visible glyphs) — a direct fidelity regression in a phase whose stated purpose is rendering fidelity. The new render-gate test (`tests/test_inline_literal_overflow_render_gate.py`) only exercises the intended `:cpp:*:` role-token case and does not cover a plain user-authored literal starting with one of the broader class characters, so this scope-creep is untested.
**Fix:** Either (a) narrow the guard to the actual diagnosed pattern (a literal whose content matches a Sphinx cross-reference role shape, e.g. `re.match(r"^:\w", code_content)` restricted to the leading colon, since the described bug and the fixture only ever exercise `:`-prefixed role tokens), or (b) if the broader UAX14 class genuinely needs the break-opportunity for other punctuation too, add an explicit test asserting the ZWSP does *not* leak into extracted text for a plain, non-role inline literal starting with `)`, `!`, `?`, etc., and document that copy/paste fidelity for those literals is intentionally traded for line-wrapping.

### WR-02: FID-14's abbreviation-suppression heuristic can silently drop a genuine `:abbr:` expansion whose acronym text happens to be exactly `"*"` or `"/"`, and ignores a more robust signal that already exists

**File:** `typsphinx/translator.py:4383-4386`
**Issue:** The guard `node.astext() not in ("*", "/")` is a text-content heuristic, not a structural one. Sphinx's auto-generated PEP 3102/570 separators are always wrapped as `addnodes.desc_sig_operator(..., classes=['positional-only-separator'])` / `classes=['keyword-only-separator']` around the `abbreviation` node (see `sphinx/domains/python/_annotations.py:519-538`) — i.e. a genuinely distinguishing, structural class marker *is* available on the abbreviation's parent node, contradicting the docstring's claim that "no distinguishing classes/ids exist" (that claim is true only of the `abbreviation` node's *own* `classes` attribute, not its parent). Relying on `node.astext()` instead means a legitimate `` :abbr:`*(the wildcard symbol)` `` or `` :abbr:`/(division operator)` `` usage — a plausible, if uncommon, real-world docstring — has its expansion silently swallowed with no warning, which is the opposite of the fidelity goal this phase targets. The new test (`tests/test_abbr_pep_separator_render_gate.py`) only exercises a genuine `:abbr:` with an unrelated acronym string (`ABBRSENTINELACRONYM`), so this false-positive path is untested.
**Fix:** Check `node.parent.get("classes", [])` for `"positional-only-separator"` / `"keyword-only-separator"` (or check that the node has no `ids`/is inside a `desc_sig_operator`) instead of matching on `node.astext()`. This closes the false-positive gap without weakening the fix's intended scope, since it targets the actual structural marker Sphinx already provides.

### WR-03: FID-11's blanket `"\n" -> " "` collapse in `visit_Text` has no test coverage for text containing a literal backslash immediately followed by `n` (pre-existing escape collision) and is asserted only via string-index slicing rather than a scoped node-level unit test

**File:** `typsphinx/translator.py:988`
**Issue:** This is a minor test-design gap rather than a functional bug: the new render-gate test (`tests/test_paragraph_soft_newline_render_gate.py`) verifies correctness only by locating two sentinel substrings in the full `.typ` output and slicing between their indices (`typ_text[alpha_idx:beta_idx]`). This pattern is fragile to unrelated future changes reordering the fixture's paragraph content, and there is no smaller unit-level test in `test_translator.py` that calls `visit_Text` directly with a synthetic `nodes.Text("a\nb")` and asserts the emitted `text("a b")` output — every other translator method in this file has such a direct unit test alongside its render-gate test. This makes the fix harder to pin down when a future refactor accidentally reintroduces the bug (the render-gate test failure would only point at "some sentinel moved" without isolating `visit_Text`).
**Fix:** Add a focused unit test in `tests/test_translator.py` that directly instantiates the translator, calls `visit_Text` with a `nodes.Text` node containing an embedded `\n`, and asserts the exact expected `text("...")` output — cheaper to run and easier to diagnose than the full `sphinx-build` + `typst.compile()` render-gate test.

## Info

### IN-01: FID-13's `visit_target` correctness relies on an implicit invariant (docutils always emits the closing paren immediately before a sibling `target`) that is not enforced or asserted anywhere in code

**File:** `typsphinx/translator.py:2801-2838`
**Issue:** The FID-13 fix's safety argument ("the preceding content is always the closing `)` of the reference's `link(...)` call") is correct for every path traced during this review, but it is an emergent property of several independently-evolving branches in `visit_reference`/`depart_reference` (same-doc refid, cross-doc xref, external URL, degraded-xref-to-text, empty-URL). A future edit to any of those branches that changes what gets emitted immediately before a target's markup-mode `[...]` closes could silently reintroduce a stray-newline-equivalent glued-token bug (e.g., emitting bare text without a trailing function call) with no test failure pointing at the actual cause, since the fix has no explicit assertion of the "always ends in `)`" invariant.
**Fix:** No code change required now; consider a one-line comment/assertion note near the top of `visit_reference` cross-referencing this invariant, or extend `test_external_link_style_render_gate.py`'s boundary test to also cover an internal same-document reference-with-target (not just external), since only the external case is currently exercised for the boundary fix.

---

_Reviewed: 2026-07-20T14:08:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: deep_
