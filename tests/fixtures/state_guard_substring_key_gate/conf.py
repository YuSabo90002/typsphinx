# Phase 49 plan 03, Task 2: the COMP-06 adjacency detector -- the guard
# tests ARRAY membership, not string containment. Master `index` toctrees,
# in this order, `guideext` (a proper prefix-extension of `guide`) then
# `guide` itself; `guideext` in turn toctrees `guide`. Under the contract's
# `<parent>#<occurrence>><child>` key format this yields: a published key
# for the master-to-longer edge (`index#0>guideext`), a published key for
# the longer-to-shorter edge (`guideext#0>guide`), and a DARK key for the
# master-to-shorter edge (`index#0>guide`) which is a proper SUBSTRING of
# the published `index#0>guideext` key (the first 13 characters of
# "index#0>guideext" are exactly "index#0>guide", since "guideext" begins
# with the literal prefix "guide"). If the array-literal construction ever
# omitted its mandatory trailing comma at arity 1 (the silent-corruption
# hazard measured in 49-EVIDENCE.md Probe 5), Typst's `in` operator would
# silently degrade from array membership to substring containment and the
# dark guard would incorrectly fire against the published string. With the
# array correctly constructed, `"index#0>guide"` is not an ELEMENT of the
# array `["index#0>guideext", "guideext#0>guide"]`, only a substring of one
# of its elements.
#
# This fixture covers the array-versus-string SEMANTICS half of the
# trailing-comma hazard, not the one-element trailing-comma ARITY half --
# that arity-1 hazard can only manifest when exactly ONE key is published
# (this fixture publishes two per master), and its real detector is the
# arity-1 Typst-type readback asserted directly against the production
# rendering function in 49-04's own unit module.
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops constructing the substring hazard:
#   - `guideext` and `guide` must stay in the prefix-extension relation
#     (`guideext` starts with the literal string `guide`) -- that relation
#     IS the hazard this fixture constructs.
#   - `index`'s toctree entry order must stay longer-first (`guideext`,
#     then `guide`) -- that is what makes the shorter-named document lose
#     first-encounter-wins and its direct, parent-side guard go dark.
#   - `guideext` must keep its own toctree of `guide` -- without it,
#     `guide` is never claimed by any parent and there is no published key
#     for the dark key to be a substring of.
#   - If the edge-key format (`<parent>#<occurrence>><child>`) ever
#     changes, this fixture stops constructing the hazard and must be
#     revisited.

project = "Substring Key Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "manual.typ", "Substring Key Gate", "Probe Author"),
]
