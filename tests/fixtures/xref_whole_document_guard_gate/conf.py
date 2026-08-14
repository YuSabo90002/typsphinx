"""Sphinx config for the whole-document cross-reference guard gate
(G-48-4 / XREF-03 gap closure, plan 48-06).

A minimal three-document project exercising the WHOLE-DOCUMENT reference
form (``:doc:``) in BOTH outcomes at once, inside a single compiled master:
``index`` (the single ``typst_documents`` master) toctrees ``included``
only, and carries one whole-document reference to each of ``included``
(toctree-reachable, so the compiled master DOES ``#include()`` it) and
``orphan`` (marked ``:orphan:``, in NO toctree, so the compiled master
never ``#include()``s it).

Pre-fix (this plan), BOTH references render as a plain string-url
``link("<target>.pdf", ...)`` naming a file the Typst output never
produces -- a dead link the build itself does not detect (exit 0, a valid
compiled PDF). Post-fix (plan 48-07), the reference to ``included`` becomes
a real, working compile-time-guarded link; the reference to ``orphan``
degrades to plain, non-clickable text (D-02: identical visible words
either way).

Every design choice below is transcribed directly from
``48-EXPECTED-STRUCTURE.md`` §4 ("Phase 48 Plan 05 -- Whole-Document
Reference Path"), written on paper before any emitter change exists --
never read off a build (binding constraint #6).
"""

project = "Whole Document Guard Gate"
author = "Probe Author"
release = "1.0"

extensions = ["typsphinx"]

# Target "index" (stem "index") would casefold-collide with the docname's
# own content path "index.typ" (fixture de-collision rule,
# 47-EXPECTED-STRUCTURE.md, the same convention every sibling fixture in
# this phase already follows); renamed to "manual.typ" per
# 48-EXPECTED-STRUCTURE.md §4.
typst_documents = [
    ("index", "manual.typ", "Whole Document Guard Gate", "Probe Author"),
]

# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising the G-48-4 gap:
#   (a) `orphan.rst` MUST keep its `:orphan:` marking AND MUST appear in NO
#       toctree -- it is the degrade half of the fixture (the whole-document
#       reference whose target is never `#include()`d into the compiled
#       master). Adding it to a toctree collapses the fixture into a
#       single-outcome case where both references legitimately link.
#   (b) The two references in `index.rst` MUST stay whole-document
#       references (`:doc:`) with NO anchor -- an anchored `:ref:`/`:doc:`
#       routes through the ALREADY-GUARDED anchored-xref path (D-06,
#       unaffected by this gap fix), and the fixture stops exercising the
#       whole-document form this gap fix targets.
#   (c) The master's target (`manual.typ`) must not casefold-equal `index`'s
#       own content path (`index.typ`) -- a target whose resolved path
#       casefold-equals the docname's own content path is a BLD-03
#       self-collision Phase 47's validator refuses. See (a) above for the
#       parallel rule this fixture's sibling gates already follow.
