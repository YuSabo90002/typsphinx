# Sphinx configuration for the DOC-14 published-Output-Layout gate --
# refused-target (parent-traversal) worked example.
#
# This fixture's ONE job: be the built proof for the parent-traversal
# refusal shape ("Targets that are refused") on
# docs/source/user_guide/output_layout.rst -- a literal copy of
# 51-RESEARCH.md Part C build 3a (measured 2026-08-14, sphinx-build -b
# typst, exited 0, warned, fell back to the target's basename).
#
# Do NOT merge this fixture with output_layout_refused_absolute_gate/ or
# output_layout_refused_drive_gate/ -- all three look nearly identical (a
# single-entry config with a refused target), but the absolute and
# drive-qualified shapes both fall back to the SAME basename ("manual"); a
# single project holding two of those would trip the self-collision abort
# instead of exercising the fallback each is meant to prove.

project = "Title"
author = "Author"
release = "1.0.0"
copyright = "2026, Author"

extensions = ["typsphinx"]

# The single load-bearing config line -- a literal copy of 51-RESEARCH.md
# Part C build 3a. A parent-traversal target, refused with a warning and a
# fallback to its basename ("escape").
typst_documents = [("index", "../escape", "Title", "Author", "typst")]
