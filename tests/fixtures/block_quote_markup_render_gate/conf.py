# Sphinx configuration for the block-quote markup-mode render-gate fixture
# (Phase 15, GATE-02, fifteenth corpus fatal).
#
# Minimal self-contained project used by tests/test_pdf_render_gate.py to
# prove, via a real compile, that visit_block_quote emits a CODE-MODE body
# -- quote(block: true, { ... }) -- rather than the markup-mode trailing
# content block quote[ ... ]. In markup mode the code-mode children
# (par({text(...)}), raw(...)) are treated as literal prose, so a lone
# markup-special char in a child string literal (e.g. the `_` in an inline
# literal ``_t``) opens a stray inline-emphasis span that never closes and
# aborts the whole compile with "TypstError: unclosed delimiter".
project = "Block Quote Markup Render Gate"
author = "typsphinx tests"
release = "0.0.0"

extensions = ["typsphinx"]

# One master document compiled straight to PDF by the typstpdf builder.
typst_documents = [
    ("index", "index", project, author),
]
