# Phase 49 plan 06 -- open question #2 / D-01 fixture: a two-master
# numbered-figure project exercising both mechanically distinct `:numref:`
# cases 49-RESEARCH.md sharpened. Per 49-EXPECTED-STRUCTURE.md's fixture
# specification entry 10 (the ONLY source of this fixture's docnames,
# figure names, captions, reference sites and traversal positions -- this
# file transcribes that specification, never invents its own shape).
#
# Case (a): `fig-x` (in `shared_fig_doc`) is reachable from BOTH masters, at
# DIFFERENT traversal positions -- directly under `index` (master A) and,
# under `other_master` (master B), AFTER `only_doc`. Sphinx's own
# `env.toc_fignumbers` is populated by a SINGLE walk rooted only at
# `root_doc` (`index`), so it bakes ONE literal number into both masters'
# `:numref:` reference text -- while Typst's own `figure()` numbering is a
# separate, per-compiled-wrapper counter, so `fig-x` is Typst's figure 1 in
# `index`'s own compile but a LATER figure in `other_master`'s compile
# (`only_doc`'s own filler figure and `fig-y` both precede it there).
#
# Case (b): `fig-y` (in `only_doc`) is reachable ONLY through `other_master`
# (never through `root_doc`), so Sphinx's root-rooted `toc_fignumbers` walk
# never visits it -- `get_fignumber()` raises, and `_resolve_numref_xref()`
# falls back to the reference's own literal `contnode` text. The fixture
# proves this fallback (and records whatever warning, if any, accompanies
# it) rather than assuming its exact shape.
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising Case (a) or Case (b):
#   - Figure numbering (`numfig = True`) must stay enabled -- Case (a) and
#     Case (b) both depend on Sphinx's own numbered-figure machinery being
#     live; with `numfig` disabled, `:numref:` behaves differently (a
#     dedicated "numfig is disabled" warning path, not the fallback this
#     fixture measures).
#   - `shared_fig_doc` (Case (a)'s subject, figure `fig-x`) MUST stay
#     reachable from BOTH `index` and `other_master`, and at DIFFERENT
#     traversal positions in each: directly under `index`'s own toctree,
#     but AFTER `only_doc` under `other_master`'s own toctree. Equal
#     positions in both masters would dissolve Case (a) -- Typst's
#     per-compile counter would then assign `fig-x` the SAME number in
#     both compiles, by construction, not by measurement.
#   - `only_doc` (Case (b)'s subject, figure `fig-y`) MUST stay unreachable
#     from `root_doc` (`index`) by ANY path -- `index.rst`'s own toctree
#     must never name it, directly or transitively. Any path from the root
#     assigns it a Sphinx figure number and dissolves Case (b).
#   - Both figures (`fig-x`, `fig-y`) must keep their exact `:name:` values
#     -- both masters' `:numref:` reference sites target them by that name.
#   - `only_doc`'s own filler figure (an anonymous, unnamed figure placed
#     BEFORE `fig-y`'s own figure) must stay present and stay BEFORE
#     `fig-y` -- it exists so Typst's per-compile figure counter and
#     Sphinx's project-wide numbering cannot coincide by accident: without
#     it, `other_master`'s own traversal order alone already diverges
#     `fig-x`'s Typst number from Sphinx's baked number, but the filler
#     figure widens that gap so the divergence is not a borderline
#     off-by-one that a future edit could accidentally close.
#   - `other_master.rst` must keep its `:orphan:` field (so Sphinx emits no
#     "isn't included in any toctree" warning).
#   - Neither `typst_documents` target below (`manual.typ`, `manual2.typ`)
#     may be renamed onto any docname's own content path (`index.typ`,
#     `other_master.typ`, `shared_fig_doc.typ`, `only_doc.typ`) -- Phase
#     47's BLD-03 self-collision validator refuses the build if either
#     target casefold-equals a docname's own content path.

project = "Numref Two Case Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]
root_doc = "index"
numfig = True

typst_documents = [
    ("index", "manual.typ", "Numref Two Case Gate - Index", "Probe Author"),
    ("other_master", "manual2.typ", "Numref Two Case Gate - Other", "Probe Author"),
]
