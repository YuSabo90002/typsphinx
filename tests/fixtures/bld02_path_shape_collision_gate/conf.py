# Phase 47 gap-closure plan 11, task 1: BLD-02's path-SHAPE fixture -- two
# typst_documents entries whose targets differ only in path shape (a
# redundant "./" prefix) while resolving to the SAME physical path,
# `manual.typ`. `_collision_key()` (typsphinx/builder.py) folds separator
# STYLE and case (D-05) but, before this plan, did NOT fold path SHAPE via
# `posixpath.normpath()` -- so this pair evaded BLD-02's own collision
# validator (47-09) and silently overwrote one master's wrapper. This
# fixture is deliberately NOT `bld02_duplicate_target_gate` (already green):
# that fixture's two entries are textually IDENTICAL strings; this one's
# are textually DIFFERENT strings that only become equal once the
# collision key normalizes shape.
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising the path-shape gap:
#   - The two targets MUST differ TEXTUALLY (`./manual.typ` vs `manual.typ`)
#     while resolving to ONE physical path -- making them identical
#     collapses this fixture into the already-green
#     `bld02_duplicate_target_gate`.
#   - The two docnames MUST differ (`index` and `other`).
#   - `index.rst`'s body marker `PATHSHAPE-INDEX-MARKER-AAA` and
#     `other.rst`'s body marker `PATHSHAPE-OTHER-MARKER-BBB` must keep their
#     exact spelling -- the pre-fix RED evidence is a `grep -c` proof that
#     the FIRST entry's marker goes missing from the surviving `manual.typ`
#     while the SECOND survives.

project = "Path Shape Collision Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "./manual.typ", "Index Master", "Probe Author"),
    ("other", "manual.typ", "Other Master", "Probe Author"),
]
