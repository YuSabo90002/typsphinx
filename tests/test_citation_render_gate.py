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
_ATTACHED_ANCHOR_CALL_RE = re.compile(r'#label\("([A-Za-z0-9_.:-]+)"\)')
_OWN_ID_SUFFIX_RE = re.compile(r":id\d+$")


def _attached_anchor_tokens(typ_text: str) -> set[str]:
    """
    Every attached anchor token in ``typ_text`` -- i.e. every label this
    translator ATTACHES to preceding content, never a link TARGET.

    This translator emits an attached anchor through two syntactically
    different but semantically equivalent Typst forms, both already
    present in the merged translator (verified this session by reading
    ``typsphinx/translator.py`` directly, not guessed): the markup-mode
    bracket-postfix shorthand ``[... <label>]`` (``visit_citation``'s own
    definition anchor, ``depart_term``'s heading anchors), and the
    explicit function-call form ``#label("...")`` (``visit_target``'s
    pre-existing ``next_is_target`` case, and D-14's own-ids anchor added
    to ``visit_reference``/``depart_reference``). ``<name>`` is parser
    sugar for ``#label("name")`` -- Typst attaches both identically to the
    immediately preceding content -- so a helper that recognised only the
    bracket form would read a real, working ``#label(...)`` anchor as
    "missing" (confirmed: a real ``-b typst`` build of this fixture emits
    ``[#link(<index:krizhevsky2012>, ...)#label("index:id1")]`` for the
    first Krizhevsky2012 citing site, and the corresponding ``-b typstpdf``
    real-compile test passes clean, proving that attachment resolves).
    """
    bracket_form = set(_ATTACHED_ANCHOR_RE.findall(typ_text))
    call_form = set(_ATTACHED_ANCHOR_CALL_RE.findall(typ_text))
    return bracket_form | call_form


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
    doctree = env.get_and_resolve_doctree(docname, builder, tags=builder.tags)
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


def _citing_site_own_anchors(env, builder, docname: str, key_text: str) -> list[str]:
    """
    Return, in document order, the expected D-14 own-anchor token
    (``_namespace_label(docname, ids[0])``) for every citing site in
    ``docname`` whose text is ``[key_text]`` -- read from Sphinx's
    RESOLVED doctree, never guessed.
    """
    doctree = env.get_and_resolve_doctree(docname, builder, tags=builder.tags)
    result = []
    for ref in doctree.findall(docutils_nodes.reference):
        if ref.astext() == f"[{key_text}]":
            ids = ref.get("ids", [])
            if ids:
                result.append(_expected_namespace_label(docname, ids[0]))
    return result


def _layout_lines(pdf_bytes: bytes, page_index: int) -> str:
    """
    Return the ``extraction_mode="layout"`` text for ONE page. Layout mode
    reconstructs a monospace-like character grid from the PDF's real glyph
    positions and preserves left-edge indentation as leading whitespace --
    verified this session (RESEARCH § Code Examples) for the citation grid
    construct specifically, mirroring the technique established by
    ``tests/test_rubric_indent_invariance.py``/
    ``tests/test_desc_content_indent_render_gate.py`` for other constructs.
    """
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    return reader.pages[page_index].extract_text(extraction_mode="layout")


def _marker_column(layout_text: str, marker_substring: str) -> int:
    """
    Return ``line.index(marker_substring)`` -- the column AT WHICH the
    marker itself begins -- for the first line of ``layout_text``
    containing ``marker_substring``. Raises ``AssertionError`` (not a bare
    ``ValueError``/``StopIteration``) if the marker is not present, so a
    missing marker fails as a clear, structural pytest assertion rather
    than an uncaught exception.

    This is deliberately NOT ``len(line) - len(line.lstrip(" "))`` (the
    line's own leading whitespace), which is the pattern
    ``tests/test_rubric_indent_invariance.py`` uses for ITS marker. There,
    the marker is the first glyph on its own line, so the two quantities
    coincide. In a citation grid, the label cell occupies the same
    physical line AHEAD OF the sentinel on an entry's first line (e.g.
    ``[Krizhevsky2012] (1,2)      CITORDERALPHA ...``), so the line's
    leading whitespace is 0 (the label starts the line) while the marker
    itself starts at the grid's real body column. Every call site in this
    module means "the column at which this entry's body starts", which is
    what the marker's own start column measures, not the line's.
    """
    for line in layout_text.splitlines():
        if marker_substring in line:
            return line.index(marker_substring)
    raise AssertionError(
        f"{marker_substring!r} not found in the given page's layout text"
    )


