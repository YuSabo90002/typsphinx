# Sphinx configuration for the DOC-14 published-Output-Layout gate --
# refused-target (drive-qualified) worked example.
#
# This fixture's ONE job: be the built proof for the drive-qualified-target
# refusal shape ("Targets that are refused") on
# docs/source/user_guide/output_layout.rst -- a literal copy of
# 51-RESEARCH.md Part C build 3c (measured 2026-08-14, sphinx-build -b
# typst, exited 0, warned, fell back to the target's basename).
#
# Do NOT merge this fixture with output_layout_refused_parent_gate/ or
# output_layout_refused_absolute_gate/ -- all three look nearly identical (a
# single-entry config with a refused target), but this shape and
# the absolute shape both fall back to the SAME basename ("manual"); a
# single project holding both would trip the self-collision abort instead of
# exercising the fallback each is meant to prove.

project = "Title"
author = "Author"
release = "1.0.0"
copyright = "2026, Author"

extensions = ["typsphinx"]

# The single load-bearing config line -- a literal copy of 51-RESEARCH.md
# Part C build 3c. A drive-qualified target (a pure string-shape test,
# refused identically on every platform), refused with a warning and a
# fallback to its basename ("manual").
typst_documents = [("index", "C:manual", "Title", "Author", "typst")]
