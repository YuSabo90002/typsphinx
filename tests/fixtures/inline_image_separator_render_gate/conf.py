# Phase 62 plan 01 (tracer), D-01: the inline-image-separator real-compile
# gate fixture. This tracer commit configures a THREE-master subset (index,
# fail_01_sub_mid_sentence, pass_parent) of the full 18-master matrix plan
# 02 completes -- one failing shape (Q1 row 1), one must-keep-passing shape
# (Q2 row A), and the image-free root master that proves the `#include()`
# blast radius (IMG-09).
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising the tracer's obligations:
#   - `index` carries NO image of any kind -- it is SC#1's blast-radius
#     document, failing today only because Typst's `#include()` re-parses
#     the poisoned `fail_01_sub_mid_sentence` content file it toctrees in.
#   - `pass_parent` is the POSITIVE CONTROL (D-03): it must stay green in
#     the same RED build in which the FAIL masters are red.
#   - Every `typst_documents` target stem is the docname with an `-out`
#     suffix (the Phase 47 de-collision rule -- a target equal to its own
#     docname would resolve to the same physical path as that docname's own
#     content file).
#   - Do NOT add `numref` usage to this fixture -- it collides with the
#     known-open NUM-01 defect (`.planning/todos/pending/
#     2026-08-14-numref-number-diverges-per-master-and-vanishes-for-
#     non-root-only-figures.md`).
#
# At phase completion (plan 02) this fixture grows to 18 masters (index +
# 16 FAIL docs + pass_parent) and 26 documents total (62-CONTEXT.md D-01).

project = "Inline Image Separator Render Gate"
author = "Test Author"
release = "1.0.0"
copyright = "2026, Test Author"

extensions = ["typsphinx"]

html_static_path = ["_static"]

root_doc = "index"

typst_documents = [
    ("index", "index-out.typ", "Inline Image Separator Render Gate", "Test Author"),
    (
        "fail_01_sub_mid_sentence",
        "fail_01_sub_mid_sentence-out.typ",
        "Fail 01 - Substitution Image Mid-Sentence",
        "Test Author",
    ),
    ("pass_parent", "pass_parent-out.typ", "Pass Parent", "Test Author"),
]
