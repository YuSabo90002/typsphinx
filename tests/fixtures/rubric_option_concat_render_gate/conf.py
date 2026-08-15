"""Sphinx config for the rubric/option render-gate fixture (FID-04).

Plain single-page project -- no ``man`` builder or intersphinx needed. A
``.. rubric::`` directive renders via ``strong()``; a subsequent
``.. option::`` also renders via ``strong()``, mirroring
``man/sphinx-quickstart.rst``'s "Structure Options"/``--sep`` pattern that
pre-fix merges onto one line.
"""

project = "Rubric Option Concat Render Gate"
author = "typsphinx tests"
release = "0.0.0"

extensions = ["typsphinx"]

# Target "index" (stem "index") casefold-collides with the docname's own
# content path "index.typ" (fixture de-collision rule, 47-EXPECTED-STRUCTURE.md);
# renamed to the canonical "master.typ".
typst_documents = [
    ("index", "master.typ", "Rubric Option Concat Render Gate", "typsphinx tests"),
]
