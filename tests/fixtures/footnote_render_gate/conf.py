# Sphinx configuration for the FN-01 footnote render-gate fixture.
#
# Minimal self-contained project used by tests/test_pdf_render_gate.py to
# prove, in a real compile (sphinx-build -> typst.compile() -> pypdf text-
# extraction), that the Plan 14-01 footnote pre-pass handlers (the
# visit_document id->node index, visit_footnote's SkipNode suppression, and
# visit_footnote_reference's definition/reuse emission) render correctly --
# covering a single-reference footnote (SC#1), a double-reference footnote
# (SC#2), a footnote body with inline markup + special characters (SC#3),
# and a footnote cited from inside a bullet-list item (SC#4).

project = "Footnote Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template -- included documents only get a minimal import
# set (see typsphinx/writer.py).
typst_documents = [
    ("index", "index", "Footnote Render Gate", "Test Author"),
]
