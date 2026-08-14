# Phase 49 plan 03, Task 1: the 2-node toctree cycle (D-06). Master `alpha`
# toctrees `beta`; `beta` toctrees `alpha` back. `derive_master_edge_keys`'s
# `traversed` list is seeded with `[alpha]` before the walk begins and
# appended to BEFORE recursing, so when `beta`'s own walk reaches `alpha`,
# `alpha` is already `in traversed` and the back edge is skipped -- no
# unbounded recursion, no second edge key ever published for the back
# edge. Only `alpha` is a `typst_documents` master (adding a second master
# here would change which document seeds the traversal, per the
# Emission-contract's Traversal rule).
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising the 2-node-cycle shape:
#   - The back edge from `beta` to `alpha` must stay in `beta`'s own
#     toctree -- it is the cycle this fixture exists to close over.
#   - Adding a second `typst_documents` master would change which document
#     seeds the DFS traversal and dissolve the intended shape.

project = "Cycle Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

root_doc = "alpha"

typst_documents = [
    ("alpha", "manual.typ", "Cycle Gate", "Probe Author"),
]
