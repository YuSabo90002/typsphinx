"""
Phase 40.1 (Citation Degradation Hardening) degradation gate: WR-01
(this plan). WR-02 / WR-03 land in plans ``40.1-02`` / ``40.1-03`` and are
NOT covered by this module's `test_wr01_*` functions -- see
``40.1-CONTEXT.md``'s D-03 warning-to-evidence-file mapping.

WR-01 is the milestone's reclaimed classic "does not compile" RED (per
``40.1-CONTEXT.md`` D-04): pre-fix, ``visit_citation``'s backref loop
(``typsphinx/translator.py:2856-2862``) treats "the citing
``nodes.reference`` could not be located in the resolved doctree" as
*eligible* rather than *skip*, because ``ref_node is not None and not ...``
short-circuits to ``False`` when ``_find_citing_reference`` returns
``None``. A citing site pruned by a real ``.. only:: never`` block is
exactly this topology (D-01's WR-01 attempt list, real ``sphinx-build``,
succeeded on the first attempt -- see ``40.1-GATE-EVIDENCE-01.md``): the
citation domain populates ``backrefs`` BEFORE the ``only``-tag filter prunes
the block's content, so a backref id can survive with no corresponding
``nodes.reference`` in the doctree the translator walks. Unfixed,
``visit_citation`` still appends a namespaced label for that unreachable
id, emitting ``link(<docname:id>, ...)`` to a Typst label nothing ever
attaches -- a whole-document compile fatal:
``typst.TypstError: label `<index:idN>` does not exist in the document``.

``test_wr01_typstpdf_build_compiles_and_emits_pdf`` is the classic
RED->GREEN flip (D-04): fails today with the fatal above, must pass
unmodified once the fix (Task 3) lands.

Every other ``test_wr01_*`` test is RED against the untouched translator
for STRUCTURAL reasons (a dangling ``link()`` target, a wrong marker
shape, a broken run) -- never a Python ``TypeError``/``KeyError``/fixture
error. No expected label or anchor token is ever written as a string
literal: every comparison is between a value extracted from emitted
``.typ`` output and one computed by calling
``typsphinx.translator.TypstTranslator._namespace_label`` directly (D-13's
single derivation point), or between two values both extracted from
Sphinx's OWN resolved doctree (``env.get_and_resolve_doctree``) -- never
guessed or transcribed (the "never a hard-coded label string" corollary,
``40.1-PATTERNS.md``).

Requirements: WR-01 (closes ``40-REVIEW.md``'s WARNING; ROADMAP SC#1).
See ``40.1-CONTEXT.md`` D-01 (RED provenance), D-02 (this module/fixture
are new and separate from Phase 40's frozen citation-render-gate pair),
D-03 (evidence file numbering), D-04 (classic-fatal RED form).
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


# ---------------------------------------------------------------------------
# Real-build half (WR-01 only -- the sole warning in this phase with a real
# sphinx-build fixture per D-01's constructibility findings). Shape copied
# from tests/test_citation_render_gate.py (FROZEN, D-02: imitate, never
# import or edit).
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def degradation_gate_dir():
    """Return the path to the citation_degradation_gate fixture."""
    return Path(__file__).parent / "fixtures" / "citation_degradation_gate"


def _run_sphinx_build_typstpdf(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typstpdf`` as a subprocess and return the completed
    process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``
    and never a bare ``sphinx-build``) -- the NixOS PATH-shadowing hazard
    restated in every render-gate module in this project (CLAUDE.md,
    tests/test_citation_render_gate.py:79-102).
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
class DegradationGateBuild:
    """One real ``-b typstpdf`` build of the WR-01 degradation-gate
    fixture, captured exactly once for the whole module."""

    result: subprocess.CompletedProcess
    build_dir: Path
    index_typ: str | None


@pytest.fixture(scope="module")
def degradation_gate_build(degradation_gate_dir, tmp_path_factory):
    """
    Run ``-b typstpdf`` over the WR-01 fixture EXACTLY ONCE for the whole
    module and return a small record carrying the ``CompletedProcess``, the
    build directory, and the text of ``index.typ`` when it exists.

    Deliberately does NOT assert on the return code: pre-fix the compile
    step is EXPECTED to fail (the classic WR-01 fatal), and an asserting
    fixture would turn every test in this module into a fixture ERROR
    instead of the readable RED this gate exists to record.
    ``write_doc`` still emits ``index.typ`` before the compile step that
    fails inside ``TypstPDFBuilder.finish()``, so it is available to every
    ``.typ``-string test in this module regardless of build outcome.
    """
    build_dir = tmp_path_factory.mktemp("degradation_gate") / "_build"
    result = _run_sphinx_build_typstpdf(degradation_gate_dir, build_dir)
    index_typ_path = build_dir / "index.typ"
    index_typ = (
        index_typ_path.read_text(encoding="utf-8") if index_typ_path.exists() else None
    )
    return DegradationGateBuild(
        result=result,
        build_dir=build_dir,
        index_typ=index_typ,
    )


def _require_typ(build: DegradationGateBuild) -> str:
    """Return ``build.index_typ``, raising a clear ``AssertionError``
    naming the missing artifact if it was never emitted -- rather than
    letting a caller hit a bare ``AttributeError``/``TypeError`` on
    ``None``."""
    if build.index_typ is None:
        raise AssertionError(
            "index.typ was never emitted by the build (missing artifact) -- "
            f"build returncode={build.result.returncode}\n"
            f"stdout: {build.result.stdout}\nstderr: {build.result.stderr}"
        )
    return build.index_typ


@pytest.fixture(scope="module")
def degradation_gate_env(degradation_gate_dir, tmp_path_factory):
    """
    Build the WR-01 fixture through a real, in-process ``SphinxTestApp``
    (``-b typst``, no compile -- works with or without ``typst-py``
    installed) and return its ``(env, builder)`` pair so tests can walk the
    RESOLVED doctree (``env.get_and_resolve_doctree``) and read the
    docutils-assigned ``ids``/``backrefs`` Sphinx's citation domain
    actually resolved -- never a hard-coded guess (mirrors
    ``tests/test_citation_render_gate.py``'s ``citation_gate_env``).

    Independent of ``degradation_gate_build`` above: that fixture proves
    what the TRANSLATOR emits (subprocess, ``-b typstpdf``); this one
    proves what SPHINX resolved before the translator ever ran (in-process,
    ``-b typst``, cheaper and importable without ``typst-py``).
    """
    from sphinx.testing.util import SphinxTestApp

    builddir = tmp_path_factory.mktemp("degradation_gate_env")
    app = SphinxTestApp(
        buildername="typst",
        srcdir=degradation_gate_dir.resolve(),
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
    instance state required. Mirrors
    ``tests/test_citation_render_gate.py``'s helper of the same name
    exactly (D-02: imitate, do not import).
    """
    return TypstTranslator._namespace_label(TypstTranslator, docname, raw_id)


_ATTACHED_ANCHOR_RE = re.compile(r"(?<!link\()<([A-Za-z0-9_.:-]+)>")
_ATTACHED_ANCHOR_CALL_RE = re.compile(r'#label\("([A-Za-z0-9_.:-]+)"\)')


def _attached_anchor_tokens(typ_text: str) -> set[str]:
    """
    Every attached anchor token in ``typ_text`` -- i.e. every label this
    translator ATTACHES to preceding content, never a link TARGET.

    Recognizes BOTH Typst anchor forms this translator emits (mirrors
    ``tests/test_citation_render_gate.py``'s helper of the same name,
    D-02: imitate, do not import): the markup-mode bracket-postfix
    shorthand ``[... <label>]`` (``visit_citation``'s own definition
    anchor), and the explicit function-call form ``#label("...")``
    (``visit_reference``'s D-14 own-anchor for a citing site with its own
    ``ids``). ``<name>`` is parser sugar for ``#label("name")`` -- Typst
    attaches both identically to the immediately preceding content.
    """
    bracket_form = set(_ATTACHED_ANCHOR_RE.findall(typ_text))
    call_form = set(_ATTACHED_ANCHOR_CALL_RE.findall(typ_text))
    return bracket_form | call_form


_LINK_TARGET_RE = re.compile(r"link\(<([A-Za-z0-9_.:-]+)>")


def _link_label_targets(typ_text: str) -> set[str]:
    """
    Every label token appearing as the FIRST argument of a ``link(<...>``
    call in ``typ_text`` -- i.e. every label token this translator
    LINKS TO, whether or not something actually attaches it.

    This is the WR-01 assertion vehicle the frozen module does not need:
    ``test_wr01_every_link_target_has_an_attached_anchor`` below computes
    ``_link_label_targets(typ) - _attached_anchor_tokens(typ)``, which is
    non-empty pre-fix (a ``link()`` targets a backref id whose citing site
    was pruned, so no anchor for it was ever attached) and empty post-fix.
    """
    return set(_LINK_TARGET_RE.findall(typ_text))


def _slice(typ_text: str, start_marker: str, end_marker: str | None) -> str:
    """
    Return the substring of ``typ_text`` from ``start_marker`` (inclusive)
    up to ``end_marker`` (exclusive), or to the end of the document if
    ``end_marker`` is ``None``. Mirrors
    ``tests/test_citation_render_gate.py``'s ``_slice`` helper exactly
    (D-02: imitate, do not import).
    """
    start_idx = typ_text.index(start_marker)
    if end_marker is None:
        return typ_text[start_idx:]
    end_idx = typ_text.index(end_marker, start_idx + len(start_marker))
    return typ_text[start_idx:end_idx]


def _live_reference_own_ids(doctree) -> set[str]:
    """Every own ``ids[0]`` of a ``nodes.reference`` surviving in the
    RESOLVED doctree -- i.e. every citing site the `only`-tag filter did
    NOT prune."""
    ids: set[str] = set()
    for ref in doctree.findall(docutils_nodes.reference):
        ref_ids = ref.get("ids") or []
        if ref_ids:
            ids.add(ref_ids[0])
    return ids


def _citation_row_region(typ_text: str, def_anchor_token: str) -> str:
    """
    Return the label-cell fragment (``[#{...} <def_anchor_token>]``) for
    the citation whose OWN definition anchor is ``def_anchor_token`` --
    computed by the caller via ``_expected_namespace_label``, never
    transcribed. Raises a clear ``AssertionError`` if the row cannot be
    found, rather than an uncaught ``ValueError``.

    Locates the row by finding ``def_anchor_token``'s own closing marker
    first and scanning BACKWARDS for its ``[#{`` opener -- a plain
    ``.*?`` regex search from the START of ``typ_text`` would instead
    match the NEAREST-following ``[#{`` opener, which for the second (or
    later) citation row is a DIFFERENT citation's opener, silently
    capturing bytes across a cell boundary that do not belong to this
    row.
    """
    anchor_marker = f"<{def_anchor_token}>]"
    anchor_idx = typ_text.find(anchor_marker)
    if anchor_idx == -1:
        raise AssertionError(
            f"No citation label cell found for def anchor "
            f"{def_anchor_token!r} in:\n{typ_text}"
        )
    row_start = typ_text.rfind("[#{", 0, anchor_idx)
    if row_start == -1:
        raise AssertionError(
            f"Found def anchor marker {anchor_marker!r} but no preceding "
            f"'[#{{' label-cell opener in:\n{typ_text}"
        )
    inner = typ_text[row_start + len("[#{") : anchor_idx]
    if inner.endswith("} "):
        inner = inner[:-2]
    elif inner.endswith("}"):
        inner = inner[:-1]
    return inner


class TestWr01DanglingLinkTargets:
    """The id-agnostic core assertion: every ``link()`` target anywhere in
    ``index.typ`` has a matching attached anchor somewhere in the same
    document. Pre-fix this is RED (the pruned citing sites' backref ids
    are still linked to); post-fix it is GREEN."""

    def test_wr01_every_link_target_has_an_attached_anchor(
        self, degradation_gate_build
    ):
        index_typ = _require_typ(degradation_gate_build)
        dangling = _link_label_targets(index_typ) - _attached_anchor_tokens(index_typ)
        assert dangling == set(), (
            "link() target(s) with no matching attached anchor anywhere in "
            f"the document (WR-01): {sorted(dangling)}\n\n{index_typ}"
        )


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the citation degradation gate's "
    "real-compile half",
)
class TestWr01RealCompile:
    """WR-01's classic D-04 RED->GREEN flip: the SAME test, over the SAME
    fixture, fails today and must pass -- unmodified -- once Task 3's fix
    lands (mirrors ``tests/test_citation_render_gate.py``'s
    ``TestCitationRenderGateRealCompile`` shape, D-02: imitate, do not
    import)."""

    def test_wr01_typstpdf_build_compiles_and_emits_pdf(self, degradation_gate_build):
        result = degradation_gate_build.result
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed (WR-01 classic RED):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        combined = result.stdout + result.stderr
        assert "does not exist in the document" not in combined, (
            "typst.compile() rejected a link() targeting a label nothing "
            f"ever attaches -- the WR-01 fix is not in effect:\n{combined}"
        )

        pdf_output = degradation_gate_build.build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted, most "
            f"likely on the WR-01 dangling-link() compile fatal:\n"
            f"stderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"


