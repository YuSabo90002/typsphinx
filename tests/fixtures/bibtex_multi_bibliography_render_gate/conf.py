"""Sphinx config for the bibtex MULTI-BIBLIOGRAPHY render-gate fixture (M001/S04, T01).

What this fixture is for: it is the isolated Sphinx project that S04's gates
assert against -- that a document with TWO ``.. bibliography::`` directives,
each scoped by its own ``:filter:`` to a single key, emits TWO independent
Typst grids, each holding exactly its own entry, and compiles to a PDF with
two separate reference lists.

WHY THIS IS A SEPARATE DIRECTORY (do not merge it into
``tests/fixtures/bibtex_citation_render_gate/``). That shared fixture's gate
pins ``content_typ.count("grid(") == 1``
(``tests/test_bibtex_citation_render_gate.py``), and its ``_split_at_grid`` /
``_body_outside_grid`` helpers both key off THE FIRST ``grid(`` occurrence.
A second bibliography directive there would break at least those gates and
violate R011 ("existing gates pass unmodified"). The footcite route set this
precedent for the same reason (MEM025/MEM030): a new citation route gets its
own fixture directory, and the pre-existing fixtures stay byte-identical.

Scope boundary: this project carries NO ``footcite`` site and NO
``.. footbibliography::`` directive -- the footnote route is owned by S03 and
lives in ``tests/fixtures/bibtex_footcite_render_gate/``. Here the contract is
grids, plural.

MEASURED ``:filter:`` SYNTAX TRAP (measured at S04 plan time). Only the
string-on-the-LEFT form works::

    :filter: "Smith2020" % key

``:filter: key == "Smith2020"`` is INVALID: the build still reports success
but every citing site degrades to
``WARNING: could not find bibtex key [bibtex.key_not_found]``.
``:filter: cited % "Smith2020"`` is also invalid
(``expected a string on left side of Mod()``). ``index.rst`` therefore uses
the string-on-left form exclusively; do not "tidy" it into the ``==`` form.

Division of labour (MEM002): registration of the ``cite`` roles and the
``.. bibliography::`` directive -- including all ``:filter:`` evaluation --
belongs entirely to ``sphinxcontrib.bibtex``. ``typsphinx`` registers nothing
in that space; it only renders the already-resolved docutils ``citation`` /
``reference`` nodes that sphinxcontrib-bibtex leaves in the doctree, which is
why two filtered directives yield two grids with no typsphinx change at all
(MEM010). Hence both extensions are loaded and ``sphinxcontrib.bibtex`` must
come FIRST, so its cite domain exists before typsphinx's builders write.

``bibtex_bibfiles`` is required by sphinxcontrib-bibtex: without it the build
errors out before any ``.typ`` is written.

Fixture de-collision rule (same measured hazard the other two bibtex
fixtures document): a ``typst_documents`` target MUST differ from its own
docname. A target of ``"index"`` for docname ``index`` makes the builder abort
with ``typst: 1 output path collision(s)``, because the two-layer split
already writes this docname's own content file as ``index.typ``. The target is
therefore ``master.typ``; a build emits BOTH ``index.typ`` (content) and
``master.typ`` (master). Gates must assert over ``index.typ``.
"""

project = "Bibtex Multi Bibliography Render Gate"
author = "Test Author"
release = "1.0.0"

# sphinxcontrib.bibtex first: it owns the cite roles, the bibliography
# directive, and all :filter: evaluation (MEM002). typsphinx only renders
# resolved nodes.
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
    ("index", "master.typ", "Bibtex Multi Bibliography Render Gate", "Test Author"),
]
