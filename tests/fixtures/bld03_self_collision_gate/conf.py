# Phase 47 plan 01, task 1: BLD-03's fixture -- D-01's canonical
# self-collision configuration, `[("index", "index.typ", ...)]`. This is the
# exact configuration `47-CONTEXT.md` D-01 names as the one that builds
# successfully in v0.7.x (via `builder.py:275`'s `effective != docname`
# escape) and MUST stop building once content files exist unconditionally
# (COMP-01): the wrapper's own target resolves onto the docname's own
# content file path.
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising BLD-03/D-01:
#   - The single entry's docname and target stem MUST both be `index` --
#     `("index", "index.typ", ...)` is the literal configuration named by
#     the decision record. Any other docname/target pair does not reproduce
#     the self-collision case.

project = "Self Collision Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "index.typ", "Self Collision Gate", "Probe Author"),
]
