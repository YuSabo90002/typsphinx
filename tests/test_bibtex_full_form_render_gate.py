"""
M001 / S06 FULL-FORM bibliography render gate, ``.typ`` level.

**What this module pins.** One multi-document Sphinx project in which the WHOLE
citation surface coexists at once -- the parenthetical form, the textual form,
a multi-key site, the footnote route (twice on one key), TWO
``.. bibliography::`` directives (one corpus-wide and bare, one chapter-local
and ``:filter:``ed with a ``:keyprefix:``), and cross-document resolution across
Typst's ``#include()`` boundary. Every prior M001 slice proved exactly ONE route
in isolation; nothing before S06 proved the routes coexist without interfering.
This module asserts the EMITTED-MARKUP half of that claim:

* the per-document census of ``grid(``, ``footnote(`` and guarded ``query(``
  calls, derived from the fixture's own sources rather than transcribed;
* all four citing forms present and RESOLVED -- each a genuine guarded
  ``link()``, matched as ONE contiguous regex so a broken ordering cannot pass;
* every citing site guarded on an anchor that byte-equals a grid row label
  defined in ANOTHER document, with the guard matched as one contiguous pattern
  carrying a BACKREFERENCE tying ``query(<L>)`` to ``link(<L>)``;
* **D013 per-route exactly-once**, scoped PER GRID and PER ROUTE -- never
  document-wide (see the next paragraph);
* ``:keyprefix:`` does not leak into either the rendered label or the emitted
  anchor (the S04 R010 verdict, re-confirmed in the combined setting);
* a strict ``-E -W`` build exits 0 with zero warnings and names neither
  ``bibtex.key_not_found`` nor ``bibtex.duplicate_citation``.

The compiled-PDF settlement and the three-way ``html`` / ``latex``
content-consistency check (R010) are T03's subject, not this module's.

**WHY THERE IS NO DOCUMENT-WIDE "EXACTLY ONCE" ASSERTION, AND WHY WRITING ONE
WOULD BE WRONG.** On a CORRECT build of this fixture one entry's title appears
TWICE in the emitted corpus: the key that the chapter-local filtered
bibliography is scoped to is ALSO cited from a chapter, so the corpus-wide bare
bibliography renders it too. Both grids legitimately own a row for it. D013's
exactly-once property is therefore PER ROUTE (per grid, per footnote id), not
per project, and every count below names the route or grid it scopes to so a
failure is diagnosable. A document-wide count would be measurably false here --
it would fail on the untouched translator -- and "fixing" it by deleting one
directive would delete the slice's subject.

**THIS GATE IS AN HONEST CHARACTERISATION GATE, GREEN ON ARRIVAL, BY DESIGN.**
``typsphinx`` needs ZERO production code for any of this: ``grep -rc bibtex
typsphinx/`` is 0 and nothing in this slice changes that. This is the SIXTH
consecutive bibliography slice to measure that conclusion -- MEM010 (S01),
MEM023 (S02), MEM026 (S03), D010 (S04) and the cross-document route (S05).
``sphinxcontrib.bibtex`` owns the ``cite`` / ``footcite`` roles and the
``bibliography`` / ``footbibliography`` directives and leaves ordinary docutils
``citation`` / ``reference`` / ``footnote`` nodes behind; the translator's
existing generic machinery (``_namespace_label`` + ``_label_existence_guard`` +
``visit_footnote_reference``) renders them with no awareness that a
bibliography is involved. A conventional RED-first gate cannot go RED here
without first breaking production code. The repo precedent for a deliberately
green-on-arrival characterisation gate is
``tests/test_typst_elements_pass_through_gate.py``; the four sibling bibtex
gates are the same shape.

**Nothing is transcribed.** Every subject is parsed out of the fixture's own
inputs or computed by the translator's own helpers:

* entry titles and authors from ``refs.bib``;
* every citing SITE, its role family, its inline form and the keys it names
  from the ``.rst`` files -- which also decides WHICH document is the master,
  WHICH hosts the bare bibliography, WHICH hosts the filtered one and WHICH
  carries the footnote route, so no docname role is assumed;
* each grid's OWNED key set from the directive's own ``:filter:`` option (bare
  means "every cited key", MEM006);
* the expected namespace from ``TypstTranslator._namespace_label`` via
  :func:`_namespace_prefix`, and the footnote label from that same helper via
  :func:`_footnote_label`, so NO namespaced-id literal appears anywhere in this
  file -- not even in prose. The slice's verification greps this very file to
  prove it.

Anchor ids are read out of the emitted grid rows, never typed: Sphinx assigns
them in toctree-assignment order and they shift freely (MEM043).

Each parse carries a vacuous-pass guard that NAMES its subject, so a fixture
edit fails LOUDLY here instead of silently degrading a count below into a
no-op.

**The citing-site parser is deliberately WIDER than the sibling gates'.** The
shared ``:cite:([a-z]*):`` pattern does NOT match ``:footcite:`` -- measured, it
returns ``[]`` (MEM030) -- because the ``cite`` in ``footcite`` is not preceded
by a colon. This fixture has footcite sites, so a narrow parser here would
under-count every citing-site guard and turn the fixture-drift protection into
a no-op. :func:`_parse_citing_sites` matches the whole ``cite`` / ``footcite``
role family and records which family each site belongs to, because the two
families render through different routes (grid vs. footnote) and the censuses
below are per route.

Like every sibling, that parser regexes the RAW rst, so a FULLY-COLONISED role
name written inside an rst comment would also count as a site (MEM022/MEM030's
trap). The fixture's comments therefore write role names un-colonised, and the
exact per-document site-count guards are what catch it if that ever slips.

**Resolve-at-most-once discipline (R014 / MEM009).** This module re-resolves
the doctree ZERO times and needs to not even once: every label, anchor and body
it compares is read out of the emitted ``.typ`` or recomputed with
``_namespace_label``. The upstream double-resolve artifact MEM009 records --
cached shared nodes being appended to on each extra resolve of a finished
environment -- is therefore structurally unreachable from here. The slice's
verification greps this very file for the name of the resolving API to prove it,
which is why that name is written nowhere in this module, prose included.

**Locale.** The strict ``-W`` build runs with ``LANG`` / ``LANGUAGE`` unset and
``LC_ALL=C``: this machine's locale is Japanese and Sphinx localises its output.
The assertions use the exit status plus the absence of the never-localised
warning CODES.

**Assertions read the per-document content files** (``index.typ``,
``chapter_one.typ``, ``chapter_two.typ``, ``refs.typ``), never only the
templated wrapper the two-layer split writes for the master target -- asserting
over the wrapper would prove nothing about rendered bodies.

**Sensitivity probes.** Because this gate is green on arrival, every assertion's
teeth were proven by driving it RED from a temporary, immediately-reverted
mutation and then confirming GREEN again. Production mutations were applied to
``typsphinx/`` and reverted with the revert verified by ``git diff --quiet``;
fixture mutations were applied in place over a tar backup and restored
byte-identically. No probe is part of the committed tree.

Production mutations, each naming the tests it turned RED:

* emit a bare ``link()`` instead of the existence guard -> the guarded-query
  census, all three inline-form tests, and both cross-document anchor tests
  (6 failures);
* stop namespacing labels by docname -> the target-namespace test and the
  chapter-local-anchor test. **This probe is why those two tests carry an
  explicit non-empty, pairwise-distinct prefix guard:** both sides of a
  ``startswith(_namespace_prefix(...))`` comparison are computed by the SAME
  helper, so without that guard the mutation moved both together and left the
  whole module GREEN. Measured, then fixed, then re-measured RED.
* suppress the footnote reuse branch so every ``:footcite:`` site emits a
  DEFINITION -> the definition/reuse form test and the footnote route's
  exactly-once body count;
* re-walk a citation's children on depart, i.e. MEM009's duplication shape
  reaching the write pass -> the per-grid exactly-once test. **This probe is why
  that test counts title occurrences inside the matching ROW's body as well as
  counting rows:** the duplication lands inside one row cell and leaves the row
  COUNT unchanged, so the row-counting half alone stayed green.
* append a stray ``grid()`` to every emitted document -> the grid census.

Fixture mutations (several are intercepted by
:func:`full_form_fixture_data`'s own parse guards, which is those guards' job --
each names its subject):

* ``:all:`` added to the bare corpus-wide ``.. bibliography::`` -> RED at the
  bare-directive guard;
* the ``:filter:`` rewritten into the key-on-left comparison form -> RED at the
  grid census AND at the owns-no-key guard. This is the fixture's measured
  SILENT degradation: the strict build still exits 0 with zero warnings through
  it, which is exactly why the per-grid row counts are asserted POSITIVELY;
* the ``:keyprefix:`` removed -> all three strict-build tests RED, the third
  specifically on ``bibtex.duplicate_citation``.

Two assertions could NOT be driven RED at their own bodies, and that is recorded
rather than papered over. ``test_the_uncited_entry_never_renders_anywhere``:
every mutation that would make an uncited entry render passes first through the
bare-directive or uncited-set parse guard, which fires by design.
``test_the_keyprefix_string_appears_in_no_label_and_no_anchor``: a leak would
have to originate in ``sphinxcontrib.bibtex``, which this project does not
patch; its sharper sibling
:meth:`TestKeyprefixDoesNotLeakIntoAnchorsOrLabels
.test_the_chapter_local_grid_labels_match_the_corpus_wide_ones` did go RED under
the no-namespacing probe.
"""

import io
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest
from docutils.nodes import make_id

from typsphinx.translator import TypstTranslator

try:
    import sphinxcontrib.bibtex  # noqa: F401

    BIBTEX_AVAILABLE = True
except ImportError:
    BIBTEX_AVAILABLE = False

# typst-py and pypdf back T03's compiled-PDF and cross-builder half ONLY.
# Probed here so the flag exists for that task's build fixtures; nothing in
# THIS module's .typ-level assertions needs either, which is why both builds
# below are -b typst and the whole module still runs on a machine without them.
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


# The two bibtex warning CODES that signal this fixture's arrangement stopped
# working. CODES, not message text: Sphinx localises the message but never the
# bracketed code, so these checks are locale-independent by construction.
#
#   key_not_found      -- a citing site resolved against nothing, so every
#                         assertion here would be characterising a typo
#                         (MEM036).
#   duplicate_citation -- the two bibliography directives both claimed the same
#                         citation id, which is exactly what the fixture's
#                         load-bearing :keyprefix: exists to prevent.
BIBTEX_KEY_NOT_FOUND_CODE = "bibtex.key_not_found"
BIBTEX_DUPLICATE_CITATION_CODE = "bibtex.duplicate_citation"

# The identifier ``_label_existence_guard`` binds in the guard it emits. Fixed
# project-wide by that method's own docstring, which is why asserting on it
# here is a contract check and not a spelling guess.
GUARD_BODY_IDENT = "__tsx_body"

# The refid template sphinxcontrib-bibtex uses for a footcite footnote, taken
# from upstream ``sphinxcontrib/bibtex/foot_roles.py`` (the default value of its
# ``bibtex_footcite_id`` config): the raw id is ``"footcite-{key}"`` run through
# docutils' ``make_id``. The fixture leaves ``bibtex_footcite_id`` unset, so
# this default applies. Formatted with the fixture's OWN parsed keys below --
# never with a hardcoded key.
FOOTCITE_ID_TEMPLATE = "footcite-{key}"

# The two role families this fixture uses, spelled as they appear in rst. Role
# NAMES, not generated label tokens, so naming them breaches no house rule.
CITE_FAMILY = "cite"
FOOTCITE_FAMILY = "footcite"


# ---------------------------------------------------------------------------
# Fixture-authored data, parsed out of the fixture rather than transcribed.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def full_form_gate_dir():
    """Return the path to the bibtex_full_form_render_gate fixture (S06/T01)."""
    return Path(__file__).parent / "fixtures" / "bibtex_full_form_render_gate"


