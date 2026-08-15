# Sphinx configuration for the bundle_exclusion_manifest_gate fixture
# (Phase 54, BLD-06, OUT-04, D-01, D-04).
#
# Declares one registry key, "styled", whose bundle directory
# (`_typst/styled/`) carries a nested non-`.typ` asset (`assets/note.txt`)
# to prove the bundle copy is RECURSIVE, not top-level-only.
#
# This fixture deliberately does NOT commit `.git/`, `.DS_Store`,
# `Thumbs.db`, or an editor backup file into the bundle -- a nested
# `.git` directory cannot be tracked by this repository at all, and the
# other three are exactly the kinds a working tree routinely gitignores.
# tests/test_bundle_copy_exclusion_manifest_gate.py materialises all four
# excluded kinds at runtime, into a COPY of this fixture under a fresh
# tmp_path, instead.

project = "Bundle Exclusion Manifest Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

typst_document_templates = {
    "styled": {"template": "_typst/styled/base.typ"},
}

typst_documents = [
    ("index", "master", project, author, "styled"),
]
