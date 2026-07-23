# Sphinx configuration for the paragraph soft-newline reflow render-gate
# fixture (FID-11).
#
# Minimal self-contained project used by
# tests/test_paragraph_soft_newline_render_gate.py to prove, via a real
# compile, that a paragraph authored with reST soft/semantic source line
# breaks collapses the intra-paragraph newline to a single space instead of
# emitting a Typst hard break.

project = "Paragraph Soft Newline Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template -- included documents only get a minimal import
# set (see typsphinx/writer.py).
typst_documents = [
    ("index", "index", "Paragraph Soft Newline Render Gate", "Test Author"),
]
