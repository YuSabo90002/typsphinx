# Phase 48 plan 01, task 1: the label-collision false-negative fixture
# (XREF-03, review finding Sonnet MEDIUM / Fable LOW). `_sanitize_label`
# maps `/` to the literal token `_u2f_`, so a nested docname `a/b` and a
# flat docname `a_u2f_b` share ONE label namespace: `_namespace_label("a/b",
# "nested-target")` and `_namespace_label("a_u2f_b", "nested-target")` both
# sanitize to `a_u2f_b:nested-target`. This makes the guard's one new
# false-negative class MEASURABLE at compile level: the guard's `query()`
# asks "does a label with THIS SPELLING exist in this compile", not "does
# the document I actually meant exist" -- so a reference whose real target
# (`a/b`, excluded from the toctree) is absent nonetheless finds the
# DECOY's (`a_u2f_b`, included) identically-spelled label and renders as a
# working link to the WRONG section.
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising the collision:
#   (a) The two docnames MUST stay exactly `a/b` and `a_u2f_b` -- the
#       collision IS the `_u2f_` transform; renaming either dissolves it.
#   (b) `a/b.rst` MUST keep `:orphan:` and MUST never be added to a
#       toctree.
#   (c) `a_u2f_b.rst`'s section title MUST stay `Nested Target` so its
#       docutils-derived auto id remains `nested-target`.
#   (d) Exactly ONE of the two documents may use an explicit
#       `.. _nested-target:` label directive (here, `a/b.rst`) -- making
#       BOTH explicit would trip Sphinx's own duplicate-label warning and
#       let SPHINX, not the guard, choose which target a `:ref:` resolves
#       to.

project = "Xref Label Collision Guard Gate"
author = "Probe Author"
release = "1.0"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "manual.typ", "Collision Gate", "Probe Author"),
]
