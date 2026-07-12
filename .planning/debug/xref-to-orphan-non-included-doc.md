---
status: resolved
trigger: "TypstError: label `<usage_u2f_extensions_u2f_example_google:example-google>` does not exist in the document (25th corpus fatal, GATE-02) — cross-ref to :orphan: / non-included document"
created: 2026-07-13
updated: 2026-07-13
---

## Current Focus

corpus_outcome: "GATE-02 GREEN. Full Sphinx doc/ corpus (v9.1.0, commit cc7c6f4) compiles end-to-end via -b typstpdf to a real %PDF (index.pdf, 15,124,122 bytes) with NO fatal. Corpus gate tests/test_corpus_gate.py::TestCorpusRenderGate PASSED. Residual unknown_visit catalogue: todo_node(10), manpage(10) — warnings, not fatals. Degrade warnings fired for napoleon->example_google/example_numpy and the orphans' mutual refs (4 occurrences), all rendered as plain text. Commits: 703eb2d fix / 2e8651c test."

reasoning_checkpoint:
  hypothesis: "An INCLUDED doc (napoleon.rst) emits link(<usage_u2f_extensions_u2f_example_google:example-google>) for :ref:`example_google`, but example_google.rst is :orphan: — excluded from EVERY toctree, so its .typ is written but never #include()d into the compiled master. The anchor exists only in a file that is not part of the master → dangling label → typst hard-fails."
  confirming_evidence:
    - "example_google.rst / example_numpy.rst both start with :orphan: + `.. _example_google:` before title (corpus cache confirmed)"
    - "napoleon.rst lines 201-202: `* :ref:`example_google`` / `* :ref:`example_numpy`` inside a seealso, and napoleon IS in the usage/extensions/index toctree"
    - "grep: example_google/example_numpy appear in NO toctree; only self-anchor + cross-refs from napoleon"
    - "#21 upgraded cross-doc string-url links into real label links → this exposed the orphan dangling-label"
  falsification_test: "If example_google were reachable from the master toctree, target_docname would be in env.toctree_includes closure — but it is not (orphan)."
  fix_rationale: "Compute the master's transitive toctree closure (env.toctree_includes from each typst_documents master + masters themselves) up-front in builder.write(); expose as builder.master_included_docnames. In visit_reference cross-doc branch, degrade to plain text (no link, + logger.warning) when target_docname is outside that set — matching LaTeX's undefined-reference behavior. Same-doc / included-target / external refs unaffected."
  blind_spots: "Glob toctrees could make toctree_includes diverge from visit_toctree entries — verified corpus has no real glob toctrees. Empty master set (no typst_documents) must NOT degrade everything — guarded via `if included and ...` (empty=falsy=no degrade)."

## Symptoms

expected: "typst.compile() on corpus doc/ produces %PDF"
actual: "TypstError: label `<usage_u2f_extensions_u2f_example_google:example-google>` does not exist in the document"
errors: "label `<usage_u2f_extensions_u2f_example_google:example-google>` does not exist in the document"
reproduction: "sphinx-build -b typstpdf on corpus doc/; or minimal: master index toctree over an included doc that has :ref: to a section in a SEPARATE :orphan: doc not in any toctree"
started: "shadowed by fatals #17-#24; surfaced after body-node anchors + #21 namespacing landed"

## Eliminated

## Evidence

- timestamp: 2026-07-13
  checked: "Corpus example_google.rst / example_numpy.rst headers + napoleon.rst refs + toctree membership"
  found: "Both orphan docs :orphan: + labeled section; napoleon (included) :ref:s both; neither orphan in any toctree"
  implication: "Cross-doc label link to a doc absent from the compiled master → dangling label fatal"
- timestamp: 2026-07-13
  checked: "env.toctree_includes shape (sphinx 9.1.0)"
  found: "dict[str, list[str]] mapping docname -> directly-included docnames; orphans excluded; transitive closure from masters = master include-set"
  implication: "Closure over toctree_includes from typst_documents masters gives the exact include-set for the degrade decision"

## Resolution

root_cause: "An :orphan: (or otherwise non-toctree-reachable) target document is written as a .typ but never #include()d into the compiled master, so its anchors do not exist in the compiled document; a cross-document :ref: from an INCLUDED doc emits a real link(<targetdoc:anchor>) label link (post-#21) that dangles → typst.compile aborts 'label ... does not exist'."
fix: "builder.py: new _compute_master_included_docnames() walks env.toctree_includes BFS from each typst_documents master (+ masters themselves) into builder.master_included_docnames, populated up-front in write() (init() seeds an empty set). translator.py visit_reference: precompute xref via _resolve_xref_docname + degrade_xref_to_text = (master_included truthy AND target docname not in it); factor into opens_wrapper (degraded ref opens NO wrapper, like empty-url); in the resolved-cross-doc elif branch, when degrade -> logger.warning + _skip_link_wrapper=True + return (render children as plain text, no link(<...>) label link). Empty include-set (no masters/mock builders) => never degrade, preserving prior behavior."
verification: "Minimal repro (index toctree over included doc + separate :orphan: doc; included :ref:s orphan section AND own section): pre-fix `label <orphan:orphan-anchor> does not exist` fatal; post-fix %PDF (21282 bytes), orphan ref -> text(\"Orphan Section\"), included ref -> link(<included:included-anchor>). New test tests/test_xref_orphan_degrade_render_gate.py FAILS pre-fix (exact dangling-label fatal via git-stash) / PASSES post-fix, asserting BOTH directions. Fixture warning-free except the intended degrade warning."
files_changed: [typsphinx/builder.py, typsphinx/translator.py, tests/test_xref_orphan_degrade_render_gate.py, tests/fixtures/xref_orphan_degrade_render_gate/conf.py, tests/fixtures/xref_orphan_degrade_render_gate/index.rst, tests/fixtures/xref_orphan_degrade_render_gate/included.rst, tests/fixtures/xref_orphan_degrade_render_gate/orphan.rst]
