# Sphinx configuration for multi-document integration testing

project = "Multi-Document Test"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# Phase 47 fixture de-collision: the target was originally "index.typ",
# whose resolved stem is identical to the docname "index" itself -- a
# self-collision under the two-layer content/wrapper split. Renamed to
# "master.typ" per 47-EXPECTED-STRUCTURE.md's fixture de-collision rule;
# no other element changed.
typst_documents = [
    ("index", "master.typ", "Multi-Document Test", "Test Author"),
]
