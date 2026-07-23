# Sphinx configuration for the BLK-01/04/05/06 trivial-blocks render-gate
# fixture.
#
# Minimal self-contained project used by tests/test_pdf_render_gate.py to
# prove the four trivial structural node handlers in a real compile:
# sphinx-build -> typst.compile() -> pypdf text-extraction. Covers a
# `----` transition, a `.. glossary::`, a `.. tabularcolumns::` (asserting
# no leaked content), and an `:abbr:` role.

project = "Trivial Blocks Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template -- included documents only get a minimal import
# set (see typsphinx/writer.py).
typst_documents = [
    ("index", "index", "Trivial Blocks Render Gate", "Test Author"),
]
