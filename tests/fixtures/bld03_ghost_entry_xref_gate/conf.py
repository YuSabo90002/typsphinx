# Phase 47 gap-closure plan 13, task 1: BLD-03's ghost-entry cross-reference
# gate -- the FIFTH site, `_compute_master_included_docnames()`, does not
# consult `_is_usable_typst_documents_entry()`. An under-length entry
# (`("ghost",)`) still contributes its docname AND ITS WHOLE TOCTREE CLOSURE
# to `master_included_docnames`, even though `_validate_output_path_
# collisions()` (already predicate-guarded, 47-11) correctly produces no
# wrapper file for it. A real master's `:ref:` into that phantom-included
# subtree is therefore judged "safe to link" and emits a label that no
# compiled document will ever contain.
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising the fifth-site gap:
#   - The SECOND entry MUST stay a 1-tuple naming a REAL docname (`ghost`)
#     -- making it well-formed removes the under-length shape and collapses
#     this fixture into the already-green `bld03_under_length_entry_gate`.
#   - `ghost.rst` MUST keep BOTH its `:orphan:` field AND its `toctree`
#     directive -- the toctree is the only thing that pulls `ghost_child`
#     into the pre-fix include closure, and without `:orphan:` the fixture
#     emits an unrelated "not included in any toctree" consistency warning
#     that muddies the transcript.
#   - `index.rst` MUST keep its `:ref:` into `ghost_child`'s label -- that
#     reference IS the defect.
#   - The FIRST entry MUST stay a well-formed 4-tuple whose target basename
#     (`manual.typ`) differs from its docname (`index`), so `manual.pdf`
#     proves the well-formed sibling master still compiles.

project = "Ghost Entry Xref Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "manual.typ", "Real Master", "Probe Author"),
    ("ghost",),
]
