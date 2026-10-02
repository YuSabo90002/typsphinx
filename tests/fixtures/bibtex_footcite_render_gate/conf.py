"""Sphinx config for the bibtex FOOTCITE render-gate fixture (M001/S03, T01).

What this fixture is for: it is the isolated Sphinx project that S03's gates
assert against -- that a ``:footcite:`` citing site plus a trailing
``.. footbibliography::`` render as REAL Typst footnotes at the page foot
(the definition form ``[#footnote({...}) <label>]`` at the first site, the
bare reuse form ``footnote(<label>)`` at a repeat site), with NO Typst grid
anywhere, and that a hand-written docutils footnote coexists with the
bibtex-generated ones under distinct labels.

WHY THIS IS A SEPARATE DIRECTORY (do not merge it into
``tests/fixtures/bibtex_citation_render_gate/``). This was MEASURED at S03
plan time, not assumed. Appending a ``footcite`` site plus a
footbibliography directive to the shared fixture's ``index.rst`` and
rerunning its gate gave **2 failed / 11 passed**:
``test_cited_entry_appears_exactly_once_in_typ`` and
``test_cited_entry_appears_exactly_once_in_pdf`` both broke, because
Smith2020's title then legitimately appears TWICE -- once as the
``.. bibliography::`` grid row, once as the footbibliography footnote body
(extracted PDF text showed count 2). Worse, the shared fixture's own
vacuous-pass guards did NOT catch the redefinition: its ``_parse_citing_sites``
regexes ``:cite:([a-z]*):``, which does not match the colonised footcite role
(measured -- returns ``[]``), so its ``citing_sites`` stayed 3 and
``cited_keys`` stayed 2 while R003's meaning was silently redefined
underneath them. See decision D008. S03 therefore builds here and leaves
``bibtex_citation_render_gate`` byte-identical.

Scope boundary: this project carries NO ``cite:p`` / ``cite:t`` site and NO
``.. bibliography::`` directive -- a grid in this fixture would destroy
S03's zero-grid contract. Any COMBINED-form project (grid and footnotes in
one document) is owned by **S06, not S03**.

Division of labour (MEM002): registration of the footcite role and the
``.. footbibliography::`` directive belongs entirely to
``sphinxcontrib.bibtex``. ``typsphinx`` registers nothing in that space -- it
only renders the already-resolved ``footnote`` / ``footnote_reference`` nodes
that sphinxcontrib-bibtex leaves in the doctree. Hence both extensions are
loaded and ``sphinxcontrib.bibtex`` must come FIRST, so its cite domain
exists before typsphinx's builders write anything.

``bibtex_bibfiles`` is required by sphinxcontrib-bibtex: without it the build
errors out before any ``.typ`` is written.

Fixture de-collision rule (same measured hazard the shared fixture
documents): a ``typst_documents`` target MUST differ from its own docname. A
target of ``"index"`` for docname ``index`` makes the builder abort with
``typst: 1 output path collision(s)``, because the two-layer split already
writes this docname's own content file as ``index.typ``. The target is
therefore ``master.typ``; a build emits BOTH ``index.typ`` (content) and
``master.typ`` (master). Gates must assert over ``index.typ``.
"""

project = "Bibtex Footcite Render Gate"
author = "Test Author"
release = "1.0.0"

# sphinxcontrib.bibtex first: it owns the footcite role and the
# footbibliography directive (MEM002). typsphinx only renders resolved nodes.
extensions = [
    "sphinxcontrib.bibtex",
    "typsphinx",
]

# Required by sphinxcontrib-bibtex -- the build errors without it. Paths are
# relative to this conf.py's directory.
bibtex_bibfiles = ["refs.bib"]

# See the "Fixture de-collision rule" paragraph in the module docstring: the
# target must NOT be "index", or the builder aborts on an output-path
# self-collision against this docname's own content file.
typst_documents = [
    ("index", "master.typ", "Bibtex Footcite Render Gate", "Test Author"),
]
