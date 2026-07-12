# Sphinx configuration for the XREF-01 xref/refid render-gate fixture.
#
# Minimal self-contained project used by tests/test_pdf_render_gate.py to
# prove that a same-document `:ref:` section-anchor cross-reference AND a
# `:term:` glossary cross-reference each resolve to a working Typst link in
# a real compile: sphinx-build -> typst.compile() -> pypdf text-extraction.
# The `:term:` case is the exact scenario that was fatal before the
# depart_term bracket-wrap <label> anchor fix (XREF-01, D-04).

project = "Xref Refid Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template -- included documents only get a minimal import
# set (see typsphinx/writer.py).
typst_documents = [
    ("index", "index", "Xref Refid Render Gate", "Test Author"),
]
