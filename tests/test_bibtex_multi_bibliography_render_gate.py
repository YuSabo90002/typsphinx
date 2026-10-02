"""
M001 / S04 multi-bibliography render gate: R006, R007, R008, R009, R010.

**Three halves, by build flavour.** The ``.typ``-level assertions (R006-R009)
read a ``-b typst`` build; the compiled-PDF exactly-once assertions (R007-PDF,
the roadmap's own acceptance wording -- "compiles to a PDF with two separate
reference lists holding the correct entries") read a ``-b typstpdf`` build
behind its own dependency skip; and two further classes build MUTATED
THROWAWAY COPIES of the fixture to prove this gate has teeth
(:class:`TestUnfilteredControlProvesTheGateHasTeeth`) and to characterise
``:keyprefix:`` for S05 (:class:`TestKeyprefixIsSourceLevelOnly`). The real
fixture directory is never mutated -- every copy lands in a pytest tmp dir.

**What this module pins.** One document, two chapter sections, each ending in
its own ``:filter:``-scoped ``.. bibliography::``. The emitted content ``.typ``
must carry TWO independent Typst grids, each holding exactly its own chapter's
entry, and each chapter's citing ``link()`` must resolve to a row anchor inside
its OWN chapter's grid -- not the other one's.

**This gate is GREEN on arrival, by design.** Measured at plan time against the
UNTOUCHED translator, ``tests/fixtures/bibtex_multi_bibliography_render_gate``
already renders exactly that shape: two ``grid(`` calls, one row each, correct
per-chapter anchors. A conventional RED-first gate therefore CANNOT go RED here
without first breaking production code, and a RED was deliberately NOT
manufactured. This is a *characterisation* gate, locking current behaviour so
later slices cannot silently regress the two-grid path. The repo precedent for
a deliberately green-on-arrival characterisation gate is
``tests/test_typst_elements_pass_through_gate.py``; the two sibling bibtex
gates (``tests/test_bibtex_citation_render_gate.py``,
``tests/test_bibtex_footcite_render_gate.py``) are the same shape.

Consistent with MEM010/MEM026: the two-grid path needs ZERO
``typsphinx``-side code. ``sphinxcontrib.bibtex`` owns the ``cite`` roles, the
``.. bibliography::`` directive and all ``:filter:`` evaluation, and leaves
ordinary docutils ``citation`` / ``reference`` nodes behind; the translator's
existing generic visitors render each resolved bibliography as its own grid
with no awareness that there are now two of them.

**Why a SEPARATE fixture directory.** The shared fixture's gate pins
``content_typ.count("grid(") == 1`` and both of its region helpers
(``_split_at_grid``, ``_body_outside_grid``) key off THE FIRST ``grid(``
occurrence. Adding a second bibliography there would break those gates and
violate R011 ("existing gates pass unmodified"), so S04 gets its own fixture
directory exactly as the footcite route did (MEM025/MEM030).

**THE PER-REGION COUNTING RULE -- read this before adding an assertion.** With
two bibliographies in one document, every entry-isolation assertion MUST parse
each grid block SEPARATELY and assert over that block alone. A document-wide
count is not allowed for isolation, because it cannot distinguish the passing
shape "one entry in each of two grids" from the failing shape "both entries in
BOTH grids" -- in the unfiltered failure mode each title is measured 2x
document-wide, which a document-wide "appears twice across two grids" count
would happily accept. :func:`_iter_grid_blocks` exists for precisely this: it
returns each balanced ``grid(...)`` call as its own string so row labels can be
attributed to the grid they actually live in. Document-wide counts are used
only for the orthogonal "no doubling / uncited entry absent" claims, where the
per-grid membership has already been established.

**Resolve-at-most-once discipline (R014, MEM009/MEM010).** The module builds
the fixture once per build flavour and makes at most ONE
``get_and_resolve_doctree()`` call, whose only purpose is to READ the
pybtex-generated citation labels and the docutils-assigned citation ids. That
extra resolve duplicates each citation's ``label``/``paragraph`` children, so
nothing here ever counts a citation node's children, and every label is read
from the FIRST matching descendant.

**Locale.** The strict ``-W`` build runs under ``LC_ALL=C``: this machine's
``LANG`` is Japanese and Sphinx localises its build output, so any assertion
touching warning or summary TEXT would be locale-dependent. The assertions
below use the exit status plus the absence of the (never-localised) warning
CODES ``bibtex.key_not_found`` / ``bibtex.duplicate_local_citation``.
"""

import io
import os
import re
import shutil
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

# typst-py and pypdf back the compiled-PDF half ONLY. Imported at module level
# so the names are bound for :func:`_pdf_text`, and gated by the
# ``PDF_DEPS_AVAILABLE`` skipif below plus a belt-and-braces
# ``pytest.importorskip`` inside the build fixture, so a machine lacking either
# SKIPS the compiled-PDF class while the whole .typ half still runs. Both were
# confirmed PRESENT at plan time: a skip in CI therefore means a real
# regression in the environment, not an expected state.
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


# The fixture's single document. A docname (a filename on disk), not a
# generated label/anchor token, so naming it here does not breach the
# derive-don't-transcribe house rule. The fixture deliberately has no second
# source file and no toctree -- the cross-document case belongs to S05.
DOCNAME = "index"

# The CONTENT file the two-layer split writes for DOCNAME. Every assertion in
# this module reads THIS file, never master.typ (which is the fixture's
# typst_documents target).
CONTENT_TYP = f"{DOCNAME}.typ"

# Warning codes sphinxcontrib-bibtex emits when a citing site or a filter does
# not resolve. Codes, not messages: Sphinx localises message text but never the
# bracketed code, so these are safe to assert on under any LANG. The
# key_not_found code is the exact signature of the invalid ``:filter: key ==
# "..."`` form the fixture's conf.py documents -- that form still exits 0, so
# without -W plus these codes the degrade would be invisible (MEM034).
BIBTEX_DEGRADE_CODES = (
    "bibtex.key_not_found",
    "bibtex.duplicate_local_citation",
)


# ---------------------------------------------------------------------------
# Fixture-authored data, parsed from the fixture rather than transcribed.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def multi_bib_gate_dir():
    """Return the path to the bibtex_multi_bibliography_render_gate fixture."""
    return Path(__file__).parent / "fixtures" / "bibtex_multi_bibliography_render_gate"


def _parse_bib_field(bib_text: str, field: str) -> dict[str, str]:
    """
    Return ``{entry_key: value}`` for one quoted ``refs.bib`` field.

    ``%``-comment lines are stripped first: this fixture's ``refs.bib`` carries
    a long header comment block that itself names entry titles, which would
    otherwise be picked up as if they were entries. Same implementation as
    ``tests/test_bibtex_citation_render_gate.py``'s, deliberately duplicated
    rather than imported -- these gate modules are independent characterisation
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


def _parse_bib_titles(bib_text: str) -> dict[str, str]:
    """Return ``{entry_key: title}`` parsed from the fixture's ``refs.bib``."""
    return _parse_bib_field(bib_text, "title")


def _parse_citing_sites(rst_text: str) -> list[str]:
    """
    Return the raw role argument of every ``:cite:*:`` site in ``index.rst``,
    in document order -- one entry per citing SITE.

    Regexes the RAW rst, so a fully-colonised role name written inside an rst
    comment would also count as a site (MEM025's trap). The fixture's own
    comments therefore write role names without their leading colon, and
    ``multi_bib_fixture_data``'s site-count guard is what catches it if that
    ever slips.
    """
    return re.findall(r":cite:[a-z]*:`([^`]+)`", rst_text)


def _parse_bibliography_directives(rst_text: str) -> list[str]:
    """
    Return the ``:filter:`` expression of every ``.. bibliography::`` directive
    in ``index.rst``, in document order.

    Anchored at column 0 with ``re.MULTILINE`` on purpose: rst comments in this
    fixture are indented, so an indented mention of the directive inside a
    comment cannot be miscounted as a real directive.
    """
    return re.findall(
        r"^\.\. bibliography::\n(?:[ \t]+:[^\n]*\n)*?[ \t]+:filter:[ \t]*([^\n]+)",
        rst_text,
        re.M,
    )


def _parse_filter_key(filter_expression: str) -> str:
    """
    Return the single bibtex key a ``:filter:`` expression scopes to.

    Only the measured-working string-on-the-LEFT form is accepted::

        "Smith2020" % key

    The fixture's ``conf.py`` records why: ``key == "Smith2020"`` builds
    "successfully" while degrading every citing site to
    ``bibtex.key_not_found``, and ``cited % "Smith2020"`` is rejected outright.
    Returning ``""`` for anything else makes ``multi_bib_fixture_data``'s guard
    fail loudly with the offending expression instead of silently attributing a
    grid to the wrong chapter.
    """
    match = re.fullmatch(r'\s*"([^"]+)"\s*%\s*key\s*', filter_expression)
    return match.group(1) if match else ""


