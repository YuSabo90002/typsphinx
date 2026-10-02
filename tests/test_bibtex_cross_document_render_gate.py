"""
M001 / S05 cross-document bibliography render gate, ``.typ`` level.

**What this module pins.** A master document that is a PURE toctree
(``index.rst``) includes three siblings: two chapter documents, each carrying
exactly one ``:cite:*`` site, and a third document (``refs.rst``) holding the
corpus's SINGLE bare ``.. bibliography::``. Per locked decision D012 the
bibliography is deliberately NOT in the master, so a chapter-to-bibliography
link cannot be satisfied by the master's own page without crossing an
``#include()`` boundary in the direction under test. This module asserts the
EMITTED-MARKUP contract of that arrangement:

* every chapter citing marker is a GUARDED cross-document link
  (``context { ... if query(<L>).len() > 0 { link(<L>, ...) } ... }``), while
  the bibliography-hosting document and the master emit no guard at all --
  the cross-document-vs-same-document discriminator;
* the guarded anchor byte-equals a grid row label defined in the TARGET
  document (``refs.typ``), and equals
  ``TypstTranslator._namespace_label("refs", <raw id>)`` -- namespaced by the
  TARGET docname, not by the master's and not root-relative;
* the bibliography renders as exactly ONE grid, in exactly ONE emitted file;
* each cited entry appears once across the whole corpus, the uncited entry
  never (MEM006).

The compiled-PDF settlement -- a live ``/Link`` annotation on a chapter page
whose destination page is the page holding the bibliography entry -- is T03's
subject, not this module's. This is the ``.typ``-level layer S06 consumes as
the cross-document citing-marker contract.

**THIS GATE IS AN HONEST CHARACTERISATION GATE, GREEN ON ARRIVAL, BY DESIGN.**
Measured at plan time and re-measured here against the UNTOUCHED translator,
``tests/fixtures/bibtex_cross_document_render_gate`` already renders exactly
the shape asserted below. ``typsphinx`` needs **ZERO** production code for
cross-document bibliography resolution: ``grep -rc bibtex typsphinx/`` is 0 and
nothing in this slice changes that. This is the FIFTH consecutive bibliography
slice to measure that same conclusion -- MEM010 (S01, the citation route),
MEM023 (S02, the multi-key / textual forms), MEM026 (S03, the footcite route),
D010 (S04, the multi-bibliography route), and now the cross-document route.
``sphinxcontrib.bibtex`` owns the ``cite`` roles and the ``.. bibliography::``
directive and leaves ordinary docutils ``citation`` / ``reference`` nodes
behind; the translator's existing generic cross-document reference machinery
(``_namespace_label`` + ``_label_existence_guard``) renders them with no
awareness that a bibliography is involved.

A conventional RED-first gate therefore CANNOT go RED here without first
breaking production code, and a RED was deliberately NOT manufactured. The repo
precedent for a deliberately green-on-arrival characterisation gate is
``tests/test_typst_elements_pass_through_gate.py``; the three sibling bibtex
gates (``tests/test_bibtex_citation_render_gate.py``,
``tests/test_bibtex_footcite_render_gate.py``,
``tests/test_bibtex_multi_bibliography_render_gate.py``) are the same shape.
Every assertion below was instead sensitivity-probed against a MUTATED
THROWAWAY COPY of the fixture (RED-then-GREEN) -- see the "Sensitivity probes"
note at the foot of this docstring.

**D011 -- "never a silently dead link" is discharged POSITIVELY here, and the
guard's degradation branch is deliberately NOT asserted.** The requirement is
settled by the positive pair of facts this module does assert: every
cross-document citing site IS guarded, and the anchor it guards on DOES exist
as a grid row label in the target document. The obvious way to try to exercise
the ``else { __tsx_body }`` plain-text degradation branch -- delete the
``.. bibliography::`` so the anchor disappears -- does NOT reach it: the
mutation is intercepted UPSTREAM by ``sphinxcontrib.bibtex``, which emits
``bibtex.key_not_found`` and leaves the citing sites unresolved, so the chapter
documents emit ZERO ``query(`` guards rather than a guard whose query fails.
``_label_existence_guard``'s degradation branch is therefore not reachable from
that mutation at all, and no test here asserts it. (Measured; the probe is
recorded in T02's summary.) The degradation branch has its own owner:
``tests/test_citation_degradation_gate.py``.

**Availability flags and skip discipline.** ``sphinxcontrib.bibtex`` backs
everything in this module; ``typst`` / ``pypdf`` back T03's compiled-PDF half
only. Each is probed at module level so a machine lacking one SKIPS rather than
ERRORS. The two builds here are keyed by ``-b typst``, never ``-b typstpdf``,
so the whole ``.typ`` half still runs when typst-py / pypdf are absent. All
three were confirmed PRESENT at plan time, so a skip in CI means a real
environment regression, not an expected state.

**Nothing is transcribed.** Every subject is parsed out of the fixture's own
inputs or computed by the translator's own helper:

* entry titles and authors from ``refs.bib``;
* citing sites, the toctree and the bibliography directive from the ``.rst``
  files, which also decides WHICH document is the master and WHICH hosts the
  bibliography -- no docname role is hard-coded;
* the expected anchor from ``TypstTranslator._namespace_label`` via
  :func:`_namespace_prefix`, so NO namespaced-id literal appears anywhere in
  this file -- not even in prose. Sphinx assigns those ids in toctree order and
  they shift freely, and the slice's verification greps this very file to prove
  none was transcribed.

Each parse carries a vacuous-pass guard naming its subject, so a fixture edit
fails LOUDLY here instead of degrading every count below into a no-op.

**Resolve-at-most-once discipline (MEM009).** This module makes ZERO
``env.get_and_resolve_doctree()`` calls -- it needs none, because the labels and
anchors it compares are read out of the emitted ``.typ`` and recomputed with
``_namespace_label``. Consequently no expectation anywhere here is derived from
a citation node's child count, which is exactly the upstream double-resolve
artifact MEM009 records as unfixable from ``typsphinx`` and only avoidable.

**Locale.** The strict ``-W`` build runs under ``LC_ALL=C``: this machine's
``LANG`` is Japanese and Sphinx localises its output. The assertions use the
exit status plus the absence of the (never-localised) warning CODE
``bibtex.key_not_found``.

**Sensitivity probes.** Every one of the eight tests below was driven RED at its
OWN assertion body and then confirmed GREEN again. Because this gate is green on
arrival, that required probing from two directions, and the split is worth
recording: the FIXTURE-level mutations the slice plan names are mostly
intercepted by ``cross_doc_fixture_data``'s parse guards -- which is those
guards' job, and each names its subject -- so the final assertions' own teeth
were proven with temporary, immediately-reverted PRODUCTION mutations instead.

Fixture-level mutations (each RED; the first two and the fourth RED at the parse
guard rather than at a final assertion):

* moving the ``.. bibliography::`` from ``refs.rst`` into ``chapter_one.rst``,
  making chapter one's resolution SAME-document;
* dropping a chapter's citing site;
* turning the textual ``:cite:t:`` site into a parenthetical ``:cite:p:`` one
  (RED at :func:`_textual_docname`, naming the subject);
* adding the ``:all:`` option to the bibliography;
* deleting the bibliography outright -- the D011 probe, which also produced the
  measurement recorded above: the build still exits 0, emits
  ``bibtex.key_not_found`` twice, and leaves BOTH chapters with ZERO ``query(``
  guards, so ``_label_existence_guard``'s degradation branch is unreachable
  from it.

Production mutations, each reverted and the revert verified with ``git diff
--quiet -- typsphinx/``, naming the test each one turned RED:

* emit a bare ``link()`` instead of the existence guard -> the guarded-link,
  anchor-equality and textual-form tests;
* stop namespacing labels by docname -> the anchor-equality test (its D012
  target-namespace assertion specifically);
* guard a citation row's own definition anchor -> the
  same-document-emits-no-guard test;
* re-walk each citation's body children on depart, i.e. MEM009's duplication
  shape reaching the write pass -> the appears-exactly-once test;
* append a stray ``grid()`` to every document that has none -> the
  one-grid-in-the-target-document-only test.

The compiled-PDF half (T03) was probed the same way, and each of its four
tests was driven RED at its OWN assertion body -- not merely at a parse guard:

* the guard emitted so it NEVER links (always degrades to plain body) -> the
  D-13 verdict test's vacuous-pass guard fires, reporting that the proof found
  no citing-marker annotation at all, and the not-a-self-link test with it;
* every guarded link pinned to ONE shared anchor -> the D-13 verdict test's
  pairwise-distinct-destinations assertion;
* the fixture's toctree reordered so ``refs`` precedes the chapters (a
  fixture-level probe that passes every parse guard) -> the not-a-self-link
  test, at ``dest_y < rect_bottom``: the destinations then sit ABOVE their own
  markers;
* citation bodies re-walked on depart, MEM009's duplication shape reaching the
  write pass -> the compiled-PDF appears-exactly-once test;
* the opening bracket stripped from every emitted ``text()`` -> the textual
  surname-outside-bracket test, whose count drops to 0.

The plan-named fixture probe -- moving the ``.. bibliography::`` into
``chapter_one.rst`` so resolution becomes SAME-document -- also goes RED, but
at ``cross_doc_fixture_data``'s zero-citing-sites-in-the-host guard rather than
at a PDF assertion, which is that guard's job. Two mutations that look like
probes are NOT: writing the textual chapter's author surname-first in
``refs.bib`` leaves the textual test GREEN (bibtex and
:func:`_author_surname` both take the last whitespace-separated word, so both
sides move together), and nothing here relies on page INDEX distinctness --
see the DEVIATION note above
:class:`TestCompiledPdfResolvesCrossDocumentCitingMarkers`.

No probe is part of the committed tree: fixture mutations were applied in place
over a tar backup and production mutations over a file copy, both restored
byte-identically and verified with ``git diff --quiet`` before this module was
committed.
"""

import io
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

from typsphinx.translator import TypstTranslator

try:
    import sphinxcontrib.bibtex  # noqa: F401

    BIBTEX_AVAILABLE = True
except ImportError:
    BIBTEX_AVAILABLE = False

# typst-py and pypdf back T03's compiled-PDF half ONLY. Probed here so the
# flags exist for that task's build fixture; nothing in THIS task's .typ-level
# assertions needs either, which is why both builds below are -b typst and the
# whole module still runs on a machine without them.
try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

try:
    import pypdf  # noqa: F401

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

PDF_DEPS_AVAILABLE = BIBTEX_AVAILABLE and TYPST_AVAILABLE and PYPDF_AVAILABLE


