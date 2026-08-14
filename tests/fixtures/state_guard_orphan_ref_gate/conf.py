# Phase 49 plan 03, Task 1: the `:orphan:` document referenced but not
# toctree'd (D-06). `index` has no toctree at all -- only a cross-reference
# to a label defined in `orphan_doc`, which carries an `:orphan:` field and
# is listed by no toctree anywhere. `env.toctree_includes["index"] == []`,
# so `derive_master_edge_keys` never visits `orphan_doc` and no wrapper's
# published state ever contains a key naming it as a child.
# `orphan_doc.typ` is written unconditionally (COMP-01) but is included by
# NO wrapper's published state, so `ORPHAN-BODY-MARKER` never appears in
# `manual.pdf`. The `:ref:` cross-reference degrades to plain text via
# Phase 48's EXISTING compile-time `query(<label>).len() > 0` guard --
# this fixture asserts that existing degradation, not a new mechanism this
# phase introduces.
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising the orphan-reference shape:
#   - `orphan_doc.rst` must keep its `:orphan:` field and must never be
#     added to any toctree.
#   - `orphan_doc.rst`'s labelled section (`orphan-target-label`) must stay
#     the reference's target.
#   - This fixture asserts Phase 48's existing compile-time degradation
#     rather than introducing a new mechanism -- do not add a toctree
#     entry for `orphan_doc` "to make the reference resolve", that would
#     defeat the shape under test.

project = "Orphan Reference Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "manual.typ", "Orphan Reference Gate", "Probe Author"),
]