@dataclass
class MultiBibFixtureData:
    """
    What the fixture itself authors, parsed out of ``refs.bib`` and
    ``index.rst`` -- never transcribed into this module.

    ``chapter_keys`` is the ordered spine of the whole gate: index ``i`` is the
    key cited by chapter ``i + 1`` AND the key its own filtered bibliography
    scopes to, which is what licenses attributing the ``i``-th emitted
    ``grid(`` to the ``i``-th chapter.
    """

    titles: dict[str, str]
    citing_sites: list[str]
    filter_keys: list[str]
    chapter_keys: list[str]

    @property
    def chapter_count(self) -> int:
        """Number of chapters, i.e. the number of grids the gate expects."""
        return len(self.chapter_keys)

    @property
    def cited_titles(self) -> list[str]:
        """Entry titles of the cited keys, in chapter order."""
        return [self.titles[key] for key in self.chapter_keys]

    @property
    def uncited_titles(self) -> list[str]:
        """Entry titles of every ``refs.bib`` key no citing site names."""
        return [
            title for key, title in self.titles.items() if key not in self.chapter_keys
        ]


@pytest.fixture(scope="module")
def multi_bib_fixture_data(multi_bib_gate_dir):
    """
    Parse the fixture into the data the assertions compare against, with
    vacuous-pass guards in the S01 style so a fixture edit that breaks a parse
    fails LOUDLY here rather than quietly degrading every count below into a
    no-op.

    The guards are deliberately exact (``== 2`` sites, ``== 2`` cited keys,
    ``== 1`` uncited key, ``== 2`` directives): this gate's whole subject is a
    two-chapter / two-bibliography document, and a slice that changes that
    shape must update these numbers deliberately.
    """
    bib_text = (multi_bib_gate_dir / "refs.bib").read_text(encoding="utf-8")
    titles = _parse_bib_titles(bib_text)
    rst_text = (multi_bib_gate_dir / f"{DOCNAME}.rst").read_text(encoding="utf-8")
    citing_sites = _parse_citing_sites(rst_text)
    filter_expressions = _parse_bibliography_directives(rst_text)

    assert titles, (
        "Vacuous-pass guard: parsed NO entries out of the fixture's refs.bib, "
        "so every title count below would compare against nothing. Did "
        "refs.bib's entry formatting change?"
    )

    assert len(citing_sites) == 2, (
        "This gate locks a TWO-chapter document with exactly one citing site "
        f"per chapter, but parsed {citing_sites!r} out of {DOCNAME}.rst. "
        "(NOTE: this regexes the RAW rst, so a fully-colonised cite role "
        "written inside an rst comment also counts as a site.)"
    )
    for site in citing_sites:
        assert "," not in site, (
            f"The citing site {site!r} names several keys. This gate's "
            "per-chapter attribution assumes ONE key per chapter, so a "
            "multi-key site would need its own measured expectation -- the "
            "multi-key FORM is owned by S02's gate."
        )

    cited_keys = [site.strip() for site in citing_sites]
    assert len(set(cited_keys)) == 2, (
        "The two chapters must cite two DISTINCT keys, otherwise 'each grid "
        f"holds exactly its OWN entry' is untestable: parsed {cited_keys!r}."
    )

    assert len(filter_expressions) == 2, (
        "R006's subject is TWO :filter:-scoped .. bibliography:: directives, "
        f"but parsed {filter_expressions!r} out of {DOCNAME}.rst. Without two "
        "directives there is no second grid to assert about."
    )
    filter_keys = [_parse_filter_key(expression) for expression in filter_expressions]
    for expression, key in zip(filter_expressions, filter_keys, strict=True):
        assert key, (
            f"The :filter: expression {expression!r} is not the measured-working "
            "string-on-the-LEFT form ('\"Key\" % key'). The other forms either "
            "degrade every citing site to bibtex.key_not_found while still "
            "exiting 0, or are rejected outright -- see the fixture's conf.py."
        )
        assert key in titles, (
            f"The :filter: expression {expression!r} scopes to {key!r}, which "
            f"refs.bib has no entry for (known entries: {sorted(titles)})."
        )

    assert filter_keys == cited_keys, (
        "Each chapter's bibliography must be filtered to the key that same "
        f"chapter cites: citing sites in document order are {cited_keys!r} but "
        f"the :filter: keys in document order are {filter_keys!r}. This gate "
        "attributes the i-th emitted grid to the i-th chapter, so the two "
        "orders must agree or every per-chapter assertion below would be "
        "comparing across chapters."
    )

    for key in cited_keys:
        assert titles[key].strip(), (
            f"The cited entry {key!r} has an empty title in refs.bib, so "
            "counting its occurrences would be meaningless."
        )
    distinct_titles = {titles[key] for key in cited_keys}
    assert len(distinct_titles) == len(cited_keys), (
        "The cited entries must have DISTINCT titles, otherwise an 'appears "
        "exactly once' count for one entry can be satisfied by another: "
        f"{[titles[key] for key in cited_keys]!r}."
    )

    uncited = [key for key in titles if key not in cited_keys]
    assert len(uncited) == 1, (
        "The fixture keeps EXACTLY ONE deliberately uncited refs.bib entry, so "
        "the zero-count assertion has a subject and cannot degrade into a "
        f"no-op (MEM006), but the uncited set is {uncited!r}. If a slice needs "
        "another cited entry, APPEND a new uncited one rather than weakening "
        "this guard."
    )

    return MultiBibFixtureData(
        titles=titles,
        citing_sites=citing_sites,
        filter_keys=filter_keys,
        chapter_keys=cited_keys,
    )


# ---------------------------------------------------------------------------
# Builds. Each runs EXACTLY ONCE per module, in its own build directory so no
# incremental-rebuild cache can let one mask another:
#   * -b typst       -> the .typ-level grid / isolation / anchor assertions
#   * -b typst -W    -> R009's strict half (warnings-as-errors), under LC_ALL=C
#   * -b typstpdf    -> R007-PDF's compiled-PDF half ONLY (typst-py + pypdf)
# The first two use -b typst rather than -b typstpdf, so the whole .typ-level
# half of this module still runs on a machine without typst-py; the typstpdf
# flavour lives behind its own dependency skip so such a machine SKIPS the
# compiled-PDF class rather than erroring it.
#
# Two further build flavours, added by T03, compile MUTATED COPIES of the
# fixture out of a pytest tmp dir (never the fixture directory itself):
#   * unfiltered control -> the non-vacuity / teeth proof
#   * :keyprefix: copy   -> R010's characterisation for S05
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
    subprocess. ``buildername`` defaults to ``typst``; only R007-PDF's
    compiled-PDF fixture passes ``typstpdf``.

    Invoked as ``sys.executable -m sphinx`` -- never ``uv run sphinx-build``
    and never a bare ``sphinx-build`` -- which is the NixOS PATH-shadowing
    hazard every render-gate module in this project restates. Under ``uv run``
    this resolves to the current venv's python, so ``import typsphinx`` binds
    to this checkout's (or worktree's) editable copy rather than another
    tree's.
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
class MultiBibGateBuild:
    """One real build of the multi-bibliography fixture, captured once."""

    result: subprocess.CompletedProcess
    build_dir: Path

    def read_content_typ(self) -> str:
        """
        Return the text of the emitted CONTENT ``.typ`` (never ``master.typ``),
        failing with an ``AssertionError`` that names the missing artifact and
        quotes the build's own output rather than letting a caller hit
        ``FileNotFoundError``.
        """
        path = self.build_dir / CONTENT_TYP
        if not path.exists():
            raise AssertionError(
                f"{CONTENT_TYP} was never emitted (missing artifact) -- build "
                f"returncode={self.result.returncode}\n"
                f"stdout: {self.result.stdout}\nstderr: {self.result.stderr}"
            )
        return path.read_text(encoding="utf-8")

    @property
    def output(self) -> str:
        """The build's combined stdout and stderr."""
        return f"{self.result.stdout}\n{self.result.stderr}"


