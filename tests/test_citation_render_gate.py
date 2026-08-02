"""
Phase 40 (Citations -- Full Round Trip) render gate: CIT-01..CIT-04, CIT-06,
D-05/D-06/D-07/D-08/D-13/D-14, SC#5.

CIT-01 is the milestone's SOLE classic "does not compile" RED (ROADMAP
binding constraint #3): pre-fix, ``docutils.nodes.citation`` and
``docutils.nodes.label`` have no translator handler, so a real
``-b typstpdf`` build aborts with the verbatim
``TypstError: expected semicolon or line break`` (see
``40-GATE-EVIDENCE-01.md``). ``test_citation_gate_compiles_via_real_typst_compile``
below is a genuine RED->GREEN flip -- the SAME test, over the SAME fixture,
fails today and must pass, unmodified, once ``visit_citation`` /
``depart_citation`` / ``visit_label`` land in ``typsphinx/translator.py``.
It is NOT the durable mechanical-reconstruction shape of
``tests/test_typst_elements_pass_through_gate.py``.

Every other test in this module is RED against the untouched translator for
STRUCTURAL reasons (a missing anchor, a missing grid, a missing separator) --
never a Python ``TypeError``/``KeyError``/fixture error. No expected label,
anchor, or link-target token is ever written as a string literal: every
comparison is between two values extracted from emitted ``.typ`` output, or
between an extracted value and one computed by calling
``typsphinx.translator.TypstTranslator``'s own ``_namespace_label`` /
``_sanitize_label`` directly (D-13's derivation point), or between an
extracted value and one read from Sphinx's OWN resolved doctree
(``env.get_and_resolve_doctree``, RESEARCH Pitfall 3's duplicate-key
resolution direction) -- never guessed or transcribed.

Requirements: CIT-01, CIT-02, CIT-03, CIT-04, CIT-06 (CIT-05 is out of scope
for this plan -- see 40-02-PLAN.md).
"""

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest
from docutils import nodes as docutils_nodes

from typsphinx.translator import TypstTranslator

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


# ---------------------------------------------------------------------------
# Shared scaffolding (copied in shape from
# tests/test_cross_doc_label_namespace_render_gate.py /
# tests/test_confval_field_body_render_gate.py, per 40-PATTERNS.md).
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def citation_render_gate_dir():
    """Return the path to the citation_render_gate fixture."""
    return Path(__file__).parent / "fixtures" / "citation_render_gate"


@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for build output."""
    return tmp_path / "_build"


def _run_sphinx_build_typstpdf(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typstpdf`` as a subprocess and return the completed
    process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``
    and never a bare ``sphinx-build``) -- the NixOS PATH-shadowing hazard
    restated in every render-gate module in this project.
    """
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            "typstpdf",
            str(source_dir),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
    )


@dataclass
class CitationGateBuild:
    """One real ``-b typstpdf`` build of the citation fixture, captured
    exactly once for the whole module."""

    result: subprocess.CompletedProcess
    build_dir: Path
    index_typ: str | None
    second_typ: str | None


@pytest.fixture(scope="module")
def citation_gate_build(citation_render_gate_dir, tmp_path_factory):
    """
    Run ``-b typstpdf`` over the citation fixture EXACTLY ONCE for the whole
    module and return a small record carrying the ``CompletedProcess``, the
    build directory, and the text of ``index.typ`` / ``second.typ`` when
    they exist.

    Deliberately does NOT assert on the return code: pre-fix the build
    fails (the classic GATE-01 compile fatal, CIT-01), and an asserting
    fixture would turn every test in this module into a fixture ERROR
    instead of the readable per-requirement RED this gate exists to record.
    ``write_doc`` still emits both ``.typ`` files before the compile step
    that fails inside ``TypstPDFBuilder.finish()``, so both are available to
    every ``.typ``-string test in this module regardless of build outcome
    (verified this session: a real subprocess run of this exact fixture
    exits non-zero with the classic fatal in stderr, while
    ``index.typ``/``second.typ`` both exist on disk afterward).
    """
    build_dir = tmp_path_factory.mktemp("citation_gate") / "_build"
    result = _run_sphinx_build_typstpdf(citation_render_gate_dir, build_dir)
    index_typ_path = build_dir / "index.typ"
    second_typ_path = build_dir / "second.typ"
    index_typ = (
        index_typ_path.read_text(encoding="utf-8") if index_typ_path.exists() else None
    )
    second_typ = (
        second_typ_path.read_text(encoding="utf-8")
        if second_typ_path.exists()
        else None
    )
    return CitationGateBuild(
        result=result,
        build_dir=build_dir,
        index_typ=index_typ,
        second_typ=second_typ,
    )


