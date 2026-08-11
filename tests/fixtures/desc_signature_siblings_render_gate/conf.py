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

# Phase 47 fixture de-collision: the target was originally "index", whose
# resolved stem is identical to the docname "index" itself -- a self-
# collision under the two-layer content/wrapper split. Renamed to
# "master.typ" per 47-EXPECTED-STRUCTURE.md's fixture de-collision rule;
# no other element changed.
typst_documents = [
    ("index", "master.typ", "Desc Signature Siblings Render Gate", "typsphinx tests"),
]