@pytest.fixture(scope="module")
def multi_bib_gate_build(multi_bib_gate_dir, tmp_path_factory):
    """
    Build the fixture with ``-b typst`` EXACTLY ONCE for the whole module.

    Asserts a clean exit here: this gate is green on arrival, so a non-zero
    build IS the regression it exists to catch, and reporting it once in the
    fixture is clearer than letting it surface as several unrelated assertion
    failures.
    """
    build_dir = tmp_path_factory.mktemp("multi_bib_gate_typ") / "_build"
    result = _run_sphinx_build(multi_bib_gate_dir, build_dir)
    assert result.returncode == 0, (
        "sphinx-build -b typst over the multi-bibliography fixture must "
        "succeed (this gate locks measured-working behaviour and is green on "
        f"arrival)\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    return MultiBibGateBuild(result=result, build_dir=build_dir)


@pytest.fixture(scope="module")
def multi_bib_gate_strict_build(multi_bib_gate_dir, tmp_path_factory):
    """
    Build the fixture with ``-b typst -W`` (warnings-as-errors) EXACTLY ONCE,
    in its OWN build directory, under ``LC_ALL=C``.

    ``LC_ALL=C`` because this project's dev shell passes the host's ``LANG``
    through and Sphinx localises its output: R009 inspects the build's text for
    bibtex degrade CODES, and only the C locale makes that text stable. The
    codes themselves are never localised, but the surrounding "WARNING"/summary
    wording is, so forcing the locale keeps a future text-level assertion
    honest too.

    Deliberately does NOT assert the exit code -- R009's own test owns that, so
    a regression is reported as a named test failure rather than as a fixture
    error.
    """
    build_dir = tmp_path_factory.mktemp("multi_bib_gate_typ_strict") / "_build"
    env = dict(os.environ)
    env["LC_ALL"] = "C"
    env.pop("LANG", None)
    env.pop("LANGUAGE", None)
    result = _run_sphinx_build(
        multi_bib_gate_dir, build_dir, extra_args=("-W",), env=env
    )
    return MultiBibGateBuild(result=result, build_dir=build_dir)


@pytest.fixture(scope="module")
def multi_bib_gate_doctree(multi_bib_gate_dir, tmp_path_factory):
    """
    Build the fixture through a real in-process ``SphinxTestApp`` (``-b
    typst``) and return the RESOLVED doctree, so the pybtex-generated citation
    labels and the citations' docutils-assigned ids can be READ rather than
    guessed (house rule).

    This is the module's ONE AND ONLY ``get_and_resolve_doctree`` call (R014).
    The resolve is measured to duplicate each ``citation`` node's children, so
    callers read the FIRST matching descendant and must never assert a child
    count from this doctree.
    """
    from sphinx.testing.util import SphinxTestApp

    builddir = tmp_path_factory.mktemp("multi_bib_gate_doctree")
    app = SphinxTestApp(
        buildername="typst",
        srcdir=multi_bib_gate_dir.resolve(),
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

    The FIRST, deliberately not a join: the module's one extra
    ``get_and_resolve_doctree()`` duplicates each ``label``/``paragraph`` pair
    (R014), and the duplicates carry identical text, so the first one already
    is the whole entry body.
    """
    paragraphs = list(citation.findall(docutils_nodes.paragraph))
    return paragraphs[0].astext() if paragraphs else ""


@dataclass
class DerivedCitationTokens:
    """Tokens read out of Sphinx's own resolved doctree, and the anchor
    computed by the translator's own helper -- never transcribed."""

    label: str
    anchor: str


@pytest.fixture(scope="module")
def derived_tokens(multi_bib_gate_doctree, multi_bib_fixture_data):
    """
    Return ``{cited_key: DerivedCitationTokens}``: for each key a chapter
    cites, the citation label read out of the resolved doctree and the Typst
    anchor its citing marker must link to, computed by calling the translator's
    own ``_namespace_label``.

    **Mapping a citation node back to its bibtex key.** A resolved ``citation``
    node carries no bibtex key, so the link is made through the entry TITLE --
    fixture-authored prose parsed out of ``refs.bib``, which that file's header
    comment deliberately keeps distinct per entry. The guards below fail loudly
    if any cited key finds no node or if two keys claim the same one.

    With two filtered bibliographies the doctree holds one ``citation`` node
    per chapter, so the node count is asserted against the chapter count --
    that count is over citation NODES, never over their (resolve-duplicated)
    children.

    Passing the class itself as ``self`` to ``_namespace_label`` is safe: it
    only calls ``self._sanitize_label(...)``, a ``staticmethod`` resolvable
    through the class object with no instance state (the technique
    ``tests/test_citation_render_gate.py`` documents).
    """
    citations = list(multi_bib_gate_doctree.findall(docutils_nodes.citation))
    expected = multi_bib_fixture_data.chapter_count
    assert len(citations) == expected, (
        "Expected exactly one resolved citation node per chapter "
        f"({expected}, for {multi_bib_fixture_data.chapter_keys!r}), found "
        f"{len(citations)}. Each chapter's bibliography is filtered to the one "
        "key that chapter cites, so these numbers must agree. (This counts "
        "CITATION nodes, not their children -- the children are duplicated by "
        "this extra resolve and are never counted.)"
    )

    tokens: dict[str, DerivedCitationTokens] = {}
    claimed_by: dict[int, str] = {}
    for key in multi_bib_fixture_data.chapter_keys:
        title = multi_bib_fixture_data.titles[key]
        matching = [
            citation
            for citation in citations
            if title in _first_paragraph_text(citation)
        ]
        assert len(matching) == 1, (
            "Expected exactly one resolved citation node whose rendered entry "
            f"body contains the title {title!r} of cited key {key!r}, found "
            f"{len(matching)}. Without a 1:1 key->node mapping the per-chapter "
            "label and anchor below would describe the wrong entry."
        )
        citation = matching[0]
        assert id(citation) not in claimed_by, (
            f"Cited keys {claimed_by[id(citation)]!r} and {key!r} both mapped "
            "to the SAME resolved citation node, so their titles are not "
            "distinguishable. Give refs.bib entries distinct titles."
        )
        claimed_by[id(citation)] = key

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
        "a per-chapter markup assertion can be satisfied by the wrong "
        f"chapter's marker: {sorted(token.label for token in tokens.values())!r}."
    )
    distinct_anchors = {token.anchor for token in tokens.values()}
    assert len(distinct_anchors) == len(tokens), (
        "The cited entries must resolve to DISTINCT anchors, otherwise R008's "
        "'each chapter's link lands in its OWN grid' claim is untestable: "
        f"{sorted(token.anchor for token in tokens.values())!r}."
    )
    return tokens


# ---------------------------------------------------------------------------
# Emitted-markup helpers.
#
# The key new helper for S04 is the grid-SPAN scanner: with two grids in one
# file, neither the shared module's `_split_at_grid` (first grid only) nor its
# `_body_outside_grid` (excises one grid) can express "each grid separately".
# ---------------------------------------------------------------------------


def _grid_block_spans(typ_text: str) -> list[tuple[int, int]]:
    """
    Return ``[(start, end), ...]`` for every balanced ``grid(...)`` call in
    ``typ_text``, in document order -- ``start`` at the ``g`` of ``grid(``,
    ``end`` one past its matching ``)``.

    Parenthesis balancing SKIPS OVER Typst string literals (and their ``\\``
    escapes), so a ``(`` or ``)`` inside ``text("...")`` cannot throw the depth
    off -- the same literal-skipping walk ``_body_outside_grid`` performs in
    ``tests/test_bibtex_citation_render_gate.py``, generalised here from "the
    first grid" to "every grid". Nested grids are handled by the depth counter
    and would be reported as one outer span, which is the right reading: a
    bibliography's grid is the outermost call.

    An unbalanced call raises a clear ``AssertionError`` rather than returning a
    truncated span, because a silently short span would scope a per-grid
    assertion to the wrong region.
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

    This is the helper the per-REGION counting rule in the module docstring
    mandates: entry-isolation assertions parse one of these blocks at a time,
    so "grid 1 holds only chapter 1's entry" is expressible at all. A
    document-wide count over ``index.typ`` cannot make that distinction.
    """
    return [typ_text[start:end] for start, end in _grid_block_spans(typ_text)]


def _body_outside_grids(typ_text: str) -> str:
    """
    Return ``typ_text`` with EVERY ``grid(...)`` call excised -- i.e. every
    region of the document that is not a bibliography.

    This is where a chapter's citing marker must be found: the grids' own label
    cells repeat the same label tokens, so an assertion run over the whole file
    could be satisfied by a bibliography row instead of by a real citing site.
    The shared module's ``_body_outside_grid`` excises only ONE grid and is
    therefore unusable here (its own vacuous-pass guard, "no 'columns:' left in
    the body", would fail with a second grid still present).

    Excision runs back-to-front so earlier spans' offsets stay valid.
    """
    spans = _grid_block_spans(typ_text)
    assert spans, (
        "No grid( call was emitted at all, so no bibliography rendered as a "
        f"Typst grid:\n{typ_text}"
    )
    body = typ_text
    for start, end in reversed(spans):
        body = body[:start] + body[end:]

    # Vacuous-pass guards: prove the excision bounded the grids rather than
    # swallowing the document (which would make every body assertion a no-op)
    # or stopping short of the grids' own label cells.
    assert "columns: (auto, 1fr)" not in body, (
        "Vacuous-pass guard: a grid's 'columns: (auto, 1fr)' declaration is "
        "still present after excision, so at least one grid region was not "
        f"removed from the body:\n{body}"
    )
    assert body.strip(), (
        "Vacuous-pass guard: excising the grids left NO body text, so every "
        f"assertion over the body region would pass vacuously:\n{typ_text}"
    )
    return body


def _parse_grid_row_anchors(grid_region: str) -> dict[str, str]:
    """
    Return ``{row_label: row_anchor}`` parsed out of ONE grid block.

    Measured shape of one row's label cell::

        [#{text("[") + text("Smi20") + text("]")} <index:id3>]

    i.e. the bracketed label built by string concatenation, followed by the
    Typst label the row is anchored at. Parsed rather than derived, so R008
    compares the body's OWN link targets against the grid's OWN anchors -- two
    independent readings of the emitted file. Both are additionally
    cross-checked against ``derived_tokens``, which reads the same tokens out
    of Sphinx's resolved doctree instead.

    Same regex as ``tests/test_bibtex_citation_render_gate.py``'s helper, but
    applied to a SINGLE grid block rather than to "everything from the first
    ``grid(`` onwards" -- which is the whole point of the per-region rule.
    """
    rows = re.findall(
        r'text\("\["\)\s*\+\s*text\("([^"]+)"\)\s*\+\s*text\("\]"\)\}\s*<([^>]+)>',
        grid_region,
    )
    return dict(rows)


@pytest.fixture(scope="module")
def grid_blocks(multi_bib_gate_build, multi_bib_fixture_data):
    """
    Return the emitted content ``.typ``'s grid blocks, one per chapter, in
    document order -- with the count guard applied once so every test below can
    index into the list without restating it.
    """
    content_typ = multi_bib_gate_build.read_content_typ()
    blocks = _iter_grid_blocks(content_typ)
    expected = multi_bib_fixture_data.chapter_count
    assert len(blocks) == expected, (
        f"R006: the fixture's {expected} :filter:-scoped .. bibliography:: "
        f"directives must emit {expected} independent Typst grids, but "
        f"{len(blocks)} balanced grid( call(s) were found in {CONTENT_TYP}. "
        f"Raw 'grid(' occurrences: {content_typ.count('grid(')}.\n"
        f"{content_typ}"
    )
    return blocks


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not BIBTEX_AVAILABLE,
    reason="sphinxcontrib-bibtex is required to resolve the :cite:p: sites and "
    "the :filter:-scoped .. bibliography:: directives of the "
    "multi-bibliography gate (declared in the dev extra only)",
)
class TestTwoIndependentGrids:
    """R006: two bibliography directives render as two independent grids."""

    def test_two_balanced_grid_calls_are_emitted(
        self, grid_blocks, multi_bib_gate_build, multi_bib_fixture_data
    ):
        """
        R006: ``index.typ`` carries exactly one balanced ``grid(`` call per
        chapter bibliography, and the raw ``grid(`` occurrence count agrees.

        Both counts are asserted because they fail differently: a mismatch
        between them would mean a ``grid(`` appeared somewhere the balancing
        walk did not treat as a block start (e.g. inside a string literal),
        which would silently change what the per-grid assertions are scoped to.
        """
        content_typ = multi_bib_gate_build.read_content_typ()
        expected = multi_bib_fixture_data.chapter_count

        assert len(grid_blocks) == expected
        assert content_typ.count("grid(") == expected, (
            f"R006: expected exactly {expected} raw 'grid(' occurrences in "
            f"{CONTENT_TYP} (one per chapter bibliography), found "
            f"{content_typ.count('grid(')}. The balanced-span scan found "
            f"{len(grid_blocks)}, so the two readings disagree:\n{content_typ}"
        )

    def test_each_grid_declares_the_two_column_shape(self, grid_blocks):
        """
        R006: EACH emitted grid independently declares the two-column
        ``columns: (auto, 1fr)`` shape (auto-width label cell + flexible
        entry-body cell).

        Asserted per grid, not once over the file: a document-wide ``in`` check
        would pass while the second bibliography rendered as something else
        entirely.
        """
        for position, block in enumerate(grid_blocks, start=1):
            assert "columns: (auto, 1fr)" in block, (
                f"R006: grid {position} of {len(grid_blocks)} does not declare "
                "the two-column 'columns: (auto, 1fr)' shape, so that "
                "bibliography did not render as the measured label-cell + "
                f"entry-body grid:\n{block}"
            )


