# Sphinx configuration for the desc_break_marker_buffer_swap_gate fixture
# (folded todo: .planning/todos/pending/
# 2026-08-01-desc-break-marker-stale-across-body-buffer-swaps.md, folded
# into Phase 38 by D-10).
#
# Minimal self-contained project used by
# tests/test_desc_break_marker_buffer_swap_gate.py to build the case the
# folded todo names as concretely reachable: a `desc` directive nested
# inside a `.. glossary::` definition's body, plus a second, nested `desc`
# pair inside that same definition -- exercising the SIG-08
# `_desc_break_marker`'s `self.body` buffer swap (via `_saved_body_stack`,
# `visit_term`/`visit_definition`) AND a nesting boundary at once. Two
# controls isolate the variable: the identical nested-desc shape at
# document top level (no buffer swap), and a record of why a `desc` cannot
# be nested inside a figure caption or an admonition title (the other two
# unguarded `self.body` reassignment sites).

project = "Desc Break Marker Buffer Swap Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document so the writer emits the full template and
# TypstPDFBuilder.finish() / a manual typst.compile() call actually
# compiles it to PDF.
#
# Target "index" (stem "index") casefold-collides with the docname's own
# content path "index.typ" (fixture de-collision rule, 47-EXPECTED-STRUCTURE.md);
# renamed to the canonical "master.typ".
typst_documents = [
    ("index", "master.typ", "Desc Break Marker Buffer Swap Gate", "Test Author"),
]
