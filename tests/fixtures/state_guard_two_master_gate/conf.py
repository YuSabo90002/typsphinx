# Phase 49 plan 02 -- COMP-07/COMP-08/COMP-09 fixture: two masters (index +
# bmaster) both toctree-reachable to a shared chapter, exercising defect A
# (the write-time ledger's per-build, not per-master, decision), the diamond
# M -> [p, q], p -> [c], q -> [c] shape (via zmid claiming `shared` before
# index's own direct entry does), and document-order interleaving (the
# "Indices and tables" trailing section after the toctree). Also carries a
# nested-docname (path-separator) shared descendant (`sub/nested`) and an
# empty-include-file-list toctree (`emptytoc`), both reachable from BOTH
# masters through the SAME `shared#0>sub/nested` / `sub/nested#0>emptytoc`
# edge keys -- executor additions beyond 49-EXPECTED-STRUCTURE.md's literal
# fixture specification entry 1, derived by hand from the Emission
# contract's traversal rule against this fixture's own conf.py/.rst content,
# per binding constraint #6 (never read off a build).
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising defect A / the diamond / interleaving:
#   - `index.rst`'s toctree MUST list `zmid` BEFORE `shared`, in that exact
#     order -- this is what makes `zmid` claim `shared` on
#     first-encounter-wins, so master A renders `shared` NESTED under
#     `zmid` rather than at the direct position. Swapping the order changes
#     which parent claims `shared` and invalidates every derived edge set
#     below.
#   - `bmaster.rst` must keep its `:orphan:` field (so Sphinx emits no
#     "isn't included in any toctree" warning) and must keep its own
#     toctree of EXACTLY `shared` -- no other entry. `bmaster` is master B;
#     adding or removing an entry there changes its own derived edge set.
#   - `shared.rst`'s body marker `SHARED-CHAPTER-MARKER` must keep its exact
#     spelling -- the pre-fix RED evidence (`49-RED-EVIDENCE.md`) is a
#     `pypdf`-extracted occurrence count of this exact string, directly
#     comparable to the 2026-08-11 baseline recorded in PROJECT.md (master
#     A: 0, master B: 1, exit 0, no warning).
#   - Neither `typst_documents` target below (`manual.typ`, `bmanual.typ`)
#     may be renamed onto any docname's own content path
#     (`index.typ`/`zmid.typ`/`shared.typ`/`bmaster.typ`/`sub/nested.typ`/
#     `emptytoc.typ`) -- Phase 47's BLD-03 self-collision validator refuses
#     the build if either target casefold-equals a docname's own content
#     path.
#   - The second master (`bmaster`) must stay in the SAME Sphinx project as
#     `index` -- `env` is per-project, so two separate projects would
#     exercise nothing about per-master divergence.
#   - `shared.rst`'s own toctree (added beyond entry 1's literal spec, to
#     the nested-docname child `sub/nested`) and `sub/nested.rst`'s own
#     toctree (to `emptytoc`) must not be reordered or removed -- both
#     masters reach `sub/nested` and `emptytoc` through the SAME edge keys
#     (`shared#0>sub/nested`, `sub/nested#0>emptytoc`), which is the whole
#     point of attaching them here rather than under `index.rst`/
#     `zmid.rst`/`bmaster.rst` directly (attaching them there would risk
#     perturbing the defect-A/diamond/interleaving measurements those three
#     files' EXACT spec-transcribed content is measured against).
#   - Every marker string in this fixture's `.rst` files is plain ASCII with
#     no zero-width characters -- a zero-width space poisons `pypdf` text
#     extraction by surfacing at an unrelated glyph boundary (a hazard
#     measured in v0.7.0 Phase 37), which would make the extraction
#     assertions unreliable for a reason unrelated to composition.

project = "Two Master Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "manual.typ", "Two Master Gate - Index", "Probe Author"),
    ("bmaster", "bmanual.typ", "Two Master Gate - B", "Probe Author"),
]
