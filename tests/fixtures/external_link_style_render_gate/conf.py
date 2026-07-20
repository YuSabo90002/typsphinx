# Sphinx configuration for the external-link styling + boundary render-gate
# fixture (FID-13, Cluster F).
#
# Minimal self-contained project used by tests/test_external_link_style_render_gate.py
# to prove, via a real compile, that:
#   1. the default template's `show link:` rule (D-01/D-02) colors + underlines
#      an EXTERNAL named hyperlink reference only, leaving a same-document
#      internal reference unstyled;
#   2. visit_target no longer emits a stray leading `\n` before the invisible
#      `#label(...)` call attached to a named external reference, which
#      previously rendered as a stray double space before the following
#      period (D-03).

project = "External Link Style Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template -- included documents only get a minimal import
# set (see typsphinx/writer.py).
typst_documents = [
    ("index", "index", "External Link Style Render Gate", "Test Author"),
]