def _parse_bib_field(bib_text: str, field: str) -> dict[str, str]:
    """
    Return ``{entry_key: value}`` for one quoted ``refs.bib`` field.

    ``%``-comment lines are stripped first: this fixture's ``refs.bib`` carries
    a long header comment block that itself names entry keys and quotes titles,
    which would otherwise be picked up as if they were entries. Same
    implementation as the sibling bibtex gates', deliberately duplicated rather
    than imported -- these gate modules are independent characterisation
    records and must not be able to break each other.
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


@dataclass(frozen=True)
class CitingSite:
    """
    One parsed citing site: its role family, its inline form, and its keys.

    ``family`` is :data:`CITE_FAMILY` or :data:`FOOTCITE_FAMILY` -- the two
    render through DIFFERENT routes (definition grid vs. footnote), and every
    census below is per route, so the distinction has to survive parsing.
    ``form`` is the role's sub-name (``p`` for parenthetical, ``t`` for
    textual) or the empty string when the role has none, as ``footcite`` does.
    ``keys`` holds one entry per key the site names, so a multi-key site is ONE
    site carrying SEVERAL keys -- which is exactly the distinction the
    ``query(`` census needs: one site, two emitted guards.
    """

    family: str
    form: str
    keys: tuple[str, ...]


def _parse_citing_sites(rst_text: str) -> list[CitingSite]:
    """
    Return every ``:cite:*:`` **and** ``:footcite:`` site in one ``.rst``, in
    document order, one :class:`CitingSite` per SITE.

    Deliberately WIDER than the sibling gates' ``:cite:([a-z]*):`` pattern,
    which does NOT match the colonised ``:footcite:`` role -- measured against a
    footcite fixture it returns ``[]`` (MEM030), because the ``cite`` in
    ``footcite`` is not preceded by a colon. This fixture carries footcite
    sites, so the narrow pattern would have silently under-counted the citing
    sites and reduced every guard below to a vacuous pass.

    The sub-name group is OPTIONAL so the bare ``:footcite:`` spelling matches
    alongside ``:cite:p:`` / ``:cite:t:``; a role with no sub-name yields an
    empty ``form``.

    Regexes the RAW rst, so a FULLY-COLONISED role name written inside an rst
    comment would also count as a site (MEM022/MEM030's trap). Every comment in
    this fixture therefore writes role names un-colonised, and
    :func:`full_form_fixture_data`'s exact per-document site-count guards are
    what catch it if that ever slips.
    """
    sites: list[CitingSite] = []
    for family, form, argument in re.findall(
        r":((?:foot)?cite)(?::([a-z]+))?:`([^`]+)`", rst_text
    ):
        keys = tuple(key.strip() for key in argument.split(",") if key.strip())
        sites.append(CitingSite(family=family, form=form, keys=keys))
    return sites


def _parse_bibliography_directives(rst_text: str) -> list[str]:
    """
    Return one entry per ``.. bibliography::`` directive in one ``.rst``: the
    directive's inline argument plus its indented option block, concatenated.

    An empty string therefore means a BARE directive -- which is what this
    fixture's corpus-wide host mandates (no ``:filter:``, no ``:keyprefix:``, no
    ``:all:``) -- while a non-empty one is the chapter-local filtered directive
    whose options :func:`_parse_filter_keys` and :func:`_parse_keyprefix` read.

    Anchored at column 0 with ``re.MULTILINE`` on purpose, which also makes it
    NOT match ``.. footbibliography::``: every rst comment in this fixture is
    INDENTED, so an indented prose mention of the directive cannot be
    miscounted as a real one, and the footnote route's own directive is counted
    separately by :func:`_parse_footbibliography_directives`. The trailing
    ``(?:\\n|$)`` tolerates the directive being the file's last line with no
    trailing newline.
    """
    return [
        (argument + "\n" + options).strip()
        for argument, options in re.findall(
            r"^\.\. bibliography::[ \t]*([^\n]*)(?:\n|$)"
            r"((?:[ \t]+:[a-z]+:[^\n]*(?:\n|$))*)",
            rst_text,
            re.M,
        )
    ]


def _parse_footbibliography_directives(rst_text: str) -> int:
    """
    Return how many ``.. footbibliography::`` directives one ``.rst`` carries.

    Counted separately from :func:`_parse_bibliography_directives` because the
    two expand differently: ``footbibliography`` produces footnote nodes, never
    a definition grid, which is precisely why the footnote-route document's
    grid census stays ZERO while its footnote census is non-zero. Conflating
    them would make that zero-grid contract unassertable.

    Anchored at column 0 for the same reason as the sibling parser.
    """
    return len(re.findall(r"^\.\. footbibliography::[ \t]*$", rst_text, re.M))


def _parse_filter_keys(options: str, known_keys: set[str]) -> set[str]:
    """
    Return the ``refs.bib`` keys a directive's ``:filter:`` option names.

    Reads the quoted strings out of the option text and keeps those that are
    actual bib keys, which is what makes a filtered grid's OWNED key set
    derived rather than transcribed. The fixture's filter is measured to need
    the string on the LEFT of ``%`` (``"<key>" % key``); the ``key == "..."``
    comparison form is a silent degradation recorded in the fixture's own
    comments, and the positive per-grid row assertions below are what detect
    it, since the strict build stays clean through it.

    Intersecting with ``known_keys`` rather than trusting every quoted token
    keeps a future ``:filter:`` that also quotes a field name (``"article" %
    type``) from inflating the owned set.
    """
    quoted = re.findall(r'"([^"]+)"', options)
    return {token for token in quoted if token in known_keys}


def _parse_keyprefix(options: str) -> str:
    """
    Return a directive's ``:keyprefix:`` value, or the empty string if it has
    none.

    Parsed rather than typed because it is the SUBJECT of the no-leak assertion
    below: the gate asserts that this very string reaches neither the rendered
    label nor the emitted anchor, so reading it from the fixture is what keeps
    that assertion honest if the prefix is ever changed.
    """
    match = re.search(r":keyprefix:[ \t]*(\S+)", options)
    return match.group(1) if match else ""


def _parse_toctree_entries(rst_text: str) -> list[str]:
    """
    Return the docnames listed in the single ``.. toctree::`` of one ``.rst``,
    in document order.

    Anchored at column 0 for the same reason as
    :func:`_parse_bibliography_directives`. The entry lines are the indented
    non-option, non-blank lines following the directive; parsing stops at the
    first dedent. Document ORDER matters and is preserved: Sphinx assigns the
    citation anchor ids in assignment order, which follows the toctree
    (MEM043).
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
    namespacing scheme by construction. This is how the module expresses the
    cross-document property -- "a chapter's anchor is namespaced by the TARGET
    document, not by its own and not root-relative" -- without a single
    namespaced-id literal anywhere in this file, and without hard-coding the
    ``docname:id`` SHAPE either: a scheme change to, say, ``docname__id`` would
    be picked up here automatically.

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


def _footcite_refid(key: str) -> str:
    """
    Return the docutils footnote id sphinxcontrib-bibtex assigns to the
    footnote it generates for bibtex ``key``.

    Derived, not transcribed: upstream formats :data:`FOOTCITE_ID_TEMPLATE`
    with the entry key and normalises it through docutils' own ``make_id``
    (which is what lowercases a mixed-case bib key), then notes the footnote as
    an explicit target so docutils derives the node id from that name.
    """
    return make_id(FOOTCITE_ID_TEMPLATE.format(key=key))


def _footnote_label(docname: str, refid: str) -> str:
    """
    Return the Typst label typsphinx emits for a footnote whose docutils id is
    ``refid`` in ``docname``, computed by calling the translator's OWN helper
    rather than spelling the label out as a literal.

    ``translator.py``'s ``visit_footnote_reference`` has exactly one label
    derivation point, ``_namespace_label(docname, f"fn-{refid}")`` -- shared by
    both the definition branch and the reuse branch -- so reproducing that call
    here is the whole expectation, and it is what makes "the reuse form names
    the SAME label as the definition" a real claim rather than a string guess.
    """
    return TypstTranslator._namespace_label(TypstTranslator, docname, f"fn-{refid}")


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


@dataclass
class FullFormFixtureData:
    """
    What the fixture itself authors, parsed out of ``refs.bib`` and the ``.rst``
    files -- never transcribed into this module.

    Every document ROLE is derived too, not assumed: the master is the one
    document carrying a ``.. toctree::``, ``bare_bibliography_docname`` the one
    whose ``.. bibliography::`` carries no options, ``filtered_docname`` the one
    whose directive carries a ``:filter:``, and ``footnote_docname`` the one
    carrying ``footcite`` sites. That is how the fixture's arrangement is
    CHECKED rather than taken on trust.
    """

    titles: dict[str, str]
    authors: dict[str, str]
    master_docname: str
    bare_bibliography_docname: str
    filtered_docname: str
    filtered_options: str
    footnote_docname: str
    toctree_entries: list[str]
    citing_sites: dict[str, list[CitingSite]]
    bibliographies: dict[str, list[str]]
    footbibliographies: dict[str, int]
    rst_text: dict[str, str]

    @property
    def docnames(self) -> list[str]:
        """Every document in the fixture, sorted."""
        return sorted(self.rst_text)

    def cite_sites(self, docname: str) -> list[CitingSite]:
        """``docname``'s ``:cite:*:`` sites (the grid route), in order."""
        return [
            site for site in self.citing_sites[docname] if site.family == CITE_FAMILY
        ]

    def footcite_sites(self, docname: str) -> list[CitingSite]:
        """``docname``'s ``:footcite:`` sites (the footnote route), in order."""
        return [
            site
            for site in self.citing_sites[docname]
            if site.family == FOOTCITE_FAMILY
        ]

    def cite_keys_in_order(self, docname: str) -> list[str]:
        """
        Every key ``docname``'s ``:cite:*:`` sites name, FLATTENED in document
        order -- one entry per key per site.

        This is the emitted-guard order: the translator emits one guarded
        ``link()`` per key named, so a multi-key site contributes several
        entries here. It is what lets a guard be attributed to the key whose
        site produced it.
        """
        return [key for site in self.cite_sites(docname) for key in site.keys]

    @property
    def grid_keys(self) -> set[str]:
        """
        Every key reached through the ``:cite:*:`` (grid) route anywhere in the
        corpus.

        This is what a BARE ``.. bibliography::`` renders: only CITED entries
        (MEM006). The footnote route's keys are deliberately excluded -- they
        are rendered by ``footbibliography`` and must appear in NO grid.
        """
        return {
            key
            for docname in self.rst_text
            for site in self.cite_sites(docname)
            for key in site.keys
        }

    @property
    def footcite_keys(self) -> set[str]:
        """Every key reached through the ``:footcite:`` (footnote) route."""
        return {
            key
            for docname in self.rst_text
            for site in self.footcite_sites(docname)
            for key in site.keys
        }

    @property
    def uncited_keys(self) -> set[str]:
        """Every ``refs.bib`` key no citing site of either family names."""
        return set(self.titles) - self.grid_keys - self.footcite_keys

    @property
    def filtered_keys(self) -> set[str]:
        """The keys the chapter-local filtered bibliography is scoped to."""
        return _parse_filter_keys(self.filtered_options, set(self.titles))

    @property
    def keyprefix(self) -> str:
        """The chapter-local directive's ``:keyprefix:`` value."""
        return _parse_keyprefix(self.filtered_options)

    def owned_keys(self, docname: str) -> set[str]:
        """
        The keys the single grid in ``docname`` is expected to render a row for.

        Bare directive -> every grid-route key in the corpus. Filtered
        directive -> the filter's own keys intersected with the keys something
        actually cites, because MEM006's "only cited entries" rule applies
        inside a filter too.
        """
        if docname == self.bare_bibliography_docname:
            return set(self.grid_keys)
        return self.filtered_keys & self.grid_keys

    def expected_grid_count(self, docname: str) -> int:
        """
        How many ``grid(`` calls ``docname`` must emit: one per
        ``.. bibliography::`` it carries.

        ``footbibliography`` contributes ZERO, which is the zero-grid contract
        that proves the footnote route and the grid route do not interfere.
        """
        return len(self.bibliographies[docname])

    def expected_footnote_count(self, docname: str) -> int:
        """
        How many ``footnote(`` calls ``docname`` must emit: one per
        ``:footcite:`` SITE.

        One per site, not one per KEY -- the first site on a key emits the
        definition form and every later site the bare reuse form, and both
        spell ``footnote(``. Counting sites is therefore what makes "the repeat
        site reused rather than redefined" visible when combined with the
        exactly-one-definition assertion.
        """
        return sum(len(site.keys) for site in self.footcite_sites(docname))

    def expected_query_count(self, docname: str) -> int:
        """
        How many guarded ``query(`` calls ``docname`` must emit: one per KEY
        named by its ``:cite:*:`` sites.

        Per key, not per site: a single multi-key site emits one guard per key
        it names, which is exactly why the chapter carrying the multi-key site
        has a higher query census than its site count.
        """
        return len(self.cite_keys_in_order(docname))


@pytest.fixture(scope="module")
def full_form_fixture_data(full_form_gate_dir):
    """
    Parse the fixture into the data every assertion compares against, with
    vacuous-pass guards in the S01 style so a fixture edit that breaks a parse
    fails LOUDLY here rather than quietly degrading the counts below.

    The guards are deliberately EXACT, and each NAMES its subject. This gate's
    whole subject is one specific arrangement -- four entries, three toctree
    entries, TWO ``.. bibliography::`` directives in two different non-master
    documents (one bare, one filtered with a keyprefix), one
    ``footbibliography``, all four inline citing forms, exactly one permanently
    uncited entry -- and a slice that changes any of it must update these
    numbers deliberately.
    """
    bib_text = (full_form_gate_dir / "refs.bib").read_text(encoding="utf-8")
    titles = _parse_bib_field(bib_text, "title")
    authors = _parse_bib_field(bib_text, "author")

    assert len(titles) == 4, (
        "Vacuous-pass guard: expected exactly FOUR entries parsed out of the "
        "fixture's refs.bib (three cited across the grid and footnote routes, "
        f"one deliberately uncited) but parsed {sorted(titles)}. Did refs.bib's "
        "entry formatting change? With no entries every per-grid row count "
        "below would compare against nothing."
    )
    assert set(authors) == set(titles), (
        "Vacuous-pass guard: every refs.bib entry must yield BOTH a title and "
        f"an author (titles: {sorted(titles)}, authors: {sorted(authors)}). "
        "The textual-form assertion needs the author field of the key its "
        "chapter cites."
    )
    assert len(set(titles.values())) == len(titles), (
        "Vacuous-pass guard: refs.bib's titles must be PAIRWISE DISTINCT, "
        "otherwise a per-grid 'exactly one row for this key' count can be "
        f"satisfied by another entry's text: {sorted(titles.values())}."
    )

    rst_paths = sorted(full_form_gate_dir.glob("*.rst"))
    assert len(rst_paths) == 4, (
        "Vacuous-pass guard: expected FOUR .rst documents in the fixture (a "
        "pure-toctree master, the four-citing-form chapter, the "
        "filtered-bibliography chapter and the corpus-wide bibliography host) "
        f"but found {[path.name for path in rst_paths]}."
    )
    rst_text = {path.stem: path.read_text(encoding="utf-8") for path in rst_paths}

    citing_sites = {
        docname: _parse_citing_sites(text) for docname, text in rst_text.items()
    }
    bibliographies = {
        docname: _parse_bibliography_directives(text)
        for docname, text in rst_text.items()
    }
    footbibliographies = {
        docname: _parse_footbibliography_directives(text)
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
        f"siblings but its toctree lists {toctree_entries}. The emitted anchor "
        "ids this gate matches are toctree-assignment-order dependent "
        "(MEM043), so a changed toctree must be a deliberate edit."
    )
    for entry in toctree_entries:
        assert entry in rst_text, (
            f"The master's toctree names {entry!r}, for which the fixture has "
            f"no {entry}.rst (documents found: {sorted(rst_text)})."
        )

    # (b) TWO .. bibliography:: directives, in TWO DIFFERENT non-master
    # documents: one BARE (corpus-wide) and one FILTERED with a :keyprefix:
    # (chapter-local). Their coexistence is the whole point of this fixture.
    hosts = {docname: found for docname, found in bibliographies.items() if found}
    assert sum(len(found) for found in hosts.values()) == 2, (
        "This fixture must carry exactly TWO .. bibliography:: directives -- "
        "that coexistence is what S06 exists to prove -- but parsed "
        f"{ {docname: len(found) for docname, found in hosts.items()} }. One "
        "would make this the single-bibliography route (S05's fixture); three "
        "would change every per-grid census below."
    )
    assert len(hosts) == 2, (
        "The two .. bibliography:: directives must live in TWO DIFFERENT "
        f"documents, but both were parsed from {sorted(hosts)}. Hosting them "
        "in one document would make the per-document grid census unable to "
        "attribute a grid to its own directive."
    )
    assert master_docname not in hosts, (
        f"Neither .. bibliography:: may live in the master ({master_docname}) "
        f"-- the D012 precedent -- but directives were parsed from "
        f"{sorted(hosts)}. Hosting one there would let a "
        "chapter-to-bibliography link be satisfied by the master's own page "
        "without crossing an #include() boundary in the direction under test."
    )
    bare_hosts = [docname for docname, found in hosts.items() if found[0] == ""]
    assert len(bare_hosts) == 1, (
        "Exactly ONE of the two .. bibliography:: directives must be BARE (no "
        ":filter:, no :keyprefix:, no :all:) -- it is the corpus-wide one -- "
        f"but the bare hosts are {bare_hosts}. An :all: option on it would "
        "surface the deliberately uncited entry and void MEM006's zero-count "
        "assertion, which is what keeps every other count non-vacuous."
    )
    bare_bibliography_docname = bare_hosts[0]
    filtered_hosts = [
        docname for docname in hosts if docname != bare_bibliography_docname
    ]
    filtered_docname = filtered_hosts[0]
    filtered_options = hosts[filtered_docname][0]
    assert ":filter:" in filtered_options, (
        f"The non-bare .. bibliography:: in {filtered_docname}.rst must carry a "
        f":filter: option, but its options parsed as {filtered_options!r}. "
        "Without a filter it is a second corpus-wide bibliography and the "
        "chapter-local route this gate scopes its counts to does not exist."
    )
    assert _parse_keyprefix(filtered_options), (
        f"The chapter-local .. bibliography:: in {filtered_docname}.rst must "
        "keep its :keyprefix: -- it is load-bearing, not cosmetic: without it "
        "sphinxcontrib-bibtex reports a duplicate citation id for the key both "
        "directives cover and the strict (-W) build FAILS. Parsed options: "
        f"{filtered_options!r}."
    )
    for docname in hosts:
        assert docname in toctree_entries, (
            f"The bibliography host {docname!r} must itself be a toctree entry "
            f"of the master, but the toctree lists {toctree_entries}. "
            "Otherwise it is never #include()d and its grid never reaches the "
            "master."
        )

    # (c) The master contributes no citing site and no directive of either
    # family: either would let the same-document (unguarded) path contaminate
    # the cross-document measurement.
    assert citing_sites[master_docname] == [], (
        f"The master ({master_docname}.rst) must carry ZERO citing sites, but "
        f"{citing_sites[master_docname]} were parsed. A citing site in the "
        "master resolves SAME-document and would emit an unguarded link. "
        "(NOTE: this regexes the RAW rst, so a fully-colonised cite or "
        "footcite role written inside an rst comment also counts -- MEM030.)"
    )
    assert footbibliographies[master_docname] == 0, (
        f"The master ({master_docname}.rst) must carry no .. footbibliography:: "
        "either; the footnote route lives entirely beside its own citing sites."
    )

    # (d) The corpus-wide host contributes no citing site, so every row it
    # emits originates in a DIFFERENT document.
    assert citing_sites[bare_bibliography_docname] == [], (
        f"The corpus-wide bibliography host ({bare_bibliography_docname}.rst) "
        f"must carry ZERO citing sites, but {citing_sites[bare_bibliography_docname]} "
        "were parsed. Its grid rows must originate exclusively in the chapter "
        "documents, or 'this row was reached from another document' stops "
        "being true."
    )

    # (e) The footnote route: exactly one document carries footcite sites, and
    # exactly that document carries the single .. footbibliography::.
    footnote_hosts = [
        docname
        for docname, sites in citing_sites.items()
        if any(site.family == FOOTCITE_FAMILY for site in sites)
    ]
    assert len(footnote_hosts) == 1, (
        "Exactly ONE document must carry the :footcite: sites, so the footnote "
        f"route's per-document census is unambiguous, but found {footnote_hosts}. "
        "If this is EMPTY, the widened citing-site parser stopped matching the "
        "footcite role family and every footnote count below is vacuous "
        "(MEM030's trap)."
    )
    footnote_docname = footnote_hosts[0]
    assert footbibliographies[footnote_docname] == 1, (
        f"The footnote-route document ({footnote_docname}.rst) must carry "
        "exactly ONE .. footbibliography:: -- the directive that renders its "
        f"footnote bodies -- but parsed {footbibliographies[footnote_docname]}."
    )
    assert sum(footbibliographies.values()) == 1, (
        "The fixture must carry exactly ONE .. footbibliography:: in total, "
        f"but parsed {footbibliographies}. A second one would duplicate "
        "footnote bodies and void the footnote route's exactly-once count."
    )
    assert bibliographies[footnote_docname] == [], (
        f"The footnote-route document ({footnote_docname}.rst) must carry NO "
        ".. bibliography:: -- its zero-grid census is what proves the footnote "
        "route and the grid route do not interfere -- but parsed "
        f"{bibliographies[footnote_docname]}."
    )

    data = FullFormFixtureData(
        titles=titles,
        authors=authors,
        master_docname=master_docname,
        bare_bibliography_docname=bare_bibliography_docname,
        filtered_docname=filtered_docname,
        filtered_options=filtered_options,
        footnote_docname=footnote_docname,
        toctree_entries=toctree_entries,
        citing_sites=citing_sites,
        bibliographies=bibliographies,
        footbibliographies=footbibliographies,
        rst_text=rst_text,
    )

    # (f) All four inline citing FORMS are present, each exactly once in the
    # role spelling that defines it. These are the subjects of the four
    # "form is resolved" assertions; if any count drifts, the corresponding
    # assertion would silently test a different shape.
    parenthetical = [
        (docname, site)
        for docname in data.docnames
        for site in data.cite_sites(docname)
        if site.form == "p"
    ]
    textual = [
        (docname, site)
        for docname in data.docnames
        for site in data.cite_sites(docname)
        if site.form == "t"
    ]
    multi_key = [
        (docname, site)
        for docname in data.docnames
        for site in data.cite_sites(docname)
        if len(site.keys) > 1
    ]
    assert len(textual) == 1, (
        "Exactly ONE citing site must use the TEXTUAL :cite:t: form -- the "
        "surname-outside-the-bracket shape is the only thing distinguishing it "
        f"from the parenthetical form -- but found {textual}."
    )
    assert len(multi_key) == 1, (
        "Exactly ONE citing site must name SEVERAL keys (the multi-key form), "
        f"but found {multi_key}. Splitting it into single-key sites would keep "
        "the query census unchanged while destroying the route itself."
    )
    assert len(multi_key[0][1].keys) == 2, (
        "The multi-key site must name exactly TWO keys, because the "
        "'one bracket group, one guard per key, comma-separated' assertion is "
        f"written for two: it names {multi_key[0][1].keys}."
    )
    assert len(set(multi_key[0][1].keys)) == 2, (
        "The multi-key site names the same key twice "
        f"({multi_key[0][1].keys}), so its two guards would be "
        "indistinguishable and the per-key attribution untestable."
    )
    single_key_parenthetical = [
        (docname, site) for docname, site in parenthetical if len(site.keys) == 1
    ]
    assert len(single_key_parenthetical) == 2, (
        "Exactly TWO single-key PARENTHETICAL :cite:p: sites must exist -- one "
        "in the four-form chapter and one in the filtered-bibliography chapter "
        f"-- but found {single_key_parenthetical}."
    )

    # (g) The footnote route: one key, cited by more than one site, so the
    # definition-plus-reuse shape has a subject.
    footcite_keys = sorted(data.footcite_keys)
    assert len(footcite_keys) == 1, (
        "The footnote route must cover EXACTLY ONE key, so its exactly-one-body "
        f"count cannot be satisfied by another key's body, but parsed {footcite_keys}."
    )
    footcite_site_count = len(data.footcite_sites(footnote_docname))
    assert footcite_site_count == 2, (
        f"The footnote-route key must be cited by exactly TWO :footcite: sites "
        f"(the definition site and the reuse site) but parsed "
        f"{footcite_site_count}. With one site there is no reuse form to "
        "assert and the doubled-body regression becomes undetectable."
    )
    assert footcite_keys[0] not in data.grid_keys, (
        f"The footnote-route key {footcite_keys[0]!r} is ALSO cited through the "
        f":cite:*: grid route (grid keys: {sorted(data.grid_keys)}). The "
        "footnote route's exactly-once count would then be satisfiable by a "
        "grid row, which is precisely what it must not be."
    )

    # (h) The negative control: exactly one permanently uncited entry.
    uncited = sorted(data.uncited_keys)
    assert len(uncited) == 1, (
        "The fixture keeps EXACTLY ONE deliberately uncited refs.bib entry so "
        "MEM006's zero-count assertion has a subject and every exactly-once "
        f"count stays non-vacuous, but the uncited set is {uncited}. If a later "
        "slice needs another CITED entry, APPEND a new uncited one rather than "
        "weakening this guard."
    )
    assert uncited[0] not in data.filtered_keys, (
        f"The uncited entry {uncited[0]!r} is named by the chapter-local "
        ":filter:, so it could legitimately render and its zero-count "
        "assertion could never hold."
    )

    # (i) The two grids must own DIFFERENT key sets, and the filtered one must
    # be a strict subset -- otherwise "per-route" scoping has nothing to scope.
    bare_owned = data.owned_keys(bare_bibliography_docname)
    filtered_owned = data.owned_keys(filtered_docname)
    assert filtered_owned, (
        f"The chapter-local filtered bibliography in {filtered_docname}.rst "
        "owns NO key: its :filter: names "
        f"{sorted(data.filtered_keys)} and the corpus's cited grid keys are "
        f"{sorted(data.grid_keys)}. Its per-grid row assertion would compare "
        "against nothing. This is the measured signature of the filter being "
        "rewritten into the key-on-left comparison form, which degrades "
        "SILENTLY -- the strict build stays clean through it."
    )
    assert filtered_owned < bare_owned, (
        "The chapter-local grid must own a STRICT SUBSET of the corpus-wide "
        f"grid's keys (filtered: {sorted(filtered_owned)}, bare: "
        f"{sorted(bare_owned)}). Equal sets would make the two grids "
        "indistinguishable; a key only the filtered grid owns would mean the "
        "corpus-wide one stopped rendering a cited entry."
    )

    return data


# ---------------------------------------------------------------------------
# Builds. Two flavours, each running EXACTLY ONCE per module in its own build
# directory so no incremental-rebuild cache can let one mask the other:
#   * -b typst          -> every emitted-markup assertion below
#   * -b typst -E -W    -> the strict/clean-build assertion, under LC_ALL=C
# Both are -b typst rather than -b typstpdf on purpose, so this whole half runs
# on a machine without typst-py; T03's compiled-PDF and cross-builder half gets
# its own builds behind PDF_DEPS_AVAILABLE.
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
class FullFormGateBuild:
    """One real build of the full-form fixture, captured once."""

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
def full_form_gate_build(full_form_gate_dir, tmp_path_factory):
    """
    Build the fixture with ``-b typst`` EXACTLY ONCE for the whole module.

    Asserts a clean exit here: this gate is green on arrival, so a non-zero
    build IS the regression it exists to catch, and reporting it once in the
    fixture is clearer than letting it surface as several unrelated assertion
    failures.
    """
    build_dir = tmp_path_factory.mktemp("full_form_gate_typ") / "_build"
    result = _run_sphinx_build(full_form_gate_dir, build_dir)
    assert result.returncode == 0, (
        "sphinx-build -b typst over the full-form bibliography fixture must "
        "succeed (this gate locks measured-working behaviour and is green on "
        f"arrival)\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    return FullFormGateBuild(result=result, build_dir=build_dir)


@pytest.fixture(scope="module")
def full_form_gate_strict_build(full_form_gate_dir, tmp_path_factory):
    """
    Build the fixture with ``-b typst -E -W`` EXACTLY ONCE, in its OWN build
    directory, with ``LANG`` / ``LANGUAGE`` unset and ``LC_ALL=C``.

    ``-E`` discards any saved environment so the warnings a cached build would
    not re-emit are actually produced; ``-W`` turns every warning into an error.
    The locale is forced because this project's dev shell passes the host's
    Japanese ``LANG`` through and Sphinx localises its output -- the bibtex
    warning CODES are never localised, but forcing the locale is what lets the
    zero-``WARNING``-line check below be meaningful too.

    Deliberately does NOT assert the exit code: the strict test owns that, so a
    regression is reported as a named test failure rather than as a fixture
    error.
    """
    build_dir = tmp_path_factory.mktemp("full_form_gate_typ_strict") / "_build"
    env = dict(os.environ)
    env["LC_ALL"] = "C"
    env.pop("LANG", None)
    env.pop("LANGUAGE", None)
    result = _run_sphinx_build(
        full_form_gate_dir, build_dir, extra_args=("-E", "-W"), env=env
    )
    return FullFormGateBuild(result=result, build_dir=build_dir)


# ---------------------------------------------------------------------------
# Emitted-markup parsing. PER GRID and PER ROW, never document-wide, wherever
# the content of a particular region is what carries the claim (MEM035) -- and
# in this module that is everywhere, because the fixture emits TWO grids and
# a document-wide count cannot attribute a row to the directive that owns it.
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

    This is the per-region helper MEM035 mandates and the critical one for this
    slice: the fixture emits MORE THAN ONE grid, and the D013 exactly-once
    property is scoped PER GRID. A document-wide count cannot distinguish "two
    grids each holding one row for a key" (correct, and measured) from "one
    grid holding that key's row twice" (the duplication regression).
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


def _guard_pattern(anchor: str, label: str) -> str:
    """
    Return the regex source for ONE guarded cross-document link: the exact
    shape ``_label_existence_guard`` emits for ``anchor``, carrying ``label``
    as its body text.

    Returned as a FRAGMENT so the four citing-form assertions can embed it in a
    single contiguous pattern together with the surrounding brackets and
    separators. That is the whole point: matching the form as one regex is what
    makes the ORDERING part of the claim, which three independent membership
    checks could never do (MEM021).

    ``\\s*`` appears throughout because the emitted guard carries a real
    newline inside its ``let`` binding, between ``[#{`` and the body's
    ``text(...)``; callers additionally compile with ``re.DOTALL``.
    """
    ident = re.escape(GUARD_BODY_IDENT)
    return (
        r"context\s*\{\s*let\s+" + ident + r"\s*=\s*\[#\{\s*"
        r'text\("' + re.escape(label) + r'"\)\}\];\s*'
        r"if\s+query\(<" + re.escape(anchor) + r">\)\.len\(\)\s*>\s*0\s*\{\s*"
        r"link\(<" + re.escape(anchor) + r">,\s*" + ident + r"\)\s*\}\s*"
        r"else\s*\{\s*" + ident + r"\s*\}\s*\}"
    )


def _guarded_anchors(typ_text: str) -> list[str]:
    """
    Return the anchor of every GUARDED cross-document link in one ``.typ``, in
    document order.

    The subject is ``_label_existence_guard``'s emitted shape: a ``context``
    block that binds the reference body to ``__tsx_body``, then links only
    ``if query(<L>).len() > 0``. Matching the whole guard as ONE contiguous
    pattern with a BACKREFERENCE (``<\\1>`` in the ``link()``) -- rather than
    collecting ``query(`` and ``link(`` hits separately -- is what makes "this
    site IS guarded" a real claim: it pins that the SAME label appears in the
    query and in the link, and that the fallback is the plain body. A pair of
    independent membership checks would also pass for a bare ``link()`` sitting
    beside an unrelated ``query()``, which is the S05 strengthening that proved
    load-bearing.
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


def _definition_marker(label: str) -> str:
    """
    Return the tail of the label-attached footnote DEFINITION form for
    ``label``: the ``}) <label>]`` closing of ``[#footnote({...}) <label>]``.

    Counting this tail rather than the whole form is what makes "exactly one
    definition per key" checkable without brace-matching: the opening
    ``[#footnote({`` carries no label, so only this tail identifies WHICH
    footnote a definition belongs to. It also cannot be confused with the reuse
    form, which emits no ``}) <`` at all.
    """
    return f"}}) <{label}>]"


def _reuse_marker(label: str) -> str:
    """Return the bare REUSE form for ``label``: ``footnote(<label>)``."""
    return f"footnote(<{label}>)"


def _definition_body(content_typ: str, label: str) -> str:
    """
    Return the body text inside ``label``'s footnote DEFINITION form.

    Spans from the ``[#footnote({`` opening nearest BEFORE the definition tail
    to that tail. Asserts there is exactly one such definition and that the span
    contains no further label attachment -- a nested or mis-spanned extraction
    would otherwise let one entry's body satisfy another entry's assertion.
    """
    tail = _definition_marker(label)
    assert content_typ.count(tail) == 1, (
        f"Expected exactly ONE footnote DEFINITION form for label {label!r} in "
        f"the footnote route's document, found {content_typ.count(tail)} "
        f"occurrences of {tail!r}; cannot extract its body unambiguously."
    )
    tail_at = content_typ.index(tail)
    opening = "[#footnote({"
    open_at = content_typ.rfind(opening, 0, tail_at)
    assert open_at != -1, (
        f"Found the definition tail {tail!r} but no preceding {opening!r} "
        "opening, so the emitted form is not the documented bracket-wrapped "
        "definition shape [#footnote({...}) <label>]."
    )
    body = content_typ[open_at + len(opening) : tail_at]
    assert "}) <" not in body, (
        f"The extracted definition body for {label!r} contains another label "
        "attachment, so the span crossed a neighbouring footnote and the body "
        f"assertion would be meaningless: {body!r}"
    )
    return body


@dataclass
class ParsedGrid:
    """One grid parsed out of the document that hosts it."""

    docname: str
    rows: list[GridRow]
    region: str

    def row_for_anchor(self, anchor: str) -> GridRow | None:
        """The row anchored at ``anchor``, or ``None`` if no row is."""
        return next((row for row in self.rows if row.anchor == anchor), None)

    @property
    def anchors(self) -> list[str]:
        """Every row anchor, in document order."""
        return [row.anchor for row in self.rows]

    @property
    def labels(self) -> list[str]:
        """Every row's rendered pybtex label, in document order."""
        return [row.label for row in self.rows]


@pytest.fixture(scope="module")
def parsed_grids(full_form_gate_build, full_form_fixture_data) -> dict[str, ParsedGrid]:
    """
    Parse the single grid out of EACH bibliography-hosting document, keyed by
    docname, with vacuous-pass guards so a failure to parse rows cannot make a
    per-grid assertion pass against an empty row set.

    Scoped per host document rather than corpus-wide because that is the unit
    D013's exactly-once property applies to in this fixture: two directives,
    two grids, two independently-owned key sets.
    """
    grids: dict[str, ParsedGrid] = {}
    for docname in (
        full_form_fixture_data.bare_bibliography_docname,
        full_form_fixture_data.filtered_docname,
    ):
        blocks = _iter_grid_blocks(full_form_gate_build.read_typ(docname))
        assert len(blocks) == 1, (
            f"The bibliography host {docname}.typ must carry exactly ONE grid( "
            f"call -- it holds exactly one .. bibliography:: directive -- but "
            f"carries {len(blocks)}."
        )
        rows = _parse_grid_rows(blocks[0])
        owned = full_form_fixture_data.owned_keys(docname)
        assert len(rows) == len(owned), (
            "Vacuous-pass guard: parsed "
            f"{len(rows)} row(s) out of {docname}.typ's grid but that "
            f"directive owns {len(owned)} key(s) ({sorted(owned)}), and a "
            "bibliography renders exactly the CITED ones within its filter "
            f"(MEM006). Parsed labels: {[row.label for row in rows]}. If zero, "
            "the row label-cell shape changed and every per-grid comparison "
            "below would compare against nothing."
        )
        assert len({row.anchor for row in rows}) == len(rows), (
            f"Two rows of {docname}.typ's grid share one Typst anchor, so "
            f"attributing a link to a row is ambiguous: {[row.anchor for row in rows]}."
        )
        grids[docname] = ParsedGrid(docname=docname, rows=rows, region=blocks[0])
    return grids


# ---------------------------------------------------------------------------
# The gate.
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not BIBTEX_AVAILABLE,
    reason="sphinxcontrib-bibtex is required for the full-form bibliography gate",
)
class TestPerFileCensus:
    """
    The per-document census of ``grid(``, ``footnote(`` and guarded ``query(``
    calls, every expectation DERIVED from the fixture's own sources.

    This is the structural frame every later assertion stands on. In particular
    the footnote-route document's ZERO grid count is the proof that the two
    routes do not interfere: its ``footbibliography`` renders footnote bodies
    and contributes no definition grid, so a grid appearing there would mean
    the footnote route started leaking into the grid route.
    """

    def test_grid_count_matches_the_bibliography_directive_count_per_document(
        self, full_form_gate_build, full_form_fixture_data
    ):
        """
        Each emitted document carries exactly one ``grid(`` per
        ``.. bibliography::`` its source holds -- and ZERO where it holds none,
        including the footnote-route document and the master.
        """
        for docname in full_form_fixture_data.docnames:
            text = full_form_gate_build.read_typ(docname)
            found = len(_iter_grid_blocks(text))
            expected = full_form_fixture_data.expected_grid_count(docname)
            assert found == expected, (
                f"Document {docname}.typ must emit {expected} grid( call(s) -- "
                "one per .. bibliography:: directive parsed from "
                f"{docname}.rst -- but emitted {found}. A grid where none is "
                "expected means a bibliography route started rendering in the "
                "wrong document; in the footnote route's document "
                f"({full_form_fixture_data.footnote_docname}) it would "
                "specifically mean footbibliography stopped routing through "
                "footnotes.\n{text}".format(text=text)
            )

    def test_footnote_count_matches_the_footcite_site_count_per_document(
        self, full_form_gate_build, full_form_fixture_data
    ):
        """
        Each emitted document carries exactly one ``footnote(`` per
        ``:footcite:`` key named in its source -- the definition form at the
        first site and the bare reuse form at the repeat site -- and ZERO
        everywhere else.
        """
        for docname in full_form_fixture_data.docnames:
            text = full_form_gate_build.read_typ(docname)
            found = text.count("footnote(")
            expected = full_form_fixture_data.expected_footnote_count(docname)
            assert found == expected, (
                f"Document {docname}.typ must emit {expected} footnote( call(s) "
                "-- one per :footcite: key parsed from "
                f"{docname}.rst -- but emitted {found}. Fewer means a footcite "
                "site stopped rendering as a Typst footnote; more means a "
                "footnote body was duplicated, which is the exact regression "
                "the footnote route's exactly-once count exists to catch."
                f"\n{text}"
            )

    def test_guarded_query_count_matches_the_cited_key_count_per_document(
        self, full_form_gate_build, full_form_fixture_data
    ):
        """
        Each emitted document carries exactly one GUARDED ``query(`` per key
        named by its ``:cite:*:`` sites -- so the multi-key site contributes
        two -- and the master and the corpus-wide host carry none.

        The count is of fully-matched GUARDS, not of the substring ``query(``:
        a bare ``query()`` with no ``link()`` on the same label would not be
        counted here at all.
        """
        for docname in full_form_fixture_data.docnames:
            text = full_form_gate_build.read_typ(docname)
            guards = _guarded_anchors(text)
            expected = full_form_fixture_data.expected_query_count(docname)
            assert len(guards) == expected, (
                f"Document {docname}.typ must emit {expected} guarded "
                "cross-document link(s) -- one per key named by the :cite:*: "
                f"sites parsed from {docname}.rst -- but emitted "
                f"{len(guards)} ({guards}). Note the count is per KEY, not per "
                "site: the multi-key site emits one guard per key it names."
                f"\n{text}"
            )
            assert text.count("query(") == len(guards), (
                f"Document {docname}.typ emits {text.count('query(')} query( "
                f"call(s) but only {len(guards)} of them are part of a "
                "fully-matched existence guard. An unguarded or half-formed "
                "query means a citing site lost its link( on the same label, "
                "i.e. a silently dead reference (D011)."
                f"\n{text}"
            )


