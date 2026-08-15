# Phase 47 gap-closure plan 13, task 1: BLD-03's unhashable-docname gate --
# the FIFTH site, `_compute_master_included_docnames()`, builds its masters
# list via a bare `if entry` truthiness filter (line 269), never consulting
# `_is_usable_typst_documents_entry()`. A non-hashable `entry[0]` (e.g. a
# `list`, a plausible `conf.py` typo since Sphinx does not type-check
# config values) therefore reaches the BFS's unguarded `docname in
# included` / `included.add(docname)` `set` operations and raises an
# uncaught `TypeError: unhashable type: 'list'`, aborting the whole build
# with a raw traceback -- instead of the graceful warn-and-skip every OTHER
# predicate-guarded site in this file already guarantees for exactly this
# shape (the collision validator and the write-phase wrapper loop both
# already tolerate this same entry, post-47-11).
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising the crash:
#   - `entry[0]` of the FIRST entry MUST stay a `list` -- a `123` or a
#     `None` docname is hashable, reaches the BFS's set operations without
#     raising, and therefore exercises only the already-covered
#     `tests/test_non_str_docname_gate.py` path rather than this crash.
#   - The well-formed SECOND entry MUST stay, because it is what proves
#     the graceful skip still lets the real master build.
#   - Its target (`real.typ`) MUST differ from its docname (`index`) so
#     the wrapper and content files are distinguishable on disk.

project = "Unhashable Docname Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

typst_documents = [
    (["weird"], "manual.typ", "Weird Master", "Probe Author"),
    ("index", "real.typ", "Real Master", "Probe Author"),
]
