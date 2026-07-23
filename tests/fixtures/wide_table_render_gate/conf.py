# Sphinx configuration for the GATE-01 wide-table render-gate fixture.
#
# Minimal self-contained project used by tests/test_wide_table_render_gate.py
# to prove the FID-01a fix (fr-columns from colwidth + in-table ZWSP
# injection for long unbroken inline-literal cell content) in a real
# compile: sphinx-build -> typst.compile() -> pypdf text-extraction,
# asserting the audit's cross-column glyph-collision signature is absent.

project = "Wide Table Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template -- included documents only get a minimal import set
# (see typsphinx/writer.py).
typst_documents = [
    ("index", "index", "Wide Table Render Gate", "Test Author"),
]