@pytest.mark.skipif(
    not BIBTEX_AVAILABLE,
    reason="sphinxcontrib-bibtex is required for the full-form bibliography gate",
)
class TestAllFourCitingFormsAreResolved:
    """
    All four citing forms are present AND resolved: each renders as a genuine
    guarded ``link()`` (or, on the footnote route, a real Typst footnote), not
    as inert text.

    Each inline form is matched as ONE contiguous regex rather than as several
    membership checks, because the ORDERING is the requirement -- and for the
    textual form specifically because the surname and the opening bracket
    arrive in a SINGLE text node, so separate checks could not prove the
    surname precedes the bracket at all (MEM021).
    """

    def test_parenthetical_form_is_a_resolved_guarded_link(
        self, full_form_gate_build, full_form_fixture_data, parsed_grids
    ):
        """
        Every single-key ``:cite:p:`` site renders as ``text("[")`` + the
        guarded link carrying that entry's own grid row label + ``text("]")``,
        contiguously, exactly once in its document.
        """
        target = parsed_grids[full_form_fixture_data.bare_bibliography_docname]
        sites = [
            (docname, site)
            for docname in full_form_fixture_data.docnames
            for site in full_form_fixture_data.cite_sites(docname)
            if site.form == "p" and len(site.keys) == 1
        ]
        assert sites, (
            "Vacuous-pass guard: no single-key parenthetical :cite:p: site was "
            "parsed out of the fixture, so this assertion has no subject."
        )
        for docname, site in sites:
            key = site.keys[0]
            text = full_form_gate_build.read_typ(docname)
            anchors = _guarded_anchors(text)
            row = next(
                (
                    target.row_for_anchor(anchor)
                    for anchor in anchors
                    if target.row_for_anchor(anchor) is not None
                    and full_form_fixture_data.titles[key]
                    in target.row_for_anchor(anchor).body
                ),
                None,
            )
            assert row is not None, (
                f"No guard in {docname}.typ targets the corpus-wide grid row "
                f"whose body renders {key!r} ({full_form_fixture_data.titles[key]!r}). "
                f"Guards found: {anchors}; grid anchors: {target.anchors}."
            )
            pattern = re.compile(
                r'text\("\["\)\s*'
                + _guard_pattern(row.anchor, row.label)
                + r'\s*text\("\]"\)',
                re.S,
            )
            found = len(pattern.findall(text))
            assert found == 1, (
                f"The parenthetical :cite:p: site for {key!r} in {docname}.typ "
                "must render as EXACTLY ONE contiguous "
                "bracket-guard-bracket group targeting "
                f"{row.anchor!r} with the label {row.label!r} (both read from "
                f"the corpus-wide grid's own row), but found {found}. Zero "
                "means the parenthetical form stopped resolving to a guarded "
                "link -- e.g. it degraded to inert text, or the guard and the "
                "brackets are no longer contiguous."
                f"\nPattern: {pattern.pattern}\n{text}"
            )

    def test_textual_form_keeps_surname_outside_the_bracket_group(
        self, full_form_gate_build, full_form_fixture_data, parsed_grids
    ):
        """
        The textual (``:cite:t:``) site emits its author surname OUTSIDE the
        bracket group, with the guarded cross-document link inside it.

        Matched as a SINGLE contiguous regex because the surname and the
        opening bracket arrive in ONE text node (measured shape:
        ``text("<Surname> [")``, then the guard, then ``text("]")``), so three
        membership checks would pass on a broken ordering (MEM021).
        ``re.DOTALL`` plus ``\\s*`` absorb the newline
        ``_label_existence_guard`` emits inside its ``let`` binding.

        The surname is parsed out of ``refs.bib``'s author field and the label
        out of the grid's own row; the anchor is read from the emitted markup.
        Nothing here is a literal.
        """
        textual = [
            (docname, site)
            for docname in full_form_fixture_data.docnames
            for site in full_form_fixture_data.cite_sites(docname)
            if site.form == "t"
        ]
        assert len(textual) == 1, (
            "Vacuous-pass guard: exactly one textual :cite:t: site must be "
            f"parsed out of the fixture, but found {textual}."
        )
        docname, site = textual[0]
        key = site.keys[0]
        surname = _author_surname(full_form_fixture_data.authors[key])
        assert surname, (
            "No surname could be parsed out of refs.bib's author field for "
            f"{key!r} ({full_form_fixture_data.authors[key]!r}), so the "
            "textual form's defining token is missing."
        )

        target = parsed_grids[full_form_fixture_data.bare_bibliography_docname]
        title = full_form_fixture_data.titles[key]
        row = next((row for row in target.rows if title in row.body), None)
        assert row is not None, (
            f"The corpus-wide grid has no row whose body renders {key!r} "
            f"({title!r}); grid labels: {target.labels}."
        )

        text = full_form_gate_build.read_typ(docname)
        pattern = re.compile(
            # ... ONE text node carrying the surname AND the opening bracket,
            # surname first -- this is the whole of the textual form ...
            r'text\("' + re.escape(surname) + r'\s*\["\)\s*'
            # ... then the GUARDED cross-document link inside the brackets ...
            + _guard_pattern(row.anchor, row.label)
            # ... then the closing bracket.
            + r'\s*text\("\]"\)',
            re.S,
        )
        found = len(pattern.findall(text))
        assert found == 1, (
            f"Expected EXACTLY ONE textual citing marker in {docname}.typ -- "
            f"the author surname {surname!r} (parsed from refs.bib) "
            f"immediately followed by '[', then the guarded link to "
            f"{row.anchor!r} carrying the label {row.label!r} (read from the "
            f"corpus-wide grid's own row), then ']' -- but found {found}. Zero "
            "means the textual form did not render the author OUTSIDE the "
            "bracket group, which is the ONLY thing distinguishing it from the "
            "parenthetical form; more than one means a second site can satisfy "
            "this assertion accidentally."
            f"\nPattern: {pattern.pattern}\n{text}"
        )

    def test_multi_key_form_emits_one_guard_per_key_in_one_bracket_group(
        self, full_form_gate_build, full_form_fixture_data, parsed_grids
    ):
        """
        The multi-key site emits ONE bracket group containing one guarded link
        per key it names, comma-separated and in source order -- matched as a
        single contiguous regex so neither the sharing of one bracket group nor
        the key order can silently break.

        Both guards are pinned to the grid rows for the two DIFFERENT keys the
        site names, so a site that resolved both of its keys to the same row
        would fail here even though the guard count stayed correct.
        """
        multi = [
            (docname, site)
            for docname in full_form_fixture_data.docnames
            for site in full_form_fixture_data.cite_sites(docname)
            if len(site.keys) > 1
        ]
        assert len(multi) == 1, (
            "Vacuous-pass guard: exactly one multi-key citing site must be "
            f"parsed out of the fixture, but found {multi}."
        )
        docname, site = multi[0]
        target = parsed_grids[full_form_fixture_data.bare_bibliography_docname]
        rows = []
        for key in site.keys:
            title = full_form_fixture_data.titles[key]
            row = next((row for row in target.rows if title in row.body), None)
            assert row is not None, (
                f"The multi-key site names {key!r} but the corpus-wide grid has "
                f"no row whose body renders {title!r}; grid labels: "
                f"{target.labels}."
            )
            rows.append(row)
        assert len({row.anchor for row in rows}) == len(rows), (
            "The multi-key site's keys resolved to grid rows sharing one "
            f"anchor ({[row.anchor for row in rows]}), so per-key attribution "
            "inside the bracket group is impossible."
        )

        text = full_form_gate_build.read_typ(docname)
        pattern = re.compile(
            r'text\("\["\)\s*'
            + _guard_pattern(rows[0].anchor, rows[0].label)
            + r'\s*text\(",\s*"\)\s*'
            + _guard_pattern(rows[1].anchor, rows[1].label)
            + r'\s*text\("\]"\)',
            re.S,
        )
        found = len(pattern.findall(text))
        assert found == 1, (
            f"The multi-key site in {docname}.typ must render as EXACTLY ONE "
            "bracket group holding one guarded link per key, comma-separated "
            f"and in the source order {site.keys} (anchors "
            f"{[row.anchor for row in rows]}, labels "
            f"{[row.label for row in rows]}), but found {found}. Zero means "
            "the multi-key form stopped sharing one bracket group, reordered "
            "its keys, or lost a guard."
            f"\nPattern: {pattern.pattern}\n{text}"
        )

    def test_footnote_route_emits_one_definition_and_one_bare_reuse(
        self, full_form_gate_build, full_form_fixture_data
    ):
        """
        The footnote route renders as ONE label-attached definition form
        carrying the entry's formatted body, plus exactly one bare reuse form
        on the SAME label for the repeat site -- never a second definition.

        Both the label and the reuse form are computed by the translator's own
        ``_namespace_label`` via :func:`_footnote_label`, over the docutils id
        :func:`_footcite_refid` derives from the fixture's parsed key, so no
        label literal appears here. The ``footnote(`` CENSUS for this document
        is asserted by :class:`TestPerFileCensus`; this test pins the two
        FORMS.
        """
        docname = full_form_fixture_data.footnote_docname
        keys = sorted(full_form_fixture_data.footcite_keys)
        assert len(keys) == 1, (
            "Vacuous-pass guard: the footnote route must cover exactly one "
            f"key, but parsed {keys}."
        )
        key = keys[0]
        label = _footnote_label(docname, _footcite_refid(key))
        text = full_form_gate_build.read_typ(docname)

        tail = _definition_marker(label)
        assert text.count(tail) == 1, (
            f"The footcited key {key!r} must emit EXACTLY ONE footnote "
            f"DEFINITION in {docname}.typ -- the [#footnote({{...}}) <label>] "
            f"shape whose tail is {tail!r} -- but found {text.count(tail)}. "
            "Zero means footbibliography stopped routing through the footnote "
            "path; two would mean the body is emitted twice, which is the "
            "doubled-footnote regression this route's exactly-once count "
            f"exists to catch.\n{text}"
        )
        body = _definition_body(text, label)
        title = full_form_fixture_data.titles[key]
        assert title in body, (
            f"The footnote definition attached to the footcited key {key!r} "
            f"must carry that entry's formatted body, but {title!r} (parsed "
            f"from refs.bib) is not inside it: {body!r}"
        )

        reuse = _reuse_marker(label)
        reuse_sites = len(full_form_fixture_data.footcite_sites(docname)) - 1
        assert text.count(reuse) == reuse_sites, (
            f"The repeat :footcite: site(s) on {key!r} must emit exactly "
            f"{reuse_sites} bare reuse form(s) {reuse!r} in {docname}.typ, but "
            f"found {text.count(reuse)}. A repeat site that emitted a second "
            "DEFINITION instead would duplicate the entry's body in the "
            f"compiled output.\n{text}"
        )