def _require_typ(build: CitationGateBuild, attr: str) -> str:
    """Return ``build.<attr>``, raising a clear ``AssertionError`` naming
    the missing artifact if that ``.typ`` was never emitted -- rather than
    letting a caller hit a bare ``AttributeError``/``TypeError`` on
    ``None``."""
    text = getattr(build, attr)
    if text is None:
        raise AssertionError(
            f"{attr} was never emitted by the build (missing artifact) -- "
            f"build returncode={build.result.returncode}\n"
            f"stdout: {build.result.stdout}\nstderr: {build.result.stderr}"
        )
    return text


@pytest.fixture(scope="module")
def citation_gate_env(citation_render_gate_dir, tmp_path_factory):
    """
    Build the fixture through a real, in-process ``SphinxTestApp`` (``-b
    typst``, no compile -- works with or without ``typst-py`` installed) and
    return its ``(env, builder)`` pair so tests can walk the RESOLVED
    doctree (``env.get_and_resolve_doctree``) and read the docutils-assigned
    ``ids`` Sphinx's citation domain actually resolved -- never a
    hard-coded guess (RESEARCH Pitfall 3: a same-document citing reference
    to a duplicate key does not always resolve to the same-document
    definition).

    Independent of ``citation_gate_build`` above: that fixture proves what
    the TRANSLATOR emits (subprocess, ``-b typstpdf``); this one proves what
    SPHINX resolved before the translator ever ran (in-process, ``-b
    typst``, cheaper and importable without ``typst-py``).
    """
    from sphinx.testing.util import SphinxTestApp

    builddir = tmp_path_factory.mktemp("citation_gate_env")
    app = SphinxTestApp(
        buildername="typst",
        srcdir=citation_render_gate_dir.resolve(),
        builddir=builddir,
    )
    app.build()
    yield app.env, app.builder
    app.cleanup()


def _expected_namespace_label(docname: str, raw_id: str) -> str:
    """
    Compute the expected namespaced label by calling the translator's own
    ``_namespace_label``/``_sanitize_label`` directly (D-13's single
    derivation point), never by transcribing the derivation as a string.

    Passing the class itself as ``self`` is safe here: ``_namespace_label``
    only ever calls ``self._sanitize_label(...)``, and ``_sanitize_label``
    is a ``@staticmethod`` resolvable through the class object with no
    instance state required.
    """
    return TypstTranslator._namespace_label(TypstTranslator, docname, raw_id)


def _strip_raw_literals(typ_text: str) -> str:
    """Drop ``raw("...")`` inline-literal segments before scanning for
    labels (copied from
    ``tests/test_cross_doc_label_namespace_render_gate.py``). This
    fixture's own ``second.rst`` deliberately quotes
    ``` ``index:same2020`` ``` / ``` ``second:same2020`` ``` as prose
    RST literals (rendering as ``raw("index:same2020")`` etc.) -- those are
    literal text, NOT real Typst label expressions, and must be excluded
    from any label/``link(<...>)`` scan or they masquerade as real anchors.
    """
    return re.sub(r'raw\("(?:[^"\\]|\\.)*"\)', "", typ_text)