# The bibtex warning CODE that signals a citing site did not resolve. A CODE,
# not a message: Sphinx localises the message text but never the bracketed
# code, so this is locale-independent by construction. Its presence would mean
# this gate is characterising a document whose citations silently stopped
# resolving -- i.e. that the characterisation describes a typo (MEM036).
BIBTEX_KEY_NOT_FOUND_CODE = "bibtex.key_not_found"

# The identifier ``_label_existence_guard`` binds in the guard it emits. Fixed
# project-wide by that method's own docstring, which is why asserting on it
# here is a contract check and not a spelling guess.
GUARD_BODY_IDENT = "__tsx_body"


# ---------------------------------------------------------------------------
# Fixture-authored data, parsed out of the fixture rather than transcribed.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def cross_doc_gate_dir():
    """Return the path to the bibtex_cross_document_render_gate fixture."""
    return Path(__file__).parent / "fixtures" / "bibtex_cross_document_render_gate"


def _parse_bib_field(bib_text: str, field: str) -> dict[str, str]:
    """
    Return ``{entry_key: value}`` for one quoted ``refs.bib`` field.

    ``%``-comment lines are stripped first: this fixture's ``refs.bib`` carries
    a long header comment block that itself names entry keys and titles, which
    would otherwise be picked up as if they were entries. Same implementation
    as the sibling bibtex gates', deliberately duplicated rather than imported
    -- these gate modules are independent characterisation records and must not
    be able to break each other.
    """
    without_comments = "\n".join(
        line for line in bib_text.splitlines() if not line.lstrip().startswith("%")
    )
    values: dict[str, str] = {}
    for key, body in re.findall(
        r"@\w+\{\s*([^,\s]+)\s*,(.*?)\n\}", without_comments, re.S
    ):
        match = re.search(re.escape(field) + r'\s*=\s*"([^"]+)"', body)
        if match:
            values[key] = match.group(1)
    return values


def _parse_citing_sites(rst_text: str) -> list[str]:
    """
    Return the raw role argument of every ``:cite:*:`` site in one ``.rst``, in
    document order -- one entry per citing SITE.

    Regexes the RAW rst, so a FULLY-COLONISED role name written inside an rst
    comment would also count as a site (MEM025's trap). Every comment in this
    fixture therefore writes role names un-colonised (``cite:p``, not
    ``:cite:p:``), and :func:`cross_doc_fixture_data`'s exact per-document
    site-count guards are what catch it if that ever slips.

    Note the other half of MEM025: this pattern does NOT match ``:footcite:``,
    because ``[a-z]*`` cannot span the ``:`` that would have to follow
    ``:cite``. That is harmless here -- the fixture has no footcite site, and
    the footnote route is S03's -- but it is why the guards assert the parsed
    COUNTS rather than trusting the regex to be exhaustive.
    """
    return re.findall(r":cite:[a-z]*:`([^`]+)`", rst_text)


def _parse_bibliography_directives(rst_text: str) -> list[str]:
    """
    Return one entry per ``.. bibliography::`` directive in one ``.rst``: the
    directive's inline argument plus its indented option block, concatenated.

    An empty string therefore means a BARE directive, which is what this
    fixture's ``refs.rst`` mandates (no ``:filter:``, no ``:keyprefix:``, no
    ``:all:``). The returned text is what :func:`cross_doc_fixture_data`'s
    guard asserts is empty, so adding ``:all:`` -- which would surface the
    deliberately uncited entry and void MEM006's zero-count assertion -- fails
    loudly here rather than silently changing what the gate measures.

    Anchored at column 0 with ``re.MULTILINE`` on purpose: every rst comment in
    this fixture is INDENTED, so an indented prose mention of the directive
    cannot be miscounted as a real one. The trailing ``(?:\\n|$)`` tolerates the
    directive being the file's last line with no trailing newline.
    """
    return [
        (argument + options).strip()
        for argument, options in re.findall(
            r"^\.\. bibliography::[ \t]*([^\n]*)(?:\n|$)"
            r"((?:[ \t]+:[a-z]+:[^\n]*(?:\n|$))*)",
            rst_text,
            re.M,
        )
    ]


def _parse_toctree_entries(rst_text: str) -> list[str]:
    """
    Return the docnames listed in the single ``.. toctree::`` of one ``.rst``,
    in document order.

    Anchored at column 0 for the same reason as
    :func:`_parse_bibliography_directives`. The entry lines are the indented
    non-option, non-blank lines following the directive; parsing stops at the
    first dedent. Document ORDER matters and is preserved: Sphinx assigns the
    citation anchor ids this gate matches in assignment order, which follows
    the toctree.
    """
    match = re.search(
        r"^\.\. toctree::[ \t]*\n((?:[ \t]+[^\n]*\n|\n)*)", rst_text, re.M
    )
    if not match:
        return []
    entries: list[str] = []
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(":"):
            continue
        entries.append(stripped)
    return entries


def _namespace_prefix(docname: str) -> str:
    """
    Return exactly what ``TypstTranslator._namespace_label`` prepends to a raw
    docutils id for ``docname``, MEASURED by calling that helper rather than
    assumed.

    The measurement passes an unmistakable probe id through the real helper and
    strips the probe back off, so the returned prefix is the translator's own
    namespacing scheme by construction. This is how the module expresses D012's
    property -- "the chapters' anchors are namespaced by the TARGET document,
    not by the master" -- without a single ``refs:`` / ``index:`` literal
    anywhere in this file, and without hard-coding the ``docname:id`` SHAPE
    either: a scheme change to, say, ``docname__id`` would be picked up here
    automatically.

    Passing the class itself as ``self`` is safe and is the established idiom
    across this repo's citation gates: ``_namespace_label`` touches no instance
    state, only its two arguments and the module-level sanitizer.
    """
    probe = "tsxprobeid"
    namespaced = TypstTranslator._namespace_label(TypstTranslator, docname, probe)
    assert namespaced.endswith(probe), (
        f"TypstTranslator._namespace_label({docname!r}, {probe!r}) returned "
        f"{namespaced!r}, which does not end with the probe id. This module "
        "derives the expected namespace by stripping the probe back off, so a "
        "helper that now rewrites the id part needs that derivation updated "
        "deliberately rather than silently mis-measured."
    )
    return namespaced[: -len(probe)]


@dataclass
class CrossDocFixtureData:
    """
    What the fixture itself authors, parsed out of ``refs.bib`` and the
    ``.rst`` files -- never transcribed into this module.

    The document ROLES are derived too, not assumed: ``master_docname`` is the
    one document carrying a ``.. toctree::``, ``bibliography_docname`` the one
    carrying the ``.. bibliography::``, and ``chapter_docnames`` the remaining
    toctree entries -- which is how D012's arrangement (bibliography in a
    sibling, NOT in the master) is checked rather than taken on trust.
    """

    titles: dict[str, str]
    authors: dict[str, str]
    master_docname: str
    bibliography_docname: str
    chapter_docnames: list[str]
    citing_sites: dict[str, list[str]]
    rst_text: dict[str, str]

    @property
    def cited_keys(self) -> list[str]:
        """Every bibtex key some chapter cites, in chapter order."""
        return [self.citing_sites[docname][0] for docname in self.chapter_docnames]

    @property
    def uncited_keys(self) -> list[str]:
        """Every ``refs.bib`` key no citing site names."""
        return [key for key in self.titles if key not in set(self.cited_keys)]

    def cited_key_of(self, docname: str) -> str:
        """The single bibtex key chapter ``docname`` cites."""
        return self.citing_sites[docname][0]


