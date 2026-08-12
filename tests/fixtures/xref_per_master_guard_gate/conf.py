# Phase 48 plan 01, task 1: the SC#1 two-master acceptance fixture (XREF-03).
# Two docnames, `index` (master alpha) and `bravo` (master bravo), both
# typst_documents entries. `index`'s toctree lists `target`; `bravo` lists
# nothing of its own and is marked `:orphan:` so Sphinx never warns it is
# missing from a toctree. Both `index.rst` and `bravo.rst` carry the SAME
# `:ref:` sentence into `target.rst`'s labelled section -- so whether that
# reference is "safe to link" must be decided PER COMPILED WRAPPER, not by a
# build-time union across all masters (which admits `target` to BOTH files
# because it is reachable from *some* master, alpha's).
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising the per-master divergence:
#   (a) Only `index.rst`'s toctree may list `target` -- adding `target` to a
#       toctree in `bravo.rst` collapses the fixture into a single-outcome
#       case where both masters legitimately include it.
#   (b) `bravo.rst` MUST keep `:orphan:` AND MUST keep no toctree of its
#       own -- the toctree is what would pull `target` into bravo's own
#       compiled wrapper, which this fixture must never do.
#   (c) The `:ref:` sentence MUST stay byte-identical between `index.rst`
#       and `bravo.rst` -- the gate asserts the two emitted content files
#       carry the identical guarded expression.
#   (d) Neither entry's target may be renamed onto a docname's own content
#       path -- `bravo`'s target is deliberately `bravo_master.typ`, NOT
#       `bravo.typ`, because a target whose resolved path casefold-equals
#       the docname's own content path is a BLD-03 self-collision that
#       Phase 47's validator refuses.

project = "Xref Per Master Guard Gate"
author = "Probe Author"
release = "1.0"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "alpha.typ", "Alpha Master", "Probe Author"),
    ("bravo", "bravo_master.typ", "Bravo Master", "Probe Author"),
]
