# Phase 49 plan 03, Task 1: D-03/D-10's `self`-entry / external-URL-entry
# shape, and the phase's one classic-`TypstError` RED. `index`'s single
# toctree lists, in order: a `self` entry, an external-URL entry (written
# with a title so docutils parses it as a link rather than a bare docname),
# then `child` TWICE. Per `sphinx/directives/other.py:146-149`, `self` and
# the external URL are appended to `entries` ONLY -- never to
# `includefiles` -- so D-03's includefiles-only iteration never sees them.
# The duplicate `child` entry exercises D-04's per-emission-site occurrence
# rule: two guard lines are emitted in `index.typ` (occurrence 0 and
# occurrence 1), and only the occurrence-0 key is ever published by any
# master's graph side. Pre-fix, the CURRENT `entries`-iterating emitter
# unconditionally emits `include("self.typ")` and
# `include("https://example.com.typ")`, neither of which exists on disk,
# so `typst.compile()` aborts with
# `TypstError: file not found (searched at .../self.typ)` -- this fixture's
# own recorded RED (49-SHAPES-RED-EVIDENCE.md).
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising D-03/D-10:
#   - The `self` entry and the external-URL entry must both stay in the
#     toctree, because Sphinx routes them to `entries` only and they are
#     what makes the current emitter emit an include of a file that does
#     not exist.
#   - The child docname must stay listed TWICE, because the duplicate is
#     what exercises the per-emission-site occurrence rule (D-04).
#   - The external URL must keep its title form ("External Site <...>"),
#     so docutils' `explicit_title_re` parses it as a link rather than a
#     bare docname reference.

project = "Self And URL Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "manual.typ", "Self And URL Gate", "Probe Author"),
]
