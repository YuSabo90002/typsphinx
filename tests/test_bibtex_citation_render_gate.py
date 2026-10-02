"""
M001 / S01+S02 bibtex citation render gate: R001, R002, R003, R004, R005, R014.

**Fixture shape as of S02 (multi-citation).** ``index.rst`` now carries THREE
``:cite:*:`` citing sites naming TWO distinct ``refs.bib`` keys between them:
the S01 parenthetical ``:cite:p:`` site for the first key, an S02 textual
``:cite:t:`` site for the second, and an S02 multi-key ``:cite:p:`` site
naming both in one role. Every guard in this module that S01 wrote against
the single-citation shape was generalised in S02 -- relaxed to the measured
multi-citation shape and never deleted, because the "appears exactly once"
counts below are only meaningful while the gate still knows which keys are
cited (MEM006). The counts are therefore driven off the parsed cited-key set
rather than off a single key.

**Region layout changed in S02, and it is not what the name suggests.** The
two S02 citing sites sit AFTER the ``.. bibliography::`` in the fixture, so
the emitted grid is in the MIDDLE of ``index.typ``, not at its end: a citing
marker can legitimately occur either before or after the grid. Hence prose
assertions run against ``_body_outside_grid()``, which excises the whole
balanced ``grid(...)`` call and returns everything else, instead of against
``_split_at_grid()[0]`` (which sees only the first site). ``_split_at_grid``
is kept unchanged for R002's grid-shape assertions.

**This gate is GREEN on arrival, by design.** Measured against the UNTOUCHED
translator, the ``tests/fixtures/bibtex_citation_render_gate`` fixture already
renders correctly: a ``:cite:p:`` citing site leaves a citing marker in the
body, and ``.. bibliography::`` renders as ONE Typst grid with each cited
entry appearing exactly once. A conventional RED-first gate therefore CANNOT
go RED here, and a RED was deliberately NOT manufactured by breaking
translator code. This module is a *characterisation* gate that locks current
behaviour so S02-S06 can extend the same fixture without silently regressing
the base path. ``tests/test_typst_elements_pass_through_gate.py`` is this
repo's precedent for that shape; ``tests/test_citation_render_gate.py`` is
the precedent for the scaffolding and the house rule below.

**House rule (binding, inherited from ``tests/test_citation_render_gate.py``):**
no expected label, anchor, or link-target token is ever written as a string
literal. The citation label is pybtex-generated, so it is read from Sphinx's
OWN resolved doctree (the ``citation`` node's ``label`` child); the Typst
anchor it must carry is computed by calling
``typsphinx.translator.TypstTranslator._namespace_label`` directly rather
than transcribing its derivation. Entry *prose* (an entry title) is
fixture-authored data rather than a derived token, so it is matched by value
-- but it too is parsed out of the fixture's own ``refs.bib`` instead of being
typed in here, and the set of cited keys is parsed out of the fixture's own
``index.rst``, so this gate follows the fixture if a later slice extends it.
Vacuous-pass guards assert the parse actually found something.

**Measured facts this module encodes** (S02 multi-citation fixture, emitted
``index.typ``): ``grid(`` still appears exactly 1x (ONE bibliography -- a
second one belongs to S04), each cited entry's title text exactly 1x, and each
label token more than once -- at every citing site that names it plus once in
the grid's label cell (measured: ``Smi20`` 3x, ``Tan19`` 3x). Hence the
entry-TITLE count is asserted to be exactly 1 PER CITED KEY and the LABEL
count is deliberately not asserted to be any particular number.

**refs.bib carries a third, deliberately-uncited entry (S02).** S02 cites both
of S01's entries, which would have emptied the uncited set and silently turned
``test_uncited_entries_render_no_row``'s MEM006 assertion into a no-op. Rather
than skip that test, S02 APPENDED a third entry that no citing site names, so
the MEM006 semantic ("a bare ``.. bibliography::`` renders only CITED
entries") keeps a real subject. That entry must stay uncited.

**Assertions target the content file ``index.typ``, never ``master.typ``** --
the master only holds ``#include("index.typ")``.

**R014 single-resolve rule.** Each Sphinx environment built here is resolved
AT MOST ONCE explicitly, and every explicit resolve lives in a module-scoped
fixture so no test can add one: ``bibtex_gate_doctree`` (which supplies the
derived label/anchor tokens) and ``resolve_count_observation`` (which pins the
hazard itself, see ``TestResolveCountHazard``) own one apiece, against two
independent ``SphinxTestApp`` environments. That single extra resolve is
measured to show a GROWN child list on EVERY ``citation`` node
(``['label', 'paragraph', 'label', 'paragraph']``, i.e. each child duplicated)
whereas the real write pass sees exactly two children
``['label', 'paragraph']`` per citation. The 4-child shape is a
double-resolve artifact: NO
child-count expectation is derived from it anywhere below EXCEPT in
``TestResolveCountHazard``, which asserts only the DIRECTION of the growth and
never the number 4; the label is read as the FIRST ``label`` descendant rather
than by counting.

**S02's own two forms are asserted separately, because the S01 classes are
form-blind.** ``TestBibtexCitationRenderGateTyp`` asserts that every cited key
leaves a resolved marker outside the grid -- which is equally true of a
parenthetical, a textual or a multi-key site. What makes each form itself is
asserted in ``TestTextualAndMultiKeyCitingForms`` (emitted ``.typ``) and
``TestTextualAndMultiKeyCitingFormsCompiledPdf`` (compiled PDF): for the
textual form, that the author surname text node precedes the ``[`` so the
author is named OUTSIDE the bracket group (R005); for the multi-key form, that
ONE bracket group holds both resolved references separated by a ``", "`` Text
node in the rst role argument's order (R004). Both are asserted as single
contiguous patterns matching EXACTLY ONCE -- separate per-token membership
checks would pass for the very shapes these requirements deny (a surname that
merely occurs earlier in the paragraph; two separate bracket groups).

Requirements: R001 (citing marker in the body), R002 (bibliography as one
Typst grid), R003 (each entry exactly once -- asserted at both the ``.typ``
and the compiled-PDF level), R004 (the multi-key citing form), R005 (the
textual citing form), R014 (the resolve-count hazard, pinned as an executable
fact).
"""

import io
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest
from docutils import nodes as docutils_nodes

from typsphinx.translator import TypstTranslator

try:
    import sphinxcontrib.bibtex  # noqa: F401

    BIBTEX_AVAILABLE = True
except ImportError:
    BIBTEX_AVAILABLE = False

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


# The fixture's single document. This is a docname (a filename on disk), not a
# generated label/anchor token, so naming it here does not breach the house
# rule -- the fixture deliberately has no second.rst and no toctree (S05 owns
# the cross-document case).
DOCNAME = "index"

# The content file the two-layer split writes for DOCNAME. Every assertion in
# this module reads THIS file, never master.typ.
CONTENT_TYP = f"{DOCNAME}.typ"


# ---------------------------------------------------------------------------
# Fixture-authored data, parsed from the fixture rather than transcribed.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def bibtex_gate_dir():
    """Return the path to the bibtex_citation_render_gate fixture (T02)."""
    return Path(__file__).parent / "fixtures" / "bibtex_citation_render_gate"


