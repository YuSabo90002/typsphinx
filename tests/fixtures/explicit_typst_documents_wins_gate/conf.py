# Sphinx configuration for the CONF-08/SC#2 explicit-wins gate.
#
# typst_documents is set explicitly to a target name -- "manual.typ" --
# that the derivation could NEVER produce for this project:
# make_filename_from_project("Explicit Wins Gate") yields the stem
# "explicitwinsgate" (measured live, Sphinx 9.1.0), never "manual". This
# deliberate mismatch is what lets the gate distinguish "the explicit
# setting won" from "the derived default happened to agree" -- if project
# or the target name were changed to make the two agree, that distinction
# would silently collapse and the gate would stop proving anything about
# SC#2.
#
# No other typst_* value is set here, so the gate cannot go red through an
# unrelated template or package interaction.

project = "Explicit Wins Gate"
author = "Test Author"
release = "1.0.0"
copyright = "2026, Test Author"

extensions = ["typsphinx"]

typst_documents = [("index", "manual.typ", project, author)]
