# Sphinx configuration for Issue #5 reproduction test
# Tests nested toctree with relative path generation

project = "Nested Toctree Test"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# Typst configuration
#
# Phase 47 fixture de-collision: the target was originally "index.typ",
# whose resolved stem is identical to the docname "index" itself -- a
# self-collision under the two-layer content/wrapper split. Renamed to
# "master.typ" per 47-EXPECTED-STRUCTURE.md's fixture de-collision rule;
# no other element changed.
typst_documents = [
    ("index", "master.typ", "Nested Toctree Test", "Test Author"),
]
