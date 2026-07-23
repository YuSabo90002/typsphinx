# Sphinx configuration for the BLK-02/BLK-03 topic+line_block render-gate
# fixture.
#
# Minimal self-contained project used by tests/test_pdf_render_gate.py to
# prove, in a real compile (sphinx-build -> typst.compile() -> pypdf text-
# extraction), that visit_topic/visit_title's generalized buffer-swap (D-01,
# D-02, D-05) and visit_line_block/visit_line (D-03, D-04) render correctly
# together -- including the SC#3 admonition-title regression (multi-child
# title, Pitfall 1 fix).

project = "Topic Line Block Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template -- included documents only get a minimal import
# set (see typsphinx/writer.py).
typst_documents = [
    ("index", "index", "Topic Line Block Render Gate", "Test Author"),
]