@pytest.fixture(scope="module")
def cross_doc_fixture_data(cross_doc_gate_dir):
    """
    Parse the fixture into the data every assertion compares against, with
    vacuous-pass guards in the S01 style so a fixture edit that breaks a parse
    fails LOUDLY here rather than quietly degrading the counts below.

    The guards are deliberately EXACT (three bib entries, three toctree
    entries, one bibliography-hosting document, two chapters with exactly one
    citing site each, one uncited key, a master with zero citing sites and no
    bibliography). This gate's whole subject is that specific arrangement, and
    a slice that changes it must update these numbers deliberately.
    """
    bib_text = (cross_doc_gate_dir / "refs.bib").read_text(encoding="utf-8")
    titles = _parse_bib_field(bib_text, "title")
    authors = _parse_bib_field(bib_text, "author")

    assert len(titles) == 3, (
        "Vacuous-pass guard: expected exactly THREE entries parsed out of the "
        f"fixture's refs.bib (two cited, one deliberately uncited) but parsed "
        f"{sorted(titles)}. Did refs.bib's entry formatting change? With no "
        "entries every title count below would compare against nothing."
    )
    assert set(authors) == set(titles), (
        "Vacuous-pass guard: every refs.bib entry must yield BOTH a title and "
        f"an author (titles: {sorted(titles)}, authors: {sorted(authors)}). "
        "The textual-form assertion needs the author field of the key its "
        "chapter cites."
    )

    rst_paths = sorted(cross_doc_gate_dir.glob("*.rst"))
    assert len(rst_paths) == 4, (
        "Vacuous-pass guard: expected FOUR .rst documents in the fixture (a "
        "master, two chapters and the bibliography host) but found "
        f"{[path.name for path in rst_paths]}."
    )
    rst_text = {path.stem: path.read_text(encoding="utf-8") for path in rst_paths}

    citing_sites = {
        docname: _parse_citing_sites(text) for docname, text in rst_text.items()
    }
    bibliographies = {
        docname: _parse_bibliography_directives(text)
        for docname, text in rst_text.items()
    }
    toctrees = {
        docname: _parse_toctree_entries(text) for docname, text in rst_text.items()
    }

    # (a) The master is the one document with a toctree, and it is the only one.
    masters = [docname for docname, entries in toctrees.items() if entries]
    assert len(masters) == 1, (
        "Exactly ONE document must carry the toctree that flattens this corpus "
        f"into one Typst master, but toctree entries were parsed from {masters}."
    )
    master_docname = masters[0]
    toctree_entries = toctrees[master_docname]
    assert len(toctree_entries) == 3, (
        f"The master ({master_docname}.rst) must include exactly THREE "
        "siblings -- two chapters plus the bibliography host -- but its "
        f"toctree lists {toctree_entries}. The emitted anchor ids this gate "
        "matches are toctree-assignment-order dependent, so a changed toctree "
        "must be a deliberate edit."
    )
    for entry in toctree_entries:
        assert entry in rst_text, (
            f"The master's toctree names {entry!r}, for which the fixture has "
            f"no {entry}.rst (documents found: {sorted(rst_text)})."
        )

    # (b) The bibliography lives in exactly one document, and -- D012 -- that
    # document is NOT the master. This is the structural premise of the whole
    # slice: if it were the master, a chapter-to-bibliography link could be
    # satisfied without crossing an #include() boundary.
    hosts = [docname for docname, found in bibliographies.items() if found]
    assert len(hosts) == 1, (
        "Exactly ONE document must carry a .. bibliography:: directive, but "
        f"directives were parsed from {hosts}. Two directives would make this "
        "the multi-bibliography route, which is S04's fixture; zero would "
        "leave the chapters' citing sites with nothing to resolve to."
    )
    bibliography_docname = hosts[0]
    assert len(bibliographies[bibliography_docname]) == 1, (
        f"{bibliography_docname}.rst must carry exactly ONE .. bibliography:: "
        f"directive but carries {len(bibliographies[bibliography_docname])}."
    )
    assert bibliographies[bibliography_docname][0] == "", (
        "D012/MEM006: the single .. bibliography:: must stay BARE (no :filter:, "
        "no :keyprefix:, no :all:), but it carries "
        f"{bibliographies[bibliography_docname][0]!r}. A bare directive renders "
        "ONLY cited entries, which is what gives the uncited-entry zero-count "
        "assertion a subject; :all: would surface that entry and void it."
    )
    assert bibliography_docname != master_docname, (
        "D012: the single bibliography must live in a SIBLING included "
        f"document, not in the master ({master_docname}). Hosting it in the "
        "master would let a chapter-to-bibliography link be satisfied by the "
        "master's own page without crossing an #include() boundary in the "
        "direction this slice measures -- the cross-document claim would "
        "become untestable."
    )
    assert bibliography_docname in toctree_entries, (
        f"The bibliography host {bibliography_docname!r} must itself be a "
        f"toctree entry of the master, but the toctree lists {toctree_entries}. "
        "Otherwise it is never #include()d and no grid reaches the master."
    )

    # (c) The master contributes no citing site: one there would let the
    # same-document (unguarded) path contaminate the measurement.
    assert citing_sites[master_docname] == [], (
        f"The master ({master_docname}.rst) must carry ZERO citing sites, but "
        f"{citing_sites[master_docname]} were parsed. A citing site in the "
        "master resolves SAME-document and would emit an unguarded link, "
        "contaminating the cross-vs-same-document discriminator below. (NOTE: "
        "this regexes the RAW rst, so a fully-colonised cite role written "
        "inside an rst comment also counts -- MEM025.)"
    )

    # (d) The bibliography host contributes no citing site either, so every
    # grid row it emits originates in a DIFFERENT document.
    assert citing_sites[bibliography_docname] == [], (
        f"The bibliography host ({bibliography_docname}.rst) must carry ZERO "
        f"citing sites, but {citing_sites[bibliography_docname]} were parsed. "
        "Its grid rows must originate exclusively in the chapter documents, "
        "or 'this row was reached from another document' stops being true."
    )

    # (e) The chapters: the toctree entries that are not the bibliography host.
    chapter_docnames = [
        entry for entry in toctree_entries if entry != bibliography_docname
    ]
    assert len(chapter_docnames) == 2, (
        "This gate locks a TWO-chapter corpus so the cross-document route is "
        "characterised for two inline citing shapes (parenthetical and "
        f"textual), but the non-bibliography toctree entries are "
        f"{chapter_docnames}."
    )
    for docname in chapter_docnames:
        sites = citing_sites[docname]
        assert len(sites) == 1, (
            f"Chapter {docname}.rst must carry EXACTLY ONE citing site -- the "
            "per-chapter 'one query( guard' count below is asserted against "
            f"this number -- but {sites} were parsed. (NOTE: this regexes the "
            "RAW rst, so a fully-colonised cite role written inside an rst "
            "comment also counts -- MEM025.)"
        )
        assert "," not in sites[0], (
            f"Chapter {docname}'s citing site {sites[0]!r} names several keys. "
            "This gate's per-chapter attribution assumes ONE key per chapter; "
            "the multi-key FORM is owned by S02's gate."
        )
        assert sites[0] in titles, (
            f"Chapter {docname} cites {sites[0]!r}, for which refs.bib has no "
            f"entry (known entries: {sorted(titles)})."
        )

    cited_keys = [citing_sites[docname][0] for docname in chapter_docnames]
    assert len(set(cited_keys)) == 2, (
        "The two chapters must cite two DISTINCT keys, otherwise 'each "
        "chapter's link lands on the row for the key IT cites' is untestable: "
        f"parsed {cited_keys}."
    )
    distinct_titles = {titles[key] for key in cited_keys}
    assert len(distinct_titles) == 2, (
        "The cited entries must have DISTINCT titles, otherwise an 'appears "
        "exactly once' count for one entry can be satisfied by the other: "
        f"{[titles[key] for key in cited_keys]}."
    )
    for key in cited_keys:
        assert titles[key].strip(), (
            f"The cited entry {key!r} has an empty title in refs.bib, so "
            "counting its occurrences would be meaningless."
        )

    uncited = [key for key in titles if key not in set(cited_keys)]
    assert len(uncited) == 1, (
        "The fixture keeps EXACTLY ONE deliberately uncited refs.bib entry so "
        "MEM006's zero-count assertion has a subject and cannot degrade into a "
        f"no-op, but the uncited set is {uncited}. If a later slice needs "
        "another CITED entry, APPEND a new uncited one rather than weakening "
        "this guard."
    )
    assert titles[uncited[0]] not in distinct_titles, (
        f"The uncited entry's title {titles[uncited[0]]!r} collides with a "
        "cited entry's, so its zero-count assertion could never hold."
    )

    return CrossDocFixtureData(
        titles=titles,
        authors=authors,
        master_docname=master_docname,
        bibliography_docname=bibliography_docname,
        chapter_docnames=chapter_docnames,
        citing_sites=citing_sites,
        rst_text=rst_text,
    )


# ---------------------------------------------------------------------------
# Builds. Two flavours, each running EXACTLY ONCE per module in its own build
# directory so no incremental-rebuild cache can let one mask the other:
#   * -b typst          -> every emitted-markup assertion below
#   * -b typst -E -W    -> the strict/clean-build assertion, under LC_ALL=C
# Both are -b typst rather than -b typstpdf on purpose, so this whole half runs
# on a machine without typst-py; T03's compiled-PDF half gets its own
# typstpdf-keyed build behind PDF_DEPS_AVAILABLE.
# ---------------------------------------------------------------------------


def _run_sphinx_build(
    source_dir: Path,
    build_dir: Path,
    extra_args: tuple[str, ...] = (),
    env: dict[str, str] | None = None,
    buildername: str = "typst",
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <buildername>`` (plus ``extra_args``) as a
    subprocess.

    Invoked as ``sys.executable -m sphinx`` -- never ``uv run sphinx-build`` and
    never a bare ``sphinx-build`` -- which is the NixOS PATH-shadowing hazard
    every render-gate module in this project restates. Under ``uv run`` this
    resolves to the current venv's python, so ``import typsphinx`` binds to this
    checkout's (or worktree's) editable copy rather than another tree's.
    """
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            buildername,
            *extra_args,
            str(source_dir),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
        env=env,
    )


@dataclass
class CrossDocGateBuild:
    """One real build of the cross-document fixture, captured once."""

    result: subprocess.CompletedProcess
    build_dir: Path

    def read_typ(self, docname: str) -> str:
        """
        Return the text of one emitted per-document content ``.typ``, failing
        with an ``AssertionError`` that names the missing artifact and quotes
        the build's own output rather than letting a caller hit
        ``FileNotFoundError``.
        """
        path = self.build_dir / f"{docname}.typ"
        if not path.exists():
            raise AssertionError(
                f"{docname}.typ was never emitted (missing artifact) -- build "
                f"returncode={self.result.returncode}\n"
                f"stdout: {self.result.stdout}\nstderr: {self.result.stderr}"
            )
        return path.read_text(encoding="utf-8")

    def emitted_typ_files(self) -> dict[str, str]:
        """
        Return ``{filename: text}`` for every ``.typ`` emitted at the build
        root, in sorted order.

        Deliberately NON-recursive: the builder also copies the template bundle
        to ``_template/<key>/``, whose own ``.typ`` files are not output of this
        corpus and must not be counted by the corpus-wide assertions.
        """
        return {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(self.build_dir.glob("*.typ"))
        }

    @property
    def output(self) -> str:
        """The build's combined stdout and stderr."""
        return f"{self.result.stdout}\n{self.result.stderr}"