@pytest.mark.skipif(
    not BIBTEX_AVAILABLE,
    reason="sphinxcontrib-bibtex is required for the multi-bibliography gate",
)
class TestPerGridEntryIsolation:
    """
    R007: each grid holds exactly its OWN chapter's entry -- nothing leaked
    from the other chapter, and nothing doubled.

    Every membership assertion here is PER GRID (module docstring's per-region
    rule). The document-wide counts at the end are the orthogonal
    no-doubling / uncited-entry claims, which only become meaningful once
    membership has been established per grid.
    """

    def test_each_grid_holds_exactly_one_row_and_it_is_its_own_chapters(
        self, grid_blocks, derived_tokens, multi_bib_fixture_data
    ):
        """
        R007: grid ``i``'s parsed row labels are EXACTLY ``{chapter i's
        label}`` -- one row, and that row is its own chapter's entry.

        The expected label is the one read out of Sphinx's resolved doctree for
        the key that chapter cites, never a string literal. A leaked entry
        shows up here as a second row or as the wrong label, which is exactly
        the unfiltered failure mode this slice exists to rule out.
        """
        for position, (block, key) in enumerate(
            zip(grid_blocks, multi_bib_fixture_data.chapter_keys, strict=True), start=1
        ):
            rows = _parse_grid_row_anchors(block)
            expected_label = derived_tokens[key].label

            assert set(rows) == {expected_label}, (
                f"R007: grid {position} must hold exactly ONE row, the one for "
                f"its own chapter's cited key {key!r} (label "
                f"{expected_label!r}), but its parsed row labels are "
                f"{sorted(rows)!r}. More than one label means the "
                f":filter: did not isolate this chapter's bibliography; a "
                "different label means the grids are attributed to the wrong "
                f"chapters.\n{block}"
            )
            assert len(rows) == 1, (
                f"R007: grid {position} parsed {len(rows)} distinct row "
                f"label(s) ({sorted(rows)!r}); exactly one is required."
            )

    def test_no_chapters_title_appears_in_the_other_chapters_grid(
        self, grid_blocks, multi_bib_fixture_data
    ):
        """
        R007, stated over entry TITLES rather than labels: chapter ``i``'s
        entry title appears in grid ``i`` and in NO other grid.

        A second, independent reading of the isolation claim -- the row-label
        test above reads the grid's generated label tokens, this one reads the
        rendered entry body text parsed from the fixture's own ``refs.bib``. In
        the unfiltered failure mode each title is present in BOTH grids, which
        this detects even if the label parse were to drift.
        """
        chapter_keys = multi_bib_fixture_data.chapter_keys
        for own_position, own_key in enumerate(chapter_keys, start=1):
            title = multi_bib_fixture_data.titles[own_key]
            for position, block in enumerate(grid_blocks, start=1):
                occurrences = block.count(title)
                if position == own_position:
                    assert occurrences == 1, (
                        f"R007: the title {title!r} of chapter {own_position}'s "
                        f"cited key {own_key!r} must appear EXACTLY ONCE in "
                        f"chapter {own_position}'s own grid, found "
                        f"{occurrences}:\n{block}"
                    )
                else:
                    assert occurrences == 0, (
                        f"R007: the title {title!r} belongs to chapter "
                        f"{own_position}, so it must NOT appear in grid "
                        f"{position} -- but it occurs {occurrences} time(s) "
                        "there. The :filter: expressions are not isolating the "
                        f"two bibliographies.\n{block}"
                    )

    def test_each_cited_title_appears_exactly_once_document_wide(
        self, multi_bib_gate_build, multi_bib_fixture_data
    ):
        """
        R007 (no-doubling corollary): each cited entry's title appears exactly
        ONCE in the whole ``index.typ``.

        This is deliberately a document-wide count, and it is sound only
        BECAUSE the per-grid membership above already holds: together they say
        "entry in its own grid, once, and nowhere else in the file". On its own
        a document-wide count could not distinguish one-per-grid from
        both-in-both (per-region rule), which is why it never stands alone
        here.

        Counts the TITLE, not the label token: a label legitimately appears
        twice (once at the citing site, once in its grid's label cell).
        """
        content_typ = multi_bib_gate_build.read_content_typ()
        for key, title in zip(
            multi_bib_fixture_data.chapter_keys,
            multi_bib_fixture_data.cited_titles,
            strict=True,
        ):
            occurrences = content_typ.count(title)
            assert occurrences == 1, (
                f"R007: the cited entry title {title!r} (key {key!r}) must "
                f"appear EXACTLY ONCE in {CONTENT_TYP}, found {occurrences}. "
                "More than one means the entry was rendered by both "
                "bibliographies (or doubled within one); zero means it never "
                f"rendered:\n{content_typ}"
            )

    def test_uncited_entry_renders_no_row_in_either_grid(
        self, multi_bib_gate_build, multi_bib_fixture_data
    ):
        """
        R007 / MEM006: a ``refs.bib`` entry no chapter cites -- and no
        ``:filter:`` names -- contributes no row to EITHER grid, so its title
        does not appear in ``index.typ`` at all.

        This pins the semantics that make the exactly-once counts above
        meaningful: they are over CITED keys only. ``multi_bib_fixture_data``
        refuses to run if the fixture ever stops keeping exactly one uncited
        entry, so this cannot silently become a no-op.
        """
        content_typ = multi_bib_gate_build.read_content_typ()
        for title in multi_bib_fixture_data.uncited_titles:
            occurrences = content_typ.count(title)
            assert occurrences == 0, (
                f"MEM006: {title!r} is cited by no chapter and named by no "
                ":filter:, so neither bibliography must render a row for it, "
                f"but it appears {occurrences} time(s) in {CONTENT_TYP}:\n"
                f"{content_typ}"
            )