def _line_after_marker(layout_text: str, marker_substring: str) -> str:
    """Return the line immediately following the first line of
    ``layout_text`` containing ``marker_substring`` -- the wrapped
    continuation line, for the hanging-indent alignment check."""
    lines = layout_text.splitlines()
    for i, line in enumerate(lines):
        if marker_substring in line:
            if i + 1 < len(lines):
                return lines[i + 1]
            raise AssertionError(
                f"{marker_substring!r} found on the LAST line of the "
                "page's layout text -- no continuation line follows"
            )
    raise AssertionError(
        f"{marker_substring!r} not found in the given page's layout text"
    )


def _find_page_and_column(
    pdf_bytes: bytes, marker_substring: str, start_page: int = 0
) -> tuple[int, int]:
    """
    Search pages ``start_page..`` onward for ``marker_substring`` and
    return ``(page_index, marker_column)`` for the first page it is found
    on. Page-index-agnostic by design: located by CONTENT, not a
    hard-coded page number.

    ``marker_column`` is ``_marker_column``'s measurement -- the column at
    which the marker substring itself begins, not the line's own leading
    whitespace. Every call site of this helper wants "the column at which
    this entry's body starts" (CIT-02/D-05's hanging-indent and
    widest-label-alignment claims), and on an entry's first line the
    marker sits past the label cell, so the marker's own start column is
    the correct quantity -- see ``_marker_column``'s docstring.
    """
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    for i in range(start_page, len(reader.pages)):
        layout_text = _layout_lines(pdf_bytes, i)
        if marker_substring in layout_text:
            return i, _marker_column(layout_text, marker_substring)
    raise AssertionError(
        f"{marker_substring!r} not found on any page from index "
        f"{start_page} onward (document has {len(reader.pages)} pages)"
    )


def _glyph_x_position(pdf_bytes: bytes, page_index: int, text_substring: str) -> float:
    """
    Return the ``cm[4]`` (content-matrix x) of the FIRST glyph run
    containing ``text_substring`` on the given page, via pypdf's per-glyph
    ``visitor_text`` callback.

    Verified this session (RESEARCH § Code Examples, a real
    ``typst.compile()`` + ``pypdf`` probe of a hand-written citation grid):
    ``cm[4]``/``cm[5]`` carry real, usable per-glyph positions for THIS
    construct, while ``tm[4]``/``tm[5]`` report ``0.0`` on every glyph --
    the opposite finding from ``38-RESEARCH.md``'s ``desc_content``/
    ``field_list`` probe (a DIFFERENT construct), which found ``tm``
    unusable and did not test ``cm``. This helper reads ``cm``, never
    ``tm``, for exactly that reason.
    """
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    page = reader.pages[page_index]
    positions: list[float] = []

    def _visitor(text, cm, tm, fontdict, fontsize):
        if text_substring in text:
            positions.append(cm[4])

    page.extract_text(visitor_text=_visitor)
    if not positions:
        raise AssertionError(
            f"{text_substring!r} not found via visitor_text on page " f"{page_index}"
        )
    return positions[0]