@pytest.fixture(scope="module")
def cross_doc_gate_build(cross_doc_gate_dir, tmp_path_factory):
    """
    Build the fixture with ``-b typst`` EXACTLY ONCE for the whole module.

    Asserts a clean exit here: this gate is green on arrival, so a non-zero
    build IS the regression it exists to catch, and reporting it once in the
    fixture is clearer than letting it surface as several unrelated assertion
    failures.
    """
    build_dir = tmp_path_factory.mktemp("cross_doc_gate_typ") / "_build"
    result = _run_sphinx_build(cross_doc_gate_dir, build_dir)
    assert result.returncode == 0, (
        "sphinx-build -b typst over the cross-document bibliography fixture "
        "must succeed (this gate locks measured-working behaviour and is green "
        f"on arrival)\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    return CrossDocGateBuild(result=result, build_dir=build_dir)


@pytest.fixture(scope="module")
def cross_doc_gate_strict_build(cross_doc_gate_dir, tmp_path_factory):
    """
    Build the fixture with ``-b typst -E -W`` EXACTLY ONCE, in its OWN build
    directory, under ``LC_ALL=C``.

    ``-E`` discards any saved environment so the warnings a cached build would
    not re-emit are actually produced; ``-W`` turns every warning into an
    error. ``LC_ALL=C`` because this project's dev shell passes the host's
    Japanese ``LANG`` through and Sphinx localises its output -- the bibtex
    warning CODE is never localised, but forcing the locale keeps the
    surrounding text honest too.

    Deliberately does NOT assert the exit code: the strict test owns that, so a
    regression is reported as a named test failure rather than as a fixture
    error.
    """
    build_dir = tmp_path_factory.mktemp("cross_doc_gate_typ_strict") / "_build"
    env = dict(os.environ)
    env["LC_ALL"] = "C"
    env.pop("LANG", None)
    env.pop("LANGUAGE", None)
    result = _run_sphinx_build(
        cross_doc_gate_dir, build_dir, extra_args=("-E", "-W"), env=env
    )
    return CrossDocGateBuild(result=result, build_dir=build_dir)


# ---------------------------------------------------------------------------
# Emitted-markup parsing. Per-grid and per-ROW, never document-wide, wherever
# the content of a particular region is what carries the claim (MEM035).
# ---------------------------------------------------------------------------


def _grid_block_spans(typ_text: str) -> list[tuple[int, int]]:
    """
    Return ``(start, end)`` offsets of every balanced ``grid(...)`` call.

    Parenthesis matching is string-aware: a grid row body legitimately contains
    ``text("(")``-style literals, and a naive depth count would unbalance on
    them. An unbalanced call raises a clear ``AssertionError`` rather than
    returning a truncated span, because a silently short span would scope a
    per-grid assertion to the wrong region.
    """
    spans: list[tuple[int, int]] = []
    search_from = 0
    while True:
        start = typ_text.find("grid(", search_from)
        if start == -1:
            return spans

        index = start + len("grid(")
        depth = 1
        in_string = False
        end = -1
        while index < len(typ_text):
            char = typ_text[index]
            if in_string:
                if char == "\\":
                    index += 2
                    continue
                if char == '"':
                    in_string = False
            elif char == '"':
                in_string = True
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    end = index + 1
                    break
            index += 1

        if end == -1:
            raise AssertionError(
                "A grid( call starting at offset "
                f"{start} is not parenthesis-balanced, so its region could not "
                f"be bounded. Depth reached {depth} at end of file:\n"
                f"{typ_text[start:]}"
            )
        spans.append((start, end))
        search_from = end


def _iter_grid_blocks(typ_text: str) -> list[str]:
    """
    Return each balanced ``grid(...)`` call's text as its OWN string, in
    document order.

    This is the per-region helper MEM035 mandates: a document-wide count cannot
    distinguish "one grid holding two rows" from "two grids holding one row
    each", and this slice's claim is specifically the former.
    """
    return [typ_text[start:end] for start, end in _grid_block_spans(typ_text)]


# One bibliography row's label cell, measured shape (ids elided -- they are
# derived, never typed)::
#
#     [#{text("[") + text("<label>") + text("]")} <docname:id>]
#
# i.e. the bracketed pybtex label built by string concatenation, followed by the
# Typst label the row is anchored at.
_GRID_ROW_LABEL_CELL_RE = re.compile(
    r'text\("\["\)\s*\+\s*text\("([^"]+)"\)\s*\+\s*text\("\]"\)\}\s*<([^>]+)>'
)


@dataclass
class GridRow:
    """One parsed bibliography row: its pybtex label, Typst anchor, and body."""

    label: str
    anchor: str
    body: str


def _parse_grid_rows(grid_region: str) -> list[GridRow]:
    """
    Return every row of ONE grid block as a :class:`GridRow`, in document order.

    The ``body`` of row *i* is the text between the end of row *i*'s label cell
    and the start of row *i + 1*'s (or the end of the grid) -- i.e. the rendered
    entry that row's anchor actually names. Parsing bodies per ROW, not per
    grid, is what lets this module assert the load-bearing attribution claim:
    that a chapter's guarded link lands on the row for the key THAT chapter
    cites, rather than merely on some row of the right bibliography.
    """
    matches = list(_GRID_ROW_LABEL_CELL_RE.finditer(grid_region))
    rows: list[GridRow] = []
    for position, match in enumerate(matches):
        body_end = (
            matches[position + 1].start()
            if position + 1 < len(matches)
            else len(grid_region)
        )
        rows.append(
            GridRow(
                label=match.group(1),
                anchor=match.group(2),
                body=grid_region[match.end() : body_end],
            )
        )
    return rows


def _guarded_anchors(typ_text: str) -> list[str]:
    """
    Return the anchor of every GUARDED cross-document link in one ``.typ``, in
    document order.

    The subject is ``_label_existence_guard``'s emitted shape: a ``context``
    block that binds the reference body to ``__tsx_body``, then links only
    ``if query(<L>).len() > 0``. Matching the whole guard as ONE contiguous
    pattern -- rather than collecting ``query(`` and ``link(`` hits separately
    -- is what makes "this site IS guarded" a real claim: it pins that the
    SAME label appears in the query and in the link, and that the fallback is
    the plain body. A pair of independent membership checks would also pass for
    a bare link next to an unrelated query.
    """
    pattern = re.compile(
        r"context\s*\{\s*let\s+"
        + re.escape(GUARD_BODY_IDENT)
        + r"\s*=\s*\[#\{.*?\}\];\s*"
        r"if\s+query\(<([^>]+)>\)\.len\(\)\s*>\s*0\s*\{\s*"
        r"link\(<\1>,\s*" + re.escape(GUARD_BODY_IDENT) + r"\)\s*\}\s*"
        r"else\s*\{\s*" + re.escape(GUARD_BODY_IDENT) + r"\s*\}\s*\}",
        re.S,
    )
    return [match.group(1) for match in pattern.finditer(typ_text)]


@dataclass
class TargetGrid:
    """The single bibliography grid, parsed out of the TARGET document."""

    docname: str
    rows: list[GridRow]

    def row_for_anchor(self, anchor: str) -> GridRow | None:
        """The row anchored at ``anchor``, or ``None`` if no row is."""
        return next((row for row in self.rows if row.anchor == anchor), None)

    @property
    def anchors(self) -> list[str]:
        """Every row anchor, in document order."""
        return [row.anchor for row in self.rows]


@pytest.fixture(scope="module")
def target_grid(cross_doc_gate_build, cross_doc_fixture_data) -> TargetGrid:
    """
    Parse the single bibliography grid out of the TARGET document's emitted
    ``.typ``, with vacuous-pass guards so a failure to parse rows cannot make
    the anchor-equality assertions pass against an empty row set.
    """
    docname = cross_doc_fixture_data.bibliography_docname
    blocks = _iter_grid_blocks(cross_doc_gate_build.read_typ(docname))
    assert len(blocks) == 1, (
        f"The target document {docname}.typ must carry exactly ONE grid( call "
        f"-- its single bare bibliography -- but carries {len(blocks)}."
    )
    rows = _parse_grid_rows(blocks[0])
    assert len(rows) == len(cross_doc_fixture_data.cited_keys), (
        "Vacuous-pass guard: parsed "
        f"{len(rows)} row(s) out of {docname}.typ's grid but the chapters cite "
        f"{len(cross_doc_fixture_data.cited_keys)} key(s), and a bare "
        ".. bibliography:: renders exactly the cited ones (MEM006). Parsed "
        f"labels: {[row.label for row in rows]}. If zero, the row label-cell "
        "shape changed and every anchor comparison below would compare "
        "against nothing."
    )
    assert len({row.anchor for row in rows}) == len(rows), (
        "Two bibliography rows share one Typst anchor, so attributing a "
        f"chapter's link to a row is ambiguous: {[row.anchor for row in rows]}."
    )
    return TargetGrid(docname=docname, rows=rows)


# ---------------------------------------------------------------------------
# The gate.
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not BIBTEX_AVAILABLE,
    reason="sphinxcontrib-bibtex is required for the cross-document bibliography gate",
)
class TestCrossDocumentCitingMarkersAreGuarded:
    """
    The cross-document-vs-same-document discriminator: a citing site whose
    bibliography lives in ANOTHER document emits a guarded link, and a document
    with no cross-document citing site emits no guard at all.
    """

    def test_each_chapter_citing_site_is_a_guarded_cross_document_link(
        self, cross_doc_gate_build, cross_doc_fixture_data
    ):
        """
        Each chapter's emitted ``.typ`` carries exactly as many ``query(``
        guards as its ``.rst`` has citing sites (measured: one each), and each
        of those guards matches ``_label_existence_guard``'s full contiguous
        shape.

        Counts ``query(``, deliberately NOT ``context {``: the master emits one
        unrelated ``context {`` for its toctree ``#include()`` block, and each
        chapter's own guard contributes one too, so a ``context {`` count would
        conflate the guard with the include machinery. ``query(`` is emitted by
        ``_label_existence_guard`` and by nothing else in this corpus.
        """
        for docname in cross_doc_fixture_data.chapter_docnames:
            text = cross_doc_gate_build.read_typ(docname)
            expected = len(cross_doc_fixture_data.citing_sites[docname])
            assert text.count("query(") == expected, (
                f"Chapter {docname}.typ must carry exactly {expected} "
                "query( guard(s) -- one per citing site parsed from "
                f"{docname}.rst -- but carries {text.count('query(')}. Zero "
                "means the citing site did not resolve as a CROSS-document "
                "reference at all (an unguarded link, or an unresolved site); "
                "more means a second guard can satisfy the anchor assertions "
                f"accidentally.\n{text}"
            )
            anchors = _guarded_anchors(text)
            assert len(anchors) == expected, (
                f"Chapter {docname}.typ has {text.count('query(')} query( "
                f"call(s) but only {len(anchors)} of them match "
                "_label_existence_guard's full guard shape (a context block "
                f"binding {GUARD_BODY_IDENT}, querying a label, linking that "
                "SAME label when it exists and falling back to the plain body "
                "otherwise). A query( that is not part of that shape is not a "
                f"guarded cross-document link.\n{text}"
            )

    def test_same_document_path_emits_no_guard(
        self, cross_doc_gate_build, cross_doc_fixture_data
    ):
        """
        The bibliography-hosting document and the master emit ZERO ``query(``
        guards.

        This is the other half of the discriminator, and it is what makes the
        previous test's count meaningful: guards are emitted for CROSS-document
        references specifically, not for every reference the translator sees.
        The bibliography host defines the grid's row anchors and cites nothing;
        the master is a pure toctree. Either emitting a guard would mean the
        count above no longer distinguishes the two resolution paths.
        """
        for docname in (
            cross_doc_fixture_data.bibliography_docname,
            cross_doc_fixture_data.master_docname,
        ):
            text = cross_doc_gate_build.read_typ(docname)
            assert text.count("query(") == 0, (
                f"{docname}.typ carries {text.count('query(')} query( "
                "guard(s) but must carry none: it hosts no cross-document "
                "citing site (the bibliography host defines the row anchors "
                "and cites nothing; the master is a pure toctree). A guard "
                "here would mean guards are not specific to the "
                f"cross-document path.\n{text}"
            )

    def test_guarded_anchor_equals_target_document_grid_row_label(
        self, cross_doc_gate_build, cross_doc_fixture_data, target_grid
    ):
        """
        Each chapter's guarded anchor byte-equals a grid row label defined in
        the TARGET document, equals
        ``_namespace_label(<target docname>, <that row's raw id>)``, and names
        the row whose body renders the key THAT chapter cites.

        D012's property is asserted both ways round: the anchor starts with the
        namespace the translator's own helper derives for the TARGET document,
        and does NOT start with the one it derives for the MASTER. A
        master-relative or root-relative scheme therefore cannot pass by
        accident. Both namespaces come from :func:`_namespace_prefix`, so no id
        or namespace literal appears in this module.
        """
        target_prefix = _namespace_prefix(target_grid.docname)
        master_prefix = _namespace_prefix(cross_doc_fixture_data.master_docname)
        assert target_prefix != master_prefix, (
            "Precondition: _namespace_label must namespace the target document "
            f"and the master DIFFERENTLY, but both derive {target_prefix!r}. "
            "Without that, 'namespaced by the target, not the master' is not a "
            "distinguishable claim."
        )

        for docname in cross_doc_fixture_data.chapter_docnames:
            text = cross_doc_gate_build.read_typ(docname)
            anchors = _guarded_anchors(text)
            assert len(anchors) == 1, (
                f"Expected exactly one guarded anchor in {docname}.typ, found "
                f"{anchors}."
            )
            anchor = anchors[0]

            # (1) The anchor is defined as a row label in the TARGET document.
            row = target_grid.row_for_anchor(anchor)
            assert row is not None, (
                f"Chapter {docname}'s guarded anchor {anchor!r} matches no row "
                f"anchor of the grid emitted in {target_grid.docname}.typ "
                f"(row anchors there: {target_grid.anchors}). The link would "
                "dangle across the #include() boundary."
            )

            # (2) D012: namespaced by the TARGET docname, not the master's.
            assert anchor.startswith(target_prefix), (
                f"Chapter {docname}'s guarded anchor {anchor!r} is not "
                "namespaced by the TARGET document "
                f"({target_grid.docname}, whose namespace "
                f"_namespace_label derives as {target_prefix!r}). Per D012 a "
                "cross-document reference must recompute the namespace from "
                "its TARGET's docname."
            )
            assert not anchor.startswith(master_prefix), (
                f"Chapter {docname}'s guarded anchor {anchor!r} is namespaced "
                "by the MASTER "
                f"({cross_doc_fixture_data.master_docname}, namespace "
                f"{master_prefix!r}) rather than by the bibliography's own "
                "document. A master-relative scheme would land on the wrong "
                "file once more than one master includes this content."
            )

            # (3) The anchor is exactly what the translator's own helper
            # computes for the target docname and this row's raw id -- the
            # round-trip that pins the SCHEME, not just the prefix.
            raw_id = row.anchor[len(target_prefix) :]
            assert raw_id, (
                f"Stripping the target namespace {target_prefix!r} off the row "
                f"anchor {row.anchor!r} left no raw id, so the expected anchor "
                "cannot be recomputed."
            )
            expected = TypstTranslator._namespace_label(
                TypstTranslator, target_grid.docname, raw_id
            )
            assert anchor == expected, (
                f"Chapter {docname}'s guarded anchor {anchor!r} does not equal "
                "TypstTranslator._namespace_label("
                f"{target_grid.docname!r}, {raw_id!r}) = {expected!r}. The "
                "demand side (the chapter's query/link) and the supply side "
                "(the grid row's anchor) must be spelled by the SAME helper or "
                "they can drift apart silently."
            )

            # (4) Attribution: the row reached is the row for the key THIS
            # chapter cites, not merely some row of the right bibliography.
            cited_key = cross_doc_fixture_data.cited_key_of(docname)
            cited_title = cross_doc_fixture_data.titles[cited_key]
            assert cited_title in row.body, (
                f"Chapter {docname} cites {cited_key!r} ({cited_title!r}) and "
                f"its guarded link targets the row anchored at {anchor!r}, but "
                "that row's rendered body does not contain that entry's "
                f"title. The link resolves to the WRONG row.\n{row.body}"
            )
            for other_key in cross_doc_fixture_data.cited_keys:
                if other_key == cited_key:
                    continue
                assert cross_doc_fixture_data.titles[other_key] not in row.body, (
                    f"The row chapter {docname} links to also renders "
                    f"{other_key!r}'s title, so 'it lands on the row for the "
                    "key this chapter cites' cannot be distinguished from "
                    f"landing on the other chapter's row.\n{row.body}"
                )