@pytest.mark.skipif(
    not BIBTEX_AVAILABLE,
    reason="sphinxcontrib-bibtex is required for the multi-bibliography gate",
)
class TestPerChapterAnchorResolution:
    """
    R008: each chapter's citing link resolves to a row anchor inside THAT
    chapter's own grid.

    This is the assertion that a document-wide check genuinely cannot make. Two
    correct-looking grids whose anchors were crossed over would satisfy R006
    and R007 while sending every reader of chapter one to chapter two's
    reference list.
    """

    def test_each_chapters_link_targets_its_own_grids_row_anchor(
        self, grid_blocks, multi_bib_gate_build, derived_tokens, multi_bib_fixture_data
    ):
        """
        R008: for each chapter, the body's citing
        ``link(<anchor>, text("<label>"))`` names the anchor that the row
        inside THAT chapter's grid is anchored at.

        Three independent readings must agree per chapter: the body's link
        target, the grid row's own ``<...>`` anchor (parsed from the emitted
        file), and the anchor computed by calling the translator's own
        ``TypstTranslator._namespace_label`` on the citation id read out of
        Sphinx's resolved doctree. No anchor is written as a string literal
        anywhere in this module.

        The body region is "``index.typ`` minus EVERY grid block"
        (:func:`_body_outside_grids`) -- the shared module's ``_split_at_grid``
        is unusable here because it assumes a single grid and would treat
        chapter two's whole section as part of the bibliography region.
        """
        content_typ = multi_bib_gate_build.read_content_typ()
        body = _body_outside_grids(content_typ)

        for position, (block, key) in enumerate(
            zip(grid_blocks, multi_bib_fixture_data.chapter_keys, strict=True), start=1
        ):
            tokens = derived_tokens[key]
            rows = _parse_grid_row_anchors(block)

            assert tokens.label in rows, (
                f"R008: grid {position} carries no row for chapter "
                f"{position}'s cited key {key!r} (label {tokens.label!r}); "
                f"parsed rows {rows!r}. Without that row there is no "
                f"in-chapter anchor for the citing link to target.\n{block}"
            )
            row_anchor = rows[tokens.label]
            assert row_anchor == tokens.anchor, (
                f"R008: chapter {position}'s grid row for {key!r} is anchored "
                f"at {row_anchor!r}, but the translator's own "
                "_namespace_label applied to the citation id read from "
                f"Sphinx's resolved doctree yields {tokens.anchor!r}. The two "
                "readings of the SAME anchor must agree, or the rest of this "
                "test is comparing against a guess."
            )

            link_pattern = re.compile(
                r"link\(<" + re.escape(row_anchor) + r">,\s*"
                r'text\("' + re.escape(tokens.label) + r'"\)',
                re.S,
            )
            assert link_pattern.search(body), (
                f"R008: chapter {position} cites {key!r}, so the body (every "
                "region of index.typ outside the grids) must carry "
                f'link(<{row_anchor}>, text("{tokens.label}")) -- a link to '
                f"the row anchor inside chapter {position}'s OWN grid. No such "
                f"link( call was found:\n{body}"
            )

    def test_no_chapters_link_targets_another_chapters_grid_anchor(
        self, grid_blocks, multi_bib_gate_build, derived_tokens, multi_bib_fixture_data
    ):
        """
        R008, stated negatively: chapter ``i``'s label is never linked to
        another chapter's grid anchor.

        The positive test above would still pass if a chapter emitted TWO
        citing links, one correct and one crossed over. Pairing each label with
        every FOREIGN anchor and requiring zero matches closes that hole, and
        is only expressible because the anchors were attributed to grids
        per-region in the first place.
        """
        body = _body_outside_grids(multi_bib_gate_build.read_content_typ())
        anchors_by_position = {
            position: _parse_grid_row_anchors(block)
            for position, block in enumerate(grid_blocks, start=1)
        }

        for own_position, own_key in enumerate(
            multi_bib_fixture_data.chapter_keys, start=1
        ):
            label = derived_tokens[own_key].label
            for position, rows in anchors_by_position.items():
                if position == own_position:
                    continue
                for foreign_anchor in rows.values():
                    crossed = re.compile(
                        r"link\(<" + re.escape(foreign_anchor) + r">,\s*"
                        r'text\("' + re.escape(label) + r'"\)',
                        re.S,
                    )
                    assert not crossed.search(body), (
                        f"R008: chapter {own_position}'s citing marker "
                        f"{label!r} is linked to {foreign_anchor!r}, an anchor "
                        f"belonging to grid {position}. A citing link must "
                        "target a row in its own chapter's reference list.\n"
                        f"{body}"
                    )


@pytest.mark.skipif(
    not BIBTEX_AVAILABLE,
    reason="sphinxcontrib-bibtex is required for the multi-bibliography gate",
)
class TestStrictBuildIsClean:
    """
    R009: a strict (``-W``, warnings-as-errors) build of the fixture exits 0
    with zero warnings.

    Why this matters more here than elsewhere in the milestone: the invalid
    ``:filter: key == "..."`` form still exits 0 on a non-strict build while
    degrading every citing site to ``bibtex.key_not_found`` (MEM034). Without
    ``-W``, a fixture edit to that form would leave R006-R008 asserting over a
    document whose citations silently stopped resolving. ``-W`` is what turns
    that degrade into a visible failure.
    """

    def test_strict_build_exits_zero(self, multi_bib_gate_strict_build):
        """
        ``sphinx-build -b typst -W`` over the fixture exits 0.

        Under ``-W`` every warning becomes an error, so exit 0 IS the
        zero-warning evidence -- and unlike grepping for the word "WARNING" it
        holds under a non-English ``LANG`` (the build runs under ``LC_ALL=C``
        anyway, belt and braces).
        """
        result = multi_bib_gate_strict_build.result
        assert result.returncode == 0, (
            "R009: a strict (-W) build of the multi-bibliography fixture must "
            f"succeed, but exited {result.returncode}. Under -W this means the "
            "build emitted at least one warning -- e.g. a :filter: expression "
            "that no longer resolves, or a citing site that lost its "
            f"target.\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_strict_build_reports_no_bibtex_degrade_codes(
        self, multi_bib_gate_strict_build
    ):
        """
        R009: the strict build's output names none of the bibtex degrade
        warning CODES.

        Asserted on CODES rather than on message text because Sphinx localises
        the message but never the bracketed code, so this check is
        locale-independent by construction. It is also strictly more
        informative than the exit code alone: if a future Sphinx or
        ``sphinxcontrib-bibtex`` stopped promoting one of these under ``-W``,
        exit 0 would hide it and this test would not.
        """
        output = multi_bib_gate_strict_build.output
        for code in BIBTEX_DEGRADE_CODES:
            assert code not in output, (
                f"R009: the strict build reported the {code!r} warning code, "
                "which means sphinxcontrib-bibtex could not resolve a citing "
                "site or a :filter: expression. Check that both :filter: "
                'expressions still use the string-on-the-LEFT form ("Key" % '
                "key) -- the comparison form degrades exactly this way while "
                f"still exiting 0 on a non-strict build.\n{output}"
            )


