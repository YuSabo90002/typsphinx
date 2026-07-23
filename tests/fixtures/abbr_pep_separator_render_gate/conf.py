# Sphinx configuration for the abbr PEP-separator suppression render-gate
# fixture (FID-14).
#
# Minimal self-contained project used by
# tests/test_abbr_pep_separator_render_gate.py to prove, via a real compile,
# that the auto-generated PEP 3102 '*' (keyword-only) and PEP 570 '/'
# (positional-only) signature separators no longer inject their <abbr>
# hover-title text inline, while a genuine :abbr: role usage in the SAME
# document keeps its inline expansion unchanged.

project = "Abbr PEP Separator Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template -- included documents only get a minimal import
# set (see typsphinx/writer.py).
typst_documents = [
    ("index", "index", "Abbr PEP Separator Render Gate", "Test Author"),
]