_ATTACHED_ANCHOR_RE = re.compile(r"(?<!link\()<([A-Za-z0-9_.:-]+)>")
_OWN_ID_SUFFIX_RE = re.compile(r":id\d+$")


def _attached_anchor_tokens(typ_text: str) -> set[str]:
    """
    Every bracket-attached anchor token (the ``[... <label>]`` postfix
    attachment form) in ``typ_text`` -- i.e. every ``<label>`` NOT
    immediately preceded by ``link(``, which would make it a link TARGET
    rather than a definition/citing-site ANCHOR. Distinguishes "this node
    anchors itself here" from "this node points at some other anchor".
    """
    return set(_ATTACHED_ANCHOR_RE.findall(typ_text))


def _definition_anchor_tokens(typ_text: str) -> set[str]:
    """
    The subset of attached anchors whose raw id is a citation KEY-derived
    slug (e.g. ``krizhevsky2012``), never a docutils auto ``idN`` -- i.e. a
    citation DEFINITION's own anchor, not a citing site's own D-14 anchor.
    Sphinx always assigns citing-site auto ids as ``id`` + a number; a
    citation key never collides with that shape in this fixture.
    """
    return {
        tok
        for tok in _attached_anchor_tokens(typ_text)
        if not _OWN_ID_SUFFIX_RE.search(tok)
    }


def _own_id_anchor_tokens(typ_text: str) -> set[str]:
    """The subset of attached anchors whose raw id IS a docutils auto
    ``idN`` -- i.e. a citing site's own D-14 anchor."""
    return {
        tok
        for tok in _attached_anchor_tokens(typ_text)
        if _OWN_ID_SUFFIX_RE.search(tok)
    }


def _expected_own_id_anchors(env, builder, docname: str) -> set[str]:
    """
    Every expected D-14 own-anchor token for ``docname``, derived from the
    RESOLVED doctree's actual ``reference`` nodes (never guessed): for each
    ``reference`` carrying a non-empty ``ids`` (citation-derived, per
    RESEARCH's real doctree evidence), the namespaced anchor Sphinx's own
    docutils resolution assigned it.
    """
    doctree = env.get_and_resolve_doctree(docname, builder)
    expected = set()
    for ref in doctree.findall(docutils_nodes.reference):
        ids = ref.get("ids", [])
        if ids:
            expected.add(_expected_namespace_label(docname, ids[0]))
    return expected


def _slice(typ_text: str, start_marker: str, end_marker: str | None) -> str:
    """
    Return the substring of ``typ_text`` from ``start_marker`` (inclusive)
    up to ``end_marker`` (exclusive), or to the end of the document if
    ``end_marker`` is ``None``. Mirrors
    ``tests/test_rubric_indent_invariance.py``'s ``_slice`` helper exactly,
    so a region-isolation assertion cannot be satisfied by bytes belonging
    to a different construct.
    """
    start_idx = typ_text.index(start_marker)
    if end_marker is None:
        return typ_text[start_idx:]
    end_idx = typ_text.index(end_marker, start_idx + len(start_marker))
    return typ_text[start_idx:end_idx]


def _grid_span(typ_text: str, region_start: str, region_end: str | None) -> str:
    """
    Return the text of the FIRST ``grid(...)`` call inside the region
    between ``region_start`` and ``region_end``, raising a clear
    ``AssertionError`` (not an uncaught ``ValueError``) if no ``grid(``
    appears there -- pre-fix, this always raises, which is the intended RED
    (D-05's citation-run grid does not exist yet).
    """
    region = _slice(typ_text, region_start, region_end)
    if "grid(" not in region:
        raise AssertionError(
            f"No grid( call found between {region_start!r} and "
            f"{region_end!r} -- pre-fix RED: D-05's citation-run grid does "
            f"not exist yet.\nRegion:\n{region}"
        )
    grid_start = region.index("grid(")
    return region[grid_start:]