@pytest.mark.skipif(
    not BIBTEX_AVAILABLE,
    reason="sphinxcontrib-bibtex is required for the cross-document bibliography gate",
)
class TestBibliographyRendersOnceInTheTargetDocument:
    """
    The single bare ``.. bibliography::`` renders as exactly one Typst grid, in
    exactly one emitted file, holding each cited entry once and the uncited
    entry never.
    """

    def test_bibliography_renders_as_one_grid_in_the_target_document_only(
        self, cross_doc_gate_build, cross_doc_fixture_data, target_grid
    ):
        """
        Exactly one emitted ``.typ`` carries a ``grid(`` call, it is the
        bibliography-hosting document's, and it carries exactly one.

        Asserted over every emitted file rather than over a named list, so a
        future document that started rendering a stray grid is caught without
        this test being updated. Grids are bounded with ``_iter_grid_blocks``
        rather than counted as substrings, so an unbalanced or nested call
        fails loudly instead of inflating a count (MEM035).
        """
        emitted = cross_doc_gate_build.emitted_typ_files()
        assert len(emitted) == 5, (
            "Vacuous-pass guard: expected FIVE .typ files at the build root -- "
            "one content file per source document plus the templated master "
            f"wrapper -- but found {sorted(emitted)}."
        )

        grids = {name: _iter_grid_blocks(text) for name, text in emitted.items()}
        with_grids = {name: len(blocks) for name, blocks in grids.items() if blocks}
        assert with_grids == {f"{target_grid.docname}.typ": 1}, (
            "The corpus's single bare .. bibliography:: must render as exactly "
            "ONE grid in exactly ONE emitted file, the bibliography host "
            f"{target_grid.docname}.typ, but the grid counts per file are "
            f"{with_grids} (files emitted: {sorted(emitted)}). A grid in a "
            "chapter or in the master would mean the bibliography was "
            "duplicated or relocated; two grids in the host would make this "
            "the multi-bibliography route (S04's fixture)."
        )

    def test_each_cited_entry_appears_once_across_the_corpus_and_uncited_appears_never(
        self, cross_doc_gate_build, cross_doc_fixture_data
    ):
        """
        Summed across EVERY emitted ``.typ``, each cited entry's title occurs
        exactly once and the deliberately uncited entry's title occurs zero
        times.

        Corpus-wide rather than per-file on purpose: the claim is that one
        bibliography serves the whole flattened master, so "exactly once
        anywhere" is the no-duplication statement. Per MEM006 a bare
        ``.. bibliography::`` renders ONLY cited entries, which is what gives
        the zero-count assertion a real subject -- ``refs.bib``'s third entry
        is cited from nowhere and must stay that way.
        """
        emitted = cross_doc_gate_build.emitted_typ_files()
        corpus = "\n".join(emitted.values())

        for key in cross_doc_fixture_data.cited_keys:
            title = cross_doc_fixture_data.titles[key]
            occurrences = corpus.count(title)
            assert occurrences == 1, (
                f"The cited entry {key!r}'s title {title!r} occurs "
                f"{occurrences} time(s) across the emitted corpus "
                f"({sorted(emitted)}) but must occur exactly once: one "
                "bibliography serves the whole flattened master. Zero means "
                "the entry never rendered; more than one means it was "
                "duplicated -- either a second bibliography or the upstream "
                "double-resolve append reaching the write pass (MEM009)."
            )

        for key in cross_doc_fixture_data.uncited_keys:
            title = cross_doc_fixture_data.titles[key]
            assert corpus.count(title) == 0, (
                f"The deliberately UNCITED entry {key!r}'s title {title!r} "
                f"occurs {corpus.count(title)} time(s) across the emitted "
                "corpus but must never render: a bare .. bibliography:: emits "
                "only CITED entries (MEM006). A non-zero count means either "
                "the directive gained an :all: option or something now cites "
                "this key -- both of which void this assertion's subject."
            )

    def test_textual_form_keeps_surname_outside_the_bracket_group(
        self, cross_doc_gate_build, cross_doc_fixture_data, target_grid
    ):
        """
        The textual (``:cite:t:``) chapter emits its author surname OUTSIDE the
        bracket group, with the guarded cross-document link inside it.

        Asserted as a SINGLE contiguous regex, not as three membership checks,
        because the ORDERING is the whole requirement -- and here specifically
        because the surname and the opening bracket arrive in ONE text node
        (measured: ``text("Tanaka [")``, then the guard, then ``text("]")``), so
        separate checks could not prove the surname precedes the bracket at all
        (MEM021). ``re.DOTALL`` plus ``\\s*`` absorb the newline
        ``_label_existence_guard`` emits inside its ``let`` binding.

        The surname is parsed out of ``refs.bib``'s author field and the label
        out of the target grid's own row; the anchor comes from
        ``_namespace_label``. Nothing here is a literal.

        The chapter under test is identified by which chapter's emitted markup
        carries its surname before a bracket -- derived from the ``.rst``'s role
        spelling, so the test follows the fixture if the two chapters swap.
        """
        docname = _textual_docname(cross_doc_fixture_data)
        key = cross_doc_fixture_data.cited_key_of(docname)
        surname = _author_surname(cross_doc_fixture_data.authors[key])
        assert surname, (
            f"No surname could be parsed out of refs.bib's author field for "
            f"{key!r} ({cross_doc_fixture_data.authors[key]!r}), so the "
            "textual form's defining token is missing."
        )

        text = cross_doc_gate_build.read_typ(docname)
        anchor = _guarded_anchors(text)[0]
        row = target_grid.row_for_anchor(anchor)
        assert row is not None, (
            f"The textual chapter {docname}'s anchor {anchor!r} names no row of "
            f"the target grid ({target_grid.anchors})."
        )

        textual_pattern = re.compile(
            # ... ONE text node carrying the surname AND the opening bracket,
            # surname first -- this is the whole of the textual form ...
            r'text\("' + re.escape(surname) + r'\s*\["\)\s*'
            # ... then the GUARDED cross-document link, inside the brackets,
            # carrying the row's own pybtex label as its body ...
            r"context\s*\{\s*let\s+" + re.escape(GUARD_BODY_IDENT) + r"\s*=\s*\[#\{\s*"
            r'text\("' + re.escape(row.label) + r'"\)\}\];\s*'
            r"if\s+query\(<" + re.escape(anchor) + r">\)\.len\(\)\s*>\s*0\s*\{\s*"
            r"link\(<"
            + re.escape(anchor)
            + r">,\s*"
            + re.escape(GUARD_BODY_IDENT)
            + r"\)\s*\}\s*"
            r"else\s*\{\s*" + re.escape(GUARD_BODY_IDENT) + r"\s*\}\s*\}\s*"
            # ... then the closing bracket.
            r'text\("\]"\)',
            re.S,
        )
        matches = textual_pattern.findall(text)
        assert len(matches) == 1, (
            f"Expected EXACTLY ONE textual citing marker in {docname}.typ -- "
            f"the author surname {surname!r} (parsed from refs.bib) "
            f"immediately followed by '[', then the guarded link to {anchor!r} "
            f"carrying the label {row.label!r} (read from the target grid's own "
            "row), then ']' -- but found "
            f"{len(matches)}. Zero means the textual form did not render the "
            "author OUTSIDE the bracket group, which is the ONLY thing "
            "distinguishing it from the parenthetical form; more than one "
            "means a second site can satisfy this assertion accidentally."
            f"\nPattern: {textual_pattern.pattern}\n{text}"
        )