def _parse_bib_field(bib_text: str, field: str) -> dict[str, str]:
    """
    Return ``{entry_key: value}`` for one quoted ``refs.bib`` field.

    ``%``-comment lines are stripped first: the fixture's ``refs.bib`` carries
    a header comment block that itself mentions entry titles, which would
    otherwise be picked up as entries.
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


def _parse_bib_titles(bib_text: str) -> dict[str, str]:
    """Return ``{entry_key: title}`` parsed from ``refs.bib``."""
    return _parse_bib_field(bib_text, "title")


def _parse_bib_authors(bib_text: str) -> dict[str, str]:
    """
    Return ``{entry_key: author}`` parsed from ``refs.bib`` (S02/T03).

    Needed by the textual-form assertion: sphinxcontrib-bibtex renders a
    ``cite:t`` site as the cited entry's author SURNAME followed by the
    bracketed label, so the surname is the token that proves the form. Like
    the titles, it is parsed out of the fixture's own ``refs.bib`` rather than
    typed in here (house rule).
    """
    return _parse_bib_field(bib_text, "author")


def _author_surname(author: str) -> str:
    """
    Return the surname sphinxcontrib-bibtex renders for a ``refs.bib`` author
    field written in ``"First Last"`` order.

    Measured against the fixture: ``"Taro Tanaka"`` -> ``"Tanaka"``, which is
    exactly what the emitted textual citing marker carries. Deliberately the
    LAST whitespace-separated word rather than a general bibtex name parser --
    the fixture authors its two names in plain ``First Last`` order, and a
    fixture edit to a ``"Last, First"`` or ``and``-joined form must fail the
    vacuous-pass guard in ``bibtex_fixture_data`` loudly rather than be
    silently mis-split here.
    """
    return author.split()[-1] if author.split() else ""


def _parse_citing_sites(rst_text: str) -> list[str]:
    """
    Return the RAW role argument of every ``:cite:*:`` site in ``index.rst``,
    one entry per citing SITE -- not per key.

    A multi-key site such as ``:cite:p:`A,B``` therefore yields the single
    pseudo-key string ``"A,B"``. Use :func:`_expand_cited_keys` to turn these
    raw arguments into the distinct set of keys actually cited; passing a raw
    argument to ``titles[...]`` would ``KeyError`` on the comma string.
    """
    return [argument for _, argument in _parse_citing_sites_with_roles(rst_text)]


def _parse_citing_sites_with_roles(rst_text: str) -> list[tuple[str, str]]:
    """
    Return ``(role_suffix, raw_argument)`` for every ``:cite:*:`` site in
    ``index.rst``, in document order (S02/T03).

    The role suffix is what distinguishes the forms this slice exists to
    prove: ``"p"`` for the parenthetical ``:cite:p:`` sites and ``"t"`` for the
    textual ``:cite:t:`` one. S01 only ever needed the arguments, so
    :func:`_parse_citing_sites` is now derived from this function -- one regex,
    so the site COUNT and the per-role lookups can never disagree.
    """
    return re.findall(r":cite:([a-z]*):`([^`]+)`", rst_text)


def _expand_cited_keys(citing_sites: list[str]) -> list[str]:
    """
    Expand raw citing-site arguments into the DISTINCT keys they cite, in
    first-appearance order.

    sphinxcontrib-bibtex lets one role name several comma-separated keys, so a
    raw argument is split on commas and each part stripped. Measured against
    the S02 fixture: the three raw captures
    ``['Smith2020', 'Tanaka2019', 'Smith2020,Tanaka2019']`` expand to the
    two distinct keys ``['Smith2020', 'Tanaka2019']``.
    """
    keys: list[str] = []
    for site in citing_sites:
        for part in site.split(","):
            key = part.strip()
            if key and key not in keys:
                keys.append(key)
    return keys


@dataclass
class BibtexFixtureData:
    """The fixture's own authored data: which keys it cites, and the title
    text of every entry in its ``refs.bib``."""

    citing_sites: list[str]
    cited_keys: list[str]
    titles: dict[str, str]
    role_sites: list[tuple[str, str]]
    authors: dict[str, str]

    @property
    def textual_key(self) -> str:
        """
        The single key cited by the fixture's TEXTUAL (``cite:t``) site (S02).

        ``bibtex_fixture_data`` guards that exactly one such site exists and
        that it names exactly one key, so this accessor cannot silently
        describe the wrong form.
        """
        textual = [argument for role, argument in self.role_sites if role == "t"]
        return textual[0].strip()

    @property
    def multi_keys(self) -> list[str]:
        """
        The keys of the fixture's MULTI-KEY site, in the order the rst role
        argument names them (S02).

        Order matters: the emitted markup is asserted to preserve it, so this
        must stay the rst order and must not be sorted or de-duplicated
        against the document-wide cited set.
        """
        multi = [argument for argument in self.citing_sites if "," in argument]
        return [part.strip() for part in multi[0].split(",") if part.strip()]

    @property
    def cited_titles(self) -> list[str]:
        """
        The titles of every DISTINCT cited entry, in first-citation order.

        Replaces S01's singular ``cited_title``: from S02 on, the fixture
        cites more than one entry, and a single-title accessor would have
        quietly described only the first of them.
        """
        return [self.titles[key] for key in self.cited_keys]

    @property
    def uncited_titles(self) -> list[str]:
        """
        Titles of ``refs.bib`` entries this fixture never cites.

        Computed against the EXPANDED key set, so a key named only inside a
        multi-key role still counts as cited.
        """
        return [
            title for key, title in self.titles.items() if key not in self.cited_keys
        ]


@pytest.fixture(scope="module")
def bibtex_fixture_data(bibtex_gate_dir):
    """
    Parse the fixture's ``refs.bib`` and ``index.rst`` into the authored data
    the assertions below compare against, with vacuous-pass guards so a
    fixture edit that breaks the parse fails loudly here instead of silently
    weakening every count assertion into a no-op.
    """
    bib_text = (bibtex_gate_dir / "refs.bib").read_text(encoding="utf-8")
    titles = _parse_bib_titles(bib_text)
    authors = _parse_bib_authors(bib_text)
    rst_text = (bibtex_gate_dir / f"{DOCNAME}.rst").read_text(encoding="utf-8")
    role_sites = _parse_citing_sites_with_roles(rst_text)
    citing_sites = _parse_citing_sites(rst_text)
    cited_keys = _expand_cited_keys(citing_sites)

    assert titles, (
        "Vacuous-pass guard: parsed NO entries out of the fixture's refs.bib, "
        "so every 'appears exactly once' count below would compare against "
        "nothing. Did refs.bib's entry formatting change?"
    )

    # S02 shape, asserted by FORM rather than by raw count alone, so the guard
    # says what it is protecting: one parenthetical single-key site (S01), one
    # textual site and one multi-key site (S02). A later slice that adds a
    # fourth site must update these numbers deliberately -- that is the point.
    assert len(citing_sites) == 3, (
        "This gate locks the S01 single-key site PLUS S02's textual and "
        "multi-key sites: it expects index.rst to carry exactly three "
        f":cite:* sites, but parsed {citing_sites!r}. A cross-document or "
        "second-bibliography case belongs to S05/S04 and needs its own "
        "counts -- do not let a new site silently redefine this gate's "
        "expectations. (NOTE: this regexes the RAW rst, so a fully-colonised "
        "role name written inside an rst comment also counts as a site.)"
    )
    multi_key_sites = [site for site in citing_sites if "," in site]
    assert len(multi_key_sites) == 1, (
        "S02 locks exactly ONE multi-key citing site (a single role naming "
        f"several comma-separated keys), but parsed {citing_sites!r}. Without "
        "it the comma-expansion below and the multi-key markup assertions "
        "have no subject."
    )
    assert len(_expand_cited_keys(multi_key_sites)) >= 2, (
        f"S02's multi-key site {multi_key_sites[0]!r} expands to fewer than "
        "two keys, so it is not actually a multi-key site."
    )
    assert len(cited_keys) == 2, (
        "S02 cites exactly TWO distinct refs.bib keys across its three sites "
        f"(measured expansion of {citing_sites!r} -> {cited_keys!r}). The "
        "per-key counts below are driven off this set, so a change here must "
        "be deliberate."
    )

    # Vacuous-pass guard, retained from S01 but now over every expanded key:
    # before S02's comma-splitting, the raw "A,B" pseudo-key would have been
    # looked up in `titles` directly and either KeyError'd or been misfiled as
    # an UNCITED key, quietly inverting test_uncited_entries_render_no_row.
    for key in cited_keys:
        assert key in titles, (
            f"index.rst cites {key!r} but refs.bib has no such entry "
            f"(known entries: {sorted(titles)}). If {key!r} still contains a "
            "comma, the citing-site arguments were not expanded into "
            "individual keys."
        )
        assert titles[key].strip(), (
            f"The cited entry {key!r} has an empty title in refs.bib, so "
            "counting its occurrences would be meaningless."
        )

    distinct_titles = {titles[key] for key in cited_keys}
    assert len(distinct_titles) == len(cited_keys), (
        "The cited entries must have DISTINCT titles, otherwise an "
        "'appears exactly once' count for one entry can be satisfied by "
        f"another: {[titles[key] for key in cited_keys]!r}."
    )

    # S02/T03 vacuous-pass guards for the two FORMS this slice proves. Without
    # them, `textual_key` / `multi_keys` could IndexError (loud but obscure) or
    # -- worse -- describe the wrong site after a fixture edit, which would
    # quietly point the form assertions below at the parenthetical S01 marker
    # they are specifically meant NOT to match.
    textual_sites = [argument for role, argument in role_sites if role == "t"]
    assert len(textual_sites) == 1, (
        "S02 locks exactly ONE textual (cite:t) citing site, but parsed "
        f"{role_sites!r}. Without it the textual-form assertion has no "
        "subject; with two, it could not say which one it describes."
    )
    assert "," not in textual_sites[0], (
        f"The textual citing site {textual_sites[0]!r} names more than one "
        "key. S02's textual form is single-key: the emitted markup puts ONE "
        "author surname before the bracket group, so a multi-key textual site "
        "would need its own measured expectation."
    )
    textual_key = textual_sites[0].strip()
    assert textual_key in authors, (
        f"The textual site cites {textual_key!r} but no author field was "
        f"parsed for it out of refs.bib (parsed authors: {sorted(authors)}). "
        "The textual-form assertion derives the expected surname from that "
        "field, so it would have nothing to assert."
    )
    surname = _author_surname(authors[textual_key])
    assert surname and surname.isalpha(), (
        f"Derived an unusable surname {surname!r} from the author field "
        f"{authors[textual_key]!r} of textual key {textual_key!r}. "
        "_author_surname takes the LAST whitespace-separated word, which "
        "assumes a plain 'First Last' author field -- a 'Last, First' or "
        "'A and B' field needs a real name parser, not this helper."
    )

    multi_sites = [argument for argument in citing_sites if "," in argument]
    multi_keys = [part.strip() for part in multi_sites[0].split(",") if part.strip()]
    assert len(multi_keys) == len(set(multi_keys)), (
        f"The multi-key site {multi_sites[0]!r} names the same key twice. The "
        "ordered two-link markup assertion needs two DISTINCT keys, otherwise "
        "the 'rst order is preserved' claim is untestable."
    )
    for key in multi_keys:
        assert key in titles, (
            f"The multi-key site names {key!r}, which refs.bib has no entry "
            f"for (known entries: {sorted(titles)})."
        )

    return BibtexFixtureData(
        citing_sites=citing_sites,
        cited_keys=cited_keys,
        titles=titles,
        role_sites=role_sites,
        authors=authors,
    )


# ---------------------------------------------------------------------------
# Builds. Two module-scoped builds, each run exactly once:
#   * -b typst    -> the .typ-level and doctree assertions (no typst-py need)
#   * -b typstpdf -> the compiled-PDF assertion only (typst-py + pypdf)
# ---------------------------------------------------------------------------


def _run_sphinx_build(
    source_dir: Path, build_dir: Path, buildername: str
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <buildername>`` as a subprocess.

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build`` and
    never a bare ``sphinx-build``) -- the NixOS PATH-shadowing hazard
    restated in every render-gate module in this project. Under ``uv run``
    this resolves to the worktree venv's python, so ``import typsphinx``
    binds to the worktree's editable copy.
    """
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            buildername,
            str(source_dir),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
    )