# Region markers shared by the structural tests below -- every heading this
# fixture emits is unique in the document, so these are safe, unambiguous
# slice boundaries.
_CITING_SITES_HEADING = '{text("Citing Sites")}'
_CONCAT_HEADING = '{text("Concat Protocol")}'
_NESTED_HEADING = '{text("Nested Protocol")}'
_REFERENCES_HEADING = '{text("References")}'
_RUN_BREAK_HEADING = '{text("Run Break")}'


# ---------------------------------------------------------------------------
# .typ-string-level tests -- no typst/pypdf skip needed, so these still run
# where the optional compiled-PDF dependencies are unavailable.
# ---------------------------------------------------------------------------


class TestCitationRenderGateStructural:
    """
    CIT-03/D-14 (``link``), D-13/D-10 (``namespace``), SC#5 (``separator``),
    D-07 (``uncited``), and D-05/D-06 (grid-count) -- pure ``.typ``-string
    assertions against the untouched translator's real output.
    """

    def test_link_citing_site_targets_match_definition_anchors_and_own_ids(
        self, citation_gate_build, citation_gate_env
    ):
        """
        CIT-03 + D-14. Every value compared here is extracted from emitted
        output or computed via ``_namespace_label`` -- never a literal.
        """
        index_typ = _strip_raw_literals(_require_typ(citation_gate_build, "index_typ"))
        second_typ = _strip_raw_literals(
            _require_typ(citation_gate_build, "second_typ")
        )
        env, builder = citation_gate_env

        link_targets_index = set(re.findall(r"link\(<([^>\n]+)>", index_typ))
        link_targets_second = set(re.findall(r"link\(<([^>\n]+)>", second_typ))
        definition_anchors_index = _definition_anchor_tokens(index_typ)

        # (1) Same-document: the first Krizhevsky2012 citing site's link
        # target must equal the anchor its OWN definition attaches.
        expected_krizhevsky = _expected_namespace_label("index", "krizhevsky2012")
        assert expected_krizhevsky in link_targets_index, (
            "index.typ's Krizhevsky2012 citing site did not emit "
            f"link(<{expected_krizhevsky}>, ...) -- this half already works "
            f"pre-fix (visit_reference is unmodified); emitted link "
            f"targets: {sorted(link_targets_index)}"
        )
        assert expected_krizhevsky in definition_anchors_index, (
            f"index.typ's Krizhevsky2012 DEFINITION carries no attached "
            f"anchor <{expected_krizhevsky}> yet -- CIT-01/D-13 RED (no "
            f"citation handler exists to emit it). Attached anchors found: "
            f"{sorted(definition_anchors_index)}"
        )

        # (2) Cross-document: second.typ's citing site must target the
        # SAME namespaced anchor index.typ's own definition attaches.
        assert expected_krizhevsky in link_targets_second, (
            "second.typ's cross-document Krizhevsky2012 citing site did "
            f"not emit link(<{expected_krizhevsky}>, ...); emitted link "
            f"targets: {sorted(link_targets_second)}"
        )
        assert expected_krizhevsky in definition_anchors_index, (
            "The cross-document citing site's target anchor must be "
            "defined in index.typ (repeated from check (1) -- if this "
            "fails independently the two checks disagree)."
        )

        # (3) D-14 positive: every citation-derived citing site in
        # index.typ/second.typ carries its OWN attached idN anchor,
        # computed from Sphinx's ACTUAL resolved doctree ids -- never
        # guessed.
        expected_own_ids_index = _expected_own_id_anchors(env, builder, "index")
        actual_own_ids_index = _own_id_anchor_tokens(index_typ)
        assert expected_own_ids_index == actual_own_ids_index, (
            "D-14: every citation-derived reference in index.typ must "
            "carry its own <docname:idN> attached anchor (so the "
            "definition's back-reference marker has a target). Expected "
            f"(from the resolved doctree): {sorted(expected_own_ids_index)}; "
            f"found in index.typ: {sorted(actual_own_ids_index)}"
        )
        expected_own_ids_second = _expected_own_id_anchors(env, builder, "second")
        actual_own_ids_second = _own_id_anchor_tokens(second_typ)
        assert expected_own_ids_second == actual_own_ids_second, (
            "D-14 (second.typ): expected "
            f"{sorted(expected_own_ids_second)}, found "
            f"{sorted(actual_own_ids_second)}"
        )

        # (4) D-14 negative control: the master's toctree inclusion of
        # second.typ carries no citation-style attached anchor. Measured
        # this session: visit_toctree reads node['entries'] directly and
        # raises nodes.SkipNode, so it NEVER walks into (or emits via)
        # visit_reference for a toctree entry -- there is no
        # toctree-generated `reference` node in this translator's real
        # write path to attach an anchor to in the first place. This
        # checks that structural fact directly on the actual include()
        # emission rather than asserting something unobservable.
        include_line = next(
            line for line in index_typ.splitlines() if 'include("second.typ")' in line
        )
        assert "<" not in include_line, (
            "The toctree inclusion of second.typ must carry no "
            f"citation-style attached-anchor bracket: {include_line!r}"
        )

        # (5) T-40-03: no link in index.typ targets an anchor derived from
        # the undefined key Nosuchkey, and its text still renders as plain
        # content (Sphinx itself warns and leaves the reference
        # unresolved before the translator ever runs).
        nosuchkey_anchor = _expected_namespace_label("index", "nosuchkey")
        assert nosuchkey_anchor not in link_targets_index, (
            f"A link targeting <{nosuchkey_anchor}> exists for the "
            "undefined key Nosuchkey -- this would be a dangling label "
            f"reference (T-40-03): {sorted(link_targets_index)}"
        )
        assert "[Nosuchkey]" in index_typ, (
            "Nosuchkey's citing-site text must still render as plain "
            f"inline content:\n{index_typ}"
        )

    def test_namespace_duplicate_key_is_document_scoped(self, citation_gate_build):
        """D-13 + D-10: definition-side namespacing, never the
        reference-resolution direction (RESEARCH Pitfall 3)."""
        index_typ = _strip_raw_literals(_require_typ(citation_gate_build, "index_typ"))
        second_typ = _strip_raw_literals(
            _require_typ(citation_gate_build, "second_typ")
        )

        expected_index_same2020 = _expected_namespace_label("index", "same2020")
        expected_second_same2020 = _expected_namespace_label("second", "same2020")
        assert expected_index_same2020 != expected_second_same2020, (
            "Precondition broken: the two namespaced tokens for the "
            "duplicate key must differ by construction."
        )

        index_definition_anchors = _definition_anchor_tokens(index_typ)
        second_definition_anchors = _definition_anchor_tokens(second_typ)
        assert expected_index_same2020 in index_definition_anchors, (
            f"index.typ's OWN Same2020 definition does not attach "
            f"<{expected_index_same2020}> -- CIT-01/D-13 RED (no citation "
            f"handler exists yet). Found: {sorted(index_definition_anchors)}"
        )
        assert expected_second_same2020 in second_definition_anchors, (
            f"second.typ's OWN Same2020 definition does not attach "
            f"<{expected_second_same2020}> -- CIT-01/D-13 RED. Found: "
            f"{sorted(second_definition_anchors)}"
        )

        # Neither anchor is a bare, un-namespaced <same2020> -- namespacing
        # is not merely present, it is document-scoped.
        assert not re.search(r"<same2020>", index_typ + second_typ), (
            "A bare, un-namespaced <same2020> anchor survived -- this is "
            "exactly the duplicate-label fatal D-13's namespacing exists "
            "to prevent."
        )

        # Sphinx's citation domain resolves a duplicate key
        # last-registered-wins ACROSS THE WHOLE BUILD (RESEARCH Pitfall 3)
        # -- never assert which of the two the index.rst citing site
        # resolves to, only that it resolved to ONE of the two.
        link_targets_index = set(re.findall(r"link\(<([^>\n]+)>", index_typ))
        possible_targets = {expected_index_same2020, expected_second_same2020}
        resolved = link_targets_index & possible_targets
        assert resolved, (
            "index.rst's duplicate-key citing site did not resolve to "
            f"either namespaced Same2020 anchor. Emitted link targets: "
            f"{sorted(link_targets_index)}; expected one of "
            f"{sorted(possible_targets)}"
        )

    def test_separator_paragraph_concat_and_list_item_boundaries(
        self, citation_gate_build
    ):
        """
        SC#5's three protocols, checked explicitly (never by analogy to the
        footnote handlers, whose separator logic never applies to a
        Body-level citation definition -- RESEARCH Pitfall 1).
        """
        index_typ = _strip_raw_literals(_require_typ(citation_gate_build, "index_typ"))

        # (b) Code-mode concat boundary: the definition-list term's
        # emission joins the citing reference to its sibling text with the
        # concat operator, with no operator left dangling. Already true
        # pre-fix -- visit_reference is unmodified by this phase, this is
        # a non-regression CONTROL within the same test.
        concat_region = _slice(index_typ, "terms(separator:", _NESTED_HEADING)
        expected_concat_target = _expected_namespace_label("index", "concat2000")
        assert (
            f'text("Concat Term ") + link(<{expected_concat_target}>,' in concat_region
        ), (
            "Concat Protocol's term must '+'-join its leading text to the "
            f"citing reference with no dangling operator:\n{concat_region}"
        )

        # (a) Paragraph boundary: the References run's grid must open as
        # its own statement -- not abutting the preceding heading/paragraph
        # on the same line. Pre-fix RED: no grid( exists at all yet.
        refs_grid = _grid_span(index_typ, _REFERENCES_HEADING, _RUN_BREAK_HEADING)
        grid_open_line = refs_grid.splitlines()[0]
        assert grid_open_line.strip().startswith("grid("), (
            "The References run's grid( must open as its own statement, "
            f"not juxtaposed against preceding text: {grid_open_line!r}"
        )

        # (c) List-item boundary: the single Nested2021 citation inside the
        # bullet list's second item must ALSO be its own one-row grid,
        # newline-separated from the introductory paragraph before it
        # (mirrors _visit_admonition's list_item_needs_separator
        # bookkeeping). Pre-fix RED: no grid( exists there either, and
        # RESEARCH independently reproduced this exact construct failing
        # with a DIFFERENT fatal (a semantic-pass missing-label error) than
        # the top-level syntax fatal -- see 40-GATE-EVIDENCE-01.md.
        nested_region = _slice(index_typ, _NESTED_HEADING, _REFERENCES_HEADING)
        assert nested_region.count("grid(") == 1, (
            "D-05: expected exactly one grid( for the single Nested2021 "
            f"citation inside the list item, found "
            f"{nested_region.count('grid(')}:\n{nested_region}"
        )
        nested_grid_line = next(
            line for line in nested_region.splitlines() if "grid(" in line
        )
        assert nested_grid_line.strip().startswith("grid("), (
            "The nested citation's grid( must open as its own statement, "
            f"not abutting the preceding paragraph on the same line "
            f"(T-40-02): {nested_grid_line!r}"
        )

    def test_uncited_entry_renders_plain_label_in_shared_grid(
        self, citation_gate_build
    ):
        """D-07: the deliberate INVERSE of the footnote precedent (Phase 14
        D-09 drops an unreferenced footnote; a citation keeps it)."""
        index_typ = _strip_raw_literals(_require_typ(citation_gate_build, "index_typ"))

        assert "CITORDERCHARLIE" in index_typ, (
            "The uncited Never1999 entry's sentinel must still render at "
            f"all (D-07):\n{index_typ}"
        )

        refs_grid = _grid_span(index_typ, _REFERENCES_HEADING, _RUN_BREAK_HEADING)
        for sentinel in (
            "CITORDERALPHA",
            "CITORDERBRAVO",
            "CITORDERCHARLIE",
            "CITORDERDELTA",
            "CITORDERECHO",
        ):
            assert sentinel in refs_grid, (
                f"{sentinel} must be a row inside the SAME References grid "
                f"as its siblings (D-05), including the uncited entry "
                f"(D-07):\n{refs_grid}"
            )

        # The uncited label carries no link call anywhere near its row.
        charlie_idx = refs_grid.index("CITORDERCHARLIE")
        never1999_row = refs_grid[max(0, charlie_idx - 40) : charlie_idx]
        assert "link(" not in never1999_row, (
            "Never1999's row must be a plain, non-linked label (D-07): "
            f"{never1999_row!r}"
        )

    def test_references_run_and_run_break_grid_counts(self, citation_gate_build):
        """
        D-05/D-06 grid-count structural test. Derived from the fixture's
        AUTHORED structure (Task 1): the References section holds five
        consecutive citation definitions separated only by an RST comment
        (which emits nothing) -> exactly ONE run/grid. The Run Break
        section holds two definitions separated by a real paragraph -> the
        paragraph breaks the run into exactly TWO independently-aligned
        grids (D-06).
        """
        index_typ = _strip_raw_literals(_require_typ(citation_gate_build, "index_typ"))

        refs_region = _slice(index_typ, _REFERENCES_HEADING, _RUN_BREAK_HEADING)
        assert refs_region.count("grid(") == 1, (
            "D-05: the References section's five citation definitions "
            "(separated only by a comment, which emits nothing) must land "
            f"in exactly ONE grid, found {refs_region.count('grid(')}:\n"
            f"{refs_region}"
        )

        run_break_region = _slice(index_typ, _RUN_BREAK_HEADING, None)
        assert run_break_region.count("grid(") == 2, (
            "D-06: the Run Break section's two citation definitions, "
            "separated by a real paragraph, must land in exactly TWO "
            f"independently-aligned grids, found "
            f"{run_break_region.count('grid(')}:\n{run_break_region}"
        )


