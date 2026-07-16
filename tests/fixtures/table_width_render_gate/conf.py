# Sphinx configuration for the GATE-01 table-width render-gate fixture.
#
# Minimal self-contained project used by tests/test_pdf_render_gate.py to
# prove the LEN-01 depart_table :width: wiring in a real compile: sphinx-build
# -> typst.compile() -> pypdf text-extraction, asserting the px case is
# converted to a pt length, the % case passes through, and the unsupported
# unit case is dropped with exactly one warning (D-03a/D-03b).

project = "Table Width Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template -- included documents only get a minimal import set
# (see typsphinx/writer.py).
typst_documents = [
    ("index", "index", "Table Width Render Gate", "Test Author"),
]
