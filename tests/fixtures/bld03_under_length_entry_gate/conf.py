# Phase 47 gap-closure plan 11, task 1: BLD-03's under-length-entry
# fixture -- a `typst_documents` entry with fewer than two elements
# (`("index",)`), naming a REAL docname. Before this plan,
# `_validate_output_path_collisions()` skipped this entry (tolerating it,
# per the locked policy), but `_write_typst_files()`'s wrapper loop did NOT
# skip it the same way -- its guard was `entry[0] != docname`, which a
# 1-tuple satisfies once `entry[0] == docname`, so a self-including wrapper
# was written OVER the docname's own content file at `index.typ`, destroying
# it. This is the drift the four wrapper-path-resolving sites' independent
# spellings produced (BLD-03).
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising the under-length-entry gap:
#   - The FIRST entry MUST stay a 1-tuple naming a REAL docname (`index`) --
#     an entry naming a docname that does not exist would not reach the
#     write-phase wrapper loop for that docname at all.
#   - The SECOND entry MUST stay a well-formed 4-tuple naming a DIFFERENT
#     docname (`other`) -- this is what proves the D-07 wrapper report
#     still names only the entries that really were written; removing it
#     makes that report assertion vacuous (nothing would be reported
#     either way).
#   - `index.rst` carries `UNDERLENGTH-CONTENT-SENTINEL-CCC` and has NO
#     toctree -- its content file legitimately contains no include
#     directive at all, so a false positive "content survived" is not
#     mistakeable for "the toctree include survived".
#   - `other.rst` starts with an `:orphan:` field so Sphinx does not warn
#     about it being outside every toctree, and carries
#     `UNDERLENGTH-OTHER-MARKER-EEE`.

project = "Under Length Entry Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

typst_documents = [
    ("index",),
    ("other", "manual.typ", "Other Master", "Probe Author"),
]
