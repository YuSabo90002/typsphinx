# Sphinx configuration for the GATE-01 figure-length render-gate fixture.
#
# Minimal self-contained project used by tests/test_pdf_render_gate.py to
# prove the FIG-01 length-unit conversion fix in a real compile: sphinx-build
# -> typst.compile() -> pypdf text-extraction, asserting the px case is
# converted to a pt length and no raw px/unsupported unit leaks into the
# generated .typ (Issue #114, D-02).

project = "Figure Length Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template -- included documents only get a minimal import set
# (see typsphinx/writer.py).
typst_documents = [
    ("index", "index", "Figure Length Render Gate", "Test Author"),
]
