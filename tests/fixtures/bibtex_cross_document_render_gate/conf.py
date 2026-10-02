"""Sphinx config for the bibtex CROSS-DOCUMENT render-gate fixture (M001/S05, T01).

What this fixture is for: it is the isolated Sphinx project that S05's gates
assert against -- that citing sites living in INCLUDED chapter documents
resolve to a single ``.. bibliography::`` living in a THIRD, different
document, across Typst's ``#include()`` boundary. The settling evidence is at
compiled-PDF level: a live ``/Link`` annotation on a chapter page whose
destination page is the page holding the bibliography entry, not merely
matching anchor strings in the ``.typ``.

WHY THIS IS A SEPARATE DIRECTORY (do not merge it into
``tests/fixtures/bibtex_citation_render_gate/``). That shared fixture is
single-document by construction, and its gate pins
``content_typ.count("grid(") == 1`` while its ``_split_at_grid`` /
``_body_outside_grid`` helpers both key off THE FIRST ``grid(`` occurrence
(``tests/test_bibtex_citation_render_gate.py``). Adding chapter documents and
a toctree there would break at least those gates and violate R011 ("existing
gates pass unmodified"). The footcite route (S03, MEM025/MEM030) and the
multi-bibliography route (S04) each set this precedent for the same reason: a
new citation route gets its own fixture directory, and the three pre-existing
bibtex fixture directories stay byte-identical.

D012 -- WHY THE BIBLIOGRAPHY LIVES IN ``refs``, NOT IN THE MASTER. The locked
decision puts the single ``.. bibliography::`` in a third sibling document
(``refs.rst``) rather than in ``index.rst``. Putting it in the master would
make the master BOTH the including document and the bibliography host, so a
chapter-to-bibliography link could be satisfied by the master's own page
without ever crossing an ``#include()`` boundary in the direction under test.
With the bibliography in ``refs``, every citing site in ``chapter_one`` /
``chapter_two`` must reach a sibling INCLUDED document -- which is exactly the
cross-document resolution S05 characterises. ``index.rst`` therefore carries
NO ``cite`` site and NO bibliography directive at all: a citing site in the
master would let the same-document (unguarded) path contaminate the
measurement.

Division of labour (MEM002): registration of the ``cite`` roles and of the
``.. bibliography::`` directive belongs entirely to ``sphinxcontrib.bibtex``.
``typsphinx`` registers nothing in that space; it only renders the
already-resolved docutils ``citation`` / ``reference`` nodes that
sphinxcontrib-bibtex leaves in the doctree (MEM010), which is why
cross-document resolution needs no typsphinx change at all. Hence both
extensions are loaded and ``sphinxcontrib.bibtex`` must come FIRST, so its
cite domain exists before typsphinx's builders write.

``bibtex_bibfiles`` is required by sphinxcontrib-bibtex: without it the build
errors out before any ``.typ`` is written.

Fixture de-collision rule (the same measured hazard the other three bibtex
fixtures document): a ``typst_documents`` target MUST differ from its own
docname. A target of ``"index"`` for docname ``index`` makes the builder abort
with ``typst: 1 output path collision(s)``, because the two-layer split
already writes this docname's own content file as ``index.typ``. The target is
therefore ``master.typ``; a build emits BOTH ``index.typ`` (the master's own
content, holding the ``#include()`` calls) and ``master.typ`` (the templated
master). Gates must assert over the per-document content files
(``index.typ``, ``chapter_one.typ``, ``chapter_two.typ``, ``refs.typ``) and
over the compiled ``master.pdf``.
"""

project = "Bibtex Cross Document Render Gate"
author = "Test Author"
release = "1.0.0"

# sphinxcontrib.bibtex first: it owns the cite roles and the bibliography
# directive (MEM002). typsphinx only renders resolved nodes.
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
    ("index", "master.typ", "Bibtex Cross Document Render Gate", "Test Author"),
]
