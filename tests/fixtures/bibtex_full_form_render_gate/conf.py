"""Sphinx config for the bibtex FULL-FORM render-gate fixture (M001/S06, T01).

What this fixture is for: it is the single isolated Sphinx project in which the
WHOLE citation surface coexists at once -- parenthetical, textual, multi-key,
the footnote route, TWO ``.. bibliography::`` directives (one chapter-local and
filtered, one corpus-wide and bare), and cross-document resolution across
Typst's ``#include()`` boundary -- compiled end-to-end through the ``typstpdf``
builder. Every prior M001 slice proved exactly ONE route in isolation; nothing
before S06 proved the routes coexist, which is the only thing this fixture is
for.

WHY THIS IS A SEPARATE DIRECTORY (do not merge it into, and do not extend, any
of the four existing bibtex fixtures: ``bibtex_citation_render_gate``,
``bibtex_footcite_render_gate``, ``bibtex_multi_bibliography_render_gate``,
``bibtex_cross_document_render_gate``). Two measured reasons, either one
sufficient:

* R011 requires the four pre-existing bibtex fixture directories to stay
  BYTE-IDENTICAL and their gates to pass unmodified. Any edit there is a
  requirement violation, not a refactor.
* The shared citation gate pins ``content_typ.count("grid(") == 1``, and its
  ``_split_at_grid`` / ``_body_outside_grid`` helpers both key off THE FIRST
  ``grid(`` occurrence (``tests/test_bibtex_citation_render_gate.py``). This
  fixture emits more than one grid by construction, so hosting it there would
  break those gates outright. S03 and S04 each set this same precedent: a new
  citation route gets its own fixture directory.

Division of labour (MEM002): registration of the ``cite`` / ``footcite`` roles
and of the ``bibliography`` / ``footbibliography`` directives belongs entirely
to ``sphinxcontrib.bibtex``. ``typsphinx`` registers nothing in that space; it
only renders the already-resolved docutils ``citation`` / ``reference`` /
``footnote`` nodes that sphinxcontrib-bibtex leaves in the doctree (MEM010),
which is why even the full-form combination needs no typsphinx change at all.
Hence both extensions are loaded and ``sphinxcontrib.bibtex`` must come FIRST,
so its cite domain exists before typsphinx's builders write.

``bibtex_bibfiles`` is required by sphinxcontrib-bibtex: without it the build
errors out before any ``.typ`` is written.

Fixture de-collision rule (the same measured hazard the other four bibtex
fixtures document): a ``typst_documents`` target MUST differ from its own
docname. A target of ``"index"`` for docname ``index`` makes the builder abort
with ``typst: 1 output path collision(s)``, because the two-layer split already
writes this docname's own content file as ``index.typ``. The target is
therefore ``master.typ``; a build emits BOTH ``index.typ`` (the master's own
content, holding the ``#include()`` calls) and ``master.typ`` (the templated
master). Gates must assert over the per-document content files (``index.typ``,
``chapter_one.typ``, ``chapter_two.typ``, ``refs.typ``) and over the compiled
``master.pdf``.

DOCUMENT LAYOUT AND WHY IT IS SPLIT THIS WAY:

* ``index`` -- a PURE toctree master. NO citing site and NO
  bibliography-family directive, so the same-document (unguarded) resolution
  path cannot contaminate the cross-document measurement. This follows the
  D012 precedent S05 locked.
* ``chapter_one`` -- all four inline citing shapes (parenthetical, textual,
  multi-key, and the footnote route twice on one key) plus the only
  ``footbibliography``, followed by filler prose whose sole job is to force a
  page break so the chapter-to-bibliography link measured later CROSSES pages.
* ``chapter_two`` -- one parenthetical site plus the chapter-local FILTERED
  bibliography, which carries a ``keyprefix``.
* ``refs`` -- the corpus-wide BARE bibliography, hosted in a third sibling
  rather than in the master, again per the D012 precedent.

MEASURED CONSTRAINT -- the chapter-local bibliography MUST keep its
``keyprefix``. With both an unprefixed chapter-local bibliography and the
corpus-wide bare bibliography covering the same key, sphinxcontrib-bibtex
reports a duplicate citation id and the strict (``-W``) build FAILS with rc=1.
The prefix is load-bearing, not cosmetic. The same constraint is restated in
``chapter_two.rst`` so an edit there cannot drop it unknowingly.

MEASURED CONSTRAINT -- ``:filter:`` needs the STRING ON THE LEFT of ``%``
(``"Tanaka2019" % key``). The ``key == "..."`` comparison form is a silent
degradation here: measured at T01 time, swapping it drops ``chapter_two``'s
grid from 1 to 0 while the build still exits 0 with ZERO warnings EVEN UNDER
``-W``, because the citing site falls back to the corpus-wide bibliography and
so no ``key_not_found`` warning ever fires. Unlike the ``keyprefix`` constraint
above, this one is NOT caught by strict-build cleanliness, so the gates must
assert ``chapter_two``'s grid count and entry text positively. See
``chapter_two.rst`` for the full measurement.

MEASURED SHAPE AT T01 TIME -- the census below was measured on THIS fixture, by
a strict ``-b typst -E -W`` build (rc=0, zero warnings) and a ``-b typstpdf -E
-W`` build (rc=0). Downstream gates should inherit these numbers rather than
re-deriving them. If a build disagrees, explain the difference; do not quietly
adjust the expectation.

Per-document ``.typ`` census (emitted content files)::

    index         grid=0  footnote=0  query=0
    master        grid=0  footnote=0  query=0
    chapter_one   grid=0  footnote=2  query=4
    chapter_two   grid=1  footnote=0  query=1
    refs          grid=1  footnote=0  query=0

``chapter_one``'s query count is FOUR, not three: the parenthetical site and the
textual site contribute one each, and the single multi-key site contributes TWO
(one per key it names).

Compiled ``master.pdf`` is 4 pages. Entry-title occurrence counts in the
extracted text::

    "A study of things"              total=1  page 4
    "Another work entirely"          total=2  page 4
    "A footnoted proceeding"         total=1  page 3
    "An intentionally uncited note"  total=0  (negative control)

CAREFUL -- "Another work entirely" is TWO, and that is CORRECT, not a doubling
bug. That key is rendered once by ``chapter_two``'s filtered chapter-local
bibliography and once by the corpus-wide bare bibliography in ``refs``. The
D013 exactly-once property is PER ROUTE (per bibliography), not per project, so
a gate must assert 1 occurrence per grid rather than 1 occurrence per document
tree. The two cited-by-one-bibliography-only keys are the ones whose project
total is 1.

"A footnoted proceeding" totalling 1 while ``chapter_one`` carries TWO footnote
citing sites on that key is the reuse-form proof: the second site emits a bare
reuse reference rather than a second definition, so the body is not duplicated.

PAGE CROSSING (why the filler in ``chapter_one`` exists, and the proof it
works): the citing sites land on pages 2-3 while every grid row lands on page 4,
so a chapter-to-bibliography link genuinely CROSSES a page boundary. Measured
``/Link`` annotation counts per page: page 1 = 0, page 2 = 4, page 3 = 7,
page 4 = 1. S05 deferred the page-crossing proof to S06 because its own fixture
could not guarantee this separation; here it is structural.
"""

project = "Bibtex Full Form Render Gate"
author = "Test Author"
release = "1.0.0"

# sphinxcontrib.bibtex first: it owns the cite/footcite roles and the
# bibliography/footbibliography directives (MEM002). typsphinx only renders
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
    ("index", "master.typ", "Bibtex Full Form Render Gate", "Test Author"),
]
