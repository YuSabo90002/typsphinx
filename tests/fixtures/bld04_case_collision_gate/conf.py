# Phase 47 plan 01, task 1: BLD-04's fixture -- a target differing from a
# docname only by case. `manual`'s own content path (`manual.typ`) and the
# `manual` entry's wrapper target (`Manual.typ`, capital M) are the SAME
# physical path on a case-insensitive filesystem (Windows, default macOS
# APFS) but DIFFERENT paths on Linux -- 47-RESEARCH.md Pitfall 5's exact
# measured gap, invisible on Linux CI.
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising BLD-04:
#   - The second entry's target MUST be `Manual.typ` (capital M) against
#     docname `manual` -- this is the fixture success criterion 4 names
#     verbatim.
#   - The first entry's target `index-wrapper.typ` deliberately does NOT
#     collide with anything, so `-b typst`'s failure (once BLD-04 closes)
#     is attributable to the SECOND entry alone.

project = "Case Collision Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "index-wrapper.typ", "Index Wrapper Master", "Probe Author"),
    ("manual", "Manual.typ", "Manual Master", "Probe Author"),
]