class TestWr01MarkerShapes:
    """G1's obligation: the marker SHAPE of every degraded citation is
    asserted, not left to chance. Covers all three D-03 transitions this
    fixture exercises (3->2 renumbered, 2->1, 1->0). Ids/backrefs are read
    from Sphinx's own resolved doctree, never hard-coded (D-13
    corollary)."""

    def test_wr01_degraded_citation_marker_shapes(
        self, degradation_gate_build, degradation_gate_env
    ):
        index_typ = _require_typ(degradation_gate_build)
        env, builder = degradation_gate_env
        docname = "index"
        doctree = env.get_and_resolve_doctree(docname, builder, tags=builder.tags)
        live_ids = _live_reference_own_ids(doctree)
        citations = list(doctree.findall(docutils_nodes.citation))
        assert len(citations) == 3, (
            f"expected 3 citation definitions in the fixture, found "
            f"{len(citations)}: {[c.get('ids') for c in citations]}"
        )

        two_or_more_count = 0
        single_count = 0
        zero_count = 0

        for citation in citations:
            cit_ids = citation.get("ids") or []
            assert cit_ids, f"citation node has no ids: {citation}"
            def_anchor = _expected_namespace_label(docname, cit_ids[0])
            backrefs = citation.get("backrefs") or []
            live_backrefs = [b for b in backrefs if b in live_ids]
            expected_targets = [
                _expected_namespace_label(docname, raw_id) for raw_id in live_backrefs
            ]

            row = _citation_row_region(index_typ, def_anchor)

            if len(expected_targets) >= 2:
                two_or_more_count += 1
                assert 'text(" (")' in row, (
                    f"citation {cit_ids[0]!r} has {len(expected_targets)} "
                    f"live backrefs but its row carries no parenthesised "
                    f"marker group:\n{row}"
                )
                markers = re.findall(r"link\(<([^>]+)>, \[(\d+)\]\)", row)
                marker_targets = [m[0] for m in markers]
                marker_ordinals = [m[1] for m in markers]
                assert marker_targets == expected_targets, (
                    f"citation {cit_ids[0]!r}: marker targets "
                    f"{marker_targets} != expected {expected_targets} "
                    f"(live backrefs, in order):\n{row}"
                )
                assert marker_ordinals == [
                    str(i) for i in range(1, len(expected_targets) + 1)
                ], (
                    f"citation {cit_ids[0]!r}: marker ordinals "
                    f"{marker_ordinals} are not contiguous from 1 (a "
                    f"dropped backref must renumber, never leave a gap "
                    f"like [3] with only 2 live markers):\n{row}"
                )
            elif len(expected_targets) == 1:
                single_count += 1
                assert 'text(" (")' not in row, (
                    f"citation {cit_ids[0]!r} has exactly 1 live backref "
                    f"but its row still carries a parenthesised marker "
                    f"group (should be the single-backref linked-label "
                    f"shape instead):\n{row}"
                )
                single_matches = re.findall(r"link\(<([^>]+)>, ", row)
                assert single_matches == expected_targets, (
                    f"citation {cit_ids[0]!r}: single-backref link "
                    f"target(s) {single_matches} != expected "
                    f"{expected_targets}:\n{row}"
                )
            else:
                zero_count += 1
                assert "link(" not in row, (
                    f"citation {cit_ids[0]!r} has zero live backrefs but "
                    f"its row still carries a link() call -- should be a "
                    f"plain, non-linked label (Phase 40 D-07):\n{row}"
                )

        assert two_or_more_count == 1, (
            f"expected exactly 1 citation with the two-or-more marker "
            f"shape, found {two_or_more_count}"
        )
        assert single_count == 1, (
            f"expected exactly 1 citation with the single-backref linked-"
            f"label shape, found {single_count}"
        )
        assert zero_count == 1, (
            f"expected exactly 1 citation with the plain non-linked "
            f"label shape, found {zero_count}"
        )


