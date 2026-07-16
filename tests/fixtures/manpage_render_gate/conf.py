# Sphinx configuration for the GATE-01 manpage render-gate fixture.
#
# Minimal self-contained project used by tests/test_pdf_render_gate.py to
# prove the MAN-01 visit_manpage/depart_manpage fix in a real compile:
# sphinx-build -> typst.compile() -> pypdf text-extraction, asserting the
# :manpage: role's literal page-reference text renders italic in all three
# separator/mode contexts (paragraph, list item, figure caption).
#
# manpages_url is deliberately NOT set: with it unset, the manpage node's
# single child stays a plain nodes.Text (D-02a) -- setting it would route
# through a different, out-of-scope reference-child code path.

project = "Manpage Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template -- included documents only get a minimal import set
# (see typsphinx/writer.py).
typst_documents = [
    ("index", "index", "Manpage Render Gate", "Test Author"),
]
