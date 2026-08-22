# Sphinx configuration for the ADM-04 greyscale-distinguishability probe.
#
# This fixture exists to be rasterised (typst.compile(..., format="png"))
# and desaturated (Pillow's Image.convert("L")) by
# scripts/render_admonition_greyscale.py, producing the PNG the owner
# inspects to sign off ADM-04 -- the milestone's only [V] (visual UAT)
# requirement. It must stay exactly one page: typst-py's PNG export
# requires a page-number template in the output filename the moment a
# document exceeds one page (39-RESEARCH.md Pitfall 4), and this pipeline
# deliberately avoids that mechanism.
#
# It is re-rendered by plan 39-07 after the bucket-routing fix (ADM-01..
# ADM-03) lands, because a render taken before that fix would show the
# pre-phase bucket assignments, not the post-phase ones this plan's sibling
# plans establish.

project = "Admonition Greyscale Probe"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the
# writer emits the full template plus the gentle-clues @preview import --
# included documents only get a minimal import set (see typsphinx/writer.py).
#
# Phase 47 de-collision (47-EXPECTED-STRUCTURE.md "Fixture de-collision
# rule"): the original target "index" resolved to the SAME physical path
# as this docname's own content file (index.typ) under the two-layer
# split -- a self-collision (D-01). A PURPOSE-SPECIFIC name is used here
# instead of the canonical "master.typ" replacement, for a reason
# unrelated to the collision itself: `scripts/render_admonition_
# greyscale.py`'s `_build_typ()` (out of this plan's files_modified
# scope, so it cannot be edited here) locates "the master document" by
# globbing `*.typ` (excluding a `_template.typ` name, a filter that
# predates Phase 54's bundle relocation and is now vestigial rather than
# load-bearing -- the bundle-copy driver's own `_template/<key>/` bundle
# is one directory down, so it never matches a non-recursive `*.typ`
# glob at all) and picking the ALPHABETICALLY FIRST result -- a
# convention that was harmless before the split (exactly one
# non-template .typ file existed) but now must sort before the
# docname-derived content file, "index.typ", or the script would
# rasterise the untemplated CONTENT file instead of the wrapper.
# "admonition-greyscale-probe.typ" sorts before "index.typ"
# ("a" < "i") and keeps `tests/test_admonition_greyscale_pipeline.py`'s
# own duplicate glob-and-sort logic pointed at the same wrapper.
typst_documents = [
    (
        "index",
        "admonition-greyscale-probe.typ",
        "Admonition Greyscale Probe",
        "Test Author",
    ),
]

# The bundled default template unconditionally emits a title page + a table
# of contents before the body (3 pages minimum, measured this session),
# which is incompatible with this fixture's one-page requirement (see
# _templates/minimal.typ's own header comment). This explicit template
# opts out of both while keeping the same #project() parameter surface.
typst_template = "_templates/minimal.typ"