def _author_surname(author: str) -> str:
    """
    Return the surname sphinxcontrib-bibtex renders for a ``refs.bib`` author
    field written in ``"First Last"`` order.

    Deliberately the LAST whitespace-separated word rather than a general bibtex
    name parser -- this fixture authors its names in plain ``First Last`` order,
    and a fixture edit to a ``"Last, First"`` or ``and``-joined form must fail
    the textual-form assertion loudly rather than be silently mis-split here.
    """
    parts = author.split()
    return parts[-1] if parts else ""


def _textual_docname(data: CrossDocFixtureData) -> str:
    """
    Return the chapter whose citing site uses the TEXTUAL ``:cite:t:`` role.

    Derived from the fixture's own role spelling rather than named, so the test
    follows the fixture if the two chapters ever swap inline forms. Raises via
    assertion if the fixture stops having exactly one textual site, because the
    textual-form assertion would otherwise silently test the parenthetical one.
    """
    textual = [
        docname
        for docname in data.chapter_docnames
        if re.search(r":cite:t:`", data.rst_text[docname])
    ]
    assert len(textual) == 1, (
        "Exactly ONE chapter must carry the textual :cite:t: form (the other "
        "carries the parenthetical :cite:p:), so the cross-document route is "
        f"characterised for both inline shapes, but found {textual}."
    )
    return textual[0]


@pytest.mark.skipif(
    not BIBTEX_AVAILABLE,
    reason="sphinxcontrib-bibtex is required for the cross-document bibliography gate",
)
class TestStrictBuildIsClean:
    """
    A strict (``-E -W``) build of the fixture exits 0 with zero warnings, and
    names no bibtex resolution-failure code.

    Why this matters for a characterisation gate specifically: an unresolved
    citing site still exits 0 on a non-strict build while emitting
    ``bibtex.key_not_found`` and rendering no guard at all. Without ``-W`` plus
    the explicit code check, a fixture typo would leave this module happily
    characterising a corpus whose citations stopped resolving -- the
    characterisation would be describing the typo (MEM036).
    """

    def test_strict_build_exits_zero(self, cross_doc_gate_strict_build):
        """
        ``sphinx-build -b typst -E -W`` over the fixture exits 0.

        Under ``-W`` every warning is an error, so exit 0 IS the zero-warning
        evidence -- and unlike grepping for the word "WARNING" it holds under a
        non-English ``LANG`` (the build runs under ``LC_ALL=C`` anyway, belt and
        braces). ``-E`` discards any saved environment so warnings a cached
        build would skip are actually re-emitted.
        """
        result = cross_doc_gate_strict_build.result
        assert result.returncode == 0, (
            "A strict (-E -W) build of the cross-document bibliography fixture "
            f"must succeed, but exited {result.returncode}. Under -W this means "
            "the build emitted at least one warning -- e.g. a citing site that "
            "lost its target, or a toctree entry that no longer exists."
            f"\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_strict_build_reports_no_bibtex_key_not_found(
        self, cross_doc_gate_strict_build
    ):
        """
        The strict build's output never names ``bibtex.key_not_found``.

        Asserted on the CODE rather than on message text because Sphinx
        localises the message but never the bracketed code, so this check is
        locale-independent by construction. It is also strictly more
        informative than the exit code alone: if a future Sphinx or
        ``sphinxcontrib-bibtex`` stopped promoting this one under ``-W``, exit 0
        would hide it and this test would not. Its presence is the exact
        signature of a cited key that no ``refs.bib`` entry defines -- i.e. of
        this gate describing a typo rather than the cross-document route
        (MEM036).
        """
        output = cross_doc_gate_strict_build.output
        assert BIBTEX_KEY_NOT_FOUND_CODE not in output, (
            f"The strict build reported the {BIBTEX_KEY_NOT_FOUND_CODE!r} "
            "warning code, which means sphinxcontrib-bibtex could not resolve "
            "a citing site. Every assertion in this module would then be "
            "characterising a corpus whose citations silently stopped "
            f"resolving.\n{output}"
        )


# ---------------------------------------------------------------------------
# D-13, settled on the COMPILED PDF.
#
# Everything above compares strings in the emitted ``.typ``: it proves the
# chapter's guard and the target grid's row label agree. It does NOT prove that
# Typst itself resolved that reference across the ``#include()`` boundary --
# a guard whose ``query()`` silently found nothing would still leave matching
# strings in two files. Only a live ``/Link`` annotation in the compiled PDF,
# whose destination resolves to the bibliography's own row, settles that.
#
# Keyed by BUILDERNAME in its own build directory (the S01/S04 pattern) rather
# than by switching the whole module to -b typstpdf, so every .typ assertion
# above still runs when typst-py / pypdf are absent.
#
# DEVIATION FROM THE TASK PLAN, recorded here because it changes what one test
# asserts. The plan specified a test named
# ``test_bibliography_page_is_distinct_from_the_citing_pages``, asserting that
# the bibliography's page INDEX differs from a citing marker's source page
# index. That assertion is unsatisfiable on this fixture, and the plan's own
# measurement says so in the same breath: both citing markers sit on source
# page 2 and both destinations resolve to page 2, because this deliberately
# minimal four-document corpus lays its entire body out on a single page. The
# substance the plan wanted from that test -- "this is a genuine jump, not a
# same-page self-link" -- is asserted instead by
# :meth:`TestCompiledPdfResolvesCrossDocumentCitingMarkers
# .test_each_destination_jumps_forward_and_is_not_a_self_link`, in the
# INTRA-page geometric form that this layout actually admits: every
# destination lands strictly below its own marker's rectangle AND below every
# citing marker on the page, i.e. inside the bibliography region. That form is
# strictly stronger than the page-index one here (a page-index check cannot
# distinguish a self-link from a real jump within a page at all) and it stays
# correct if the fixture ever grows onto a second page, because it compares
# positions in reading order rather than page numbers. Growing the fixture
# until the bibliography spilled onto its own page was the alternative; it was
# rejected because the task plan forbids fixture modification and requires
# ``git diff --stat`` on the fixture to be EMPTY.
# ---------------------------------------------------------------------------


def _normalise_whitespace(text: str) -> str:
    """
    Collapse every whitespace run to a single space.

    MANDATORY before counting a title in PDF-extracted text, and the reason is
    not cosmetic: Typst breaks lines inside a justified bibliography row and
    pypdf reports those breaks literally, so an un-normalised ``str.count()``
    of a multi-word title silently reads 0 and the assertion then fails for a
    reason that has nothing to do with the contract. Both the extracted text
    and the expected title are normalised through this one function, so they
    cannot disagree about whitespace. Same implementation as the sibling
    multi-bibliography gate's, deliberately duplicated rather than imported --
    these gate modules are independent characterisation records.
    """
    return re.sub(r"\s+", " ", text)


@dataclass(frozen=True)
class PdfCoordinateLink:
    """
    One ``/Link`` annotation whose destination is an explicit COORDINATE
    destination -- an indirect array ``[<page ref> /XYZ x y zoom]``.

    Measured on this fixture: the two chapter citing markers are exactly these,
    while the four toctree entries are NAMED (string) destinations instead.
    Both shapes must be tolerated by the walker; only this shape is a citing
    marker, and it is deliberately NOT reverse-mapped through the ``/Names``
    tree, because the citing markers are not named destinations at all
    (measured: no ``/Names`` entry for either).
    """

    source_page: int
    rect: tuple[float, float, float, float]
    target_page: int
    dest_kind: str
    dest_y: float | None

    @property
    def rect_bottom(self) -> float:
        """The marker rectangle's lower edge, in PDF user space."""
        return min(self.rect[1], self.rect[3])

    @property
    def rect_top(self) -> float:
        """The marker rectangle's upper edge, in PDF user space."""
        return max(self.rect[1], self.rect[3])


@dataclass
class CrossDocPdf:
    """The compiled ``master.pdf``, parsed once: text, lines and link annots."""

    page_texts: list[str]
    page_lines: list[list[tuple[float, str]]]
    coordinate_links: list[PdfCoordinateLink]
    named_destinations: list[str]

    @property
    def text(self) -> str:
        """Whitespace-normalised text of every page, joined."""
        return _normalise_whitespace(" ".join(self.page_texts))

    def line_covering(self, page: int, low: float, high: float) -> str | None:
        """
        Return the extracted text line whose BASELINE falls inside
        ``[low, high]`` on ``page``, or ``None``.

        Used to read a citing marker's own visible text out of the PDF -- the
        line its annotation rectangle sits on -- so a marker can be attributed
        to the entry it cites by what the PAGE says, rather than by assuming
        annotations arrive in document order.
        """
        found = [
            line for baseline, line in self.page_lines[page] if low <= baseline <= high
        ]
        if len(found) != 1:
            return None
        return found[0]


def _page_lines(page) -> list[tuple[float, str]]:
    """
    Return ``(baseline_y, normalised_line_text)`` for one page, top-first.

    The baseline comes from ``cm[5] + tm[5]``, not from ``tm[5]`` alone:
    measured on this Typst-produced PDF, ``tm[5]`` is 0 for every run and the
    whole vertical position lives in the current transformation matrix, so a
    ``tm``-only reading collapses every line onto y=0 and the geometric
    assertions below would compare nonsense. Fragments sharing a baseline are
    re-joined in ``x`` order.
    """
    collected: dict[float, list[tuple[float, str]]] = {}

    def visitor(text, cm, tm, font_dict, font_size):
        if not text.strip():
            return
        collected.setdefault(round(cm[5] + tm[5], 2), []).append((cm[4] + tm[4], text))

    page.extract_text(visitor_text=visitor)
    return [
        (
            baseline,
            _normalise_whitespace(
                "".join(fragment for _, fragment in sorted(fragments))
            ).strip(),
        )
        for baseline, fragments in sorted(collected.items(), reverse=True)
    ]


