# Sphinx configuration for the rubric_indent_invariance_gate fixture
# (Phase 39, ADM-05, D-12).
#
# This fixture backs an INVARIANCE GUARD, not a GATE-01 RED: 39-CONTEXT.md
# measured (real -b typstpdf build + pypdf layout-mode extraction) that a
# rubric's left edge already equals the left edge of the description body
# containing it, at two nesting levels, with a top-level rubric (no
# containing description body) sitting flush with ordinary top-level text.
# Phase 38's pad(left: SHARED_INDENT_STEP, {...}) wrapper around
# desc_content already carries the rubric structurally -- visit_rubric
# performs no indent logic of its own. This guard exists to catch a
# regression, exactly as Phase 36's SC#3 was resolved (D-12).
#
# index must be a master document so the writer emits the full template
# and a manual typst.compile() call actually compiles it to PDF.

project = "Rubric Indent Invariance Gate"
author = "typsphinx tests"
release = "0.0.0"

extensions = [
    "typsphinx",
]

# Phase 47 de-collision (47-EXPECTED-STRUCTURE.md "Fixture de-collision
# rule"): the original target "index" resolved to the SAME physical path
# as this docname's own content file (index.typ) under the two-layer
# split -- a self-collision (D-01). Retargeted to the canonical
# replacement "master.typ"; the docname, title and author are unchanged.
typst_documents = [
    ("index", "master.typ", "Rubric Indent Invariance Gate", "typsphinx tests"),
]