@pytest.mark.skipif(
    not BIBTEX_AVAILABLE,
    reason="sphinxcontrib-bibtex is required for the full-form bibliography gate",
)
class TestGuardedCrossDocumentAnchors:
    """
    Every citing site's guard is a genuine CROSS-document reference: its anchor
    is namespaced by the document that DEFINES the row, that document is not
    the citing one, and the row it names is the row for the key the site cites.
    """

    def test_every_guard_targets_a_grid_row_in_another_document(
        self, full_form_gate_build, full_form_fixture_data, parsed_grids
    ):
        """
        Each guarded anchor byte-equals a grid row anchor defined in a DIFFERENT
        document, and carries that target document's own namespace prefix as
        computed by ``_namespace_label``.

        This is the cross-vs-same-document discriminator: a same-document
        reference would be namespaced by the citing document and would need no
        guard at all.
        """
        rows_by_anchor = {
            row.anchor: (grid.docname, row)
            for grid in parsed_grids.values()
            for row in grid.rows
        }
        assert rows_by_anchor, (
            "Vacuous-pass guard: no grid rows were parsed out of either "
            "bibliography host, so every anchor comparison below would "
            "compare against nothing."
        )
        checked = 0
        for docname in full_form_fixture_data.docnames:
            for anchor in _guarded_anchors(full_form_gate_build.read_typ(docname)):
                assert anchor in rows_by_anchor, (
                    f"The guard in {docname}.typ targets {anchor!r}, which is "
                    "not the anchor of any grid row in either bibliography "
                    f"host ({sorted(rows_by_anchor)}). The citing site is "
                    "guarded on a label nothing defines -- a silently dead "
                    "reference (D011)."
                )
                target_docname, _row = rows_by_anchor[anchor]
                assert target_docname != docname, (
                    f"The guard in {docname}.typ targets a row defined in the "
                    "SAME document, so its resolution never crosses an "
                    "#include() boundary and the cross-document claim is not "
                    f"under test: {anchor!r}."
                )
                target_prefix = _namespace_prefix(target_docname)
                citing_prefix = _namespace_prefix(docname)
                # The DISCRIMINATION guard, and it is load-bearing rather than
                # decorative: both sides of the comparison below are computed by
                # the same `_namespace_label`, so a translator that stopped
                # namespacing labels ALTOGETHER would move both sides together
                # and leave "the anchor carries the target's namespace"
                # trivially true against an empty prefix. Requiring the prefixes
                # to be non-empty AND to differ per document is what turns it
                # back into a real claim -- measured: without it, dropping the
                # docname namespace entirely left this test GREEN.
                assert target_prefix and citing_prefix, (
                    "_namespace_label computes an EMPTY namespace for "
                    f"{target_docname!r} / {docname!r}, so 'namespaced by the "
                    "target document' has no content: every anchor would "
                    "trivially start with it. A translator that stopped "
                    "namespacing labels by docname reaches exactly this state."
                )
                assert target_prefix != citing_prefix, (
                    "_namespace_label computes the SAME namespace "
                    f"({target_prefix!r}) for the defining document "
                    f"{target_docname!r} and the citing document {docname!r}, "
                    "so the namespace cannot discriminate between a "
                    "cross-document and a same-document anchor."
                )
                assert anchor.startswith(target_prefix), (
                    f"The guard in {docname}.typ targets {anchor!r}, which does "
                    "not carry the namespace _namespace_label computes for the "
                    f"DEFINING document {target_docname!r} ({target_prefix!r}). "
                    "A cross-document anchor must be namespaced by the target, "
                    "not root-relative."
                )
                assert not anchor.startswith(citing_prefix), (
                    f"The guard in {docname}.typ targets {anchor!r}, which "
                    "carries the CITING document's own namespace "
                    f"({citing_prefix!r}) rather than the defining document's. "
                    "A reference namespaced by its own document can never land "
                    "on another document's anchor."
                )
                checked += 1
        assert checked == sum(
            full_form_fixture_data.expected_query_count(docname)
            for docname in full_form_fixture_data.docnames
        ), (
            "Vacuous-pass guard: checked "
            f"{checked} guard(s) but the fixture's :cite:*: sites name "
            f"{sum(full_form_fixture_data.expected_query_count(d) for d in full_form_fixture_data.docnames)} "
            "key(s) in total."
        )

    def test_each_guard_lands_on_the_row_for_the_key_its_site_cites(
        self, full_form_gate_build, full_form_fixture_data, parsed_grids
    ):
        """
        Row-level ATTRIBUTION: within each citing document, the guards in
        document order land on the rows whose BODIES render the keys that
        document's ``:cite:*:`` sites name, in the same order.

        Asserted against each row's parsed BODY, not merely its label or
        anchor, so "the link lands on the right row" means the row that
        actually renders that entry's text.
        """
        rows_by_anchor = {
            row.anchor: row for grid in parsed_grids.values() for row in grid.rows
        }
        citing_docnames = [
            docname
            for docname in full_form_fixture_data.docnames
            if full_form_fixture_data.cite_keys_in_order(docname)
        ]
        assert citing_docnames, (
            "Vacuous-pass guard: no document was parsed as carrying a "
            ":cite:*: site, so there is no attribution to check."
        )
        for docname in citing_docnames:
            expected_keys = full_form_fixture_data.cite_keys_in_order(docname)
            anchors = _guarded_anchors(full_form_gate_build.read_typ(docname))
            assert len(anchors) == len(expected_keys), (
                f"{docname}.typ emits {len(anchors)} guard(s) but its sites "
                f"name {len(expected_keys)} key(s) ({expected_keys}), so "
                "pairing them positionally would mis-attribute."
            )
            for position, (anchor, key) in enumerate(
                zip(anchors, expected_keys, strict=True)
            ):
                row = rows_by_anchor.get(anchor)
                assert row is not None, (
                    f"Guard #{position} in {docname}.typ targets {anchor!r}, "
                    "which names no parsed grid row."
                )
                title = full_form_fixture_data.titles[key]
                assert title in row.body, (
                    f"Guard #{position} in {docname}.typ was emitted for the "
                    f"key {key!r} but lands on the row anchored at {anchor!r}, "
                    f"whose rendered body does not contain that entry's title "
                    f"{title!r}. The citing site resolves to the WRONG "
                    f"bibliography row.\nRow body: {row.body!r}"
                )


