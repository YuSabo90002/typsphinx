# Sphinx configuration for the paragraph-concat render-gate fixture
# (Phase 19, GATE-01, FID-02).
#
# Minimal self-contained project used by
# tests/test_paragraph_concat_render_gate.py to prove the translator emits a
# real parbreak() between consecutive paragraphs inside a bullet list item.
# This is the fast, offline reproduction of the dominant v0.6.1-audit finding
# (F1): in Typst's unified code mode a bare source '\n'/'\n\n' between two
# top-level statements is COSMETIC ONLY (zero visual break), so adjacent
# inline text() results concatenate -- "role.For example" instead of
# "role. For example" -- matching usage/referencing.rst's "Suppressed link:"
# item.
#
# Fix: visit_paragraph emits self._emit_forced_break("parbreak()") when
# in_list_item, and depart_paragraph now sets list_item_needs_separator =
# True in its in_list_item branch (previously missing).

project = "Paragraph Concat Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document so the writer emits the full template and
# TypstPDFBuilder.finish() actually compiles it to PDF.
typst_documents = [
    ("index", "index", "Paragraph Concat Render Gate", "Test Author"),
]
