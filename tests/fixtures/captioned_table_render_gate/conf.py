# Sphinx configuration for the GATE-01 captioned-table render-gate fixture.
#
# Minimal self-contained project used by tests/test_pdf_render_gate.py to
# prove the Plan 25-01 TBL-01/TBL-02 depart_table figure-wrap + single
# <label> fix in a real compile: sphinx-build -> typst.compile() -> pypdf
# text-extraction. `numfig = True` is required for `:numref:` to resolve
# without a warning (25-RESEARCH.md Pitfall 4) -- the gate asserts the
# cross-reference RESOLVES (a `link(<` anchor in the emitted source), never
# a specific "Table N" numbering string.

project = "Captioned Table Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template -- included documents only get a minimal import
# set (see typsphinx/writer.py).
typst_documents = [
    ("index", "index", "Captioned Table Render Gate", "Test Author"),
]

numfig = True