@pytest.mark.skipif(
    not BIBTEX_AVAILABLE,
    reason="sphinxcontrib-bibtex is required for the full-form bibliography gate",
)
class TestPerRouteExactlyOnce:
    """
    D013, scoped PER ROUTE -- the central rule of this module.

    There is deliberately NO document-wide "each title appears exactly once"
    assertion: on a correct build the key both bibliographies cover renders
    TWICE across the corpus, once per grid, and that is right. Instead each
    count below names the grid or the route it scopes to. The only
    document-wide count that survives is the uncited entry's ZERO, which is
    what keeps every other count non-vacuous (MEM006).
    """

    def test_each_grid_holds_exactly_one_row_per_key_it_owns(
        self, full_form_fixture_data, parsed_grids
    ):
        """
        Within EACH grid: exactly one row whose body renders each key that grid
        OWNS -- the corpus-wide grid owning every ``:cite:*:``-cited key, the
        chapter-local one owning its ``:filter:``'s keys.
        """
        for docname, grid in parsed_grids.items():
            owned = full_form_fixture_data.owned_keys(docname)
            assert owned, (
                f"Vacuous-pass guard: the grid in {docname}.typ was computed to "
                "own no key, so its row counts below would be vacuous."
            )
            for key in sorted(owned):
                title = full_form_fixture_data.titles[key]
                matching = [row for row in grid.rows if title in row.body]
                assert len(matching) == 1, (
                    f"The grid in {docname}.typ owns {key!r} and must hold "
                    f"EXACTLY ONE row whose body renders {title!r}, but holds "
                    f"{len(matching)}. Zero means that directive stopped "
                    "rendering a key it covers -- the measured SILENT "
                    "degradation mode of this fixture's :filter:, which keeps "
                    "the strict build clean. More than one means the row was "
                    "duplicated inside this one grid, e.g. the upstream "
                    "double-resolve append reaching the write pass (MEM009)."
                    f"\nGrid labels: {grid.labels}"
                )
                # Per-ROW, not merely per-grid: MEM009's duplication shape
                # appends to a citation's already-rendered children, which
                # doubles the entry text INSIDE one row's body cell rather than
                # adding a second row. A row-COUNTING assertion alone cannot see
                # that -- measured: re-walking a citation's children on depart
                # leaves the row count unchanged and only this check goes RED.
                occurrences = matching[0].body.count(title)
                assert occurrences == 1, (
                    f"The row for {key!r} in {docname}.typ's grid renders its "
                    f"title {title!r} {occurrences} time(s) inside a SINGLE row "
                    "body. More than one is the upstream double-resolve append "
                    "reaching the write pass (MEM009): the entry's rendered "
                    "text emitted twice into one cell."
                    f"\nRow body: {matching[0].body!r}"
                )

    def test_no_grid_holds_a_row_for_a_key_it_does_not_own(
        self, full_form_fixture_data, parsed_grids
    ):
        """
        Within EACH grid: no row renders a key that grid does NOT own --
        including the footnote-route key, which must be rendered by
        ``footbibliography`` only, and the permanently uncited entry.

        This is the half that makes the per-grid scoping a real partition
        rather than a lower bound: without it, a filtered bibliography that
        quietly ignored its filter would still pass the owns-exactly-one test.
        """
        for docname, grid in parsed_grids.items():
            owned = full_form_fixture_data.owned_keys(docname)
            foreign = sorted(set(full_form_fixture_data.titles) - owned)
            assert foreign, (
                f"Vacuous-pass guard: every refs.bib key was computed as owned "
                f"by the grid in {docname}.typ, so this assertion has no "
                "subject."
            )
            for key in foreign:
                title = full_form_fixture_data.titles[key]
                assert title not in grid.region, (
                    f"The grid in {docname}.typ does NOT own {key!r} (owned: "
                    f"{sorted(owned)}) yet renders its title {title!r}. For "
                    "the footnote-route key this means footbibliography's "
                    "entry leaked into a definition grid; for the filtered "
                    "directive it means its :filter: stopped scoping; for the "
                    "uncited entry it means a bibliography began rendering "
                    "uncited entries (MEM006), which would inflate every other "
                    f"count here.\nGrid region: {grid.region}"
                )

    def test_footnote_route_emits_exactly_one_body_per_cited_key(
        self, full_form_gate_build, full_form_fixture_data
    ):
        """
        Within the FOOTNOTE route: exactly one footnote BODY per footcited key
        across the whole emitted corpus, even though the key is cited twice --
        the repeat site emits the bare reuse form, not a second body.

        Counted over every emitted ``.typ`` rather than only the route's own
        document, because a body leaking into another file would be exactly the
        kind of interference this slice exists to rule out.
        """
        emitted = full_form_gate_build.emitted_typ_files()
        assert emitted, (
            "Vacuous-pass guard: the build emitted no .typ files at its root, "
            "so the corpus-wide count has nothing to count."
        )
        corpus = "".join(emitted.values())
        for key in sorted(full_form_fixture_data.footcite_keys):
            title = full_form_fixture_data.titles[key]
            occurrences = corpus.count(title)
            assert occurrences == 1, (
                f"The footcited key {key!r}'s title {title!r} occurs "
                f"{occurrences} time(s) across the emitted corpus "
                f"({sorted(emitted)}) but the FOOTNOTE route must render it "
                "exactly once: the first site defines the footnote and the "
                "repeat site reuses it. Zero means the footnote body never "
                "rendered; more than one means either a second definition was "
                "emitted or the key also reached a definition grid."
            )

    def test_the_uncited_entry_never_renders_anywhere(
        self, full_form_gate_build, full_form_fixture_data
    ):
        """
        The only DOCUMENT-WIDE exactly-``n`` assertion in this module: the
        permanently uncited entry's title occurs ZERO times across the emitted
        corpus.

        A bibliography renders only CITED entries (MEM006), so a non-zero count
        would mean a directive gained an ``:all:`` option or something started
        citing the negative control -- either of which would inflate, and
        thereby invalidate, every per-route count above.
        """
        emitted = full_form_gate_build.emitted_typ_files()
        corpus = "".join(emitted.values())
        uncited = sorted(full_form_fixture_data.uncited_keys)
        assert uncited, (
            "Vacuous-pass guard: no refs.bib entry was parsed as uncited, so "
            "the negative control is gone and this assertion has no subject."
        )
        for key in uncited:
            title = full_form_fixture_data.titles[key]
            assert corpus.count(title) == 0, (
                f"The deliberately UNCITED entry {key!r}'s title {title!r} "
                f"occurs {corpus.count(title)} time(s) across the emitted "
                f"corpus ({sorted(emitted)}) but must never render."
            )


@pytest.mark.skipif(
    not BIBTEX_AVAILABLE,
    reason="sphinxcontrib-bibtex is required for the full-form bibliography gate",
)
class TestKeyprefixDoesNotLeakIntoAnchorsOrLabels:
    """
    R010, re-confirmed in the COMBINED setting: the chapter-local directive's
    ``:keyprefix:`` is a source-level key namespace only. It reaches neither
    the rendered pybtex label nor the emitted Typst anchor, even while it is
    load-bearing for build cleanliness (without it the two directives collide
    on one citation id and the strict build fails).
    """

    def test_the_keyprefix_string_appears_in_no_label_and_no_anchor(
        self, full_form_fixture_data, parsed_grids
    ):
        """
        The ``:keyprefix:`` value parsed from the fixture's own directive
        appears in no grid row label and in no grid row anchor, in EITHER grid.
        """
        prefix = full_form_fixture_data.keyprefix
        assert prefix, (
            "Vacuous-pass guard: no :keyprefix: was parsed out of the "
            "chapter-local .. bibliography:: directive "
            f"({full_form_fixture_data.filtered_options!r}), so this "
            "assertion has no subject -- and the fixture has lost the option "
            "that lets its two directives coexist."
        )
        for docname, grid in parsed_grids.items():
            for row in grid.rows:
                assert prefix not in row.label, (
                    f"The :keyprefix: {prefix!r} leaked into the rendered "
                    f"label {row.label!r} of a row in {docname}.typ. It is a "
                    "SOURCE-LEVEL key namespace only (R010): a reader must see "
                    "the same label whether or not the directive carries one."
                )
                assert prefix not in row.anchor, (
                    f"The :keyprefix: {prefix!r} leaked into the emitted anchor "
                    f"{row.anchor!r} of a row in {docname}.typ. A prefixed "
                    "anchor would silently rename this grid's labels and break "
                    "every cross-document link that targets it."
                )

    def test_the_chapter_local_grid_labels_match_the_corpus_wide_ones(
        self, full_form_fixture_data, parsed_grids
    ):
        """
        For the key BOTH grids cover, the chapter-local (prefixed) grid renders
        the SAME pybtex label as the corpus-wide (unprefixed) one, while
        anchoring it under its OWN document's namespace.

        This is the sharper form of the no-leak claim: it compares the prefixed
        directive's output against an unprefixed rendering of the same entry
        measured in the same build, so it holds no matter what label style
        pybtex uses.
        """
        bare = parsed_grids[full_form_fixture_data.bare_bibliography_docname]
        filtered = parsed_grids[full_form_fixture_data.filtered_docname]
        shared = sorted(
            full_form_fixture_data.owned_keys(full_form_fixture_data.filtered_docname)
            & full_form_fixture_data.owned_keys(
                full_form_fixture_data.bare_bibliography_docname
            )
        )
        assert shared, (
            "Vacuous-pass guard: the two grids own no key in common, so there "
            "is no unprefixed rendering to compare the prefixed one against."
        )
        own_namespace = _namespace_prefix(full_form_fixture_data.filtered_docname)
        bare_namespace = _namespace_prefix(
            full_form_fixture_data.bare_bibliography_docname
        )
        # Same discrimination guard as in TestGuardedCrossDocumentAnchors, for
        # the same measured reason: without it, a translator that stopped
        # namespacing labels by docname would leave the per-host namespace
        # assertion below trivially true against an empty prefix.
        assert own_namespace and own_namespace != bare_namespace, (
            "_namespace_label computes an empty or non-discriminating namespace "
            f"for the two bibliography hosts ({own_namespace!r} vs "
            f"{bare_namespace!r}), so 'this grid defines its anchors in its own "
            "document' has no content."
        )
        for key in shared:
            title = full_form_fixture_data.titles[key]
            bare_row = next((row for row in bare.rows if title in row.body), None)
            filtered_row = next(
                (row for row in filtered.rows if title in row.body), None
            )
            assert bare_row is not None and filtered_row is not None, (
                f"Both grids must hold a row rendering {key!r} ({title!r}): "
                f"corpus-wide {bare_row}, chapter-local {filtered_row}."
            )
            assert filtered_row.label == bare_row.label, (
                f"The chapter-local (prefixed) grid renders {key!r} with the "
                f"label {filtered_row.label!r} while the corpus-wide "
                f"(unprefixed) grid renders it as {bare_row.label!r}. A "
                "difference means the :keyprefix: reached the rendered label."
            )
            assert filtered_row.anchor != bare_row.anchor, (
                f"Both grids anchor their {key!r} row at {filtered_row.anchor!r}. "
                "Two directives sharing one anchor is a duplicate citation id, "
                "which is exactly what the :keyprefix: exists to prevent."
            )
            assert filtered_row.anchor.startswith(own_namespace), (
                f"The chapter-local grid's row for {key!r} is anchored at "
                f"{filtered_row.anchor!r}, which does not carry the namespace "
                "_namespace_label computes for its own host document "
                f"({own_namespace!r}). A chapter-local bibliography must define "
                "its anchors in its own document."
            )


