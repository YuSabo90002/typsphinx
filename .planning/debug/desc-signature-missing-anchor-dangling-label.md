---
status: investigating
trigger: "Corpus gate fatal #17 (first SEMANTIC/non-parse fatal): TypstError: label `<c._u40_alias.data>` does not exist in the document. desc_signature emits no <label> anchor for node['ids'] so refid link(<...>) references to API declarations dangle."
created: 2026-07-12T00:00:00
updated: 2026-07-12T00:00:00
---

## Current Focus

reasoning_checkpoint:
  hypothesis: "visit_desc_signature/depart_desc_signature wrap the signature in strong({...}) and never read node['ids'], so no Typst <label> anchor is emitted for API declarations. depart_reference's refid branch (line 2850) emits link(<_sanitize_label(refid)>, ...) for same-document xrefs; the anchor those links target is thus never defined -> typst.compile fails at the semantic label-resolution pass with 'label does not exist'. visit_target/visit_title/depart_term all DO emit anchors from their ids; desc_signature is the sole anchorable-id node type that does not."
  confirming_evidence:
    - "Minimal fixture (.. c:function:: void foo(int x) + :c:func:`foo` in same doc) emits `link(<c.foo>, raw(\"foo()\"))` at index.typ:30 but the signature at 24-26 is `strong({text(\"void\") ...})` with NO <c.foo> anchor. grep: `c.foo` appears ONLY inside link(...), never as an anchor definition."
    - "typst.compile('out/index.typ') raises TypstError: label `<c.foo>` does not exist in the document -- exact corpus fatal class (`<c._u40_alias.data>`)."
    - "depart_reference refid branch line 2850 uses _sanitize_label(refid); visit_target block form line 2317 uses [#metadata(none) <_sanitize_label(id)>] -- the anchor and ref sides both route through _sanitize_label, so an anchor emitted the same way on desc_signature will byte-match the ref name."
  falsification_test: "If, after emitting [#metadata(none) <_sanitize_label(id)>] for each id in depart_desc_signature, the fixture STILL raises 'label does not exist' OR the emitted anchor name != the link(<...>) ref name for the same id, the hypothesis/fix is wrong. Also: if the anchor reintroduces 'expected expression'/stray-'+' the composition is wrong."
  fix_rationale: "Emit the proven target-anchor form ([#metadata(none) <id>], bug #2) for every id on the desc_signature, each sanitized via _sanitize_label (bug #10) so it byte-matches the refid link side. Placed in depart_desc_signature AFTER depart_strong closes the strong({...}) statement, newline-separated, so it composes as its own code-mode statement without juxtaposition or stray-+. This addresses the ROOT (anchorless API-declaration signatures) generally -- every refid link to any desc_signature now resolves, not just the C alias."
  blind_spots: "Empty node['ids'] must emit nothing (byte-unchanged). Multiple ids (aliases/overloads) each get an anchor. Assumes desc_signature ids are globally unique in the doc (docutils make_id guarantees) so no 'label occurs multiple times'. Verified via corpus gate re-run for the next distinct fatal."

hypothesis: CONFIRMED (see reasoning_checkpoint)
test: "Emit anchor in depart_desc_signature; rebuild fixture; typst.compile; add fast regression test; fast suite + lint; corpus gate."
expecting: "fixture emits <c.foo> anchor == link(<c.foo>) ref; compiles to %PDF; corpus advances past the dangling-label fatal."
next_action: "Edit depart_desc_signature (translator.py ~3666) to emit [#metadata(none) <_sanitize_label(id)>] for each id."

## Symptoms

expected: Sphinx doc/ corpus compiles through -b typstpdf with no fatal; same-document xrefs to API declarations (c:alias/c:function/py:function) resolve.
actual: "TypstError: label `<c._u40_alias.data>` does not exist in the document" at semantic label-resolution pass (corpus now parses fully).
errors: "TypstError: label `<c._u40_alias.data>` does not exist in the document"
reproduction: uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -v -s
started: Pre-existing gap surfaced by Phase 15 corpus gate; FIRST semantic (non-parse) fatal after bugs #1-#16 unblocked the parse path.

