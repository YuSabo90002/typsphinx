---
status: resolved
trigger: "TypstError: label `<info-field-lists>` occurs multiple times in the document (21st corpus fatal, GATE-02) — SYSTEMIC cross-document label collision class"
created: 2026-07-12
updated: 2026-07-12
resolution: "#21 collision class fixed via per-document label namespacing (commits 510f8e1 fix / 5db0564 test). Corpus advanced past collisions to next distinct fatal #22 (option-directive propagated-target missing anchor)."
---

## Current Focus

corpus_outcome: "GATE-02 NOT green. #21 collision class RESOLVED (no more 'occurs multiple times'; fatal changed class). NEXT DISTINCT FATAL (#22): TypstError: label `<man_u2f_sphinx-build:make-mode>` does not exist. Construct: `.. _make_mode:` (man/sphinx-build.rst:33) propagates its id onto the FOLLOWING `.. option:: -M` (line 35); the option desc_signature emits only its own id `<...:cmdoption-...-M>`, never the propagated `make-mode`, so cross-doc :ref: (man/sphinx-quickstart.rst:127 `:ref:\`make-mode <make_mode>\``, target in-master via man/index toctree) now dangles. Missing-anchor family (#2/#20), option-directive gap — exposed (not caused) by the correct cross-doc string-url→label-link upgrade. Occurrence: 1 (explicit-target-before-.. option::) in corpus."

reasoning_checkpoint:
  hypothesis: "Corpus flattened to ONE Typst master via #include(). docutils ids are unique per-doc only; two docs both emit `<info-field-lists>`. Typst raises 'occurs multiple times' ONLY when a duplicated label is also REFERENCED via link(<label>)/@label (verified: dup-unreferenced compiles OK, dup+link fatals). A same-doc refid `:ref:` emits link(<info-field-lists>) → dup+ref → abort."
  confirming_evidence:
    - "Minimal 2-doc build: pagea.typ AND pageb.typ both emit `[#heading(...) <overview>]` for their 'Overview' section"
    - "Raw typst.compile probe: `<overview>` defined twice compiles OK; add `#link(<overview>)[go]` → FAILED: label `<overview>` occurs multiple times"
    - "Cross-doc `:ref:` currently emits `link(\"pageb.pdf#target-in-b\", ...)` (dead STRING url, silent mislink); same-doc `:ref:` emits `link(<shared-slug>, ...)` (refid)"
  falsification_test: "If ids were globally unique, no two docs would emit the same `<slug>` — but two do. If dup labels alone fatal-ed, dup-unreferenced would fail — it compiles."
  fix_rationale: "Namespace EVERY emitted label as _sanitize_label(f'{docname}:{id}') so <overview> becomes two distinct labels <a:overview>/<b:overview>; namespace EVERY reference to recompute the SAME string (same-doc=current docname, cross-doc=target docname parsed from refuri path+out_suffix). Distinct labels → no collision; matched namespaces → links land correctly. Also converts cross-doc string-url links into real label links, fixing the silent mislink."
  blind_spots: "Whole-doc refs (no anchor) + external http(s) must stay link(\"url\",...) — unaffected. Unresolved pending_xref fallback namespaced to current docname (best-effort same-doc). Many existing single-doc test expectations assert bare <id> — will churn to <index:id>."

## Symptoms

expected: "typst.compile() on corpus doc/ produces %PDF"
actual: "TypstError: label `<info-field-lists>` occurs multiple times in the document"
errors: "label `<info-field-lists>` occurs multiple times in the document"
reproduction: "sphinx-build -b typstpdf on corpus doc/; or minimal: master toctree over doc A + doc B, both with same section slug, plus a same-doc :ref: to that slug"
started: "shadowed by fatals #17-#20; surfaced after those fixed"

## Eliminated

- hypothesis: "Duplicate labels alone abort the compile"
  evidence: "typst.compile probe: two `<overview>` anchors with NO reference compiles OK; only dup + link(<overview>)/@overview fatals with 'occurs multiple times'"
  timestamp: 2026-07-12

## Symptoms

expected: "typst.compile() on corpus doc/ produces %PDF"
actual: "TypstError: label `<info-field-lists>` occurs multiple times in the document"
errors: "label `<info-field-lists>` occurs multiple times in the document"
reproduction: "sphinx-build -b typstpdf on corpus doc/; or minimal: master toctree over doc A + doc B, both with same section slug"
started: "shadowed by fatals #17-#20; surfaced after those fixed"

## Eliminated

## Evidence

- timestamp: 2026-07-12
  checked: "Minimal 2-doc typst build (pagea/pageb both 'Overview')"
  found: "Both emit `<overview>`; cross-doc ref → `link(\"pageb.pdf#target-in-b\", ...)` string url; same-doc ref → `link(<shared-slug>, ...)`"
  implication: "Definition sites collide across docs; cross-doc refs are dead string urls (silent mislink)"
- timestamp: 2026-07-12
  checked: "Raw typst.compile duplicate-label semantics"
  found: "dup-unreferenced=OK, dup+link(<l>)=FATAL 'occurs multiple times', dup+@l=FATAL"
  implication: "Fatal requires dup label AND a link/ref to it; namespacing definitions makes labels distinct → fatal cleared"
- timestamp: 2026-07-12
  checked: "Enumerated all label DEFINITION + REFERENCE sites in translator.py"
  found: "DEF: _emit_id_anchors:293, depart_title:489/491, depart_term:1703, literal_block:1462/1467, figure:1812, footnote:1950, visit_target:2413/2451, math:3272/3327, desc_signature:3861. REF: visit_reference refid:3009, refuri#:3041, refuri-else:3045, footnote-ref:1962, pending_xref:2493"
  implication: "All must adopt _namespace_label(docname, id); refs compute matching namespace by target"

## Resolution

root_cause: "Corpus flattened to ONE Typst master via #include(); docutils ids unique per-doc only, so two docs emit the same bare <slug> anchor. Typst aborts 'label occurs multiple times' when a duplicated label is also referenced via link(<label>) (a same-doc :ref: emits exactly that)."
fix: "New _namespace_label(docname, id)=_sanitize_label(f'{docname}:{id}') + _resolve_xref_docname(refuri) helpers. DEFINITION sites namespaced with current docname: _emit_id_anchors, depart_title (primary+extra), depart_term, literal_block(caption+:name:), figure, footnote, visit_target(#label+metadata), math(inline+block), desc_signature. REFERENCE sites: refid & refuri#-branch → current docname; new cross-doc branch parses target docname from refuri (<relpath><out_suffix>#anchor) → target docname (also upgrades dead string-url link into real label link); footnote-ref shares namespaced label; pending_xref fallback → current docname. Whole-doc + external http(s) refs left as link(\"url\",...)."
verification: "Minimal 2-doc typstpdf build: <pagea:overview>/<pageb:overview> distinct, cross-doc link(<pageb:target-in-b>) matches pageb anchor, %PDF. Pre-fix repro of exact '<shared-topic> occurs multiple times' fatal confirmed via git-stash; post-fix %PDF. New regression test fails pre-fix / passes post-fix. Fast suite 423 passed."
files_changed: [typsphinx/translator.py, tests/test_cross_doc_label_namespace_render_gate.py, tests/fixtures/cross_doc_label_namespace_render_gate/*, tests/test_paragraph_propagated_target_render_gate.py, tests/test_desc_signature_anchor_render_gate.py, tests/test_deflist_nested_definition_render_gate.py, tests/test_label_at_char_render_gate.py, tests/test_ref_target_nested_list_render_gate.py, tests/test_duplicate_include_label_render_gate.py]
