"""Sphinx config for the sibling-desc_signature render-gate fixture (FID-03).

Plain single-page project -- no intersphinx needed. Exercises a
``.. py:function::`` directive with multiple signature lines (producing
sibling ``desc_signature`` nodes under one ``desc``) and a separate
single-signature ``.. py:function::`` for the byte-unchanged cardinality
edge.
"""

project = "Desc Signature Siblings Render Gate"
author = "typsphinx tests"
release = "0.0.0"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "index", "Desc Signature Siblings Render Gate", "typsphinx tests"),
]
