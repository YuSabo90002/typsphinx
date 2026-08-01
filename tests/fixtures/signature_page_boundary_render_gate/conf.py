# Sphinx configuration for the SIG-09 signature-page-boundary render-gate
# fixture (37-03-PLAN.md Task 2).
#
# Minimal self-contained project used by
# tests/test_signature_page_boundary_render_gate.py to prove that a
# signature and the first line of its description body are not split
# across a page break.

project = "Signature Page Boundary Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template -- the SIG-09 gate places a signature relative to
# a real page boundary reached by compiling the real production template.
typst_documents = [
    ("index", "index", "Signature Page Boundary Render Gate", "Test Author"),
]