def _read_compiled_pdf(pdf_path: Path) -> CrossDocPdf:
    """
    Parse one compiled PDF into :class:`CrossDocPdf`.

    The page-object map (``indirect_reference.idnum -> page index``) is what
    turns a destination's page REFERENCE into a page INDEX; there is no other
    reliable route, because a coordinate destination names its page by object
    reference and never by number.
    """
    reader = pypdf.PdfReader(io.BytesIO(pdf_path.read_bytes()))
    page_indices = {
        page.indirect_reference.idnum: index for index, page in enumerate(reader.pages)
    }

    coordinate_links: list[PdfCoordinateLink] = []
    named_destinations: list[str] = []
    for index, page in enumerate(reader.pages):
        for reference in page.get("/Annots") or []:
            annotation = reference.get_object()
            if annotation.get("/Subtype") != "/Link":
                continue
            destination = annotation.get("/Dest")
            if destination is None:
                action = annotation.get("/A")
                destination = action.get_object().get("/D") if action else None
            if destination is None:
                continue
            # A NAMED destination: measured to be a toctree entry, never a
            # citing marker. Recorded, then skipped -- never crashed on.
            if isinstance(destination, (str, bytes)):
                named_destinations.append(str(destination))
                continue
            if hasattr(destination, "get_object"):
                destination = destination.get_object()
            page_reference = destination[0]
            assert getattr(page_reference, "idnum", None) in page_indices, (
                "A coordinate /Link destination names a page object "
                f"({page_reference!r}) that is not one of this document's "
                "pages, so its destination page index cannot be resolved."
            )
            dest_kind = str(destination[1])
            dest_y = (
                float(destination[3])
                if dest_kind == "/XYZ" and destination[3] is not None
                else None
            )
            coordinate_links.append(
                PdfCoordinateLink(
                    source_page=index,
                    rect=tuple(float(value) for value in annotation["/Rect"]),
                    target_page=page_indices[page_reference.idnum],
                    dest_kind=dest_kind,
                    dest_y=dest_y,
                )
            )

    return CrossDocPdf(
        page_texts=[
            _normalise_whitespace(page.extract_text()) for page in reader.pages
        ],
        page_lines=[_page_lines(page) for page in reader.pages],
        coordinate_links=coordinate_links,
        named_destinations=named_destinations,
    )


