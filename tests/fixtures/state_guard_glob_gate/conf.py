# Phase 49 plan 03, Task 1: the `:glob:` toctree shape (D-06). `index`'s
# single `:glob:`-optioned toctree matches three sibling documents under
# `guide/`, authored on disk in `zulu, alpha, mike` order (deliberately NOT
# alphabetical) so the sorted glob expansion is observable against
# on-disk/authoring order. Per `sphinx/directives/other.py:109-129`, glob
# entries are expanded at PARSE time into `sorted(patfilter(all_docnames,
# pat_name))` and appended to BOTH `entries` and `includefiles` in that
# sorted order -- by the time the builder's DFS or the translator's
# `visit_toctree` sees the node, this glob toctree is indistinguishable
# from an explicit toctree listing `guide/alpha, guide/mike, guide/zulu` in
# that sorted order. No special handling is needed anywhere in the new
# mechanism.
#
# (glob_image_render_gate, the only other fixture whose name signals glob
# handling, exercises IMAGE URI glob resolution -- a `.. figure::
# /_static/pic.*` glob, resolved by post_process_images() -- not a
# `:glob:` toctree option at all. This fixture is the first `:glob:`
# toctree fixture in the repository.)
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising the `:glob:` shape:
#   - The glob pattern `guide/*` must stay, matching exactly the three
#     `guide/zulu`, `guide/alpha`, `guide/mike` documents.
#   - The three docnames' sorted order (alpha, mike, zulu) is deliberately
#     NOT their title/authoring order (zulu, alpha, mike) -- this is what
#     makes the sorted expansion observable rather than coincidental.
#   - Adding a fourth matching document under `guide/` changes every
#     expected position derived from this fixture's sorted order.

project = "Glob Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "manual.typ", "Glob Gate", "Probe Author"),
]