@pytest.mark.skipif(
    not BIBTEX_AVAILABLE,
    reason="sphinxcontrib-bibtex is required for the full-form bibliography gate",
)
class TestStrictBuildIsClean:
    """
    A strict (``-E -W``) build of the fixture exits 0 with zero ``WARNING``
    lines and names neither bibtex resolution code.

    Why this matters for a characterisation gate specifically: an unresolved
    citing site still exits 0 on a non-strict build while emitting
    ``bibtex.key_not_found`` and rendering no guard at all. Without ``-W`` plus
    the explicit code checks, a fixture typo would leave this module happily
    characterising a corpus whose citations stopped resolving -- the
    characterisation would be describing the typo (MEM036).

    NOT sufficient on its own, and the fixture's own comments record why: this
    fixture has a measured degradation (the ``:filter:`` rewritten into the
    key-on-left comparison form) that drops the chapter-local grid entirely
    while the strict build still exits 0 with ZERO warnings. That is what
    :class:`TestPerRouteExactlyOnce`'s POSITIVE per-grid row counts are for.
    """

    def test_strict_build_exits_zero(self, full_form_gate_strict_build):
        """
        ``sphinx-build -b typst -E -W`` over the fixture exits 0.

        Under ``-W`` every warning is an error, so exit 0 IS the zero-warning
        evidence, and unlike grepping for the word "WARNING" it holds under a
        non-English ``LANG`` (the build forces ``LC_ALL=C`` anyway, belt and
        braces). ``-E`` discards any saved environment so warnings a cached
        build would skip are actually re-emitted.
        """
        result = full_form_gate_strict_build.result
        assert result.returncode == 0, (
            "A strict (-E -W) build of the full-form bibliography fixture must "
            f"succeed, but exited {result.returncode}. Under -W this means the "
            "build emitted at least one warning -- e.g. a citing site that "
            "lost its target, a toctree entry that no longer exists, or the "
            "two bibliography directives colliding on one citation id because "
            "the chapter-local one lost its :keyprefix:."
            f"\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_strict_build_emits_no_warning_lines(self, full_form_gate_strict_build):
        """
        The strict build's combined output contains zero ``WARNING`` lines.

        Strictly weaker than the exit code under ``-W``, and kept anyway
        because it is the check that still reports something useful if a future
        Sphinx stopped promoting some warning class to an error. Meaningful
        only because the build forces ``LC_ALL=C``: under this machine's
        Japanese locale the word would be localised.
        """
        lines = [
            line
            for line in full_form_gate_strict_build.output.splitlines()
            if "WARNING" in line
        ]
        assert lines == [], (
            "The strict (-E -W) build emitted WARNING line(s), so the corpus "
            "this gate characterises is not clean:\n" + "\n".join(lines)
        )

    def test_strict_build_names_neither_bibtex_resolution_code(
        self, full_form_gate_strict_build
    ):
        """
        The strict build's output never names ``bibtex.key_not_found`` or
        ``bibtex.duplicate_citation``.

        Asserted on the CODES rather than on message text because Sphinx
        localises the message but never the bracketed code, so these checks are
        locale-independent by construction. ``key_not_found`` is the signature
        of a cited key no ``refs.bib`` entry defines -- this gate describing a
        typo (MEM036). ``duplicate_citation`` is the signature of the two
        directives claiming one citation id, which is the specific collision
        this fixture's ``:keyprefix:`` exists to prevent and which nothing else
        in this module would name explicitly.
        """
        output = full_form_gate_strict_build.output
        for code in (BIBTEX_KEY_NOT_FOUND_CODE, BIBTEX_DUPLICATE_CITATION_CODE):
            assert code not in output, (
                f"The strict build reported the {code!r} warning code, which "
                "means sphinxcontrib-bibtex could not resolve a citing site or "
                "could not keep the two bibliography directives apart. Every "
                "assertion in this module would then be characterising a "
                f"corpus that silently stopped working.\n{output}"
            )


# ---------------------------------------------------------------------------
# T03, part one: the COMPILED PDF.
#
# Everything above this line asserts over emitted ``.typ`` markup. Everything
# below asserts over the real compiled artifact -- R009 is explicit that the
# full form must be proven on a PDF a reader could open, not on the markup that
# produces it -- and over the ``latex`` / ``html`` builds of the SAME sources,
# which is R010.
#
# The whole half sits behind PDF_DEPS_AVAILABLE so a machine without typst-py
# or pypdf SKIPS it rather than erroring, exactly as the sibling gates do.
# ---------------------------------------------------------------------------


def _normalise_whitespace(text: str) -> str:
    """
    Collapse every whitespace run to a single space.

    MANDATORY on BOTH sides of every comparison below, and the reason is not
    cosmetic. Typst breaks lines inside a justified bibliography row and pypdf
    reports those breaks literally, so an un-normalised ``str.count()`` of a
    multi-word title silently reads 0 and the assertion then fails for a reason
    that has nothing to do with the contract. The same function also normalises
    the ``latex`` and ``html`` extractions in part two, so the three builders
    cannot be reported as disagreeing merely about whitespace -- measured at
    T03 time, ``latex`` wraps its ``\\bibitem`` bodies at a different column
    than ``html`` emits its ``<p>``, and the bodies are character-identical
    only after this call.

    Deliberately duplicated from the sibling gates rather than imported: these
    gate modules are independent characterisation records.
    """
    return re.sub(r"\s+", " ", text)


@dataclass(frozen=True)
class PdfCoordinateLink:
    """
    One ``/Link`` annotation whose destination is an explicit COORDINATE
    destination -- an indirect array ``[<page ref> /XYZ x y zoom]``.

    MEASURED on this fixture (MEM046): every citation link typsphinx emits is
    exactly this shape, while the master's four toctree entries are NAMED
    (string) destinations instead. Both shapes must be TOLERATED by the walker
    and only this one is a citation marker, which is why
    :func:`_read_compiled_pdf` records the named ones and skips them rather
    than crashing on them (MEM053).
    """

    source_page: int
    rect: tuple[float, float, float, float]
    target_page: int
    dest_kind: str
    dest_y: float | None

    @property
    def crosses_pages(self) -> bool:
        """Whether this link lands on a STRICTLY LATER page than its marker."""
        return self.target_page > self.source_page

    @property
    def rect_bottom(self) -> float:
        """The marker rectangle's lower edge, in PDF user space."""
        return min(self.rect[1], self.rect[3])


@dataclass
class FullFormPdf:
    """The compiled ``master.pdf``, parsed exactly once per module."""

    page_texts: list[str]
    coordinate_links: list[PdfCoordinateLink]
    named_destinations: list[str]

    @property
    def text(self) -> str:
        """Whitespace-normalised text of every page, joined."""
        return _normalise_whitespace(" ".join(self.page_texts))

    @property
    def crossing_links(self) -> list[PdfCoordinateLink]:
        """Every coordinate link that lands on a strictly later page."""
        return [link for link in self.coordinate_links if link.crosses_pages]


def _read_compiled_pdf(pdf_path: Path) -> FullFormPdf:
    """
    Parse one compiled PDF into :class:`FullFormPdf`.

    The page-object map (``indirect_reference.idnum -> page index``) is what
    turns a destination's page REFERENCE into a page INDEX; there is no other
    reliable route, because a coordinate destination names its page by object
    reference and never by number (MEM046).

    Both ``/Dest`` and ``/A``->``/D`` are read. Reading only one of the two is
    the measured trap MEM060 records: a walk that consults ``/A``->``/D`` alone
    and skips the ``/Dest`` key reports ZERO annotations on a document that
    plainly has them, which reads as a regression in typsphinx rather than as a
    bug in the probe. That is why this helper is shared by every assertion
    below instead of each one hand-rolling its own walk.
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
            # A NAMED destination: measured to be a toctree entry of the
            # master, never a citation marker. Recorded, then skipped -- never
            # crashed on (MEM053).
            if isinstance(destination, (str, bytes)):
                named_destinations.append(str(destination))
                continue
            if hasattr(destination, "get_object"):
                destination = destination.get_object()
            page_reference = destination[0]
            assert getattr(page_reference, "idnum", None) in page_indices, (
                "A coordinate /Link destination names a page object "
                f"({page_reference!r}) that is not one of this document's "
                "pages, so its destination page index cannot be resolved and "
                "the page-crossing assertion below would be comparing against "
                "a page that does not exist."
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

    return FullFormPdf(
        page_texts=[
            _normalise_whitespace(page.extract_text()) for page in reader.pages
        ],
        coordinate_links=coordinate_links,
        named_destinations=named_destinations,
    )


@pytest.fixture(scope="module")
def full_form_gate_pdf_build(full_form_gate_dir, tmp_path_factory):
    """
    Compile the fixture through ``-b typstpdf`` EXACTLY ONCE for the whole
    module, in its own build directory.

    ``pytest.importorskip`` as well as the class-level ``skipif``: a missing
    ``typst-py`` or ``pypdf`` must SKIP this half, not ERROR it, and this
    fixture-level belt-and-braces covers the case where a class guard is ever
    loosened. Declared at module level rather than in a class body: a
    class-scoped fixture that depends on these broader-scoped ones trips
    pytest's own ``assert not self._finalizers`` internal check, which every
    sibling gate in this project records.
    """
    pytest.importorskip("typst", reason="typst-py backs the typstpdf builder")
    pytest.importorskip("pypdf", reason="pypdf extracts the compiled PDF's text")

    build_dir = tmp_path_factory.mktemp("full_form_gate_pdf") / "_build"
    result = _run_sphinx_build(full_form_gate_dir, build_dir, buildername="typstpdf")
    assert result.returncode == 0, (
        "sphinx-build -b typstpdf over the full-form bibliography fixture must "
        "succeed -- this is R009's whole subject, the full citation surface "
        "compiling end-to-end to a real PDF\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    return FullFormGateBuild(result=result, build_dir=build_dir)


@pytest.fixture(scope="module")
def full_form_pdf(full_form_gate_pdf_build) -> FullFormPdf:
    """
    Locate and parse the fixture's single compiled PDF ONCE, behind the two
    MANDATORY vacuous-pass guards.

    The PDF is found by GLOB rather than by filename, and "exactly one" is
    itself worth asserting: the fixture declares a single ``typst_documents``
    master, so a second PDF would mean the master registry changed shape under
    this gate.

    Both guards exist because of the specific silent failure they rule out. If
    pypdf extracted nothing, every ``str.count()`` below would read 0 and the
    uncited-entry negative control would still "pass" -- the suite would report
    green on a document it never actually read. If the ``/Link`` annotation
    count were 0, every resolution and page-crossing assertion below would be
    quantifying over an empty set and pass vacuously. Each guard names its own
    condition so a failure says which one tripped.
    """
    pdfs = sorted(full_form_gate_pdf_build.build_dir.glob("*.pdf"))
    assert len(pdfs) == 1, (
        "Expected exactly ONE compiled PDF for this single-master fixture, "
        f"found {[pdf.name for pdf in pdfs]} -- build "
        f"returncode={full_form_gate_pdf_build.result.returncode}\n"
        f"stderr: {full_form_gate_pdf_build.result.stderr}"
    )
    parsed = _read_compiled_pdf(pdfs[0])
    assert parsed.text.strip(), (
        "Vacuous-pass guard: pypdf extracted NO text from the compiled PDF, so "
        "every entry-title count below would read 0 regardless of what the "
        f"document actually contains ({pdfs[0]})."
    )
    assert len(parsed.coordinate_links) > 0, (
        "Vacuous-pass guard: the compiled PDF carries ZERO coordinate /Link "
        "annotations, so every resolution and page-crossing assertion below "
        "would quantify over an empty set and pass without measuring "
        f"anything ({pdfs[0]}). Named destinations seen: "
        f"{parsed.named_destinations}."
    )
    return parsed


def _expected_pdf_title_occurrences(data: FullFormFixtureData, key: str) -> int:
    """
    How many times ``key``'s entry title must appear in the WHOLE compiled
    PDF's extracted text, DERIVED by summing the routes that render it.

    This is the compiled-artifact form of D013's exactly-once property, and the
    summation is the entire point. D013 is exactly-once PER ROUTE, not per
    document tree, and in this fixture one key is deliberately rendered by TWO
    routes at once: the corpus-wide bare bibliography AND the filtered
    chapter-local one. A document-wide ``== 1`` would therefore FAIL on
    CORRECT output -- measured at T03 time, "Another work entirely" occurs
    twice and both occurrences are legitimate, each owned by a different
    directive.

    The count is assembled from the fixture's own parsed ownership data, never
    transcribed, so adding a third bibliography or moving a key between filters
    re-derives the expectation instead of invalidating it:

    * one occurrence per bibliography directive whose owned key set contains
      ``key`` (that directive renders it one grid row);
    * plus one if ``key`` is reached through the footnote route, which renders
      exactly one footnote BODY however many times it is cited -- the second
      citing site emits the bare reuse form.

    An uncited key sums to 0, which is what makes the negative control a real
    assertion rather than an absence of one.
    """
    grid_rows = sum(
        1
        for docname in (data.bare_bibliography_docname, data.filtered_docname)
        if key in data.owned_keys(docname)
    )
    footnote_bodies = 1 if key in data.footcite_keys else 0
    return grid_rows + footnote_bodies


@pytest.fixture(scope="module")
def corpus_bibliography_page(full_form_pdf, full_form_fixture_data) -> int:
    """
    DERIVE -- never hard-code -- the index of the page holding the corpus-wide
    bibliography, by searching extracted text for the titles parsed out of
    ``refs.bib``.

    No page number may be encoded in this module. At T03 time the citing
    markers sat on page index 2 and every grid row on page index 3, and either
    number moves the moment the fixture's filler prose or the template's front
    matter changes length. The page-crossing assertion needs to name the TARGET
    page, so it asks this fixture, which answers from the artifact.
    """
    titles = [
        _normalise_whitespace(full_form_fixture_data.titles[key])
        for key in sorted(full_form_fixture_data.grid_keys)
    ]
    pages = [
        index
        for index, text in enumerate(full_form_pdf.page_texts)
        if all(title in text for title in titles)
    ]
    assert len(pages) == 1, (
        "Exactly ONE page must carry every grid-route entry title together -- "
        f"the corpus-wide bibliography's page -- but {titles} were all found "
        f"together on pages {pages}. Zero means the corpus-wide bibliography "
        "did not render (or its titles wrapped in a way whitespace "
        "normalisation did not repair); more than one means the grid rows are "
        "duplicated across pages and 'the bibliography page' is not a "
        "well-defined thing to link to."
    )
    return pages[0]


@pytest.mark.skipif(
    not PDF_DEPS_AVAILABLE,
    reason="sphinxcontrib-bibtex, typst-py and pypdf back the compiled-PDF half",
)
class TestCompiledPdfPerRouteExactlyOnce:
    """
    R009 on the REAL artifact: in the compiled PDF's extracted text, every
    entry appears exactly as many times as it has OWNING routes -- which is
    one per route, and therefore two for the one key two directives render.

    Asserted on TITLES, never on label tokens. A label legitimately appears
    twice per route (once at the citing marker, once on the grid row), and a
    short generated label collides with page numbers and ordinary prose in
    extracted text -- the rule S04 established and every bibtex gate since has
    followed. The four fixture titles are pairwise distinct by construction
    (``refs.bib``'s own header says so), so one entry's count can never be
    satisfied by another's text.
    """

    def test_every_entry_appears_once_per_owning_route(
        self, full_form_pdf, full_form_fixture_data
    ):
        """
        Each cited entry's title occurs exactly ``sum(owning routes)`` times.

        This is the assertion a document-wide ``== 1`` would have got WRONG.
        See :func:`_expected_pdf_title_occurrences` for why the expectation is
        a sum rather than a constant.
        """
        text = full_form_pdf.text
        for key in sorted(full_form_fixture_data.titles):
            title = _normalise_whitespace(full_form_fixture_data.titles[key])
            expected = _expected_pdf_title_occurrences(full_form_fixture_data, key)
            assert text.count(title) == expected, (
                f"Entry {key!r} (title {title!r}) occurs "
                f"{text.count(title)} time(s) in the compiled PDF's extracted "
                f"text but is rendered by {expected} route(s): one grid row "
                "per bibliography directive that owns the key, plus one "
                "footnote body if the footnote route reaches it. More than "
                "expected means a route rendered it twice (D013 broken for "
                "that route); fewer means a route that should render it did "
                "not."
            )

    def test_the_multiply_owned_entry_really_is_owned_twice(
        self, full_form_fixture_data
    ):
        """
        At least one key is owned by BOTH bibliography directives.

        Without this, :meth:`test_every_entry_appears_once_per_owning_route`
        would be indistinguishable from a document-wide ``== 1`` check and the
        per-route scoping it exists to prove would be untested. This asserts
        the fixture still presents the two-owner case at all -- if a fixture
        edit ever made every key single-owner, the sum above would silently
        degenerate and nobody would notice.
        """
        multiply_owned = sorted(
            key
            for key in full_form_fixture_data.titles
            if _expected_pdf_title_occurrences(full_form_fixture_data, key) > 1
        )
        assert multiply_owned, (
            "No entry in this fixture is rendered by more than one route, so "
            "the per-route (rather than document-wide) scoping of the count "
            "above is no longer being exercised. The fixture is supposed to "
            "carry one key covered by BOTH the corpus-wide bare bibliography "
            "and the filtered chapter-local one -- that coexistence is what "
            "S06 exists to prove."
        )

    def test_the_uncited_entry_is_absent_from_the_compiled_pdf(
        self, full_form_pdf, full_form_fixture_data
    ):
        """
        The permanently uncited entry's title appears NOWHERE in the PDF.

        The negative control that keeps every count above non-vacuous: a bare
        or filtered ``.. bibliography::`` renders only CITED entries (MEM006),
        so if this title ever appeared, some directive started rendering
        uncited entries and every exactly-once count above would be inflated
        by entries nothing cites.
        """
        uncited = full_form_fixture_data.uncited_keys
        assert len(uncited) == 1, (
            "Vacuous-pass guard: this fixture must carry exactly ONE "
            f"permanently uncited entry as its negative control, found "
            f"{sorted(uncited)}. With none, this test asserts nothing."
        )
        key = next(iter(uncited))
        title = _normalise_whitespace(full_form_fixture_data.titles[key])
        assert title not in full_form_pdf.text, (
            f"The permanently uncited entry {key!r} (title {title!r}) was "
            "rendered into the compiled PDF. A bibliography must render only "
            "CITED entries (MEM006), so some directive started rendering the "
            "whole .bib -- which inflates, and thereby invalidates, every "
            "exactly-once count in this class."
        )

    def test_the_footnote_route_body_is_not_duplicated_by_the_reuse_site(
        self, full_form_pdf, full_form_fixture_data
    ):
        """
        The footnote-route entry's title appears exactly ONCE even though the
        fixture cites it TWICE.

        This is the reuse-form proof carried onto the compiled artifact: the
        second ``:footcite:`` site must emit a bare reuse reference rather than
        a second definition. A second definition would put the formatted body
        in the PDF twice, which is precisely what this count detects -- and it
        is a sharper check here than in markup, because a duplicated body is
        something a reader would actually SEE.
        """
        footnote_only = sorted(
            full_form_fixture_data.footcite_keys - full_form_fixture_data.grid_keys
        )
        assert len(footnote_only) == 1, (
            "Vacuous-pass guard: expected exactly ONE key reached through the "
            "footnote route and no other, so its PDF count cannot be "
            f"satisfied by a grid row, found {footnote_only}."
        )
        key = footnote_only[0]
        sites = [
            site
            for docname in full_form_fixture_data.rst_text
            for site in full_form_fixture_data.footcite_sites(docname)
            if key in site.keys
        ]
        assert len(sites) >= 2, (
            "Vacuous-pass guard: the reuse form is only under test if the "
            f"fixture cites {key!r} through the footnote route at least "
            f"TWICE, but it carries {len(sites)} such site(s). With one site "
            "there is no reuse to distinguish from a redefinition."
        )
        title = _normalise_whitespace(full_form_fixture_data.titles[key])
        assert full_form_pdf.text.count(title) == 1, (
            f"The footnote-route entry {key!r} (title {title!r}) occurs "
            f"{full_form_pdf.text.count(title)} time(s) in the compiled PDF "
            f"while the fixture carries {len(sites)} citing sites on it. "
            "Exactly one occurrence is the contract: the first site emits the "
            "definition form carrying the body and every later site the bare "
            "reuse form. More than one means a repeat citation re-emitted the "
            "whole footnote body."
        )


@pytest.mark.skipif(
    not PDF_DEPS_AVAILABLE,
    reason="sphinxcontrib-bibtex, typst-py and pypdf back the compiled-PDF half",
)
class TestCompiledPdfCitationLinksCrossPages:
    """
    The page-CROSSING proof S05 explicitly deferred to S06.

    S05 could assert that a citing marker's link RESOLVED, but not that it
    crossed a page boundary: its fixture was too short to guarantee the marker
    and its target ever landed on different pages, and a same-page link proves
    nothing about crossing. This fixture makes the separation STRUCTURAL --
    ``chapter_one``'s filler prose exists for no other reason than to push the
    bibliography-bearing documents onto a later page -- so a strictly-later-page
    assertion is valid here, and it is the one thing about the compiled artifact
    that no prior M001 slice could state.

    MEM054's prohibition is respected rather than circumvented. What MEM054
    forbids is using a page-index comparison to prove a SAME-page link
    resolved, because there it cannot distinguish a self-link from a real jump.
    Here the crossing itself is the claim, so comparing page indices is exactly
    the right instrument, and the companion check below is page-level forward
    reading order rather than a restatement of the same-page form.
    """

    def test_at_least_one_citation_link_lands_on_a_later_page(self, full_form_pdf):
        """
        Some coordinate ``/Link`` destination resolves to a page STRICTLY LATER
        than the annotation's own page.

        The minimal statement of the deferred proof: a citation link really
        does cross a page boundary in the compiled artifact.
        """
        crossing = full_form_pdf.crossing_links
        assert crossing, (
            "NO coordinate /Link annotation in the compiled PDF lands on a "
            "later page than its own, so the page-CROSSING property S05 "
            "deferred to S06 is not being demonstrated. Either the fixture's "
            "filler prose stopped forcing a page break (conf.py's own note "
            "says to ADD filler, never to weaken this assertion) or citation "
            "links stopped resolving across the include() boundary. Observed "
            "page pairs (source -> target): "
            f"{[(link.source_page, link.target_page) for link in full_form_pdf.coordinate_links]}."
        )

    def test_every_crossing_link_lands_on_the_corpus_bibliography_page(
        self, full_form_pdf, corpus_bibliography_page
    ):
        """
        Every page-crossing link targets the page that actually holds the
        corpus-wide bibliography.

        Crossing alone is weaker than it looks: a link could cross onto some
        unrelated page and still satisfy the previous test. This pins the
        DESTINATION to the derived bibliography page, so the crossing is
        attributable to citation resolution rather than to any forward jump.
        """
        for link in full_form_pdf.crossing_links:
            assert link.target_page == corpus_bibliography_page, (
                "A page-crossing /Link annotation on page "
                f"{link.source_page} lands on page {link.target_page}, but the "
                "corpus-wide bibliography was derived (from the entry titles "
                f"in the extracted text) to be on page {corpus_bibliography_page}. "
                "A citation marker that crosses onto any other page is not "
                "resolving to the grid row it names."
            )

    def test_no_citation_link_points_to_an_earlier_page(self, full_form_pdf):
        """
        No coordinate link's destination page precedes its own page: the
        companion forward-reading-order check.

        Deliberately asserted at PAGE granularity, and deliberately NOT in the
        geometric within-page form the sibling cross-document gate uses. That
        form was measured here at T03 time and is FALSE on correct output: the
        footnote route emits a BACK-link from the footnote body at the bottom
        of the page up to its citing marker higher on the same page, which
        points legitimately UPWARD. A blanket "every destination sits below its
        marker" assertion would therefore fail on a document that is behaving
        correctly. Page-level forward order is the strongest statement that is
        actually true of this fixture, and it still catches the regression that
        matters: a citation resolving backwards to a stale anchor.
        """
        backward = [
            (link.source_page, link.target_page)
            for link in full_form_pdf.coordinate_links
            if link.target_page < link.source_page
        ]
        assert not backward, (
            "Coordinate /Link annotation(s) point to an EARLIER page than "
            f"their own (source -> target): {backward}. Every bibliography in "
            "this fixture is hosted in a document that comes after every "
            "citing site in toctree order, so a backward citation link means "
            "a marker resolved to the wrong anchor."
        )

    def test_the_crossing_links_are_exactly_the_filler_chapter_guards(
        self, full_form_pdf, full_form_fixture_data
    ):
        """
        The NUMBER of crossing links equals the number of guarded ``query(``
        calls the filler-bearing chapter emits.

        The sharp census, derived rather than transcribed. The chapter that
        carries the footnote route is also the one carrying the filler prose
        (``chapter_one`` -- both facts are derived from the fixture, never
        named here), so every one of ITS grid-route guards must end up on the
        far side of the page break, while the other chapter's single site sits
        on the bibliography page already and legitimately does not cross.

        Expressing it as a count rather than ``>= 1`` is what makes a partial
        regression visible: if three of the four guards crossed and one
        silently stopped resolving, the previous tests would still pass.
        """
        expected = full_form_fixture_data.expected_query_count(
            full_form_fixture_data.footnote_docname
        )
        assert expected > 0, (
            "Vacuous-pass guard: the filler-bearing chapter "
            f"({full_form_fixture_data.footnote_docname}) emits ZERO guarded "
            "query() calls, so this census would compare against nothing."
        )
        crossing = full_form_pdf.crossing_links
        assert len(crossing) == expected, (
            f"{len(crossing)} coordinate /Link annotation(s) cross onto a "
            "later page, but the filler-bearing chapter "
            f"({full_form_fixture_data.footnote_docname}) emits {expected} "
            "guarded query() call(s), one per key its :cite:*: sites name, and "
            "every one of them must resolve across the page break its own "
            "filler creates. Fewer means a guard stopped resolving; more means "
            "something other than that chapter's citing sites is now crossing."
        )

    def test_the_crossing_links_reach_every_corpus_grid_row(
        self, full_form_pdf, full_form_fixture_data
    ):
        """
        The crossing links address as many DISTINCT destinations as the
        corpus-wide bibliography has rows.

        Without this, every crossing link could be pointing at the SAME grid
        row and the counts above would still agree. Measured at T03 time: the
        four crossing links carry exactly two distinct destination ordinates --
        the parenthetical site reaches the first row, the textual site the
        second, and the single multi-key site reaches BOTH, which is also the
        compiled-artifact proof that a multi-key role resolves per key rather
        than once.

        Compared on destination ordinates rather than on anchor names because a
        PDF coordinate destination carries no name at all (MEM046); the ordinal
        is the only identity a resolved coordinate link has.
        """
        destinations = {link.dest_y for link in full_form_pdf.crossing_links}
        assert None not in destinations, (
            "A crossing /Link destination carries no resolvable ordinate, so "
            "distinct grid rows cannot be told apart. Destination kinds seen: "
            f"{sorted({link.dest_kind for link in full_form_pdf.crossing_links})}."
        )
        expected_rows = len(full_form_fixture_data.grid_keys)
        assert len(destinations) == expected_rows, (
            f"The crossing links address {len(destinations)} distinct "
            f"destination(s) but the corpus-wide bibliography renders "
            f"{expected_rows} row(s) (one per grid-route key: "
            f"{sorted(full_form_fixture_data.grid_keys)}). Fewer distinct "
            "destinations means several citing sites collapsed onto one row -- "
            "including the case where a multi-key role resolved only its first "
            "key."
        )

    def test_named_destinations_are_tolerated_and_excluded(self, full_form_pdf):
        """
        The master's toctree entries use NAMED string destinations, and the
        walker records them without crashing and without counting them as
        citation links.

        MEM053's requirement, asserted rather than assumed. The two destination
        shapes coexist in this document, and a walker that assumed every
        ``/Link`` carried a coordinate array would raise on the toctree
        entries -- turning this whole class into ERRORs rather than a
        measurement. Asserting the named ones are present is what keeps the
        tolerance path exercised instead of merely written.
        """
        assert full_form_pdf.named_destinations, (
            "No NAMED /Link destinations were found in the compiled PDF, so "
            "the walker's tolerate-and-exclude path (MEM053) is no longer "
            "being exercised. The master's toctree entries are measured to "
            "produce exactly this shape, so zero of them suggests the master "
            "stopped emitting a toctree -- which would also void the "
            "cross-document arrangement the rest of this module measures."
        )
        assert all(
            link.dest_kind == "/XYZ" for link in full_form_pdf.coordinate_links
        ), (
            "A coordinate /Link destination is not the measured ``/XYZ`` "
            "explicit-coordinate shape, so the named-vs-coordinate split this "
            "walker relies on has changed: "
            f"{sorted({link.dest_kind for link in full_form_pdf.coordinate_links})}."
        )


# ---------------------------------------------------------------------------
# T03, part two: R010, the THREE-WAY cross-builder consistency check.
#
# The only requirement in M001 with no local precedent: verified at plan time
# that no existing test in this project invokes the ``html`` or ``latex``
# builder at all. Both are core Sphinx builders, so this half needs neither
# typst-py nor pypdf -- and the ``latex`` builder emits ``.tex`` only, so NO
# pdflatex run is involved and the half stays fast and hermetic.
#
# What is compared is the CORPUS-WIDE bibliography (the bare directive's), and
# the scoping is deliberate. The chapter-local directive carries a
# ``:keyprefix:``, and ``latex`` merges BOTH directives into a single
# ``sphinxthebibliography`` region, so an unscoped comparison would be matching
# a two-row list against a three-row one and the mismatch would be "explained
# away" by the prefix rather than measured. The three builders are therefore
# aligned on the one list they all render identically, keyed by the
# docname-namespaced citation id that ALL THREE agree on.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BibliographyEntry:
    """
    One rendered bibliography entry, reduced to the three properties the three
    builders must agree on: its namespaced id, its rendered label, and its
    formatted body.

    Ordering is carried by the LIST these are collected into, not by a field,
    so comparing two lists compares ordering as well as content.
    """

    key: str
    label: str
    body: str


def _namespaced_citation_id(docname: str, raw_id: str) -> str:
    """
    Join a docname and a raw docutils citation id into the namespaced form.

    Measured at T03 time: the ``latex`` builder's ``\\bibitem`` key is the SAME
    docname-namespaced id typsphinx emits as its Typst grid-row anchor
    (``refs:id2``), while ``html`` uses the BARE docutils id (``id2``) because
    each document is its own page there and needs no namespace. Namespacing the
    html side through this one helper is what makes the three keys comparable
    without rewriting either builder's output.

    The separator is taken from the translator's OWN namespacing helper rather
    than spelled as a literal, so a scheme change to, say, ``docname__id`` is
    picked up here automatically -- the same derivation
    :func:`_namespace_prefix` performs for the Typst side.
    """
    return f"{_namespace_prefix(docname)}{raw_id}"


def _extract_typst_entries(grid: ParsedGrid, docname: str) -> list[BibliographyEntry]:
    """
    Collect one Typst grid's rows as :class:`BibliographyEntry` values, in
    document order.

    The body is the concatenation of the row's ``text("...")`` payloads, joined
    with the EMPTY string. That is load-bearing and was measured: an emphasised
    run inside an entry body is a separate payload, so joining with a space
    inserts one before the following punctuation ("A study of things. J ,
    2020.") and the three-way comparison then fails on a space this module
    itself invented rather than on anything the builders disagree about.
    """
    entries: list[BibliographyEntry] = []
    for row in grid.rows:
        payloads = re.findall(r'text\("((?:[^"\\]|\\.)*)"\)', row.body)
        entries.append(
            BibliographyEntry(
                key=row.anchor,
                label=_normalise_whitespace(row.label).strip(),
                body=_normalise_whitespace("".join(payloads)).strip(),
            )
        )
    return entries


_LATEX_BIBITEM_RE = re.compile(
    r"\\bibitem\[([^\]]+)\]\{([^}]+)\}(.*?)(?=\\bibitem|\\end\{)", re.DOTALL
)


def _extract_latex_entries(tex_text: str, namespace: str) -> list[BibliographyEntry]:
    """
    Collect the ``\\bibitem`` entries of the ``sphinxthebibliography`` region
    whose keys carry ``namespace``, in document order.

    Two LaTeX-only wrappers are removed so the body compares against the other
    builders' plain text: ``\\sphinxAtStartPar`` (a paragraph-start hook with
    no rendered content) and ``\\sphinxstyleemphasis{...}`` (unwrapped to its
    argument, which is what ``html``'s ``<em>`` and Typst's emphasis both
    reduce to under tag-stripping).

    The ``namespace`` filter is what scopes this to the corpus-wide directive:
    ``latex`` merges every ``.. bibliography::`` in the project into ONE
    region, so the chapter-local directive's row sits in the same region and
    must be excluded by its own docname rather than by position.
    """
    region = re.search(
        r"\\begin\{sphinxthebibliography\}.*?\\end\{sphinxthebibliography\}",
        tex_text,
        re.DOTALL,
    )
    assert region is not None, (
        "The latex build emitted no ``sphinxthebibliography`` region at all, "
        "so there is nothing to compare the other two builders against. "
        "Either the bibliography directives stopped rendering under -b latex "
        "or the environment name changed upstream."
    )
    entries: list[BibliographyEntry] = []
    for label, key, body in _LATEX_BIBITEM_RE.findall(region.group(0)):
        if not key.startswith(namespace):
            continue
        cleaned = body.replace("\\sphinxAtStartPar", "")
        cleaned = re.sub(r"\\sphinxstyleemphasis\{([^}]*)\}", r"\1", cleaned)
        entries.append(
            BibliographyEntry(
                key=key,
                label=_normalise_whitespace(label).strip(),
                body=_normalise_whitespace(cleaned).strip(),
            )
        )
    return entries


_HTML_CITATION_RE = re.compile(
    r'<div class="citation" id="([^"]+)"[^>]*>(.*?)</div>', re.DOTALL
)
# The label span up to the entry's first paragraph. The trailing ``<p>`` is
# REQUIRED in this pattern and is not decoration: the label's own content is
# itself wrapped in nested ``<span class="fn-bracket">`` elements, so a
# non-greedy match terminated at the first ``</span>`` captures only the
# opening bracket and the extracted label comes back EMPTY -- measured at T03
# time, and it fails as a three-way label mismatch that looks like a builder
# disagreement rather than like a bad regex.
_HTML_LABEL_RE = re.compile(r'<span class="label">(.*?)</span>\s*<p>', re.DOTALL)
_HTML_BODY_RE = re.compile(r"<p>(.*?)</p>", re.DOTALL)


def _strip_html_tags(fragment: str) -> str:
    """Remove every tag from an HTML fragment, leaving its text content."""
    return re.sub(r"<[^>]+>", "", fragment)


def _extract_html_entries(html_text: str, docname: str) -> list[BibliographyEntry]:
    """
    Collect one HTML page's ``<div class="citation">`` blocks, in document
    order, with their ids namespaced so they compare against the other two
    builders.

    The ``id`` attribute match tolerates further attributes after it: measured
    at T03 time Sphinx also emits ``role="doc-biblioentry"`` on these divs, and
    a pattern anchored on ``id="..."&gt;`` matches NOTHING against that.
    """
    entries: list[BibliographyEntry] = []
    for raw_id, block in _HTML_CITATION_RE.findall(html_text):
        label_match = _HTML_LABEL_RE.search(block)
        body_match = _HTML_BODY_RE.search(block)
        assert label_match is not None and body_match is not None, (
            f"An html citation block (id={raw_id!r}) carries no label span or "
            "no paragraph, so its label/body cannot be compared against the "
            f"other builders: {block!r}"
        )
        entries.append(
            BibliographyEntry(
                key=_namespaced_citation_id(docname, raw_id),
                label=_normalise_whitespace(_strip_html_tags(label_match.group(1)))
                .strip()
                .strip("[]"),
                body=_normalise_whitespace(
                    _strip_html_tags(body_match.group(1))
                ).strip(),
            )
        )
    return entries


@pytest.fixture(scope="module")
def full_form_latex_build(full_form_gate_dir, tmp_path_factory):
    """
    Build the fixture with ``-b latex`` EXACTLY ONCE, in its own build
    directory.

    No pdflatex is involved: the builder emits ``.tex`` sources only, which is
    all R010 needs -- the comparison is of rendered bibliography CONTENT, not
    of a typeset page.
    """
    build_dir = tmp_path_factory.mktemp("full_form_gate_latex") / "_build"
    result = _run_sphinx_build(full_form_gate_dir, build_dir, buildername="latex")
    assert result.returncode == 0, (
        "sphinx-build -b latex over the full-form bibliography fixture must "
        "succeed -- R010 compares this build's bibliography against the typst "
        f"and html ones\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    return FullFormGateBuild(result=result, build_dir=build_dir)


@pytest.fixture(scope="module")
def full_form_html_build(full_form_gate_dir, tmp_path_factory):
    """Build the fixture with ``-b html`` EXACTLY ONCE, in its own build dir."""
    build_dir = tmp_path_factory.mktemp("full_form_gate_html") / "_build"
    result = _run_sphinx_build(full_form_gate_dir, build_dir, buildername="html")
    assert result.returncode == 0, (
        "sphinx-build -b html over the full-form bibliography fixture must "
        "succeed -- R010 compares this build's bibliography against the typst "
        f"and latex ones\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    return FullFormGateBuild(result=result, build_dir=build_dir)


@pytest.fixture(scope="module")
def three_builder_entries(
    parsed_grids,
    full_form_latex_build,
    full_form_html_build,
    full_form_fixture_data,
) -> dict[str, list[BibliographyEntry]]:
    """
    Extract the corpus-wide bibliography from all three builders, keyed by
    builder name, behind guards that fail LOUDLY per builder.

    Each extraction is guarded on its own so a failure names the builder that
    produced nothing. Without that, an empty extraction on one side would make
    the three-way comparison fail as an unhelpful "``[] != [...]``" and the
    natural reading would be that the builders disagree -- when in fact one
    builder's markup shape changed and the probe stopped parsing it. That
    distinction is the whole value of R010, so it is protected here rather than
    left to the comparison.
    """
    docname = full_form_fixture_data.bare_bibliography_docname

    tex_files = sorted(full_form_latex_build.build_dir.glob("*.tex"))
    assert len(tex_files) == 1, (
        "Expected exactly ONE .tex source from the latex build of this "
        f"single-master fixture, found {[path.name for path in tex_files]}."
    )
    html_path = full_form_html_build.build_dir / f"{docname}.html"
    assert html_path.exists(), (
        f"The html build emitted no {docname}.html, which is the page hosting "
        "the corpus-wide bibliography and therefore the only page R010 "
        f"compares. Emitted: "
        f"{sorted(path.name for path in full_form_html_build.build_dir.glob('*.html'))}"
    )

    entries = {
        "typst": _extract_typst_entries(parsed_grids[docname], docname),
        "latex": _extract_latex_entries(
            tex_files[0].read_text(encoding="utf-8"),
            _namespace_prefix(docname),
        ),
        "html": _extract_html_entries(html_path.read_text(encoding="utf-8"), docname),
    }

    expected = len(full_form_fixture_data.owned_keys(docname))
    for builder, extracted in entries.items():
        assert len(extracted) == expected, (
            f"Vacuous-pass guard: the {builder} extraction yielded "
            f"{len(extracted)} corpus-wide bibliography entr(y/ies) but the "
            f"bare .. bibliography:: in {docname} owns {expected} cited key(s) "
            f"({sorted(full_form_fixture_data.owned_keys(docname))}). Parsed: "
            f"{[entry.key for entry in extracted]}. If zero, that builder's "
            "bibliography markup shape changed and the three-way comparison "
            "below would be reporting a parse failure as a builder "
            "disagreement."
        )
    return entries


@pytest.mark.skipif(
    not BIBTEX_AVAILABLE,
    reason="sphinxcontrib-bibtex is required for the full-form bibliography gate",
)
class TestThreeBuilderBibliographyConsistency:
    """
    R010: the ``typst``, ``latex`` and ``html`` builders render the SAME
    bibliography from the same sources -- same keys, same labels, same entry
    bodies, same order.

    This is the requirement that makes the Typst output trustworthy as a
    PEER of Sphinx's established builders rather than merely self-consistent:
    every other gate in M001 compares typsphinx against typsphinx's own
    measured output, so none of them could detect typsphinx rendering a
    bibliography differently from how Sphinx itself does.

    Measured green at T03 time -- all three agree exactly. Were they ever to
    disagree, the correct response is to REPORT the disagreement, never to
    weaken these assertions to accommodate it: detecting exactly that is why
    R010 exists.
    """

    def test_the_three_builders_agree_on_the_citation_keys_and_order(
        self, three_builder_entries
    ):
        """
        All three builders emit the same namespaced citation ids in the same
        order.

        Keys first, and separately from bodies, because a key mismatch has a
        different cause than a body mismatch: the keys are the anchors
        cross-references resolve against, so a divergence there means a link
        that works in one builder would dangle in another.
        """
        keyed = {
            builder: [entry.key for entry in entries]
            for builder, entries in three_builder_entries.items()
        }
        assert keyed["typst"] == keyed["latex"] == keyed["html"], (
            "The three builders do NOT agree on the corpus-wide "
            f"bibliography's citation keys or their order: {keyed}. The latex "
            "\\bibitem key and the typst grid-row anchor are both the "
            "docname-namespaced docutils id, and the html side is namespaced "
            "through the translator's own scheme, so these are directly "
            "comparable."
        )

    def test_the_three_builders_agree_on_the_rendered_labels(
        self, three_builder_entries
    ):
        """
        All three builders render the same pybtex label for each entry.

        The labels come from ``sphinxcontrib.bibtex``'s pybtex style, which is
        builder-independent, so a divergence here means one builder's label
        rendering (not its bibliography) has drifted.
        """
        labelled = {
            builder: [entry.label for entry in entries]
            for builder, entries in three_builder_entries.items()
        }
        assert labelled["typst"] == labelled["latex"] == labelled["html"], (
            "The three builders do NOT agree on the rendered bibliography "
            f"labels: {labelled}."
        )

    def test_the_three_builders_agree_on_the_entry_bodies(self, three_builder_entries):
        """
        All three builders render character-identical entry bodies, after each
        builder's own markup wrappers are removed and all three are normalised
        through the one shared whitespace helper.

        The sharpest of the three comparisons and the real substance of R010:
        author, title, container and year must read the same to a reader of
        any of the three outputs.
        """
        bodied = {
            builder: [entry.body for entry in entries]
            for builder, entries in three_builder_entries.items()
        }
        assert bodied["typst"] == bodied["latex"] == bodied["html"], (
            "The three builders do NOT agree on the rendered bibliography "
            f"entry bodies: {bodied}. All three are normalised through "
            "_normalise_whitespace and have their builder-specific wrappers "
            "removed (latex's \\sphinxAtStartPar and \\sphinxstyleemphasis, "
            "html's tags, typst's text() payload quoting), so a difference "
            "here is a genuine rendering disagreement and must be reported as "
            "a finding rather than accommodated."
        )

    def test_the_compared_bibliography_is_not_empty_and_carries_real_text(
        self, three_builder_entries, full_form_fixture_data
    ):
        """
        The compared entries carry the fixture's actual entry TITLES.

        The last vacuous-pass guard of the half: three builders that all
        extracted the same EMPTY bodies would satisfy every equality above.
        Anchoring on titles parsed out of ``refs.bib`` is what makes the
        agreement an agreement about real content.
        """
        owned = full_form_fixture_data.owned_keys(
            full_form_fixture_data.bare_bibliography_docname
        )
        expected_titles = sorted(
            _normalise_whitespace(full_form_fixture_data.titles[key]) for key in owned
        )
        for builder, entries in three_builder_entries.items():
            joined = " ".join(entry.body for entry in entries)
            for title in expected_titles:
                assert title in joined, (
                    f"The {builder} extraction's entry bodies do not contain "
                    f"the title {title!r} parsed out of refs.bib, so the "
                    "three-way agreement above may be an agreement about "
                    f"empty or truncated text. Extracted bodies: "
                    f"{[entry.body for entry in entries]}"
                )

    def test_the_keyprefixed_chapter_local_entry_is_excluded_from_the_comparison(
        self, full_form_latex_build, full_form_fixture_data
    ):
        """
        The latex build's single merged bibliography region DOES also carry the
        chapter-local directive's entry, and the comparison above excludes it
        by docname rather than by accident.

        This is the scoping decision made explicit and checkable. The task plan
        requires that if the chapter-local ``:keyprefix:`` list were included,
        the prefix be accounted for EXPLICITLY rather than letting a mismatch
        be explained away. The choice made here is to scope the three-way
        comparison to the corpus-wide list, so this test proves the excluded
        row genuinely exists and is genuinely owned by the other document --
        i.e. that the scoping removes a real entry rather than silently
        matching everything.
        """
        tex_files = sorted(full_form_latex_build.build_dir.glob("*.tex"))
        tex_text = tex_files[0].read_text(encoding="utf-8")
        corpus = _extract_latex_entries(
            tex_text,
            _namespace_prefix(full_form_fixture_data.bare_bibliography_docname),
        )
        chapter_local = _extract_latex_entries(
            tex_text, _namespace_prefix(full_form_fixture_data.filtered_docname)
        )
        assert chapter_local, (
            "The latex build's bibliography region carries NO entry namespaced "
            "to the filtered chapter-local directive's document "
            f"({full_form_fixture_data.filtered_docname}), so the three-way "
            "comparison's docname scoping is excluding nothing and the "
            "two-directive coexistence is not present in this build at all. "
            "Note that the chapter-local grid IS expected to render under "
            "-b latex just as it does under -b typst."
        )
        assert not (
            {entry.key for entry in corpus} & {entry.key for entry in chapter_local}
        ), (
            "The corpus-wide and chapter-local latex extractions share a "
            "citation key, so scoping by docname namespace does not separate "
            f"the two directives: corpus={[e.key for e in corpus]}, "
            f"chapter_local={[e.key for e in chapter_local]}"
        )
        prefix = full_form_fixture_data.keyprefix
        assert prefix and not any(
            prefix in entry.key or prefix in entry.label for entry in corpus
        ), (
            f"The chapter-local directive's :keyprefix: ({prefix!r}) leaked "
            "into the corpus-wide latex entries that the three-way comparison "
            "uses, which would make the comparison compare prefixed content "
            f"against unprefixed content: {[(e.key, e.label) for e in corpus]}"
        )
