# Sphinx configuration for the DOC-14 published-Output-Layout gate --
# bare-target worked example.
#
# This fixture's ONE job: be the built proof for the bare-target worked
# example on docs/source/user_guide/output_layout.rst -- a literal copy of
# 51-RESEARCH.md Part C build 1 (measured 2026-08-14, sphinx-build -b typst,
# exited 0, no warnings).
#
# This fixture is NOT the same as tests/fixtures/quickstart_docs_gate/ (that
# one exercises an UNSET typst_documents -- the CONF-08 default derivation)
# or tests/fixtures/default_typst_documents_gate/ (that one proves the
# CONF-08 derivation mechanism itself with a synthetic project name). This
# fixture exists solely to prove the bare-target ("manual") worked example
# on output_layout.rst. Do not merge them and do not modify the existing
# fixtures.

project = "Title"
author = "Author"
release = "1.0.0"
copyright = "2026, Author"

extensions = ["typsphinx"]

# The single load-bearing config line -- a literal copy of 51-RESEARCH.md
# Part C build 1. A bare (no-path) target written at the outdir root.
typst_documents = [("index", "manual", "Title", "Author", "typst")]
