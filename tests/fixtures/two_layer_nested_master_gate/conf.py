# Phase 47 plan 01, task 1: the B-1/B-2 fixture (COMP-03, COMP-04, OUT-03).
# Two docnames, `index` and `guide/index`, BOTH are typst_documents entries
# (both a wrapper and, for `guide/index`, also a toctree child of `index`).
# This is the exact shape that reproduces B-1 (nested master-as-toctree-child
# fails to compile: "file not found") and B-2 (nested master's template
# re-expands mid-body) on the unfixed tree.
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising COMP-03/COMP-04:
#   - The SECOND entry's docname MUST be `guide/index` (not `guide`) --
#     `guide/index` is the docname Sphinx derives from `guide/index.rst`;
#     `chapter1` style flat docnames would not exercise the directory-nested
#     case the "resolved wrapper location, not raw docname" fix targets.
#   - The SECOND entry's target `manuals/guide.typ` MUST differ from the
#     docname's own basename (`index`) AND MUST sit in a directory
#     (`manuals/`) unrelated to the docname's own directory (`guide/`) --
#     per 47-CONTEXT.md "Specific Ideas", this is the ONLY shape that proves
#     wrapper->content include paths are computed from the wrapper's
#     RESOLVED output location rather than from the raw docname string.
#     A target such as `guide/manual.typ` (still under `guide/`) would not
#     distinguish "resolved location" reasoning from "docname" reasoning.
#   - `index.rst` MUST toctree-include `guide/index` -- this is what makes
#     `guide/index` BOTH a typst_documents entry and another master's
#     toctree child, the exact B-1/B-2 shape.
#   - `index.rst`'s body marker `OUTER-PROSE-MARKER` and `guide/index.rst`'s
#     body marker `GUIDE-BODY-MARKER` must keep their exact spelling -- the
#     COMP-04 pypdf structural assertion locates each marker by substring.

project = "Outer Master"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "outer.typ", "Outer Master", "Probe Author"),
    ("guide/index", "manuals/guide.typ", "Nested Master", "Probe Author"),
]
