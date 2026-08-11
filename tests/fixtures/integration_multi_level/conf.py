# Sphinx configuration for multi-level nested toctree test
# Tests 3-level directory structure (root → part1 → chapter1)

project = "Multi-Level Toctree Test"
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
    ("index", "master.typ", "Multi-Level Toctree Test", "Test Author"),
]