def _link_rect_x0_values(pdf_bytes: bytes, page_index: int) -> list[float]:
    """Return the left-edge (``/Rect`` x0) of every ``/Link`` annotation on
    the given page."""
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    page = reader.pages[page_index]
    annots = page.get("/Annots") or []
    values = []
    for annot in annots:
        obj = annot.get_object()
        if obj.get("/Subtype") == "/Link":
            rect = obj.get("/Rect")
            if rect:
                values.append(float(rect[0]))
    return values


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
            f"pre-fix (visit_reference's pre-existing refid/xref branches "
            f"are unchanged by this phase; D-14 only ADDS an own-ids "
            f"anchor on top of them); emitted link "
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
        # concat operator, with no operator left dangling. visit_reference's
        # pre-existing refid/xref branches are unchanged by this phase, but
        # D-14 ADDS an own-ids bracket-wrap anchor around the citing
        # reference here too (this citing site's citation has backrefs, so
        # the anchor is load-bearing, not incidental) -- this sub-check
        # tolerates that wrap rather than assuming the pre-fix shape.
        concat_region = _slice(index_typ, "terms(separator:", _NESTED_HEADING)
        expected_concat_target = _expected_namespace_label("index", "concat2000")

        # SC#5's concat protocol requires the term's leading text and the
        # citing reference to be '+'-joined with no operator left dangling
        # -- it does NOT require a bare `link(` immediately after the `+`.
        # D-14 wraps a citation-derived citing site as
        # `[#link(<...>, ...)#label("...")]`; that bracket-wrap satisfies
        # the concat protocol in substance (operands `+`-joined, no
        # operator left without a right operand), so this regex tolerates
        # an optional `[#` between the operator and `link(`.
        concat_operand_match = re.search(
            r'text\("Concat Term "\) \+ (?:\[#)?link\(<([^>]+)>', concat_region
        )
        assert concat_operand_match, (
            "Concat Protocol's term must '+'-join its leading text to the "
            "citing reference (tolerating D-14's bracket-wrap around a "
            f"bare link(...)):\n{concat_region}"
        )
        assert concat_operand_match.group(1) == expected_concat_target, (
            "SC#5/D-14: the concat operator's right operand must be the "
            f"citing reference targeting {expected_concat_target!r}, found "
            f"link target {concat_operand_match.group(1)!r} instead"
        )

        # No '+' concat operator anywhere in the region is left without a
        # right operand -- a broader dangling-operator guard than the
        # single Concat Term check above.
        for plus_match in re.finditer(r" \+ ", concat_region):
            right_operand = concat_region[plus_match.end() :].lstrip()
            assert right_operand and not right_operand.startswith((")", "}", ",")), (
                "SC#5: a '+' concat operator in the region has no right "
                f"operand (dangling operator) at position "
                f"{plus_match.start()}:\n{concat_region}"
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

        pdf_output = citation_gate_build.build_dir / "master.pdf"
        assert pdf_output.exists(), (
            "master.pdf was not produced -- typst.compile() aborted, most "
            f"likely on the classic citation compile fatal:\n"
            f"stderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"


@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the citation render "
    "gate's compiled-PDF structural half",
)
class TestCitationRenderGateCompiledPdf:
    """
    CIT-02 (``layout``), CIT-04/D-01/D-02/D-03/D-08 (``backref``), and
    CIT-06/SC#4 (``order``) -- compiled-PDF structural assertions, reusing
    ``citation_gate_build`` rather than compiling the fixture a second
    time. Every test here requires a real, non-empty ``index.pdf``, which
    does not exist pre-fix (``TypstPDFBuilder.finish()`` aborts on the
    classic CIT-01 compile fatal before ever writing a PDF) -- so every
    test below is RED on a missing artifact, never on an unhandled
    exception.
    """

    def test_layout_hanging_indent_and_widest_label_alignment(
        self, citation_gate_build
    ):
        """CIT-02 + D-05 + D-06."""
        pdf_output = citation_gate_build.build_dir / "master.pdf"
        assert pdf_output.exists(), (
            "master.pdf was not produced -- typst.compile() aborted "
            "pre-fix on the classic CIT-01 compile fatal:\n"
            f"stderr: {citation_gate_build.result.stderr}"
        )
        pdf_bytes = pdf_output.read_bytes()

        page_index, alpha_column = _find_page_and_column(pdf_bytes, "CITORDERALPHA")
        layout_text = _layout_lines(pdf_bytes, page_index)

        # The wrapped continuation line of Krizhevsky2012's (padded, multi-
        # line) entry body must align at the SAME column as its own start
        # -- the hanging indent CIT-02 asks for.
        continuation_line = _line_after_marker(layout_text, "CITORDERALPHA")
        continuation_column = len(continuation_line) - len(
            continuation_line.lstrip(" ")
        )
        assert continuation_column == alpha_column, (
            "CIT-02: the wrapped continuation line of Krizhevsky2012's "
            f"entry must align at the same column as its own start "
            f"({alpha_column}), got {continuation_column}: "
            f"{continuation_line!r}"
        )
        assert alpha_column > 0, (
            "CIT-02: the entry body must sit strictly PAST the label, not "
            f"under it (column {alpha_column} must be > 0)"
        )

        # D-05: all five References entries share ONE grid, so the widest
        # label (Krizhevsky2012's) governs every row's start column --
        # every sibling's body must start at the SAME column.
        for sentinel in (
            "CITORDERBRAVO",
            "CITORDERCHARLIE",
            "CITORDERDELTA",
            "CITORDERECHO",
        ):
            _, column = _find_page_and_column(
                pdf_bytes, sentinel, start_page=page_index
            )
            assert column == alpha_column, (
                f"D-05: {sentinel}'s body must start at the SAME column "
                f"as CITORDERALPHA's ({alpha_column}, the widest label's "
                f"column), got {column}"
            )

        # D-06 counterpart: the Run Break section's two entries are TWO
        # independently-aligned runs -- each column must be > 0, but they
        # are NOT required to match the References run's column (or each
        # other). This is expected behavior, not a bug (40-CONTEXT.md
        # D-06).
        _, break_one_column = _find_page_and_column(
            pdf_bytes, "CITBREAKONESENTINEL", start_page=page_index
        )
        _, break_two_column = _find_page_and_column(
            pdf_bytes, "CITBREAKTWOSENTINEL", start_page=page_index
        )
        assert break_one_column > 0, (
            "D-06: Break2021's body must sit strictly past its own label "
            f"(column {break_one_column} must be > 0)"
        )
        assert break_two_column > 0, (
            "D-06: Break2022's body must sit strictly past its own label "
            f"(column {break_two_column} must be > 0)"
        )

    def test_backref_markers_order_and_pdf_link_geometry(
        self, citation_gate_build, citation_gate_env
    ):
        """CIT-04 + D-01 + D-02 + D-03 + D-08."""
        index_typ = _strip_raw_literals(_require_typ(citation_gate_build, "index_typ"))
        env, builder = citation_gate_env

        refs_grid = _grid_span(index_typ, _REFERENCES_HEADING, _RUN_BREAK_HEADING)
        alpha_idx = refs_grid.index("CITORDERALPHA")
        bravo_idx = refs_grid.index("CITORDERBRAVO")

        # (1) Krizhevsky2012's label cell (everything from the grid's open
        # up to its own body sentinel -- its body text carries no link()
        # calls itself, so every link( match in this span belongs to the
        # label cell) must carry exactly TWO back-reference link calls
        # (2+ backrefs -> plain label + numbered markers, D-03), targeting
        # -- IN ORDER -- the citing sites' own D-14 anchors, extracted from
        # Sphinx's resolved doctree, never written as literals.
        # 48-03 (D-05): each marker is now an independently-guarded
        # `context { let __tsx_body = [#{[N]}]; if query(<L>).len() > 0 {
        # link(<L>, __tsx_body) } else { __tsx_body } }` expression, not a
        # bare `link(<L>, [N])` call -- match the WHOLE guarded marker so
        # the separator check below (between two full markers, not two
        # bare `link()` calls) still finds a bare comma with nothing else
        # between them.
        krizhevsky_label_cell = refs_grid[:alpha_idx]
        marker_pattern = re.compile(
            r"context \{ let __tsx_body = \[#\{\[\d+\]\}\]; "
            r"if query\(<([^>]+)>\)\.len\(\) > 0 \{ "
            r"link\(<[^>]+>, __tsx_body\) \} else \{ __tsx_body \} \}"
        )
        backref_matches = list(marker_pattern.finditer(krizhevsky_label_cell))
        backref_targets = [m.group(1) for m in backref_matches]
        assert len(backref_targets) == 2, (
            "D-03: Krizhevsky2012's label cell must carry exactly TWO "
            f"back-reference link calls (2+ backrefs), found "
            f"{len(backref_targets)}: {backref_targets}"
        )
        expected_krizhevsky_own_anchors = _citing_site_own_anchors(
            env, builder, "index", "Krizhevsky2012"
        )
        assert backref_targets == expected_krizhevsky_own_anchors, (
            "D-08/CIT-04: Krizhevsky2012's back-reference markers must "
            f"target, in order, the citing sites' own anchors "
            f"{expected_krizhevsky_own_anchors}; found {backref_targets}"
        )
        between_markers = krizhevsky_label_cell[
            backref_matches[0].end() : backref_matches[1].start()
        ]
        assert between_markers == ",", (
            "D-03: the back-reference marker separator must be a bare "
            f"comma with no space, found {between_markers!r}"
        )

        # (2) Solo1998's label cell (from Krizhevsky2012's own body
        # sentinel up to Solo1998's own body sentinel -- Krizhevsky2012's
        # body text carries no link() calls, so this span's only link(
        # matches belong to Solo1998's label cell) must carry exactly ONE
        # link call (the label ITSELF is the back-link for a single
        # citing site) and no 2+-backref marker-group opener.
        solo_region = refs_grid[alpha_idx:bravo_idx]
        solo_link_matches = re.findall(r"link\(<([^>]+)>", solo_region)
        assert len(solo_link_matches) == 1, (
            "D-03: Solo1998's label cell must carry exactly ONE link "
            f"call, found {len(solo_link_matches)}: {solo_link_matches}"
        )
        # A single-backref entry's label_expr never appends the 2+-backref
        # marker group: visit_citation only emits that group's opening
        # fragment, ``text(" (")``, when 2+ backrefs exist (verified this
        # session by reading typsphinx/translator.py). A naive
        # ``\(\d+\)`` scan of the raw .typ SOURCE is unsound here: it can
        # never match the REAL 2+-marker shape (each ordinal is emitted
        # inside a ``[1]``/``[2]`` content block passed to link(), never
        # adjacent to a literal '('), and this span still carries the
        # TAIL of Krizhevsky2012's own body prose (e.g. "Hinton, G. E.
        # (2012)"), which a bare digit-in-parens scan misreads as a
        # marker. Scanning for the marker group's own source fragment
        # avoids both the false negative and the false positive.
        assert 'text(" (")' not in solo_region, (
            "D-03: a single-backref entry must not emit the 2+-backref "
            f"marker-group opener (reserved for 2+ backrefs): "
            f"{solo_region!r}"
        )

        # (3) D-08: no back-reference marker anywhere in the References
        # grid may target a second: anchor -- backrefs are same-document
        # only, even though second.rst cites Krizhevsky2012.
        all_targets_in_grid = re.findall(r"link\(<([^>]+)>", refs_grid)
        second_targets = [t for t in all_targets_in_grid if t.startswith("second:")]
        assert not second_targets, (
            "D-08: no back-reference marker in index.typ's References "
            f"grid may target a second: anchor, found: {second_targets}"
        )

        # (4) Compiled-PDF half: on the page holding CITORDERALPHA, at
        # least one /Link annotation's left edge (x0) must lie to the
        # LEFT of CITORDERALPHA's own x position -- i.e. a real, clickable
        # back-reference marker living in the grid's LEFT column (D-02's
        # placement claim), not merely a string in the .typ source.
        pdf_output = citation_gate_build.build_dir / "master.pdf"
        assert pdf_output.exists(), (
            "master.pdf was not produced -- typst.compile() aborted "
            "pre-fix on the classic CIT-01 compile fatal:\n"
            f"stderr: {citation_gate_build.result.stderr}"
        )
        pdf_bytes = pdf_output.read_bytes()
        page_index, _ = _find_page_and_column(pdf_bytes, "CITORDERALPHA")

        alpha_x = _glyph_x_position(pdf_bytes, page_index, "CITORDERALPHA")
        if alpha_x == 0.0:
            # cm[4] came back zero for this construct on this build --
            # fall back to the layout-mode column rather than silently
            # weakening the assertion (explicitly instructed): the
            # relative LEFT-of comparison below still holds structurally
            # against the layout-mode column measurement.
            _, alpha_x = _find_page_and_column(pdf_bytes, "CITORDERALPHA")
            alpha_x = float(alpha_x)

        link_x0_values = _link_rect_x0_values(pdf_bytes, page_index)
        assert link_x0_values, (
            f"No /Link annotations found on page {page_index} -- CIT-04's "
            "back-reference markers are not real clickable links (pre-fix "
            "RED: no citation handler exists to emit them)."
        )
        assert any(x0 < alpha_x for x0 in link_x0_values), (
            "D-02: expected at least one /Link annotation whose left "
            f"edge (x0) lies to the LEFT of CITORDERALPHA's own x "
            f"position ({alpha_x}) -- i.e. a back-reference marker living "
            f"in the grid's left column. Link x0 values found: "
            f"{sorted(link_x0_values)}"
        )

    def test_order_references_sentinels_match_document_order(self, citation_gate_build):
        """
        CIT-06 + ROADMAP SC#4. Document order by construction: docutils'
        own depth-first traversal order IS document order, and the
        design contains no sort step to defeat it (40-RESEARCH.md § Don't
        Hand-Roll). Assert on the SENTINELS, never on label text, because
        a citation key's label text ALSO appears at its own citing site(s)
        earlier in the document.
        """
        pdf_output = citation_gate_build.build_dir / "master.pdf"
        assert pdf_output.exists(), (
            "master.pdf was not produced -- typst.compile() aborted "
            "pre-fix on the classic CIT-01 compile fatal:\n"
            f"stderr: {citation_gate_build.result.stderr}"
        )
        pdf_bytes = pdf_output.read_bytes()

        page_index, _ = _find_page_and_column(pdf_bytes, "CITORDERALPHA")
        layout_text = _layout_lines(pdf_bytes, page_index)

        sentinels = [
            "CITORDERALPHA",
            "CITORDERBRAVO",
            "CITORDERCHARLIE",
            "CITORDERDELTA",
            "CITORDERECHO",
        ]
        positions = []
        for sentinel in sentinels:
            idx = layout_text.find(sentinel)
            assert idx != -1, f"{sentinel} not found on the References page"
            positions.append(idx)

        assert positions == sorted(positions), (
            "CIT-06: the five References sentinels must appear in "
            "exactly document order (ALPHA<BRAVO<CHARLIE<DELTA<ECHO); "
            f"found byte offsets {dict(zip(sentinels, positions, strict=True))}"
        )