class TestWr01RunAdjacency:
    """Phase 40 D-05 is not re-opened by the WR-01 filter: the three
    adjacent citation definitions still render as ONE grid."""

    def test_wr01_run_still_renders_as_one_grid(self, degradation_gate_build):
        index_typ = _require_typ(degradation_gate_build)
        region = _slice(index_typ, "Reference list follows.", "End of citation block.")
        grid_count = region.count("grid(")
        assert grid_count == 1, (
            f"expected exactly one grid( call across the three adjacent "
            f"citation definitions (D-05 run rule), found "
            f"{grid_count}:\n{region}"
        )


class TestWr01SilentDegradation:
    """G1: a back-reference dropped by the WR-01 filter emits no Sphinx
    warning."""

    def test_wr01_dropped_backref_is_silent(self, degradation_gate_build):
        combined = (
            degradation_gate_build.result.stdout + degradation_gate_build.result.stderr
        ).lower()
        forbidden_phrases = [
            "skipped back-reference",
            "skipped backreference",
            "dropped back-reference",
            "dropped backreference",
            "backref dropped",
            "backreference dropped",
            "citing reference not found",
            "citing site not found",
            "unresolved back-reference",
            "unresolved backreference",
        ]
        offending = [p for p in forbidden_phrases if p in combined]
        assert not offending, (
            "G1 requires a dropped back-reference to degrade silently; "
            f"found forbidden phrase(s) {offending} in the build's combined "
            f"output:\n{combined}"
        )
