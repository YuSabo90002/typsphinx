---
status: investigating
trigger: "Corpus gate fatal #19 (semantic): TypstError: label `<module-sphinx.ext.apidoc>` occurs multiple times in the document. One .. py:module:: sphinx.ext.apidoc directive, included once, yet the module-... id is emitted as a Typst <label> DEFINITION >=2 times in the compiled master; Typst rejects the 2nd."
created: 2026-07-12T00:00:00
updated: 2026-07-12T00:00:00
---

## Current Focus

hypothesis: TBD — must first determine WHY twice and the SCOPE (within one doc vs across #included docs in the master).
test: Build full corpus with -b typst; grep emitted .typ files for `<module-sphinx.ext.apidoc>` label DEFINITIONS; count and locate.
expecting: >=2 definitions. Their file location(s) tell us scope: same .typ (within-doc) vs two .typ (cross-include).
next_action: Build corpus typst target; grep for the anchor across all emitted .typ.

## Symptoms

expected: Sphinx doc/ corpus compiles through -b typstpdf with no fatal; a py:module target anchor is defined exactly once and every reference resolves.
actual: "TypstError: label `<module-sphinx.ext.apidoc>` occurs multiple times in the document" at the semantic pass (corpus parses fully after #17/#18).
errors: "TypstError: label `<module-sphinx.ext.apidoc>` occurs multiple times in the document"
reproduction: uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -v -s
started: Pre-existing gap surfaced by Phase 15 corpus gate; 19th fatal; first DUPLICATE-label-definition class.

## Eliminated

- hypothesis: The duplicate is two visitors emitting the anchor within ONE document (apidoc.typ), fixable by a per-translator anchor-definition dedup set.
  evidence: grep of built apidoc.typ shows exactly ONE bare-label DEFINITION `) <module-sphinx.ext.apidoc>]` (the section heading, line 13); the other three occurrences are `link(<...>, ...)` REFERENCES. So within-doc there is only one definition. Per-translator/per-doc dedup is architecturally incapable anyway: apidoc.typ is TRANSLATED once but #INCLUDEd twice at Typst compile time.
  timestamp: investigation

## Evidence

- timestamp: build+grep
  checked: Built full corpus with `-b typst`; grepped all .typ for `<module-sphinx.ext.apidoc>` definitions and references; traced the include() graph.
  found: apidoc.typ defines the label ONCE (section heading, because the py:module target id propagated into the section's ids). But the INCLUDE GRAPH is a diamond: master index.typ includes `usage/index.typ` (line 156) AND directly `usage/extensions/index.typ` (line 195); usage/index.typ includes `extensions/index.typ` (line 27). So usage/extensions/index (-> apidoc.typ) is #included TWICE into the master. Same diamond for usage/configuration and usage/restructuredtext/index.
  implication: Every label in a doubly-included doc is emitted twice in the flattened master. Typst aborts at the FIRST duplicate: <module-sphinx.ext.apidoc>. Root = toctree->#include generation with no cross-master dedup. Cause is index.rst having a "Reference" toctree listing usage/extensions/index etc. DIRECTLY while its "User guide" toctree lists usage/index which nests the same docs.

- timestamp: baseline-compile
  checked: typst.compile(built index.typ)
  found: "TypstError: label `<module-sphinx.ext.apidoc>` occurs multiple times in the document" -- reproduces the corpus fatal from the pre-built .typ (no PDF build needed).
  implication: Confirmed reproducible; scope is master-wide (across #included docs), not within-document.

- timestamp: dedup-experiment
  checked: DFS-from-master dedup of include() statements (each resolved target #included once), then typst.compile.
  found: "occurs multiple times" GONE. Advances to `label <xref-modifiers> does not exist` -- a DISTINCT, pre-existing dangling same-doc reference (xref-modifiers defined NOWHERE in the built corpus, yet referenced via <label> in usage/referencing.typ:338), previously shadowed by the earlier duplicate-label abort.
  implication: Include-level dedup is the correct fix for #19. xref-modifiers is the NEXT fatal (#20), independent of the dedup.

## Resolution

root_cause: Sphinx's doc/index.rst has multiple sibling toctrees -- a "User guide" toctree listing `usage/index` (whose own toctree nests usage/configuration, usage/extensions/index, usage/restructuredtext/index) AND a "Reference" toctree listing those same three docs DIRECTLY. typsphinx's visit_toctree emits an include() for every toctree entry with NO deduplication across the master's whole include graph, so each diamond-child document is physically #included TWICE into the one compiled master. Typst labels must be unique per compiled document; every label a doubly-included doc defines is emitted twice, and Typst aborts at the first duplicate it encounters: `<module-sphinx.ext.apidoc>` (the py:module target id, which docutils propagates into apidoc's section ids -> emitted as the section heading's label). Not a within-document anchor bug: apidoc.typ defines the label exactly once; the duplication is the whole .typ being #included twice. SCOPE = master-wide (across #included docs), and the duplication UNIT is a whole document, so the correct dedup is at include() granularity (a per-translator/per-doc OR even per-anchor set is architecturally incapable: apidoc.typ is TRANSLATED once but #INCLUDEd twice at Typst compile time -- Python never sees the second emission).
fix: Added a builder-scoped ledger TypstBuilder._included_docnames (initialized in init(), reset at write() start) shared across every document translated for one master. visit_toctree (translator.py) now records each entry's ABSOLUTE docname the first time it emits an include() and SKIPS a repeat toctree entry for an already-included docname. Each document is therefore #included at most once, every <label> it defines is emitted exactly once, and every reference is kept intact (never dropped) so it still resolves to the single surviving anchor. Mock builders in unit tests lack the ledger; getattr(self.builder, "_included_docnames", None) falls back to the original no-dedup path (those tests unaffected).
verification: New tests/test_duplicate_include_label_render_gate.py (+ fixtures/duplicate_include_label_render_gate/{conf.py,index.rst,sub.rst,shared.rst}) PASSES with fix, FAILS pre-fix (git stash builder.py+translator.py) with the exact `label <shared-anchor> occurs multiple times` fatal. Fixture is a minimal diamond (master reaches `shared` directly AND nested under `sub`); asserts include("shared.typ") appears exactly once across the emitted graph, the <shared-anchor> anchor is defined once, the same-doc link(<shared-anchor>) reference survives, and index.pdf is %PDF. Fast suite 421 passed / 15 deselected (420 prior + 1 new; NO existing expectation updated -- toctree/translator/nested-toctree tests all still green). black/ruff/mypy clean. Corpus gate (slow, real -b typstpdf on sphinx v9.1.0 doc/, SHA cc7c6f4): bug #19 FIXED -- `<module-sphinx.ext.apidoc> occurs multiple times` GONE; usage/extensions/index now #included exactly once. NOT GATE-02 green. Next distinct fatal #20 = `TypstError: label <xref-modifiers> does not exist in the document` -- DISTINCT ROOT CAUSE (dangling same-doc reference, not a duplicate): `.. _xref-modifiers:` (usage/referencing.rst:24) is an explicit target placed before a PARAGRAPH (not a section); docutils propagates its id onto that paragraph (usage/referencing.typ:34), and visit_paragraph emits no <label> anchor, so <xref-modifiers> is DEFINED 0 times while a same-doc :ref: (referencing.rst:257) emits link(<xref-modifiers>) at referencing.typ:338 -> dangles. Previously shadowed by the earlier duplicate-label abort. Occurrence: 1 dangling <label> reference (referencing.typ:338), 0 definitions (plus 3 harmless cross-doc string-path refs in domains/index, python, restructuredtext/directives). Reported, NOT fixed (bounded scope: distinct root cause).
files_changed: [typsphinx/builder.py, typsphinx/translator.py, tests/test_duplicate_include_label_render_gate.py, tests/fixtures/duplicate_include_label_render_gate/conf.py, tests/fixtures/duplicate_include_label_render_gate/index.rst, tests/fixtures/duplicate_include_label_render_gate/sub.rst, tests/fixtures/duplicate_include_label_render_gate/shared.rst]
