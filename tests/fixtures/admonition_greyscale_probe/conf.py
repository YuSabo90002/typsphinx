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
typst_documents = [
    ("index", "index", "Admonition Greyscale Probe", "Test Author"),
]

# The bundled default template unconditionally emits a title page + a table
# of contents before the body (3 pages minimum, measured this session),
# which is incompatible with this fixture's one-page requirement (see
# _templates/minimal.typ's own header comment). This explicit template
# opts out of both while keeping the same #project() parameter surface.
typst_template = "_templates/minimal.typ"