## Eliminated

## Evidence

- timestamp: repro
  checked: Built minimal C-domain fixture (c:function foo + same-doc :c:func:`foo`) via -b typst; grepped emitted index.typ; ran typst.compile.
  found: index.typ:30 emits `link(<c.foo>, raw("foo()"))`; signature at 24-26 `strong({text("void") text("foo") text("(") + ... })` carries NO <c.foo> anchor. `c.foo` appears ONLY inside link(...). typst.compile -> TypstError: label `<c.foo>` does not exist in the document.
  implication: Root confirmed -- desc_signature never emits node['ids'] as an anchor; the refid link dangles. Fix = emit anchor in depart_desc_signature.

## Resolution

root_cause: depart_desc_signature wrapped the signature in strong({...}) but never read node["ids"], so no Typst <label> anchor was emitted for API declarations. depart_reference's refid branch (line 2850) emits link(<_sanitize_label(refid)>, ...) for same-document xrefs to declarations, but the anchor those links point at was never defined -- unlike visit_target/visit_title/depart_term. So typst.compile aborted at the semantic label-resolution pass with 'label `<c._u40_alias.data>` does not exist'.
fix: depart_desc_signature now emits [#metadata(none) <_sanitize_label(id)>] (the proven target-anchor form, bug #2) for every id in node["ids"], each sanitized via _sanitize_label (bug #10) so the anchor name byte-matches the refid link side. Placed after depart_strong closes strong({...}), newline-separated, composing as its own code-mode statement. Empty ids -> nothing emitted (byte-unchanged). Multiple ids (aliases/overloads) each anchored; deduped defensively.
verification: New tests/test_desc_signature_anchor_render_gate.py PASSES with fix, FAILS pre-fix (git stash translator.py) with the exact 'label `<c._u40_alias.data>` does not exist' fatal; asserts every same-doc link(<name>) has a matching [#metadata(none) <name>] anchor (anchor==ref) incl. the corpus id c._u40_alias.data. Fast suite 419 passed / 15 deselected (418 prior + 1 new; NO existing expectation updated -- none encoded anchorless signatures). black/ruff/mypy clean. Corpus gate: bug #17 FIXED -- corpus advances PAST all desc_signature dangling labels (C-alias c._u40_alias.data/.f now resolve; ObjType/Index/IndexEntry/PythonDomain all anchor). NOT GATE-02 green. Next distinct fatal #18 = TypstError 'label `<sphinx.domains.Domain>` does not exist' -- DISTINCT ROOT CAUSE (not the anchor gap): the class `sphinx.domains.Domain` desc_signature render AND its anchor are appended to self.body but then ORPHANED by a PRE-EXISTING NESTED-DEFINITION-LIST buffer bug. visit_term/visit_definition use a single-slot self.saved_body (not a stack); a definition list nested inside a definition clobbers the outer saved_body, so the outer main body (holding the leading desc_signature + anchor) is never restored/joined. Confirmed via body-id trace: outer main body abandoned at the nested term/definition swap. My additive fix cannot cause a drop (the class signature NAME is dropped too, independent of my anchor). Construct: `.. module:: sphinx.domains` + `.. autoclass:: Domain` whose docstring begins with a nested definition list, referenced as param type Index(domain: Domain) at extdev/domainapi.typ:379 and via :class: in development/tutorials/adding_domain.rst:152. Reported, NOT fixed (distinct root cause + node interaction; bounded scope).
files_changed: [typsphinx/translator.py, tests/test_desc_signature_anchor_render_gate.py, tests/fixtures/desc_signature_anchor_render_gate/conf.py, tests/fixtures/desc_signature_anchor_render_gate/index.rst]
