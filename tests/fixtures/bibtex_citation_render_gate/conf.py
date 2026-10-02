"""Sphinx config for the bibtex citation render-gate fixture (M001/S01, T02).

What this fixture is for: it is the single reusable Sphinx project that every
bibtex render gate in this milestone builds on. S01's gates (T03/T04) assert
against the ``.typ`` files this project emits -- that a ``:cite:p:`` citing
site leaves a citing marker in the body, and that ``.. bibliography::``
renders as ONE Typst grid with each entry appearing exactly once. Later
slices (S02-S06) extend this same project rather than cloning it, so keep
additions additive and keep ``refs.bib`` stable.

Division of labour (MEM002): registration of the ``:cite:*`` roles, the
``cite`` domain and the ``.. bibliography::`` / ``.. footbibliography::``
directives belongs entirely to ``sphinxcontrib.bibtex``. ``typsphinx``
registers nothing in that space -- it only renders the already-resolved
``citation`` / ``reference`` nodes that sphinxcontrib-bibtex leaves in the
doctree (MEM001). Hence both extensions must be loaded, and
``sphinxcontrib.bibtex`` must come first so its domain exists before
typsphinx's builders write anything.

``bibtex_bibfiles`` is required by sphinxcontrib-bibtex: without it the build
errors out before any ``.typ`` is written.

Fixture de-collision rule (measured hazard, same rule the precedent fixture
``tests/fixtures/citation_render_gate/conf.py`` documents): a
``typst_documents`` target MUST differ from its own docname. A target of
``"index"`` for docname ``index`` makes the builder abort with
``typst: 1 output path collision(s): 'index.typ' ... both resolve to the
same output path``, because the two-layer split already writes this
docname's own content file as ``index.typ``. The target is therefore
``master.typ``; a build emits BOTH ``index.typ`` (content) and
``master.typ`` (master).
"""

project = "Bibtex Citation Render Gate"
author = "Test Author"
release = "1.0.0"

# sphinxcontrib.bibtex first: it owns the cite roles, the cite domain and the
# bibliography directives (MEM002). typsphinx only renders the resolved nodes.
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
    ("index", "master.typ", "Bibtex Citation Render Gate", "Test Author"),
]
