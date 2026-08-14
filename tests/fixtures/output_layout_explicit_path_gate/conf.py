# Sphinx configuration for the DOC-14 published-Output-Layout gate --
# explicit-path-target worked example.
#
# This fixture's ONE job: be the built proof for the explicit-path worked
# example on docs/source/user_guide/output_layout.rst -- a literal copy of
# 51-RESEARCH.md Part C build 2 (measured 2026-08-14, sphinx-build -b typst,
# exited 0, no warnings).
#
# This fixture is NOT the same as tests/fixtures/output_layout_bare_target_gate/
# (that one exercises a bare, no-path target) or
# tests/fixtures/quickstart_docs_gate/ (that one exercises an UNSET
# typst_documents). This fixture exists solely to prove the explicit-path
# worked example (an explicit path in the target) on output_layout.rst.
# Do not merge them and do not modify the existing fixtures.

project = "Title"
author = "Author"
release = "1.0.0"
copyright = "2026, Author"

extensions = ["typsphinx"]

# The single load-bearing config line -- a literal copy of 51-RESEARCH.md
# Part C build 2. An explicit path in the target, honoured relative to the
# output directory.
typst_documents = [("index", "manuals/guide.typ", "Title", "Author", "typst")]