@dataclass
class BibtexGateBuild:
    """One real build of the bibtex fixture, captured once per module."""

    result: subprocess.CompletedProcess
    build_dir: Path

    def read_content_typ(self) -> str:
        """
        Return the text of the emitted content ``.typ``, failing with a clear
        ``AssertionError`` naming the missing artifact and the build's own
        stderr rather than letting a caller hit ``FileNotFoundError``.
        """
        path = self.build_dir / CONTENT_TYP
        if not path.exists():
            raise AssertionError(
                f"{CONTENT_TYP} was never emitted (missing artifact) -- build "
                f"returncode={self.result.returncode}\n"
                f"stdout: {self.result.stdout}\nstderr: {self.result.stderr}"
            )
        return path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def bibtex_gate_build(bibtex_gate_dir, tmp_path_factory):
    """
    Build the fixture with ``-b typst`` EXACTLY ONCE for the whole module.

    Unlike the pre-fix gate in ``tests/test_citation_render_gate.py``, this
    fixture DOES assert a clean exit: this gate is green on arrival, so a
    non-zero build is itself the regression it exists to catch, and reporting
    it once here is clearer than letting it surface as four unrelated
    assertion failures.
    """
    build_dir = tmp_path_factory.mktemp("bibtex_gate_typ") / "_build"
    result = _run_sphinx_build(bibtex_gate_dir, build_dir, "typst")
    assert result.returncode == 0, (
        "sphinx-build -b typst over the bibtex fixture must succeed (this "
        "gate locks measured-working behaviour and is green on arrival)\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    return BibtexGateBuild(result=result, build_dir=build_dir)


@pytest.fixture(scope="module")
def bibtex_gate_pdf_build(bibtex_gate_dir, tmp_path_factory):
    """
    Compile the fixture through ``-b typstpdf`` EXACTLY ONCE for the whole
    module, for the compiled-PDF half only.

    Declared at module level rather than inside the PDF test class: a
    class-scoped fixture defined in the class body and depending on these
    broader-scoped fixtures trips pytest's own
    ``assert not self._finalizers`` internal check (observed as a fixture
    ERROR, not a test failure, on pytest 8 / python 3.14).
    """
    build_dir = tmp_path_factory.mktemp("bibtex_gate_pdf") / "_build"
    result = _run_sphinx_build(bibtex_gate_dir, build_dir, "typstpdf")
    assert result.returncode == 0, (
        "sphinx-build -b typstpdf over the bibtex fixture must succeed "
        "(this gate is green on arrival)\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    return BibtexGateBuild(result=result, build_dir=build_dir)


@pytest.fixture(scope="module")
def bibtex_gate_doctree(bibtex_gate_dir, tmp_path_factory):
    """
    Build the fixture through a real in-process ``SphinxTestApp`` (``-b
    typst``) and return the RESOLVED doctree, so the pybtex-generated citation
    label and the citation's docutils-assigned id can be READ rather than
    guessed (house rule).

    This is the module's ONE AND ONLY ``get_and_resolve_doctree`` call (R014).
    The resolve is measured to duplicate the ``citation`` node's children, so
    callers must read the FIRST matching descendant and must never assert a
    child count from this doctree.
    """
    from sphinx.testing.util import SphinxTestApp

    builddir = tmp_path_factory.mktemp("bibtex_gate_doctree")
    app = SphinxTestApp(
        buildername="typst",
        srcdir=bibtex_gate_dir.resolve(),
        builddir=builddir,
    )
    try:
        app.build()
        yield app.env.get_and_resolve_doctree(
            DOCNAME, app.builder, tags=app.builder.tags
        )
    finally:
        app.cleanup()


def _first_paragraph_text(citation) -> str:
    """
    Return the text of a resolved ``citation`` node's FIRST ``paragraph``
    descendant -- the rendered entry body.

    Reads the FIRST descendant rather than joining them all, for the same R014
    reason the label is read that way: the module's one extra
    ``get_and_resolve_doctree()`` duplicates each ``label``/``paragraph`` pair,
    so joining would double the text. The duplicates carry identical text, so
    the first one is the whole entry body.
    """
    paragraphs = list(citation.findall(docutils_nodes.paragraph))
    return paragraphs[0].astext() if paragraphs else ""


@dataclass
class DerivedCitationTokens:
    """Tokens read out of Sphinx's own resolved doctree / computed by the
    translator's own helper -- never transcribed."""

    label: str
    anchor: str


@pytest.fixture(scope="module")
def derived_tokens(bibtex_gate_doctree, bibtex_fixture_data):
    """
    Return ``{cited_key: DerivedCitationTokens}`` -- for each key the fixture
    cites, the citation label read out of the resolved doctree and the Typst
    anchor its citing markers must link to, computed by calling the
    translator's own ``_namespace_label``.

    Generalised from S01's single ``DerivedCitationTokens``: S02's fixture
    cites both ``refs.bib`` entries, so the bibliography holds TWO resolved
    ``citation`` nodes and a scalar accessor could only have described one.

    **Mapping a citation node back to its bibtex key.** The resolved
    ``citation`` node carries no bibtex key at all -- measured, its attributes
    are only ``['backrefs', 'classes', 'docname', 'dupnames', 'ids', 'names']``
    with ``ids=['id3']`` / ``['id4']`` and ``names=[]``. The link is therefore
    made through the entry TITLE, which the house rule classifies as
    fixture-authored prose (parsed out of the fixture's own ``refs.bib``, not
    typed in here) and which ``refs.bib``'s header comment deliberately keeps
    distinct per entry. A vacuous-pass guard below fails loudly if any cited
    key finds no node or if two keys claim the same one.

    Passing the class itself as ``self`` is safe: ``_namespace_label`` only
    calls ``self._sanitize_label(...)``, which is a ``staticmethod``
    resolvable through the class object with no instance state (the same
    technique ``tests/test_citation_render_gate.py`` documents).
    """
    citations = list(bibtex_gate_doctree.findall(docutils_nodes.citation))
    expected = len(bibtex_fixture_data.cited_keys)
    assert len(citations) == expected, (
        "Expected exactly one resolved citation node per DISTINCT cited key "
        f"({expected}, for {bibtex_fixture_data.cited_keys!r}), found "
        f"{len(citations)}. A bare .. bibliography:: renders only cited "
        "entries (MEM006), so these numbers must agree. (Note: this counts "
        "CITATION nodes, not their children -- the children are duplicated by "
        "this extra resolve and are never counted here.)"
    )

    tokens: dict[str, DerivedCitationTokens] = {}
    claimed_by: dict[int, str] = {}
    for key in bibtex_fixture_data.cited_keys:
        title = bibtex_fixture_data.titles[key]
        matching = [
            citation
            for citation in citations
            if title in _first_paragraph_text(citation)
        ]
        assert len(matching) == 1, (
            f"Expected exactly one resolved citation node whose rendered entry "
            f"body contains the title {title!r} of cited key {key!r}, found "
            f"{len(matching)}. Without a 1:1 key->node mapping the per-key "
            "label and anchor below would describe the wrong entry."
        )
        citation = matching[0]
        assert id(citation) not in claimed_by, (
            f"Cited keys {claimed_by[id(citation)]!r} and {key!r} both mapped "
            "to the SAME resolved citation node, so their titles are not "
            "distinguishable. Give refs.bib entries distinct titles."
        )
        claimed_by[id(citation)] = key

        # FIRST label descendant, deliberately not a count: the extra resolve
        # duplicates it.
        labels = list(citation.findall(docutils_nodes.label))
        assert (
            labels
        ), f"Resolved citation node for {key!r} carries no label child to read."
        label = labels[0].astext().strip()
        assert label, f"Resolved citation label for {key!r} is empty."

        ids = citation.get("ids") or []
        assert (
            ids
        ), f"Resolved citation node for {key!r} carries no id to anchor against."
        anchor = TypstTranslator._namespace_label(TypstTranslator, DOCNAME, ids[0])
        tokens[key] = DerivedCitationTokens(label=label, anchor=anchor)

    distinct_labels = {token.label for token in tokens.values()}
    assert len(distinct_labels) == len(tokens), (
        "The cited entries must resolve to DISTINCT citation labels, otherwise "
        "a per-key markup assertion can be satisfied by the wrong entry's "
        f"marker: {sorted(token.label for token in tokens.values())!r}."
    )
    return tokens


@dataclass
class ResolveCountObservation:
    """
    Two measurements of the citation nodes' child lists: what the real write
    pass handed ``visit_citation``, and what one further
    ``get_and_resolve_doctree()`` on the finished environment yields.

    Both counts are measured, never transcribed -- see ``TestResolveCountHazard``
    for why the comparison between them must stay directional.

    S02 generalised the two scalar counts into per-citation lists, because the
    fixture now renders one citation node per cited key and ``visit_citation``
    is consequently called once per key. The scalar accessors the directional
    assertion reads are deliberately the CONSERVATIVE ends of those lists --
    the largest write-pass count against the smallest resolved count -- so the
    comparison cannot pass merely because one citation happened to grow while
    another did not.
    """

    write_pass_child_names: list[list[str]]
    resolved_again_child_names: list[list[str]]

    @property
    def write_pass_children(self) -> int:
        """The LARGEST child count any citation handed the write pass."""
        return max(len(names) for names in self.write_pass_child_names)

    @property
    def resolved_again_children(self) -> int:
        """The SMALLEST child count any citation shows after the extra resolve."""
        return min(len(names) for names in self.resolved_again_child_names)


@pytest.fixture(scope="module")
def resolve_count_observation(bibtex_gate_dir, tmp_path_factory, bibtex_fixture_data):
    """
    Build the fixture once through its own ``SphinxTestApp``, recording the
    citation's child count as the REAL write pass sees it, then resolve the
    finished environment's doctree ONE more time and record the grown count.

    The write-pass count is captured by temporarily wrapping
    ``TypstTranslator.visit_citation`` -- the same technique planning used to
    measure the figure in the first place. The wrapper is installed through
    ``pytest.MonkeyPatch`` so the class attribute is restored even if
    ``app.build()`` raises; a leaked wrapper would silently record counts for
    every later test module in the session.

    This fixture owns the module's SECOND and last explicit resolve (R014).
    It runs against its own app/environment, independent of
    ``bibtex_gate_doctree``, so neither fixture perturbs the other's counts.
    """
    from sphinx.testing.util import SphinxTestApp

    observed_child_names: list[list[str]] = []
    original_visit_citation = TypstTranslator.visit_citation

    def recording_visit_citation(self, node):
        observed_child_names.append([child.tagname for child in node.children])
        return original_visit_citation(self, node)

    builddir = tmp_path_factory.mktemp("bibtex_gate_resolve_count")
    app = SphinxTestApp(
        buildername="typst",
        srcdir=bibtex_gate_dir.resolve(),
        builddir=builddir,
    )
    try:
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(TypstTranslator, "visit_citation", recording_visit_citation)
            app.build()

        expected = len(bibtex_fixture_data.cited_keys)
        assert len(observed_child_names) == expected, (
            "Vacuous-pass guard: expected visit_citation to be called EXACTLY "
            "once per DISTINCT cited key during the write pass "
            f"({expected}, for {bibtex_fixture_data.cited_keys!r}), but "
            f"recorded {len(observed_child_names)} call(s) "
            f"({observed_child_names!r}). With no recorded call the R014 "
            "comparison below would have nothing to compare against; with a "
            "count that does not track the cited keys, the write pass is not "
            "seeing the bibliography this fixture describes."
        )

        resolved = app.env.get_and_resolve_doctree(
            DOCNAME, app.builder, tags=app.builder.tags
        )
        citations = list(resolved.findall(docutils_nodes.citation))
        assert len(citations) == expected, (
            "Expected exactly one resolved citation node per distinct cited "
            f"key ({expected}), found {len(citations)}."
        )
        resolved_child_names = [
            [child.tagname for child in citation.children] for citation in citations
        ]

        yield ResolveCountObservation(
            write_pass_child_names=observed_child_names,
            resolved_again_child_names=resolved_child_names,
        )
    finally:
        app.cleanup()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _split_at_grid(typ_text: str) -> tuple[str, str]:
    """
    Split the emitted ``.typ`` into ``(before_grid, grid_onwards)`` at the
    first ``grid(`` call, raising a clear ``AssertionError`` if no grid was
    emitted at all.

    ``before_grid`` is the document body proper -- where a citing marker must
    appear for R001 -- and excludes the bibliography's own label cell, which
    repeats the same label token.
    """
    index = typ_text.find("grid(")
    if index == -1:
        raise AssertionError(
            "No grid( call was emitted, so the bibliography did not render as "
            f"a Typst grid at all:\n{typ_text}"
        )
    return typ_text[:index], typ_text[index:]


def _body_outside_grid(typ_text: str) -> str:
    """
    Return the emitted ``.typ`` with the whole balanced ``grid(...)`` call
    EXCISED -- i.e. every region of the document that is not the bibliography.

    **Why this exists and why ``_split_at_grid`` is not enough.** S02 appended
    its textual and multi-key citing sites AFTER the ``.. bibliography::``, so
    the grid is emitted in the MIDDLE of ``index.typ`` (measured: it starts at
    offset 727 of 1571, with the "Textual Site" and "Multi Site" paragraphs
    following it). ``_split_at_grid(...)[0]`` therefore sees only S01's first
    citing site, and a per-key marker assertion run against it would fail for
    every key cited only below the bibliography. Excising the grid keeps the
    property that actually matters -- a citing marker must be found OUTSIDE
    the bibliography's own label cells, which repeat the same label tokens --
    while staying indifferent to where in the document the bibliography sits.

    The end of the call is found by balancing parentheses from ``grid(``,
    skipping over Typst string literals (and their ``\\`` escapes) so a ``(``
    or ``)`` inside ``text("...")`` cannot throw the depth off.
    """
    start = typ_text.find("grid(")
    if start == -1:
        raise AssertionError(
            "No grid( call was emitted, so the bibliography did not render as "
            f"a Typst grid at all:\n{typ_text}"
        )

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
            "The emitted grid( call is not parenthesis-balanced, so the "
            "bibliography region could not be excised. Depth reached "
            f"{depth} at end of file:\n{typ_text[start:]}"
        )

    grid_region = typ_text[start:end]
    body = typ_text[:start] + typ_text[end:]

    # Vacuous-pass guards: prove the excision actually bounded the grid rather
    # than swallowing the document (which would make every assertion over
    # `body` a no-op) or stopping short of the grid's own label cells.
    assert "columns: (auto, 1fr)" in grid_region, (
        "Vacuous-pass guard: the excised region does not contain the "
        "bibliography grid's own 'columns: (auto, 1fr)' declaration, so the "
        f"parenthesis balancing bounded the wrong span:\n{grid_region}"
    )
    assert "columns: (auto, 1fr)" not in body, (
        "Vacuous-pass guard: the grid's 'columns: (auto, 1fr)' declaration is "
        "still present after excision, so the grid region was not removed "
        f"from the body:\n{body}"
    )
    assert body.strip(), (
        "Vacuous-pass guard: excising the grid left NO body text, so every "
        f"assertion over the body region would pass vacuously:\n{typ_text}"
    )
    return body


def _parse_grid_row_anchors(grid_region: str) -> dict[str, str]:
    """
    Return ``{row_label: row_anchor}`` parsed out of the bibliography grid
    region (S02/T03).

    Measured shape of one row's label cell::

        [#{text("[") + text("Smi20") + text("]")} <index:id3>]

    i.e. the bracketed label built by string concatenation, followed by the
    Typst label the row is anchored at. This is parsed rather than derived so
    the cross-reference assertion compares the body's OWN link targets against
    the grid's OWN anchors -- two independent readings of the emitted file.
    Both are also cross-checked against ``derived_tokens``, which reads the
    same tokens out of Sphinx's resolved doctree instead.
    """
    rows = re.findall(
        r'text\("\["\)\s*\+\s*text\("([^"]+)"\)\s*\+\s*text\("\]"\)\}\s*<([^>]+)>',
        grid_region,
    )
    return dict(rows)


def _normalise_whitespace(text: str) -> str:
    """
    Collapse every whitespace run to a single space.

    Required before counting a title in PDF-extracted text: Typst breaks lines
    inside a justified paragraph, which splits a title string across a newline
    and defeats a naive ``str.count()``.
    """
    return re.sub(r"\s+", " ", text)


def _pdf_text(pdf_path: Path) -> str:
    """Return whitespace-normalised text extracted from every page."""
    reader = pypdf.PdfReader(io.BytesIO(pdf_path.read_bytes()))
    return _normalise_whitespace(" ".join(page.extract_text() for page in reader.pages))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not BIBTEX_AVAILABLE,
    reason="sphinxcontrib-bibtex is required for the bibtex citation render "
    "gate (declared in the dev extra only -- see T01)",
)
class TestBibtexCitationRenderGateTyp:
    """R001, R002 and R003 at the emitted-``.typ`` level."""

    def test_body_carries_citing_marker(
        self, bibtex_gate_build, derived_tokens, bibtex_fixture_data
    ):
        """
        R001: the content ``.typ`` body carries a citing marker for EVERY key
        the fixture cites.

        Each key's doctree-derived label token must appear in the body region
        OUTSIDE the bibliography grid (the grid's own label cells repeat them),
        and must be wrapped in a ``link()`` to that citation's anchor as
        computed by the translator's own ``_namespace_label`` -- proving each
        citing SITE rendered as a resolved cross-reference, not merely that the
        characters occur somewhere in the file.

        Generalised in S02 from one key to the whole cited set, and switched
        from ``_split_at_grid(...)[0]`` to ``_body_outside_grid`` because S02's
        sites sit after the bibliography (see that helper's docstring).
        """
        content_typ = bibtex_gate_build.read_content_typ()
        body = _body_outside_grid(content_typ)

        for key in bibtex_fixture_data.cited_keys:
            tokens = derived_tokens[key]

            assert tokens.label in body, (
                f"R001: the citing marker {tokens.label!r} for cited key "
                f"{key!r} (read from Sphinx's resolved doctree) does not "
                "appear anywhere outside the bibliography grid, so that "
                f":cite:* site did not render a marker:\n{body}"
            )

            link_pattern = re.compile(
                r"link\(<" + re.escape(tokens.anchor) + r">,\s*"
                r'text\("' + re.escape(tokens.label) + r'"\)',
                re.S,
            )
            assert link_pattern.search(body), (
                f"R001: expected the body citing marker {tokens.label!r} for "
                f"cited key {key!r} to be a link to the citation anchor "
                f"{tokens.anchor!r} (computed via "
                "TypstTranslator._namespace_label), but no such link( call "
                f"was found outside the grid:\n{body}"
            )

    def test_bibliography_renders_as_exactly_one_two_column_grid(
        self, bibtex_gate_build
    ):
        """
        R002: the bibliography renders as exactly one ``grid(`` in the content
        ``.typ``, and that grid carries the two-column ``columns: (auto, 1fr)``
        shape (label cell + entry-body cell).
        """
        content_typ = bibtex_gate_build.read_content_typ()

        grid_count = content_typ.count("grid(")
        assert grid_count == 1, (
            "R002: the single bibliography must render as exactly ONE Typst "
            f"grid, found {grid_count} grid( call(s) in {CONTENT_TYP}:\n"
            f"{content_typ}"
        )

        _, grid_onwards = _split_at_grid(content_typ)
        assert "columns: (auto, 1fr)" in grid_onwards, (
            "R002: the bibliography grid must declare the two-column "
            "'columns: (auto, 1fr)' shape (auto-width label cell, flexible "
            f"entry-body cell), but that declaration is absent:\n{grid_onwards}"
        )

    def test_cited_entry_appears_exactly_once_in_typ(
        self, bibtex_gate_build, bibtex_fixture_data
    ):
        """
        R003 (``.typ`` level): EACH cited bibliography entry's title text
        appears exactly once in the content ``.typ`` -- every entry is rendered
        once, not doubled.

        Counts the entry TITLE, not the label token: a label legitimately
        appears once per citing site that names it plus once in the grid label
        cell (measured: 3x each under S02's three sites), which is why no label
        count is asserted here.
        """
        content_typ = bibtex_gate_build.read_content_typ()

        for key, title in zip(
            bibtex_fixture_data.cited_keys,
            bibtex_fixture_data.cited_titles,
            strict=True,
        ):
            occurrences = content_typ.count(title)
            assert occurrences == 1, (
                f"R003: the cited entry title {title!r} (key {key!r}) must "
                f"appear EXACTLY ONCE in {CONTENT_TYP}, found {occurrences}. "
                "More than one means the bibliography entry was doubled; zero "
                f"means it never rendered:\n{content_typ}"
            )

    def test_uncited_entries_render_no_row(
        self, bibtex_gate_build, bibtex_fixture_data
    ):
        """
        R003 (corollary, MEM006): a bare ``.. bibliography::`` renders ONLY
        cited entries, so an entry present in ``refs.bib`` but never cited
        contributes no row and its title must not appear at all.

        This pins the measured semantics that make the exactly-once counts
        above meaningful: those counts are over CITED keys only.

        S02 cites BOTH of S01's ``refs.bib`` entries, which would have emptied
        the uncited set and tripped the vacuous-pass guard below. Rather than
        skip this test -- MEM006 is a measured semantic worth keeping
        executable -- S02 APPENDED a third entry to ``refs.bib`` that no citing
        site names. That entry exists for this test; keep it uncited.
        """
        content_typ = bibtex_gate_build.read_content_typ()
        uncited = bibtex_fixture_data.uncited_titles
        assert uncited, (
            "Vacuous-pass guard: refs.bib has no uncited entry, so this test "
            "would assert nothing. The fixture is meant to keep at least one "
            "uncited entry so 'exactly once' can never be satisfied by the "
            "wrong entry. If a slice started citing the entry refs.bib marks "
            "as deliberately uncited, APPEND a new uncited entry rather than "
            "weakening this guard."
        )

        for title in uncited:
            occurrences = content_typ.count(title)
            assert occurrences == 0, (
                f"MEM006: {title!r} is never cited by the fixture, so a bare "
                ".. bibliography:: must not render a row for it, but it "
                f"appears {occurrences} time(s) in {CONTENT_TYP}:\n"
                f"{content_typ}"
            )