# ---------------------------------------------------------------------------
# (a) The compiled-PDF half (R007-PDF).
#
# The roadmap states S04's acceptance on the COMPILED PDF, not on the emitted
# .typ: "compiles to a PDF with two separate reference lists holding the
# correct entries". These assertions are the PDF-level restatement of the
# per-grid isolation already pinned above in .typ text.
#
# Keyed by BUILDERNAME in its own build directory (the S01 pattern) rather than
# by switching the whole module to -b typstpdf, so every .typ assertion above
# still runs when typst-py / pypdf are absent.
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
    cannot disagree about whitespace.
    """
    return re.sub(r"\s+", " ", text)


def _pdf_text(pdf_path: Path) -> str:
    """Return whitespace-normalised text extracted from every page, joined."""
    reader = pypdf.PdfReader(io.BytesIO(pdf_path.read_bytes()))
    return _normalise_whitespace(" ".join(page.extract_text() for page in reader.pages))


@pytest.fixture(scope="module")
def multi_bib_gate_pdf_build(multi_bib_gate_dir, tmp_path_factory):
    """
    Compile the fixture through ``-b typstpdf`` EXACTLY ONCE for the whole
    module, for the compiled-PDF half only.

    ``pytest.importorskip`` rather than a bare import: a missing ``typst-py``
    or ``pypdf`` must SKIP this half, not ERROR it, and a fixture-level skip
    covers the case where the class-level ``skipif`` is ever loosened.

    Declared at module level rather than inside the PDF class: a class-scoped
    fixture defined in a class body and depending on these broader-scoped
    fixtures trips pytest's own ``assert not self._finalizers`` internal check
    (the sibling gates record the same hazard).
    """
    pytest.importorskip("typst", reason="typst-py backs the typstpdf builder")
    pytest.importorskip("pypdf", reason="pypdf extracts the compiled PDF's text")

    build_dir = tmp_path_factory.mktemp("multi_bib_gate_pdf") / "_build"
    result = _run_sphinx_build(multi_bib_gate_dir, build_dir, buildername="typstpdf")
    assert result.returncode == 0, (
        "sphinx-build -b typstpdf over the multi-bibliography fixture must "
        "succeed (this gate locks measured-working behaviour and is green on "
        f"arrival)\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    return MultiBibGateBuild(result=result, build_dir=build_dir)


@pytest.fixture(scope="module")
def multi_bib_gate_pdf_text(multi_bib_gate_pdf_build):
    """
    Return the whitespace-normalised text of the fixture's single compiled PDF,
    extracting it ONCE for the whole class.

    The PDF is located by glob rather than by filename: the fixture's
    ``typst_documents`` target owns that name, and asserting there is EXACTLY
    one compiled PDF is itself worth checking -- the fixture declares a single
    master, so a second PDF would mean the two-layer split or the master
    registry changed shape under this gate. The non-empty guard then rules out
    the silent degrade where extraction yields nothing and every count below
    would read 0 for the wrong reason.
    """
    pdfs = sorted(multi_bib_gate_pdf_build.build_dir.glob("*.pdf"))
    assert len(pdfs) == 1, (
        "Expected exactly one compiled PDF for this single-master fixture, "
        f"found {[pdf.name for pdf in pdfs]} -- build "
        f"returncode={multi_bib_gate_pdf_build.result.returncode}\n"
        f"stderr: {multi_bib_gate_pdf_build.result.stderr}"
    )
    text = _pdf_text(pdfs[0])
    assert text.strip(), (
        "Vacuous-pass guard: pypdf extracted NO text from the compiled PDF, so "
        "every count below would read 0 regardless of what the document "
        f"actually contains ({pdfs[0]})."
    )
    return text


@pytest.mark.skipif(
    not PDF_DEPS_AVAILABLE,
    reason="sphinxcontrib-bibtex, typst-py and pypdf are all required for the "
    "multi-bibliography gate's compiled-PDF half",
)
class TestCompiledPdfHoldsEachEntryExactlyOnce:
    """
    R007-PDF: the roadmap's acceptance, measured on the compiled ``master.pdf``
    -- two separate reference lists holding the correct entries.

    Every assertion counts the entry TITLE, never a label token: labels appear
    twice by design (the citing marker plus the bibliography row), and short
    label tokens are the kind of string that collides with page numbers in
    extracted text. A title is fixture-authored prose, parsed out of
    ``refs.bib``, and this fixture's ``refs.bib`` header deliberately keeps the
    three titles pairwise distinct so one entry's count can never be satisfied
    by another.

    Why "exactly once" is the right PDF-level restatement of per-grid
    isolation: with each bibliography filtered to one key, the document holds
    two reference lists of one row each, so each cited title is rendered once
    in total. Under the measured isolation FAILURE mode (both filters removed)
    each title is rendered in BOTH lists and this count reads 2 --
    :class:`TestUnfilteredControlProvesTheGateHasTeeth` measures exactly that,
    which is what makes this assertion non-vacuous.
    """

    def test_each_cited_entry_title_appears_exactly_once(
        self, multi_bib_gate_pdf_text, multi_bib_fixture_data
    ):
        """
        R007-PDF: each cited entry's title occurs exactly once in the compiled
        PDF's extracted text.
        """
        for key, raw_title in zip(
            multi_bib_fixture_data.chapter_keys,
            multi_bib_fixture_data.cited_titles,
            strict=True,
        ):
            title = _normalise_whitespace(raw_title)
            count = multi_bib_gate_pdf_text.count(title)
            assert count == 1, (
                f"R007-PDF: cited entry {key!r}'s title {title!r} appears "
                f"{count} time(s) in the compiled PDF, expected exactly 1. "
                "A count of 2 is the measured signature of lost :filter: "
                "isolation (every entry rendered into BOTH reference lists); "
                "a count of 0 usually means the title's whitespace was not "
                "normalised on both sides of the comparison.\n"
                f"Extracted text: {multi_bib_gate_pdf_text}"
            )

    def test_uncited_entry_title_is_absent(
        self, multi_bib_gate_pdf_text, multi_bib_fixture_data
    ):
        """
        R007-PDF, negative half: the deliberately uncited ``refs.bib`` entry
        reaches NEITHER reference list in the compiled PDF.

        Per MEM006 a bibliography renders only cited entries, so this is the
        PDF-level statement that neither ``:filter:`` widened to the whole
        ``.bib`` file. The fixture guarantees exactly one such entry exists
        (``multi_bib_fixture_data``'s guard), so this cannot pass vacuously by
        iterating an empty list.
        """
        for raw_title in multi_bib_fixture_data.uncited_titles:
            title = _normalise_whitespace(raw_title)
            count = multi_bib_gate_pdf_text.count(title)
            assert count == 0, (
                f"R007-PDF: the uncited entry title {title!r} appears {count} "
                "time(s) in the compiled PDF. No citing site names that key "
                "and no :filter: expression selects it, so a non-zero count "
                "means a bibliography rendered the whole .bib file rather than "
                "its filtered selection.\n"
                f"Extracted text: {multi_bib_gate_pdf_text}"
            )


# ---------------------------------------------------------------------------
# (b) Non-vacuity / teeth proof.
#
# This gate is green on arrival, so without this section a reader cannot tell
# whether the per-grid assertions above have any discriminating power at all.
# The two classes below build MUTATED THROWAWAY COPIES of the fixture and
# measure that the broken shape really is distinguishable. The real fixture
# directory is NEVER written to -- `_copy_fixture` copies out to a pytest tmp
# dir, and the task's own verification re-asserts
# `git diff --quiet -- tests/fixtures/bibtex_multi_bibliography_render_gate/`.
# ---------------------------------------------------------------------------


def _copy_fixture(fixture_dir: Path, destination: Path) -> Path:
    """
    Copy the whole fixture directory to ``destination`` and return it.

    A COPY, never an edit in place: the mutation-based tests below deliberately
    break the fixture's filters, and doing that to
    ``tests/fixtures/bibtex_multi_bibliography_render_gate/`` would silently
    break every other test in this module (and leave the working tree dirty).
    """
    shutil.copytree(fixture_dir, destination)
    return destination


@dataclass
class MutatedFixtureBuilds:
    """
    Builds of one mutated throwaway copy: the plain build whose emitted
    ``.typ`` is inspected, plus the strict (``-W``) build whose exit status and
    warning codes are inspected.
    """

    source_dir: Path
    plain: MultiBibGateBuild
    strict: subprocess.CompletedProcess

    @property
    def strict_output(self) -> str:
        """The strict build's combined stdout and stderr."""
        return f"{self.strict.stdout}\n{self.strict.stderr}"


def _strict_env() -> dict[str, str]:
    """
    Return an environment forcing ``LC_ALL=C`` with ``LANG`` removed.

    Same reason as ``multi_bib_gate_strict_build``'s: this machine's ``LANG`` is
    Japanese and Sphinx localises its build output. The bracketed warning CODES
    the assertions below match on are never localised, but forcing the locale
    keeps the captured output readable in a failure message and keeps any
    future text-level assertion honest.
    """
    env = dict(os.environ)
    env["LC_ALL"] = "C"
    env.pop("LANG", None)
    return env


@pytest.fixture(scope="module")
def unfiltered_control(multi_bib_gate_dir, tmp_path_factory):
    """
    Build a copy of the fixture with BOTH ``:filter:`` lines stripped -- the
    measured isolation-failure control -- once for the whole class.

    Stripping the filters turns both directives into bare ``.. bibliography::``
    calls, which per MEM006 render every CITED entry; with two citing sites in
    the document that means both entries land in both reference lists. That is
    precisely the failure mode the per-grid assertions above exist to catch.

    The guards here are load-bearing: if the strip removed nothing (because the
    fixture's option formatting changed), the "control" would be an exact copy
    of the fixture and every assertion in the teeth-proof class would invert
    into a false alarm. So the removal is measured, not assumed.
    """
    workdir = tmp_path_factory.mktemp("multi_bib_unfiltered_control")
    source_dir = _copy_fixture(multi_bib_gate_dir, workdir / "src")

    rst_path = source_dir / f"{DOCNAME}.rst"
    original = rst_path.read_text(encoding="utf-8")
    stripped = "\n".join(
        line for line in original.splitlines() if not re.match(r"^[ \t]+:filter:", line)
    )
    removed = len(original.splitlines()) - len(stripped.splitlines())
    expected_removals = len(_parse_bibliography_directives(original))
    assert removed == expected_removals == 2, (
        "Vacuous-control guard: stripping ':filter:' option lines removed "
        f"{removed} line(s) but the fixture declares {expected_removals} "
        "filtered .. bibliography:: directive(s) (this gate's subject is two). "
        "A control that still carries its filters is an exact copy of the "
        "fixture, and every assertion in the teeth proof would then describe "
        "the PASSING shape."
    )
    assert not _parse_bibliography_directives(stripped), (
        "Vacuous-control guard: the stripped copy still parses as having "
        "filtered .. bibliography:: directives, so the control is not actually "
        f"unfiltered:\n{stripped}"
    )
    rst_path.write_text(stripped, encoding="utf-8")

    plain_dir = workdir / "build_plain"
    plain_result = _run_sphinx_build(source_dir, plain_dir)
    assert plain_result.returncode == 0, (
        "The unfiltered control's NON-strict build is measured to exit 0 (that "
        "is the whole hazard: the broken shape builds 'successfully'), but it "
        f"exited {plain_result.returncode}.\nstdout: {plain_result.stdout}\n"
        f"stderr: {plain_result.stderr}"
    )

    strict_result = _run_sphinx_build(
        source_dir, workdir / "build_strict", extra_args=("-W",), env=_strict_env()
    )
    return MutatedFixtureBuilds(
        source_dir=source_dir,
        plain=MultiBibGateBuild(result=plain_result, build_dir=plain_dir),
        strict=strict_result,
    )


@pytest.mark.skipif(
    not BIBTEX_AVAILABLE,
    reason="sphinxcontrib-bibtex is required for the multi-bibliography gate",
)
class TestUnfilteredControlProvesTheGateHasTeeth:
    """
    **This class is the reason every filtered assertion in this module means
    anything.** The rest of the gate is green on arrival against the untouched
    translator, so on its own it cannot demonstrate that it would notice
    isolation breaking. Here the isolation IS broken -- deliberately, on a
    throwaway copy -- and the broken shape is measured.

    Measured at plan time and re-measured by these tests: with both
    ``:filter:`` lines stripped the document still emits TWO ``grid(`` calls,
    but each cited title now appears in BOTH of them (count 2 document-wide),
    and a ``-W`` build fails emitting ``bibtex.duplicate_local_citation``.

    The first test is the important one to read: **the two-grid COUNT passes
    under the failure mode.** That is the concrete justification for the
    per-region counting rule in the module docstring -- R006's grid count alone
    has no teeth, and only the per-grid row attribution does.

    Asserted on the warning CODE, never on the message prose: Sphinx localises
    its messages and this machine's ``LANG`` is Japanese, so a prose assertion
    would pass here and fail in CI (or vice versa). The strict build runs under
    ``LC_ALL=C`` regardless.
    """

    def test_control_still_emits_one_grid_per_chapter(
        self, unfiltered_control, multi_bib_fixture_data
    ):
        """
        The failure mode does NOT change the grid count: the control still
        emits one ``grid(`` per chapter.

        So R006's count assertion is satisfied by the broken document too, and
        a gate built on the count alone would be vacuous. Documented as a test
        rather than as a comment so it cannot drift away from the truth.
        """
        content_typ = unfiltered_control.plain.read_content_typ()
        blocks = _iter_grid_blocks(content_typ)
        assert len(blocks) == multi_bib_fixture_data.chapter_count, (
            "The unfiltered control is measured to emit the SAME number of "
            f"grids as the filtered fixture ({multi_bib_fixture_data.chapter_count}), "
            f"but emitted {len(blocks)}. If this ever changes, the claim that "
            "R006's grid count has no discriminating power needs re-measuring "
            f"-- do not simply relax it.\n{content_typ}"
        )

    def test_control_leaks_every_cited_entry_into_every_grid(
        self, unfiltered_control, multi_bib_fixture_data
    ):
        """
        The teeth proof proper: in the control, EVERY grid holds EVERY cited
        entry, so the per-grid isolation assertions above would fail here.

        This is the exact inverse of
        ``TestPerGridEntryIsolation::test_each_grid_holds_exactly_one_row_and_it_is_its_own_chapters``
        and of
        ``test_no_chapters_title_appears_in_the_other_chapters_grid``: what
        those require to be absent from a foreign grid is measured PRESENT in
        every grid here.
        """
        content_typ = unfiltered_control.plain.read_content_typ()
        blocks = _iter_grid_blocks(content_typ)
        titles = multi_bib_fixture_data.cited_titles
        assert len(titles) > 1, (
            "Vacuous-pass guard: the leak claim needs at least two cited "
            f"entries to be meaningful, got {titles!r}."
        )

        for position, block in enumerate(blocks, start=1):
            for title in titles:
                assert title in block, (
                    f"The unfiltered control's grid {position} does NOT hold "
                    f"the entry {title!r}. The control is measured to render "
                    "every cited entry into every bibliography (that is the "
                    "failure mode the filtered gate guards against), so this "
                    "means the control no longer reproduces it and the teeth "
                    f"proof has stopped proving anything.\n{block}"
                )

    def test_control_doubles_each_cited_title_document_wide(
        self, unfiltered_control, multi_bib_fixture_data
    ):
        """
        The same leak stated as the document-wide count the compiled-PDF
        assertion uses: each cited title appears once per chapter, i.e. twice.

        This is what makes
        ``TestCompiledPdfHoldsEachEntryExactlyOnce::test_each_cited_entry_title_appears_exactly_once``
        non-vacuous: its expected count of 1 and the broken shape's 2 are
        genuinely different numbers measured on the same fixture.
        """
        content_typ = unfiltered_control.plain.read_content_typ()
        expected = multi_bib_fixture_data.chapter_count
        for key, title in zip(
            multi_bib_fixture_data.chapter_keys,
            multi_bib_fixture_data.cited_titles,
            strict=True,
        ):
            count = content_typ.count(title)
            assert count == expected, (
                f"The unfiltered control is measured to render cited entry "
                f"{key!r}'s title {title!r} once per bibliography, i.e. "
                f"{expected} time(s) document-wide, but counted {count}. The "
                "'exactly once' expectation the filtered gate asserts is only "
                "meaningful while this number differs from it."
            )

    def test_control_strict_build_fails_with_duplicate_local_citation(
        self, unfiltered_control
    ):
        """
        A ``-W`` build of the control FAILS, and names the
        ``bibtex.duplicate_local_citation`` code.

        Two independent signals, both needed. The exit status alone would not
        say WHY (it could regress into some unrelated warning); the code alone
        would not prove ``-W`` still promotes it to an error. Together they are
        what licenses this module's ``-W``-based R009 half: a degrade in this
        document really does become a non-zero exit.
        """
        result = unfiltered_control.strict
        output = unfiltered_control.strict_output
        assert result.returncode != 0, (
            "A strict (-W) build of the UNFILTERED control must FAIL -- it is "
            "measured to emit one bibtex.duplicate_local_citation warning per "
            f"leaked key -- but it exited 0. That would mean -W no longer "
            "converts this degrade into an error, and R009's strict half would "
            f"no longer protect the fixture.\n{output}"
        )
        assert "bibtex.duplicate_local_citation" in output, (
            "The unfiltered control's strict build failed, but WITHOUT naming "
            "the bibtex.duplicate_local_citation code it is measured to emit, "
            "so the failure may have an unrelated cause and this test would be "
            f"proving the wrong thing.\n{output}"
        )


# ---------------------------------------------------------------------------
# (c) :keyprefix: characterisation (R010). S05 consumes this verdict.
#
# S05 needs to know whether a per-directive `:keyprefix:` perturbs the rendered
# label or the emitted Typst anchor -- because if it did, S05's cross-document
# anchor expectations would have to be computed per directive. Measured answer:
# it does not. `:keyprefix:` is a SOURCE-LEVEL key namespace only.
# ---------------------------------------------------------------------------

# The prefix this characterisation injects. Test-authored INPUT -- a string this
# module writes into a throwaway copy's rst -- not a transcribed output token,
# so naming it here breaches no derive-don't-transcribe rule. The whole point
# of the class below is that this string must NOT appear in any output.
KEYPREFIX = "ch1-"


@pytest.fixture(scope="module")
def keyprefix_build(multi_bib_gate_dir, multi_bib_fixture_data, tmp_path_factory):
    """
    Build a copy of the fixture in which CHAPTER ONE's bibliography carries
    ``:keyprefix: ch1-`` and its citing site names the PREFIXED key, strictly
    (``-W``), once for the whole class.

    Both halves of the mutation are required and are derived from the fixture's
    own parsed data, never transcribed: ``:keyprefix:`` namespaces the keys a
    directive's local citations are registered under, so a citing site that
    still named the bare key would simply fail to resolve and the build would
    report ``bibtex.key_not_found`` -- which would characterise a typo, not
    ``:keyprefix:``.

    Chapter TWO is left untouched on purpose, so the copy also shows a prefixed
    and an unprefixed bibliography coexisting in one document.
    """
    workdir = tmp_path_factory.mktemp("multi_bib_keyprefix")
    source_dir = _copy_fixture(multi_bib_gate_dir, workdir / "src")

    first_key = multi_bib_fixture_data.chapter_keys[0]
    rst_path = source_dir / f"{DOCNAME}.rst"
    original = rst_path.read_text(encoding="utf-8")

    # Prefix chapter one's citing site: :cite:p:`Smith2020` -> `ch1-Smith2020`.
    prefixed_site, site_substitutions = re.subn(
        r"(:cite:[a-z]*:`)" + re.escape(first_key) + r"(`)",
        r"\g<1>" + KEYPREFIX + first_key + r"\g<2>",
        original,
    )
    assert site_substitutions == 1, (
        "Vacuous-mutation guard: expected exactly one citing site naming the "
        f"first chapter's key {first_key!r} to prefix, rewrote "
        f"{site_substitutions}. Without the rewrite the prefixed bibliography "
        "would have no resolving citation and this would characterise a "
        "key_not_found typo instead of :keyprefix:."
    )

    # Add :keyprefix: to the FIRST .. bibliography:: directive only, reusing the
    # indentation of the option line already there so the rst stays valid.
    with_keyprefix, directive_substitutions = re.subn(
        r"^(\.\. bibliography::\n)([ \t]+)(:filter:)",
        r"\g<1>\g<2>:keyprefix: " + KEYPREFIX + r"\n\g<2>\g<3>",
        prefixed_site,
        count=1,
        flags=re.M,
    )
    assert directive_substitutions == 1, (
        "Vacuous-mutation guard: failed to insert ':keyprefix:' into the first "
        ".. bibliography:: directive of the copy. The fixture's directive "
        "formatting must have changed; re-derive the insertion rather than "
        "hardcoding a line number."
    )
    assert with_keyprefix.count(f":keyprefix: {KEYPREFIX}") == 1, (
        "Vacuous-mutation guard: the copy must carry EXACTLY ONE :keyprefix: "
        "option (chapter one's), so the coexistence of a prefixed and an "
        f"unprefixed bibliography is part of what is measured:\n{with_keyprefix}"
    )
    rst_path.write_text(with_keyprefix, encoding="utf-8")

    build_dir = workdir / "build_strict"
    result = _run_sphinx_build(
        source_dir, build_dir, extra_args=("-W",), env=_strict_env()
    )
    return MutatedFixtureBuilds(
        source_dir=source_dir,
        plain=MultiBibGateBuild(result=result, build_dir=build_dir),
        strict=result,
    )


@pytest.mark.skipif(
    not BIBTEX_AVAILABLE,
    reason="sphinxcontrib-bibtex is required for the multi-bibliography gate",
)
class TestKeyprefixIsSourceLevelOnly:
    """
    R010, the verdict S05 consumes: a bibliography's ``:keyprefix:`` is a
    SOURCE-LEVEL key namespace only. It perturbs neither the rendered citation
    label nor any emitted Typst anchor.

    Measured at plan time and re-measured here: with ``:keyprefix: ch1-`` on
    chapter one's bibliography and its citing site naming the prefixed key, a
    ``-W`` build exits 0 with no warnings, chapter one's row label is still the
    unprefixed label the untouched fixture produces, and the string ``ch1-``
    appears in NO emitted anchor -- the anchors keep the plain
    ``<index:idN>`` shape.

    Why S05 cares: if ``:keyprefix:`` DID leak into labels or anchors, S05's
    cross-document expectations would have to be computed per directive rather
    than per document. The explicit no-leak assertion below is that exact
    property, stated as a property of the whole emitted file rather than of one
    sampled anchor.
    """

    def test_keyprefix_strict_build_exits_zero_with_no_degrade_codes(
        self, keyprefix_build
    ):
        """
        A ``-W`` build of the ``:keyprefix:`` copy exits 0 and names no bibtex
        degrade code.

        Under ``-W`` exit 0 IS the zero-warning evidence, locale-independently;
        the code check adds the information the exit status cannot carry, in
        case a future ``sphinxcontrib-bibtex`` stops promoting one of these to
        an error. Together they establish that ``:keyprefix:`` plus a matching
        prefixed citing site is a fully RESOLVING configuration -- without
        that, the label and anchor assertions below would be describing a
        degraded document.
        """
        result = keyprefix_build.strict
        output = keyprefix_build.strict_output
        assert result.returncode == 0, (
            "R010: a strict (-W) build of the :keyprefix: copy is measured to "
            f"exit 0 with zero warnings, but exited {result.returncode}. Under "
            "-W that means at least one warning was emitted -- most likely the "
            "citing site and the directive's keyprefix disagreeing, which "
            "would make the rest of this class describe a degraded "
            f"document.\n{output}"
        )
        for code in BIBTEX_DEGRADE_CODES:
            assert code not in output, (
                f"R010: the :keyprefix: copy's strict build reported the "
                f"{code!r} warning code, so its citations did not resolve "
                "cleanly and the label/anchor characterisation below would be "
                f"reading a degraded document.\n{output}"
            )

    def test_keyprefix_does_not_perturb_the_rendered_label(
        self, keyprefix_build, derived_tokens, multi_bib_fixture_data
    ):
        """
        R010: chapter one's grid row still carries the SAME label the untouched
        fixture produces -- the prefix does not reach the rendered label.

        The expected label is read from ``derived_tokens`` (Sphinx's resolved
        doctree over the REAL fixture), not written here as a literal, so this
        compares two measurements of the same thing rather than a measurement
        against a transcription. Equally important is the negative half: the
        prefixed form of that label must appear NOWHERE in the emitted file.
        """
        content_typ = keyprefix_build.plain.read_content_typ()
        blocks = _iter_grid_blocks(content_typ)
        expected_count = multi_bib_fixture_data.chapter_count
        assert len(blocks) == expected_count, (
            f"R010: the :keyprefix: copy must still emit {expected_count} "
            f"grids (the prefix changes key namespacing, not document "
            f"structure), but emitted {len(blocks)}.\n{content_typ}"
        )

        first_key = multi_bib_fixture_data.chapter_keys[0]
        expected_label = derived_tokens[first_key].label
        rows = _parse_grid_row_anchors(blocks[0])
        assert expected_label in rows, (
            f"R010: chapter one's grid carries no row labelled "
            f"{expected_label!r} -- the label the UNTOUCHED fixture produces "
            f"for {first_key!r}. Parsed rows: {rows!r}. If :keyprefix: now "
            "perturbs the label, S05's anchor expectations must be computed "
            "per directive; record the new measurement rather than relaxing "
            f"this.\n{blocks[0]}"
        )
        assert f"{KEYPREFIX}{expected_label}" not in content_typ, (
            f"R010: the prefixed label {KEYPREFIX + expected_label!r} appears "
            "in the emitted .typ, so :keyprefix: is NOT source-level only and "
            "leaks into rendered labels. That contradicts the measurement S05 "
            f"relies on.\n{content_typ}"
        )

    def test_keyprefix_never_leaks_into_any_emitted_anchor(self, keyprefix_build):
        """
        R010, the property S05 relies on, stated explicitly: the prefix appears
        in NO emitted Typst anchor, and every grid row anchor keeps the plain
        ``<index:idN>`` shape.

        Scoped to every ``<...>`` token in the whole emitted file rather than to
        a sampled anchor, so a leak anywhere -- section anchor, row anchor, link
        target -- is caught. The non-empty guard rules out the degenerate pass
        where no anchors were parsed at all.
        """
        content_typ = keyprefix_build.plain.read_content_typ()
        anchors = sorted(set(re.findall(r"<([^<>\s]+)>", content_typ)))
        assert anchors, (
            "Vacuous-pass guard: parsed NO Typst anchors out of the "
            f":keyprefix: copy's emitted .typ, so the no-leak assertion below "
            f"would hold trivially.\n{content_typ}"
        )
        leaking = [anchor for anchor in anchors if KEYPREFIX in anchor]
        assert not leaking, (
            f"R010: the anchors {leaking!r} carry the :keyprefix: value "
            f"{KEYPREFIX!r}. S05 relies on :keyprefix: being a source-level key "
            "namespace that never reaches an anchor; if that has changed, S05's "
            "cross-document anchor expectations must be recomputed per "
            f"directive.\nAll anchors: {anchors!r}"
        )

        row_anchors = [
            anchor
            for block in _iter_grid_blocks(content_typ)
            for anchor in _parse_grid_row_anchors(block).values()
        ]
        assert row_anchors, (
            "Vacuous-pass guard: parsed no grid ROW anchors out of the "
            f":keyprefix: copy, so the shape assertion below is empty.\n"
            f"{content_typ}"
        )
        plain_shape = re.compile(re.escape(DOCNAME) + r":id\d+")
        for anchor in row_anchors:
            assert plain_shape.fullmatch(anchor), (
                f"R010: the grid row anchor {anchor!r} is not of the plain "
                f"'{DOCNAME}:id<N>' form the untouched fixture emits. "
                ":keyprefix: is measured not to perturb anchor shape, so a "
                "different shape here is a change S05 must be told about."
            )
