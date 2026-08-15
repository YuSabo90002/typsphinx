# Minimal Sphinx config for the reference-with-target + block-quote-in-list
# render gate (Phase 15, GATE-02, eleventh corpus fatal).
project = "Ref Target Nested List Render Gate"
author = "typsphinx tests"
release = "0.0.0"

extensions = ["typsphinx"]

# One master document compiled straight to PDF by the typstpdf builder.
#
# Phase 47 fixture de-collision: the target was originally "index", whose
# resolved stem is identical to the docname "index" itself -- a self-
# collision under the two-layer content/wrapper split. Renamed to
# "master.typ" per 47-EXPECTED-STRUCTURE.md's fixture de-collision rule;
# no other element changed.
typst_documents = [
    ("index", "master.typ", project, author),
]
