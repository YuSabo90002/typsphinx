# Phase 49 plan 03, Task 1: the literal self-referencing toctree (a document
# toctreeing its OWN docname -- not the `self` magic keyword, covered
# separately by state_guard_self_and_url_gate). `index`'s single toctree
# lists its own docname `index`, then one ordinary child `other`.
# Sphinx's OWN `TocTree.parse_content` removes the current document from its
# candidate pool BEFORE the entry loop starts
# (`all_docnames.remove(current_docname)`, `sphinx/directives/other.py:98`),
# so the self-listing entry hits the SAME "reference to nonexisting
# document" branch a genuinely broken entry would -- it warns and
# `continue`s, NEVER reaching `entries` OR `includefiles`. There is nothing
# for the guard mechanism to see: no guard line is ever emitted for it at
# all, not even a dark one. This is a DIFFERENT mechanism than the 2-node
# cycle case's `traversed`-list handling, though both produce the same
# "skip, silently" outcome.
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising the self-reference shape:
#   - The self-listing entry (`index` listing itself) must stay first in
#     the toctree -- it is the shape under test.
#   - The ordinary child `other` must stay, because it is what proves the
#     self entry was skipped rather than the whole toctree being dropped
#     (an empty resulting `includefiles` would look identical to a
#     silently-broken toctree without this second entry).

project = "Self Reference Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "manual.typ", "Self Reference Gate", "Probe Author"),
]
