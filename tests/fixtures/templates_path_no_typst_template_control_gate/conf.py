# Phase 54.1 plan 04, task 2: WR-01's D-02 bullet 2 measured-shape
# control -- the layout examples/basic has.
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising D-02 bullet 2's measured shape:
#   - `templates_path` is set, but NO Typst template is configured at
#     all -- no `typst_document_templates`, no `typst_template`. The
#     built-in "typst" registry key therefore resolves to the PACKAGED
#     default template, whose bundle lives inside the installed Python
#     package, never under `srcdir` -- the containment test is never
#     applied to it (`resolution.source == "default"` is skipped).
#   - The build must succeed and produce the packaged default's own
#     wrapper output.

project = "Templates Path No Typst Template Control Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

templates_path = ["_templates"]

typst_documents = [
    ("index", "index_out.typ", "No Typst Template Control", "Probe Author"),
]