@pytest.fixture(scope="module")
def cross_doc_gate_pdf_build(cross_doc_gate_dir, tmp_path_factory):
    """
    Compile the fixture through ``-b typstpdf`` EXACTLY ONCE for the whole
    module, for the compiled-PDF half only.

    ``pytest.importorskip`` rather than a bare import: a missing ``typst-py``
    or ``pypdf`` must SKIP this half, not ERROR it, and this fixture-level
    belt-and-braces covers the case where the class-level ``skipif`` is ever
    loosened. Declared at module level rather than inside the PDF class: a
    class-scoped fixture defined in a class body and depending on these
    broader-scoped fixtures trips pytest's own ``assert not self._finalizers``
    internal check (the sibling gates record the same hazard).
    """
    pytest.importorskip("typst", reason="typst-py backs the typstpdf builder")
    pytest.importorskip("pypdf", reason="pypdf extracts the compiled PDF's text")

    build_dir = tmp_path_factory.mktemp("cross_doc_gate_pdf") / "_build"
    result = _run_sphinx_build(cross_doc_gate_dir, build_dir, buildername="typstpdf")
    assert result.returncode == 0, (
        "sphinx-build -b typstpdf over the cross-document bibliography fixture "
        "must succeed (this gate locks measured-working behaviour and is green "
        f"on arrival)\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    return CrossDocGateBuild(result=result, build_dir=build_dir)


@pytest.fixture(scope="module")
def cross_doc_pdf(cross_doc_gate_pdf_build) -> CrossDocPdf:
    """
    Parse the fixture's single compiled PDF ONCE for the whole class.

    The PDF is located by glob rather than by filename: the fixture's
    ``typst_documents`` target owns that name, and asserting there is EXACTLY
    one compiled PDF is itself worth checking -- the fixture declares a single
    master, so a second PDF would mean the master registry changed shape under
    this gate. The non-empty guard then rules out the silent degrade where
    extraction yields nothing and every count below would read 0 for the wrong
    reason.
    """
    pdfs = sorted(cross_doc_gate_pdf_build.build_dir.glob("*.pdf"))
    assert len(pdfs) == 1, (
        "Expected exactly one compiled PDF for this single-master fixture, "
        f"found {[pdf.name for pdf in pdfs]} -- build "
        f"returncode={cross_doc_gate_pdf_build.result.returncode}\n"
        f"stderr: {cross_doc_gate_pdf_build.result.stderr}"
    )
    parsed = _read_compiled_pdf(pdfs[0])
    assert parsed.text.strip(), (
        "Vacuous-pass guard: pypdf extracted NO text from the compiled PDF, so "
        "every count below would read 0 regardless of what the document "
        f"actually contains ({pdfs[0]})."
    )
    assert any(lines for lines in parsed.page_lines), (
        "Vacuous-pass guard: the position-aware extraction yielded no text "
        "lines on any page, so every geometric assertion below would have "
        f"nothing to compare against ({pdfs[0]})."
    )
    return parsed


@pytest.fixture(scope="module")
def bibliography_page_index(cross_doc_pdf, cross_doc_fixture_data) -> int:
    """
    Derive -- never hard-code -- the index of the page that holds the rendered
    bibliography, by searching extracted text for the entry titles parsed out
    of ``refs.bib``.

    The task plan is explicit that no page index may be encoded here: at plan
    time the citing markers and their target both sat on page 2, and either
    number could move the moment the fixture's prose or the template's front
    matter changes length.
    """
    cited_titles = [
        _normalise_whitespace(cross_doc_fixture_data.titles[key])
        for key in cross_doc_fixture_data.cited_keys
    ]
    pages = [
        index
        for index, text in enumerate(cross_doc_pdf.page_texts)
        if all(title in text for title in cited_titles)
    ]
    assert len(pages) == 1, (
        "Exactly ONE page must hold the rendered bibliography -- the page "
        f"carrying every cited entry title {cited_titles} -- but the titles "
        f"were all found together on pages {pages}. Zero means the "
        "bibliography did not render (or the titles wrapped in a way "
        "whitespace normalisation did not repair); more than one means the "
        "entries are duplicated across pages and 'the bibliography page' is "
        "not a single place."
    )
    return pages[0]


def _marker_cited_key(
    pdf: CrossDocPdf,
    link: PdfCoordinateLink,
    target_grid: TargetGrid,
    data: CrossDocFixtureData,
) -> str:
    """
    Return the bibtex key of the citing marker that ``link`` annotates, read
    out of the PDF ITSELF.

    The marker's own text line -- the line whose baseline falls inside the
    annotation rectangle -- is matched against the row LABELS parsed from the
    target grid (e.g. the alpha-style token sphinxcontrib-bibtex renders for an
    entry). Attributing this way rather than by annotation ORDER is what keeps
    the attribution assertion non-circular: nothing here assumes the
    annotations arrive in document order, or that document order follows the
    toctree.
    """
    line = pdf.line_covering(link.source_page, link.rect_bottom, link.rect_top)
    assert line is not None, (
        "Could not read the text line that citing marker "
        f"{link.rect} on page {link.source_page} sits on -- exactly one "
        "extracted line must have its baseline inside the annotation "
        "rectangle. Without it the marker cannot be attributed to the entry "
        f"it cites.\nLines on that page: {pdf.page_lines[link.source_page]}"
    )
    label_to_key = {}
    for key in data.cited_keys:
        row = next(
            (
                candidate
                for candidate in target_grid.rows
                if data.titles[key] in candidate.body
            ),
            None,
        )
        assert row is not None, (
            f"No row of the grid emitted in {target_grid.docname}.typ renders "
            f"the title of cited key {key!r}, so its rendered label -- which "
            "is how a PDF marker is attributed back to a key -- is unknown."
        )
        label_to_key[_normalise_whitespace(row.label)] = key

    matched = [key for label, key in label_to_key.items() if label in line]
    assert len(matched) == 1, (
        f"The citing marker's own text line {line!r} must contain EXACTLY ONE "
        f"bibliography row label (labels: {sorted(label_to_key)}) so the "
        f"marker can be attributed to a single cited entry, but matched "
        f"{matched}."
    )
    return matched[0]


@pytest.mark.skipif(
    not PDF_DEPS_AVAILABLE,
    reason="sphinxcontrib-bibtex, typst-py and pypdf are all required for the "
    "cross-document gate's compiled-PDF half",
)
class TestCompiledPdfResolvesCrossDocumentCitingMarkers:
    """
    D-13, the milestone's single declared "cannot be simulated" risk
    (``01-CONTEXT.md`` § Final Integrated Acceptance: "#include()-crossing
    label resolution"), settled on the compiled PDF.

    A ``.typ``-level match between a chapter's ``query(<L>)`` guard and a row
    label in ``refs.typ`` proves the two STRINGS agree. It does not prove Typst
    resolved the reference: the guard is written precisely so that a failed
    lookup degrades to plain text, silently and with the same strings still
    present in both files. These tests read the compiled artefact instead, and
    require a live ``/Link`` annotation on each chapter's citing marker whose
    destination resolves into the bibliography that lives in a DIFFERENT source
    document.
    """

    def test_cross_document_citing_markers_are_live_pdf_links_to_the_bibliography_page(
        self,
        cross_doc_pdf,
        cross_doc_fixture_data,
        target_grid,
        bibliography_page_index,
    ):
        """
        THE D-13 VERDICT. Every cross-document citing site is a live ``/Link``
        whose destination resolves to the page holding the bibliography, and
        each one lands on the row for the key THAT marker cites.

        Four things are asserted together, and each closes a way the other
        three could pass vacuously:

        1. the number of coordinate-destination links equals the number of
           cross-document citing sites parsed from the chapters -- with a loud
           guard first, because an EMPTY list would otherwise satisfy every
           ``for`` loop below and report the D-13 proof as passing having found
           nothing at all;
        2. every destination resolves to the derived bibliography page;
        3. the destinations are pairwise DISTINCT, so two markers cannot have
           collapsed onto one shared anchor;
        4. each marker, identified from the PDF by the row label printed in its
           own text line, resolves to the destination whose rank in
           bibliography-row order matches that entry's rank in the grid -- so
           one marker pointing at the right page cannot cover for a sibling
           pointing at the wrong row.
        """
        links = cross_doc_pdf.coordinate_links
        expected_sites = sum(
            len(cross_doc_fixture_data.citing_sites[docname])
            for docname in cross_doc_fixture_data.chapter_docnames
        )

        # (1) Vacuous-pass guard FIRST: never pass by finding nothing.
        assert links, (
            "The D-13 proof found NO citing-marker annotation at all: the "
            "compiled PDF holds zero /Link annotations with a coordinate "
            "destination, so there is nothing to prove that Typst resolved a "
            "cross-document citation. Either every chapter's guarded link "
            "degraded to plain text across the #include() boundary (exactly "
            "the failure this test exists to catch), or the destination shape "
            "changed and the walker no longer recognises it. Named "
            f"destinations seen: {cross_doc_pdf.named_destinations}."
        )
        assert len(links) == expected_sites, (
            f"Expected exactly {expected_sites} coordinate-destination /Link "
            "annotation(s) -- one per cross-document citing site parsed from "
            f"the chapters {cross_doc_fixture_data.chapter_docnames} -- but "
            f"found {len(links)}: {links}. Fewer means a citing site did not "
            "become a live link; more means something other than a citing "
            "marker is emitting coordinate destinations and the attribution "
            "below is measuring the wrong annotations."
        )
        for link in links:
            assert link.dest_kind == "/XYZ" and link.dest_y is not None, (
                f"Citing-marker destination {link} is not the measured "
                "coordinate shape ([<page> /XYZ x y zoom]); the vertical "
                "position the attribution below ranks on cannot be read from "
                "it."
            )

        # (2) Every destination lands on the derived bibliography page.
        for link in links:
            assert link.target_page == bibliography_page_index, (
                f"A citing marker on page {link.source_page} resolves to page "
                f"{link.target_page}, but the bibliography was derived (from "
                "the entry titles parsed out of refs.bib) to be on page "
                f"{bibliography_page_index}. The link crosses the #include() "
                "boundary to the WRONG place."
            )
            page_text = cross_doc_pdf.page_texts[link.target_page]
            assert any(
                _normalise_whitespace(cross_doc_fixture_data.titles[key]) in page_text
                for key in cross_doc_fixture_data.cited_keys
            ), (
                f"The page a citing marker resolves to ({link.target_page}) "
                "contains none of the cited entry titles, so it is not the "
                f"bibliography page.\n{page_text}"
            )

        # (3) Distinct destinations: not two markers on one shared anchor.
        destinations = [(link.target_page, link.dest_y) for link in links]
        assert len(set(destinations)) == len(destinations), (
            "Two citing markers resolve to the SAME destination "
            f"{destinations}, so each landing 'on its own row' cannot be "
            "distinguished from both landing on one shared anchor."
        )

        # (4) Per-marker attribution, by rank in bibliography-row order.
        destination_rank = {
            destination: rank
            for rank, destination in enumerate(
                sorted(destinations, key=lambda item: (item[0], -item[1]))
            )
        }
        row_rank = {}
        for rank, row in enumerate(target_grid.rows):
            for key in cross_doc_fixture_data.cited_keys:
                if cross_doc_fixture_data.titles[key] in row.body:
                    row_rank[key] = rank
        assert set(row_rank) == set(cross_doc_fixture_data.cited_keys), (
            "Vacuous-pass guard: every cited key must map to a grid row before "
            f"ranks can be compared, but only {sorted(row_rank)} of "
            f"{sorted(set(cross_doc_fixture_data.cited_keys))} did."
        )

        reached_keys = []
        for link in links:
            key = _marker_cited_key(
                cross_doc_pdf, link, target_grid, cross_doc_fixture_data
            )
            reached_keys.append(key)
            actual = destination_rank[(link.target_page, link.dest_y)]
            assert actual == row_rank[key], (
                f"The citing marker for {key!r} resolves to the destination "
                f"ranked {actual} among the markers' destinations (ordered "
                "down the bibliography page), but that entry's row is ranked "
                f"{row_rank[key]} in the grid emitted by "
                f"{target_grid.docname}.typ. The marker landed on ANOTHER "
                "entry's row."
            )

        # Coverage: every cited key is reached, so a correct sibling cannot
        # cover for a broken one.
        assert sorted(reached_keys) == sorted(cross_doc_fixture_data.cited_keys), (
            "The set of entries reached by a live PDF link is "
            f"{sorted(reached_keys)} but the chapters cite "
            f"{sorted(cross_doc_fixture_data.cited_keys)}. Every cited key must "
            "be reached by its own marker."
        )

    def test_each_destination_jumps_forward_and_is_not_a_self_link(
        self, cross_doc_pdf, bibliography_page_index
    ):
        """
        Each citing marker's destination is strictly LATER in reading order
        than the marker itself, and later than EVERY citing marker on the page
        -- i.e. it lands in the bibliography region, not back on the marker.

        This is the intra-page form of the task plan's
        "bibliography page is distinct from the citing pages" check; see the
        DEVIATION note above this class for why the page-index form is
        unsatisfiable on this single-body-page fixture and why this form is
        the stronger replacement. A page-index comparison cannot tell a
        self-link from a real jump at all when both are on one page; comparing
        positions in reading order can, and keeps working unchanged if the
        fixture ever spills onto a second page.
        """
        links = cross_doc_pdf.coordinate_links
        assert links, (
            "Vacuous-pass guard: no coordinate-destination /Link annotations, "
            "so 'the destination is not a self-link' would hold trivially."
        )

        highest_marker_bottom = min(link.rect_bottom for link in links)
        for link in links:
            assert link.target_page >= link.source_page, (
                f"A citing marker on page {link.source_page} resolves BACKWARD "
                f"to page {link.target_page}. The bibliography is included "
                "after the chapters, so a backward jump means the destination "
                "is not the bibliography."
            )
            if link.target_page == link.source_page:
                assert link.dest_y < link.rect_bottom, (
                    f"A citing marker whose rectangle is {link.rect} resolves "
                    f"to y={link.dest_y} on its OWN page -- not strictly below "
                    "its own rectangle. A destination inside or above the "
                    "marker is a self-link, which would satisfy 'there is a "
                    "live /Link' while proving nothing about cross-document "
                    "resolution."
                )
                assert link.dest_y < highest_marker_bottom, (
                    f"A citing marker resolves to y={link.dest_y}, which is "
                    "not below EVERY citing marker on the page (the lowest "
                    f"marker edge is {highest_marker_bottom}). The "
                    "bibliography renders after all chapter prose, so a "
                    "destination among the markers is not in the bibliography "
                    "region."
                )

        assert all(link.target_page == bibliography_page_index for link in links), (
            "Every destination must land on the derived bibliography page "
            f"({bibliography_page_index}), but the markers resolve to "
            f"{sorted({link.target_page for link in links})}."
        )

    def test_each_cited_entry_appears_exactly_once_in_the_compiled_pdf(
        self, cross_doc_pdf, cross_doc_fixture_data
    ):
        """
        In whitespace-normalised text over ALL pages, each cited entry title
        occurs exactly once and the deliberately uncited entry's title never
        (MEM006: a bare ``.. bibliography::`` renders only cited entries).

        Counting the TITLE rather than a label token is deliberate: labels
        appear twice by design (the citing marker plus the bibliography row),
        and short label tokens are the kind of string that collides with page
        numbers in extracted text. Titles are fixture-authored prose, parsed
        out of ``refs.bib``, and the fixture's parse guards keep them pairwise
        distinct so one entry's count can never be satisfied by another.

        Exactly ONE is the cross-document claim restated as a count: the single
        bibliography lives in one included document, so even though two
        chapters in two other documents cite into it, each entry is rendered
        once in the flattened master -- not once per citing document.
        """
        text = cross_doc_pdf.text
        assert text.strip(), (
            "Vacuous-pass guard: pypdf extracted no text from the compiled "
            "PDF, so every count below would read 0 for the wrong reason."
        )

        for key in cross_doc_fixture_data.cited_keys:
            title = _normalise_whitespace(cross_doc_fixture_data.titles[key])
            count = text.count(title)
            assert count == 1, (
                f"The cited entry {key!r} ({title!r}) must be rendered EXACTLY "
                f"ONCE in the compiled PDF but was found {count} time(s). Zero "
                "means the bibliography did not reach the compiled master "
                "across the #include() boundary (or the title wrapped in a way "
                "whitespace normalisation did not repair); more than one means "
                "the single bibliography was rendered once per citing "
                "document, which is the duplication this slice's single-grid "
                "contract rules out."
            )

        for key in cross_doc_fixture_data.uncited_keys:
            title = _normalise_whitespace(cross_doc_fixture_data.titles[key])
            count = text.count(title)
            assert count == 0, (
                f"The deliberately UNCITED entry {key!r} ({title!r}) must not "
                f"appear in the compiled PDF but was found {count} time(s). A "
                "bare .. bibliography:: renders only cited entries (MEM006); "
                "its presence means the directive gained :all: or the filter "
                "semantics changed, either of which voids this fixture's "
                "uncited-entry control."
            )

    def test_textual_surname_outside_bracket_reaches_the_page(
        self, cross_doc_pdf, cross_doc_fixture_data
    ):
        """
        The textual ``:cite:t:`` form renders its author surname OUTSIDE the
        bracket group in the compiled PDF, proving S02's inline-form contract
        survives the ``#include()`` boundary.

        The surname-then-bracket sequence is the only thing distinguishing the
        textual form from the parenthetical one, and it is asserted exactly
        once so a second site cannot satisfy it accidentally. Both the chapter
        that carries the textual form and the surname itself are derived from
        the fixture (:func:`_textual_docname`, :func:`_author_surname`), so no
        author literal appears here.
        """
        docname = _textual_docname(cross_doc_fixture_data)
        key = cross_doc_fixture_data.cited_key_of(docname)
        surname = _author_surname(cross_doc_fixture_data.authors[key])
        assert surname, (
            f"Vacuous-pass guard: no surname could be derived from the author "
            f"field of {key!r} "
            f"({cross_doc_fixture_data.authors[key]!r}), so the sequence "
            "searched for below would degrade to a bare '['."
        )

        needle = f"{surname} ["
        count = cross_doc_pdf.text.count(needle)
        assert count == 1, (
            f"Expected the textual citing form in {docname} to render "
            f"{needle!r} EXACTLY ONCE in the compiled PDF -- the surname "
            "rendered OUTSIDE the bracket group, which is what distinguishes "
            f":cite:t: from :cite:p: -- but found {count}. Zero means the "
            "textual form collapsed to the parenthetical one across the "
            "#include() boundary; more than one means a second site can "
            f"satisfy this assertion accidentally.\n{cross_doc_pdf.text}"
        )