@pytest.mark.skipif(
    not (BIBTEX_AVAILABLE and TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="sphinxcontrib-bibtex, typst-py and pypdf are all required for the "
    "bibtex citation render gate's compiled-PDF half",
)
class TestBibtexCitationRenderGateCompiledPdf:
    """
    R003 at the compiled-PDF level -- the durable proof.

    Unlike a ``.typ``-exact-content match, counting the entry title in
    extracted PDF text is insensitive to how many times Sphinx resolved the
    doctree and to the translator's internal emission shape: it measures what
    a reader actually sees.
    """

    def test_cited_entry_appears_exactly_once_in_pdf(
        self, bibtex_gate_pdf_build, bibtex_fixture_data
    ):
        """
        R003 (PDF level): in the compiled PDF's extracted text, EACH cited
        entry's title appears exactly once.

        Whitespace is normalised before counting, because Typst line-breaks
        inside the justified entry paragraph otherwise split the title across
        a newline and defeat a naive ``count()``.
        """
        # The master document is what gets compiled; its name comes from the
        # fixture's typst_documents target.
        pdfs = sorted(bibtex_gate_pdf_build.build_dir.glob("*.pdf"))
        assert len(pdfs) == 1, (
            "Expected exactly one compiled PDF for the single-master fixture, "
            f"found {[p.name for p in pdfs]} -- build "
            f"returncode={bibtex_gate_pdf_build.result.returncode}\n"
            f"stderr: {bibtex_gate_pdf_build.result.stderr}"
        )

        text = _pdf_text(pdfs[0])

        for key, raw_title in zip(
            bibtex_fixture_data.cited_keys,
            bibtex_fixture_data.cited_titles,
            strict=True,
        ):
            title = _normalise_whitespace(raw_title)
            occurrences = text.count(title)
            assert occurrences == 1, (
                f"R003: the cited entry title {title!r} (key {key!r}) must "
                f"appear EXACTLY ONCE in the compiled PDF's text, found "
                f"{occurrences}. More than one means the reader sees a doubled "
                "bibliography entry; zero means the entry never reached the "
                f"page.\nExtracted text:\n{text}"
            )

    def test_citing_marker_and_entry_both_reach_the_page(
        self, bibtex_gate_pdf_build, derived_tokens, bibtex_fixture_data
    ):
        """
        R001 + R002 (PDF level): EVERY cited key's citing marker reaches the
        page, and each doctree-derived label appears there at least twice --
        at least once at a citing site and once as its bibliography row's
        label.

        Asserted as ``>= 2`` per label rather than ``== 2`` deliberately, and
        kept that way in S02: the exact label count on the page is not the
        locked behaviour (a running header or a future ToC entry could
        legitimately add one, and S02's multi-key site genuinely adds a third
        occurrence of each label), whereas "the marker rendered AND the row is
        labelled" is.
        """
        pdfs = sorted(bibtex_gate_pdf_build.build_dir.glob("*.pdf"))
        text = _pdf_text(pdfs[0])

        for key in bibtex_fixture_data.cited_keys:
            label = derived_tokens[key].label
            label_occurrences = text.count(label)
            assert label_occurrences >= 2, (
                f"R001/R002: the citation label {label!r} for cited key "
                f"{key!r} should appear at least twice in the compiled PDF "
                "(citing marker + bibliography row label), found "
                f"{label_occurrences}.\nExtracted text:\n{text}"
            )


@pytest.mark.skipif(
    not BIBTEX_AVAILABLE,
    reason="sphinxcontrib-bibtex is required for the bibtex citation render "
    "gate (declared in the dev extra only -- see T01)",
)
class TestResolveCountHazard:
    """
    R014: pin the resolve-count hazard as an executable fact.

    **The hazard.** Resolving the same Sphinx doctree more than once grows a
    bibtex ``citation`` node's child list monotonically. Upstream
    ``sphinxcontrib/bibtex/transforms.py`` appends the rendered label and entry
    body onto nodes it keeps in a cache shared across resolves, so each further
    ``env.get_and_resolve_doctree()`` adds another ``label`` + ``paragraph``
    pair (+2 children per resolve, with the duplicated ``paragraph`` objects
    distinct by identity but carrying identical text). It is builder-
    independent -- nothing in typsphinx causes it and nothing in typsphinx can
    fix it; a test can only AVOID it.

    **Why pin it.** The artifact is easy to mistake for real structure. Both
    this slice's roadmap entry and ``01-01-RESEARCH.md`` initially encoded the
    grown 4-child shape as if it were what the translator receives. Leaving the
    hazard as a prose comment invites the next reader to do the same and write
    ``assert len(node.children) == 4``, which would then "fail" the moment a
    test stopped double-resolving. So the growth is asserted here instead: once
    it is a named, passing test, a future contributor who trips over a strange
    child count is pointed at this module rather than at the translator.

    **Why the assertion is directional.** The write-pass count is MEASURED
    (recorded from inside ``TypstTranslator.visit_citation`` during a real
    build) rather than hard-coded as ``2``, and the comparison is
    ``resolved_again > write_pass`` rather than an equality on ``4``. An
    upstream change to how much is appended per resolve must not turn this pin
    into a false failure -- only the *existence* of the accumulation is the
    locked fact.
    """

    def test_extra_resolve_grows_citation_children(self, resolve_count_observation):
        """
        R014: an extra ``get_and_resolve_doctree()`` on a finished environment
        yields MORE children on the ``citation`` node than the real write pass
        handed to ``visit_citation``.

        This is the whole hazard in one line, and it is why every other test in
        this module reads the FIRST matching descendant out of
        ``bibtex_gate_doctree`` instead of counting children.
        """
        observation = resolve_count_observation

        assert observation.resolved_again_children > observation.write_pass_children, (
            "R014: the resolve-count hazard this module is written around did "
            "NOT reproduce. The write pass saw "
            f"{observation.write_pass_children} children "
            f"{observation.write_pass_child_names!r} and an extra "
            f"get_and_resolve_doctree() yielded "
            f"{observation.resolved_again_children} "
            f"{observation.resolved_again_child_names!r}, so children did not "
            "accumulate. If upstream sphinxcontrib-bibtex stopped appending to "
            "cached shared nodes, that is good news -- delete this test and the "
            "R014 single-resolve rule in this module's docstring together, and "
            "say so in the commit. Do NOT instead relax the assertion: a "
            "silently-weakened pin is how the 4-child artifact got mistaken "
            "for real structure in the first place."
        )

    def test_write_pass_child_names_are_the_unduplicated_shape(
        self, resolve_count_observation
    ):
        """
        R014 (corollary): what the translator ACTUALLY receives is the
        unduplicated shape -- no child name repeats in the write pass, for ANY
        of the citations it visits.

        Asserted over the set of child names rather than over the count, so
        this stays true if a future fixture entry legitimately renders an extra
        kind of child. Generalised in S02 to check EVERY recorded
        ``visit_citation`` call rather than only the first, so a second cited
        entry cannot arrive doubled unnoticed. It is the half of the hazard a
        reader most needs: the translator never sees a doubled citation, so no
        de-dup rule or discrimination predicate belongs in ``visit_citation``.
        """
        per_citation = resolve_count_observation.write_pass_child_names
        assert per_citation, (
            "Vacuous-pass guard: no visit_citation call was recorded, so this "
            "test would assert nothing."
        )

        for position, names in enumerate(per_citation):
            assert len(names) == len(set(names)), (
                "R014: the real write pass handed visit_citation a citation "
                f"node (call #{position + 1} of {len(per_citation)}) with "
                f"REPEATED child kinds {names!r}. That is the double-resolve "
                "artifact leaking into the build itself, not just into a "
                "test's extra resolve -- investigate before adding any de-dup "
                "logic to the translator."
            )


@pytest.mark.skipif(
    not BIBTEX_AVAILABLE,
    reason="sphinxcontrib-bibtex is required for the bibtex citation render "
    "gate (declared in the dev extra only -- see T01)",
)
class TestTextualAndMultiKeyCitingForms:
    """
    R004 + R005 at the emitted-``.typ`` level -- the two citing forms S02
    exists to prove, which the S01 classes above do not distinguish.

    The classes above assert that EVERY cited key leaves a resolved marker
    somewhere outside the grid. That is form-blind: it passes equally for a
    parenthetical, a textual or a multi-key site. This class asserts the thing
    that makes each form itself:

    * **R005, textual (``cite:t``)** -- the author surname text node precedes
      the ``[`` of the bracket group, so the author is named OUTSIDE the
      brackets. That ordering is the ONLY difference from the parenthetical
      form.
    * **R004, multi-key (one ``cite:p`` naming two keys)** -- ONE bracket group
      holds both resolved references, separated by a ``", "`` Text node, in the
      same order the rst role argument names them.

    **House rule, restated because it is what shapes these assertions.** No
    label, anchor or surname is written as a literal: labels and anchors come
    from ``derived_tokens`` (Sphinx's own resolved doctree + the translator's
    own ``_namespace_label``), and the surname is parsed out of the fixture's
    own ``refs.bib`` author field. The docutils-assigned ids measured at
    development time (``index:id3`` / ``index:id4``) are therefore nowhere in
    this file -- they shift freely.

    Every assertion runs against ``_body_outside_grid(...)``, never the grid
    region: the grid repeats both labels in its own row-label cells, so a
    body-form assertion run over the whole file could be satisfied by the
    bibliography instead of by a citing site. (S01's ``_split_at_grid(...)[0]``
    is NOT usable here -- S02's two sites sit AFTER the bibliography, so that
    half of the split contains neither of them. See ``_body_outside_grid``.)
    """

    def test_textual_form_names_author_outside_the_bracket_group(
        self, bibtex_gate_build, derived_tokens, bibtex_fixture_data
    ):
        """
        R005: the textual ``cite:t`` site emits the cited entry's author
        surname immediately BEFORE the opening bracket, with the resolved link
        inside the brackets.

        Measured emission (ids elided -- they are derived, never typed)::

            text("<Surname> [")
            link(<anchor>,
            text("<label>"))
            text("]")

        The surname-before-bracket ordering is asserted as a single contiguous
        pattern rather than as three independent ``in`` checks, because the
        ordering IS the requirement: three separate membership checks would
        pass just as well for a parenthetical marker that happened to have the
        surname somewhere earlier in the paragraph.
        """
        body = _body_outside_grid(bibtex_gate_build.read_content_typ())
        key = bibtex_fixture_data.textual_key
        surname = _author_surname(bibtex_fixture_data.authors[key])
        tokens = derived_tokens[key]

        textual_pattern = re.compile(
            # ... one text node carrying the surname AND the opening bracket,
            # surname first -- this is the whole of R005 ...
            r'text\("' + re.escape(surname) + r'\s*\["\)\s*'
            # ... then the resolved cross-reference INSIDE the brackets ...
            r"link\(<" + re.escape(tokens.anchor) + r">,\s*"
            r'text\("' + re.escape(tokens.label) + r'"\)\)\s*'
            # ... then the closing bracket.
            r'text\("\]"\)',
            re.S,
        )
        matches = textual_pattern.findall(body)
        assert len(matches) == 1, (
            f"R005: expected EXACTLY ONE textual citing marker for cited key "
            f"{key!r} -- the author surname {surname!r} (parsed from refs.bib) "
            f"immediately followed by '[', then a link to {tokens.anchor!r} "
            f"carrying the label {tokens.label!r}, then ']' -- but found "
            f"{len(matches)} in the body outside the grid. Zero means the "
            "textual form did not render the author OUTSIDE the bracket group "
            "(which is what distinguishes it from the parenthetical form); "
            "more than one means a second site can satisfy this assertion "
            f"accidentally.\nPattern: {textual_pattern.pattern}\nBody:\n{body}"
        )

    def test_multi_key_form_emits_one_comma_separated_bracket_group(
        self, bibtex_gate_build, derived_tokens, bibtex_fixture_data
    ):
        """
        R004: the multi-key ``cite:p`` site emits ONE bracket group holding
        both resolved references, separated by a ``", "`` Text node, in the
        rst role argument's order.

        Measured emission (ids elided)::

            text("[")
            link(<anchor_A>,
            text("<label_A>"))
            text(", ")
            link(<anchor_B>,
            text("<label_B>"))
            text("]")

        Asserted as exactly one occurrence, so a future third citing site
        cannot satisfy it accidentally, and as a single contiguous pattern so
        "one group" and "this order" are both real claims: two separate
        per-key link assertions would pass for two SEPARATE bracket groups,
        which is precisely the shape R004 denies.
        """
        body = _body_outside_grid(bibtex_gate_build.read_content_typ())
        keys = bibtex_fixture_data.multi_keys
        assert len(keys) == 2, (
            "This assertion is written against the measured TWO-key form; the "
            f"fixture's multi-key site now names {keys!r}. Extend the pattern "
            "deliberately rather than loosening it."
        )
        first, second = (derived_tokens[key] for key in keys)

        multi_pattern = re.compile(
            r'text\("\["\)\s*'
            r"link\(<" + re.escape(first.anchor) + r">,\s*"
            r'text\("' + re.escape(first.label) + r'"\)\)\s*'
            # The separator is the load-bearing token: ONE group, not two.
            r'text\(", "\)\s*'
            r"link\(<" + re.escape(second.anchor) + r">,\s*"
            r'text\("' + re.escape(second.label) + r'"\)\)\s*'
            r'text\("\]"\)',
            re.S,
        )
        matches = multi_pattern.findall(body)
        assert len(matches) == 1, (
            f"R004: expected EXACTLY ONE bracket group holding both cited keys "
            f"{keys!r} as resolved links separated by a ', ' text node, in "
            f"that rst order ({first.label!r} then {second.label!r}), but "
            f"found {len(matches)} in the body outside the grid. Zero means "
            "either the two references did not share one bracket group, or "
            "the ', ' separator is absent, or the order was not preserved."
            f"\nPattern: {multi_pattern.pattern}\nBody:\n{body}"
        )

    def test_both_new_form_markers_are_resolved_cross_references(
        self, bibtex_gate_build, derived_tokens, bibtex_fixture_data
    ):
        """
        R004 + R005: the link targets the two new sites emit are the ACTUAL
        anchors of the bibliography rows, so the textual site resolves to its
        entry's row and the multi-key site to BOTH rows.

        This reads the body's link targets and the grid's row anchors
        independently out of the emitted file -- the labels and anchors are
        CAPTURED here rather than escaped into the pattern -- and asserts they
        agree, then cross-checks both against ``derived_tokens`` (which reads
        the same tokens out of Sphinx's resolved doctree instead). A marker
        pointing at a plausible-but-wrong anchor would satisfy neither. This
        is the markup S05's cross-file test asserts against.
        """
        content_typ = bibtex_gate_build.read_content_typ()
        body = _body_outside_grid(content_typ)
        _, grid_region = _split_at_grid(content_typ)

        grid_rows = _parse_grid_row_anchors(grid_region)
        assert len(grid_rows) == len(bibtex_fixture_data.cited_keys), (
            "Vacuous-pass guard: expected one parsed grid row per distinct "
            f"cited key ({bibtex_fixture_data.cited_keys!r}), parsed "
            f"{grid_rows!r}. Without the row anchors there is nothing to "
            f"compare the body's link targets against.\nGrid:\n{grid_region}"
        )

        textual_key = bibtex_fixture_data.textual_key
        surname = _author_surname(bibtex_fixture_data.authors[textual_key])
        textual_links = re.findall(
            r'text\("' + re.escape(surname) + r'\s*\["\)\s*'
            r'link\(<([^>]+)>,\s*text\("([^"]+)"\)\)',
            body,
            re.S,
        )
        assert len(textual_links) == 1, (
            f"Vacuous-pass guard: found {len(textual_links)} textual citing "
            f"markers for {textual_key!r} to read a link target out of, "
            f"expected 1.\nBody:\n{body}"
        )
        multi_links = re.findall(
            r'text\("\["\)\s*link\(<([^>]+)>,\s*text\("([^"]+)"\)\)\s*'
            r'text\(", "\)\s*link\(<([^>]+)>,\s*text\("([^"]+)"\)\)',
            body,
            re.S,
        )
        assert len(multi_links) == 1, (
            f"Vacuous-pass guard: found {len(multi_links)} comma-separated "
            "two-link bracket groups to read link targets out of, expected 1."
            f"\nBody:\n{body}"
        )
        multi_anchor_a, multi_label_a, multi_anchor_b, multi_label_b = multi_links[0]

        emitted = [
            (textual_key, textual_links[0][1], textual_links[0][0]),
            (bibtex_fixture_data.multi_keys[0], multi_label_a, multi_anchor_a),
            (bibtex_fixture_data.multi_keys[1], multi_label_b, multi_anchor_b),
        ]
        for key, label, anchor in emitted:
            assert label in grid_rows, (
                f"R004/R005: the citing marker for {key!r} carries the label "
                f"{label!r}, but the bibliography grid has no row labelled "
                f"that (rows: {grid_rows!r}), so the marker does not name any "
                "rendered entry."
            )
            assert grid_rows[label] == anchor, (
                f"R004/R005: the citing marker for {key!r} links to "
                f"{anchor!r}, but the grid row labelled {label!r} is anchored "
                f"at {grid_rows[label]!r}, so the cross-reference does not "
                "resolve to that entry's row."
            )
            assert (label, anchor) == (
                derived_tokens[key].label,
                derived_tokens[key].anchor,
            ), (
                f"R004/R005: the emitted marker for {key!r} carries "
                f"({label!r}, {anchor!r}), but Sphinx's own resolved doctree "
                f"plus TypstTranslator._namespace_label say "
                f"({derived_tokens[key].label!r}, "
                f"{derived_tokens[key].anchor!r}). The emitted file and the "
                "doctree disagree about which entry this marker names."
            )


@pytest.mark.skipif(
    not (BIBTEX_AVAILABLE and TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="sphinxcontrib-bibtex, typst-py and pypdf are all required for the "
    "bibtex citation render gate's compiled-PDF half",
)
class TestTextualAndMultiKeyCitingFormsCompiledPdf:
    """
    R004 + R005 at the compiled-PDF level -- what a reader actually sees.

    Deliberately LOOSER than the ``.typ`` assertions above: pypdf extraction
    breaks lines inside a justified paragraph and gives no reliable token
    ordering within one, so these assert PRESENCE on the page rather than
    position. The emitted-``.typ`` class owns the ordering claims (surname
    before the bracket, ``", "`` between the two links); this class owns the
    claim that the forms survive compilation at all.
    """

    def test_textual_form_author_surname_reaches_the_page(
        self, bibtex_gate_pdf_build, bibtex_fixture_data
    ):
        """
        R005 (PDF level): the author surname the textual form renders inline is
        present in the compiled PDF's extracted text.

        Presence only, per this class's docstring. Note the surname also occurs
        inside that entry's bibliography row ("Taro Tanaka. ..."), so a COUNT
        here would pin the row's formatting rather than the citing form -- the
        ``.typ`` class is where the form itself is asserted.
        """
        pdfs = sorted(bibtex_gate_pdf_build.build_dir.glob("*.pdf"))
        assert len(pdfs) == 1, (
            "Expected exactly one compiled PDF for the single-master fixture, "
            f"found {[path.name for path in pdfs]} -- build "
            f"returncode={bibtex_gate_pdf_build.result.returncode}\n"
            f"stderr: {bibtex_gate_pdf_build.result.stderr}"
        )
        text = _pdf_text(pdfs[0])

        key = bibtex_fixture_data.textual_key
        surname = _normalise_whitespace(
            _author_surname(bibtex_fixture_data.authors[key])
        )
        assert surname in text, (
            f"R005: the textual citing form for {key!r} names the author "
            f"surname {surname!r} inline, but it does not appear in the "
            f"compiled PDF's extracted text at all.\nExtracted text:\n{text}"
        )

    def test_multi_key_form_puts_both_labels_on_the_page(
        self, bibtex_gate_pdf_build, derived_tokens, bibtex_fixture_data
    ):
        """
        R004 (PDF level): both labels the multi-key site cites reach the page.

        Asserted as presence per label, for the same line-breaking reason as
        above. The sibling test in
        ``TestBibtexCitationRenderGateCompiledPdf`` asserts ``>= 2``
        occurrences per label across the whole document (citing marker +
        bibliography row); this one is specifically about the multi-key site's
        own two keys, so it stays a presence check and does not re-pin a count.
        """
        pdfs = sorted(bibtex_gate_pdf_build.build_dir.glob("*.pdf"))
        text = _pdf_text(pdfs[0])

        keys = bibtex_fixture_data.multi_keys
        assert keys, (
            "Vacuous-pass guard: the fixture's multi-key site expanded to no "
            "keys, so this test would assert nothing."
        )
        for key in keys:
            label = derived_tokens[key].label
            assert label in text, (
                f"R004: the multi-key citing site names {key!r}, whose "
                f"citation label is {label!r}, but that label does not appear "
                f"in the compiled PDF's extracted text at all.\n"
                f"Extracted text:\n{text}"
            )
