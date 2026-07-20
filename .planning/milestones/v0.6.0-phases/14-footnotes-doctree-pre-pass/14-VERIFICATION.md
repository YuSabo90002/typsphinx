---
phase: 14-footnotes-doctree-pre-pass
verified: 2026-07-12T05:50:58Z
status: passed
score: 10/10 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 14: Footnotes (doctree pre-pass) Verification Report

**Phase Goal:** `footnote`/`footnote_reference` render via Typst-native `footnote[...]` using a new
document-order pre-pass that indexes footnote bodies by id. Notes appear inline at the reference
site (not at the docutils definition location), and a footnote cited more than once reuses its
placed note by label rather than duplicating it.
**Verified:** 2026-07-12T05:50:58Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `visit_document` builds a document-order `{footnote-id: footnote-node}` pre-pass index (`self._footnote_index`) and an empty `self._emitted_footnote_ids` set before body content is visited | ✓ VERIFIED | `typsphinx/translator.py:200-205` — dict comprehension over `self.document.findall(nodes.footnote)`, placed before `self.add_text("#{\n")`. `tests/test_footnotes.py::test_footnote_index_built` passes. |
| 2 | `visit_footnote` raises `SkipNode`, emitting nothing at the definition's natural location; unreferenced footnote silently dropped | ✓ VERIFIED | `typsphinx/translator.py:1410-1425`. `tests/test_footnotes.py::test_visit_footnote_skips_definition` passes — body marker absent from output. |
| 3 | FIRST `footnote_reference` to an id emits `[#footnote({body}) <fn-id>]`, body sourced via buffer-swap of `footnote_node.children[1:]` walked through the normal visitor chain, never `astext()` | ✓ VERIFIED | `typsphinx/translator.py:1490-1520` — `self.body = []`, `child.walkabout(self)` loop over `footnote_node.children[1:]`, no `.astext()` call anywhere in the handler. `tests/test_footnotes.py::test_first_reference_definition_form` passes. |
| 4 | REPEAT `footnote_reference` to an already-emitted id emits bare `footnote(<fn-id>)`, no bracket-wrap, no re-rendered body; numbering owned by Typst's native `footnote()` | ✓ VERIFIED | `typsphinx/translator.py:1485-1489`. `tests/test_footnotes.py::test_repeat_reference_reuse_form` passes — `output.count("footnote({") == 1`, body marker count == 1. |
| 5 | Dangling `footnote_reference` (refid absent from index) logs `logger.warning` naming the refid, skips, emits no `footnote(...)` call; `citation`/`citation_reference` untouched | ✓ VERIFIED | `typsphinx/translator.py:1467-1475` — guard runs before any emission. `tests/test_footnotes.py::test_dangling_reference_warns` passes. No `visit_citation`/`visit_citation_reference` handlers were added or modified (git diff confirms no change outside the three new/edited footnote methods). |
| 6 | `tests/test_footnotes.py` exercises all five branches and all pass | ✓ VERIFIED | `uv run python -m pytest tests/test_footnotes.py -q` → 5 passed. |
| 7 (SC#1) | Single-ref renders one footnote at the reference site, body present exactly once in the compiled PDF, no floating body at the definition location | ✓ VERIFIED | `tests/test_pdf_render_gate.py::TestFootnoteRenderGate::test_single_reference_body_once` — real, uncaught `typst.compile()` + `pypdf` text extraction, asserts `full_text.count(FOOTNOTE_SINGLE_SENTINEL) == 1`. Ran and passed. |
| 8 (SC#2) | Double-ref renders a marker at both sites without duplicating the body; second citation reuses by label | ✓ VERIFIED | `tests/test_pdf_render_gate.py::TestFootnoteRenderGate::test_double_reference_body_not_duplicated` — asserts body sentinel count == 1 while both citing paragraphs appear exactly once each. Ran and passed. |
| 9 (SC#3) | Body with inline markup (emph/literal) + markup-special chars renders correctly via buffer-swap, never `astext()` | ✓ VERIFIED | `tests/test_pdf_render_gate.py::TestFootnoteRenderGate::test_body_inline_markup_and_special_chars` — asserts sentinel, "emphasis", "literal", and `"@ # $ _ * < >"` all present in extracted PDF text. Ran and passed. |
| 10 (SC#4) | Real-compile GATE-01 fixture exercises single-ref, double-ref, and footnote-inside-a-list-item | ✓ VERIFIED | `tests/fixtures/footnote_render_gate/index.rst` combines all four shapes in one master document; `tests/test_pdf_render_gate.py::TestFootnoteRenderGate::test_footnote_inside_list_item` passes; class-scoped fixture runs one real `sphinx-build` + uncaught `typst.compile()` + `pypdf` extraction per class. Ran and passed. |

**Score:** 10/10 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `typsphinx/translator.py::visit_document` (pre-pass index) | Builds `_footnote_index`/`_emitted_footnote_ids` before body visited | ✓ VERIFIED | Lines 175-208; correctly ordered before `#{` wrapper. |
| `typsphinx/translator.py::visit_footnote` | `SkipNode`, no `depart_footnote` | ✓ VERIFIED | Lines 1410-1425; no matching `depart_footnote` exists in file. |
| `typsphinx/translator.py::visit_footnote_reference` | definition/reuse/dangling branches | ✓ VERIFIED | Lines 1427-1527; no matching `depart_footnote_reference` exists. |
| `tests/test_footnotes.py` | 5 unit tests, all 5 branches | ✓ VERIFIED | 5 test functions present, all pass. |
| `tests/fixtures/footnote_render_gate/conf.py` | minimal single-master fixture project | ✓ VERIFIED | Present, matches `topic_line_block_render_gate` pattern. |
| `tests/fixtures/footnote_render_gate/index.rst` | combines SC#1-4 with 4 distinct sentinels | ✓ VERIFIED | Present; all 4 sentinels (`FOOTNOTESINGLESENTINEL`, `FOOTNOTEDOUBLESENTINEL`, `FOOTNOTEMARKUPSENTINEL`, `FOOTNOTELISTSENTINEL`) present. |
| `tests/test_pdf_render_gate.py::TestFootnoteRenderGate` | class + class-scoped fixture + 4 methods | ✓ VERIFIED | Lines 1150-1324; class-scoped fixture runs uncaught `typst.compile()`; 4 thin methods, each closing with `LEAK_SIGNATURES` negative control. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `footnote_reference['refid']` | `footnote['ids'][0]` | `self._footnote_index` built from `self.document.findall(nodes.footnote)` | ✓ WIRED | `translator.py:200-205`, consumed at `:1468`. Deviation from plan's literal `.traverse()` wording documented and justified in SUMMARY (deprecated API, `findall()` is the non-deprecated equivalent) — this is a Rule-1 auto-fix, not a scope deviation; behavior identical. |
| definition body | rendered inline | buffer-swap of `footnote_node.children[1:]` via `child.walkabout(self)`, never `node.astext()` | ✓ WIRED | `translator.py:1497-1519`; confirmed no `.astext()` call in the handler. |
| first-cite vs reuse | branch selection | `refid in self._emitted_footnote_ids` | ✓ WIRED | `translator.py:1485`; dangling guard (`:1470-1475`) runs before this check. |
| `footnote_render_gate_pdf_text` fixture | `typst.compile()` | uncaught real compile, no try/except | ✓ WIRED | `test_pdf_render_gate.py:1166-1191`; confirmed no try/except wraps the `typst.compile()` call. |

### Behavioral Spot-Checks / Real-Compile Gate

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Unit branch tests (index/skip/definition/reuse/dangling) | `uv run python -m pytest tests/test_footnotes.py -q` | 5 passed | ✓ PASS |
| Real-compile GATE-01 render gate (SC#1-4) | `uv run python -m pytest tests/test_pdf_render_gate.py -k FootnoteRenderGate -q` | 4 passed | ✓ PASS |
| Full non-integration suite regression check | `uv run python -m pytest -q --ignore=tests/test_integration_{advanced,basic,multi_doc,nested_toctree}.py` | 402 passed | ✓ PASS |
| Lint/format/type parity | `nix-shell -p ruff --run "ruff check ."`, `uv run black --check .`, `uv run mypy typsphinx/` | all clean | ✓ PASS |
| Version-sync surface untouched | `git diff --stat aa0b810..HEAD -- typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ` | no output | ✓ PASS |

Note: the 45 tests in `tests/test_integration_{advanced,basic,multi_doc,nested_toctree}.py` were excluded per the known pre-existing NixOS sandbox environmental failure (subprocess `uv run sphinx-build` incompatibility), not a phase regression — consistent with the orchestrator's prior confirmation.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|--------------|------------|--------------|--------|----------|
| FN-01 | 14-01-PLAN.md, 14-02-PLAN.md | `footnote`/`footnote_reference` render via Typst-native `footnote[...]`, doctree pre-pass, inline-at-reference, reuse-by-label | ✓ SATISFIED | Both plans declare `requirements: [FN-01]`; REQUIREMENTS.md marks FN-01 `[x]` Complete, mapped to Phase 14 (only requirement mapped to this phase — no orphans). All 10 truths above verified. |

No orphaned requirements found for Phase 14 (REQUIREMENTS.md's phase-mapping table lists only FN-01 for Phase 14).

### Anti-Patterns Found

None. Grep for `TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER` across `typsphinx/translator.py`, `tests/test_footnotes.py`, `tests/test_pdf_render_gate.py`, and the new fixture files returned no matches. No stub returns, no hardcoded empty data flowing to rendering, no `node.astext()` shortcuts in the footnote body path.

### Notable Deviation (Documented, Not a Gap)

Plan 14-02's own scope fence stated "No edits to `typsphinx/` runtime code" for that plan, but the real-compile GATE-01 gate (the plan's entire purpose) surfaced a genuine paragraph-state-clobbering bug in `visit_footnote_reference`'s buffer-swap (footnote body's nested `paragraph` child unconditionally reset `self.in_paragraph`/`self.paragraph_has_content`, dropping the outer paragraph's separator and producing a FATAL Typst compile abort for any footnote followed by trailing text — i.e. the overwhelming majority of realistic usage). This was fixed with a 6-line save/restore matching the established `visit_emphasis`/`visit_strong`/`visit_subscript`/`visit_superscript` convention, and verified by the real compile passing. This is exactly the scenario the plan's own threat model anticipated (T-14-03: the uncaught `typst.compile()` is the verification that the guards hold). Confirmed present in the code at `translator.py:1499-1519` and confirmed the render-gate tests pass with it in place. Not a gap — this is the GATE-01 mechanism working as designed.

### Human Verification Required

None. All must-haves are verified by automated string-assertion unit tests and a real, uncaught `typst.compile()` → `pypdf` text-extraction acceptance gate — no visual, real-time, or subjective judgment items remain.

### Gaps Summary

No gaps found. All 4 ROADMAP.md Success Criteria and all must_haves truths from both PLAN frontmatters are verified against the actual codebase (not just SUMMARY.md claims): the three translator handlers exist with the exact documented behavior, the pre-pass index is built before body visitation, the buffer-swap idiom is used (no `astext()`), the definition/reuse split is gated by a set, the dangling-refid guard runs before emission, and the GATE-01 real-compile fixture proves all of this compiles cleanly end-to-end via an uncaught `typst.compile()` call — including catching and fixing a real bug (the paragraph-state clobber) that would otherwise have made most real-world footnote usage a fatal compile abort. `citation`/`citation_reference` handlers are confirmed untouched (D-07). The `@preview` package version-sync surface (`writer.py`, `template_engine.py`, `templates/base.typ`) is confirmed untouched. Requirement FN-01 is the only requirement mapped to Phase 14 and is fully satisfied with no orphans.

---

_Verified: 2026-07-12T05:50:58Z_
_Verifier: Claude (gsd-verifier)_