# ---------------------------------------------------------------------------
# Real-compile / compiled-PDF tests -- gated behind TYPST_AVAILABLE (and, for
# the compiled-PDF half in Task 3, PYPDF_AVAILABLE too).
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the citation render gate's real-compile half",
)
class TestCitationRenderGateRealCompile:
    """
    CIT-01, the classic GATE-01 RED. This is a genuine RED->GREEN flip
    (mirrors ``tests/test_confval_field_body_render_gate.py``'s shape
    exactly): the SAME test, over the SAME fixture, fails today and must
    pass -- unmodified -- once the citation handlers land.
    """

    def test_citation_gate_compiles_via_real_typst_compile(self, citation_gate_build):
        """
        Build the fixture through ``-b typstpdf`` and confirm the build
        exits cleanly and produces a real, non-empty PDF. Pre-fix, all of
        these fail because ``TypstPDFBuilder.finish()`` raises
        ``ExtensionError`` wrapping the verbatim ``TypstError: expected
        semicolon or line break`` (see ``40-GATE-EVIDENCE-01.md``).
        """
        result = citation_gate_build.result
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed (CIT-01 classic RED):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        combined = result.stdout + result.stderr
        assert "expected semicolon or line break" not in combined, (
            "typst.compile() rejected the citation definition's juxtaposed "
            f"label/body -- the CIT-01 fix is not in effect:\n{combined}"
        )
        assert "Typst compilation failed" not in combined, (
            f"TypstPDFBuilder.finish() logged a compilation failure:\n" f"{combined}"
        )

        pdf_output = citation_gate_build.build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted, most "
            f"likely on the classic citation compile fatal:\n"
            f"stderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"
