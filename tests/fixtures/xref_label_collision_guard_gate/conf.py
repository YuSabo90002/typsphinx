# Phase 48 plan 01, task 1 (origin) / Phase 55 plan 01 (XREF-05, D-01/D-02/
# D-04: CLOSED). `_sanitize_label` maps `/` to the literal token `_u2f_`, so
# a nested docname `a/b` and a flat docname `a_u2f_b` collide as RAW
# docnames onto the SAME token shape: `_namespace_label("a/b",
# "nested-target")` and `_namespace_label("a_u2f_b", "nested-target")` both
# used to sanitize to the identical label `a_u2f_b:nested-target` (measured,
# pre-fix, in `55-01-RED-EVIDENCE.md`). This fixture now proves the
# sanitizer keeps their LABELS distinct: `_sanitize_label` re-escapes any
# literal occurrence of its own encoding token (`_u<hex>_`) in the raw
# input BEFORE the main substitution runs, so `a/b:nested-target` still
# sanitizes to `a_u2f_b:nested-target` (the REFERENCE side, namespaced by
# the TARGET docname `a/b`, is unmoved) while `a_u2f_b:nested-target` (the
# DECOY's own raw namespaced id) now sanitizes to
# `a_u5f_u2f_b:nested-target` -- a reference whose real target (`a/b`,
# excluded from the toctree) is absent from the compiled master now
# degrades to plain text instead of resolving to the decoy's
# identically-spelled-before-this-fix label.
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
#   (e) The decoy's emitted anchor label MUST stay
#       `a_u5f_u2f_b:nested-target` (XREF-05, D-02) -- if that spelling
#       ever changes, this fixture and the render gate that reads it
#       (`test_label_collision_no_longer_links_to_decoy`) must be revisited
#       together.

project = "Xref Label Collision Guard Gate"
author = "Probe Author"
release = "1.0"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "manual.typ", "Collision Gate", "Probe Author"),
]
