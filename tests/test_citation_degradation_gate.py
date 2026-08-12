"""
Phase 40.1 (Citation Degradation Hardening) degradation gate: WR-01
(plan ``40.1-01``), WR-02 (plan ``40.1-02``), and WR-03 (this plan) --
see ``40.1-CONTEXT.md``'s D-03 warning-to-evidence-file mapping.

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

WR-02 (this plan) is a SILENT structural misalignment, not a compile fatal
(D-04): ``_citation_run_neighbour`` (``typsphinx/translator.py:2644-2683``)
skips only ``nodes.comment``/``nodes.system_message`` when scanning for the
next emitting sibling of a citation, but an ids-less ``nodes.target`` also
emits zero bytes into the body (``visit_target``'s "ids falsy" branch) and
is not on that skip list -- so it is treated as a real, run-breaking
sibling, silently splitting one intended reference list into TWO
independently-aligned ``grid(columns: (auto, 1fr))`` calls instead of one.
Per D-01, every plausible RST shape for the minimal single-blocker topology
was attempted this session and none reproduces it (docutils' target-chaining
transform never leaves a solitary ids-less target -- see
``40.1-GATE-EVIDENCE-02.md`` § "D-01 attempt list" for the full five-attempt
enumeration), so WR-02's RED falls back to a directly-assembled doctree,
bypassing the RST parser and Sphinx's build pipeline entirely. Because the
misaligned output still compiles cleanly, WR-02's RED is a STRUCTURAL
assertion on the emitted body -- ``body.count("grid(") == 1`` -- rather than
a ``typst.compile()`` failure.

``test_wr02_idsless_target_between_citations_keeps_one_grid`` is the
structural RED->GREEN flip: ``grid(`` appears twice pre-fix, once post-fix.
``test_wr02_target_with_ids_still_breaks_the_run`` and
``test_wr02_comment_between_citations_keeps_one_grid`` are negative
controls, GREEN both before and after the fix, bounding the fix to exactly
the ids-less-target case (G2, ``40.1-CONTEXT.md``/``40.1-02-PLAN.md``).

WR-03 (plan ``40.1-03``) closed ``40-REVIEW.md``'s WARNING that the D-14
citing-site anchor eligibility judgement was written independently in TWO
places that could silently disagree: ``visit_reference``
(``typsphinx/translator.py``, three conditions -- ``node.get("ids")``,
``opens_wrapper``, ``not next_is_target``) and
``_citing_reference_has_own_anchor`` (re-derived the same answer from the
``next_is_target`` half alone, assuming the other two). D-08 measured both
of the assumption's condition-breaking routes against a REAL build that
session and found NEITHER constructible (``40.1-GATE-EVIDENCE-03.md`` §2):
Route A (``ids`` empty) was unreachable through
``_citing_reference_has_own_anchor``'s only real caller, a control-flow
fact independent of Sphinx version (Pitfall 4); Route B (``opens_wrapper``
forced false by a build-time cross-document exclusion decision, since
deleted -- Phase 48, D-09) was unreachable because a node reachable
through ``_find_citing_reference`` never carries a ``refuri``. WR-03's
original RED therefore hand-assembled a doctree via
``_make_citing_reference`` that violated BOTH of those real-build
invariants at once -- a citing ``nodes.reference`` carrying a populated
own ``ids`` AND a ``refuri`` resolving to a document the build-time
mechanism excluded -- which forced ``opens_wrapper`` to ``False`` in
``visit_reference`` (no anchor ever emitted) while pre-fix
``_citing_reference_has_own_anchor`` still reported "anchor exists" (it
only checked ``next_is_target``, which was ``False`` there), so
``visit_citation``'s backref loop appended a ``link()`` to a label
nothing ever attached -- D-04's classic ``typst.compile()`` fatal,
reproduced on hand-built input rather than a real ``sphinx-build``. Phase
48, D-09 subsequently made ``opens_wrapper`` unconditional, closing Route
B's premise entirely -- the same topology is now ALWAYS eligible; see
``TestWr03DegradedCitingSiteAnchor`` below for the post-D-09 behaviour.

Requirements: WR-01 (closes ``40-REVIEW.md``'s WARNING; ROADMAP SC#1),
WR-02 (closes ``40-REVIEW.md``'s WARNING; ROADMAP SC#2), WR-03 (closes
``40-REVIEW.md``'s WARNING; ROADMAP SC#3).
See ``40.1-CONTEXT.md`` D-01 (RED provenance), D-02 (this module/fixture
are new and separate from Phase 40's frozen citation-render-gate pair),
D-03 (evidence file numbering), D-04 (classic-fatal RED form for WR-01/
WR-03, structural RED form for WR-02), D-05/D-06/D-07 (WR-03's shared D-14
predicate), D-08 (WR-03's RED provenance, both routes attempted and
unreachable).
"""

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from unittest import mock

import pytest
from docutils import nodes as docutils_nodes
from docutils.parsers.rst import states
from docutils.utils import Reporter

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

        # Phase 47 (R4): the PDF is the WRAPPER's own output ("master.pdf",
        # this fixture's typst_documents target after de-collision).
        pdf_output = degradation_gate_build.build_dir / "master.pdf"
        assert pdf_output.exists(), (
            "master.pdf was not produced -- typst.compile() aborted, most "
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


# ---------------------------------------------------------------------------
# Assembled-doctree half (WR-02 from plan 40.1-02, extended by WR-03 in this
# plan). Built once, generally, here -- shape mirrors tests/conftest.py's
# `sample_doctree`/`mock_builder` fixtures (D-02: the established repo
# idiom, not reinvented) plus the extra StubBuilder attributes the
# D-06/D-08 xref-resolution routes need, which mock_builder lacks. No RST
# is parsed for either warning (40.1-RESEARCH.md: docutils' target-chaining
# transform never produces WR-02's minimal single-blocker topology via a
# real sphinx-build, and NEITHER of WR-03's two D-08 routes is
# constructible via a real build either -- see 40.1-GATE-EVIDENCE-02.md's
# and 40.1-GATE-EVIDENCE-03.md's D-01 attempt lists), so this harness
# bypasses the parser and Sphinx's build pipeline entirely and builds the
# doctree directly via the docutils node API.
# ---------------------------------------------------------------------------


class _MockConfig:
    """Minimal stand-in config object -- ``TypstTranslator`` reads
    ``builder.config`` in a few places but neither WR-02 nor WR-03's
    topologies exercise any config-dependent branch."""


class _MockDomains:
    """Minimal stand-in for ``env.domains`` -- unused by WR-02/WR-03's
    topologies but required for attribute access to succeed without
    raising."""


class _MockEnv:
    domains = _MockDomains()


class _StubBuilder:
    """
    A locally-scoped stub builder for the assembled-doctree harness, NOT
    imported from ``tests/conftest.py``'s ``mock_builder`` and NOT from the
    frozen ``tests/test_citation_render_gate.py`` module (D-02).

    Shaped on ``conftest.py``'s ``mock_builder`` (nested ``MockConfig``/
    ``MockDomains``/``MockEnv``) plus three extra attributes that fixture's
    ``mock_builder`` lacks and the D-06/D-08 xref-resolution routes need:
    ``out_suffix``, ``current_docname``, and ``get_target_uri``. WR-02's own
    topology needs none of these three -- they exist here because this
    harness is shared with (and extended by) plan ``40.1-03``, which does
    need them, and building the harness once, generally, avoids a second
    near-duplicate stub later. (Phase 48, D-09: this stub used to also carry
    the all-masters include-set attribute that seeded the now-deleted
    build-time degrade route -- removed along with that route; whether a
    cross-document target is reachable is decided at Typst compile time
    now, never by builder state.)
    """

    config = _MockConfig()
    env = _MockEnv()
    out_suffix = ".typ"
    current_docname = "index"

    def get_target_uri(self, docname: str, typ: str | None = None) -> str:
        return docname + self.out_suffix


def _make_document() -> docutils_nodes.document:
    """
    Build a minimal ``nodes.document`` the same way
    ``tests/conftest.py``'s ``sample_doctree`` fixture does: a real
    ``Reporter``, ``doc.settings`` as a docutils ``states.Struct()`` with
    just the attributes ``TypstTranslator``'s constructor and visitor chain
    touch. No RST parser and no Sphinx application are involved.
    """
    reporter = Reporter("", 2, 4)
    doc = docutils_nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    doc.settings.env = None
    doc.settings.language_code = "en"
    doc.settings.strict_visitor = False
    return doc


def _make_citation(
    key: str, text: str, *, backrefs: list[str] | None = None
) -> docutils_nodes.citation:
    """
    Build a ``nodes.citation`` with ``ids=[key]``, ``docname="index"``, an
    empty ``backrefs`` list by default (overridable -- WR-03 needs a
    non-empty one), a ``nodes.label`` child carrying ``key`` as its text,
    and a ``nodes.paragraph`` body child carrying ``text``. Mirrors Pattern
    3's ``make_citation`` helper verified in ``40.1-RESEARCH.md``.
    """
    cit = docutils_nodes.citation()
    cit["ids"] = [key]
    cit["docname"] = "index"
    cit["backrefs"] = list(backrefs) if backrefs is not None else []
    label = docutils_nodes.label()
    label += docutils_nodes.Text(key)
    cit += label
    body = docutils_nodes.paragraph()
    body += docutils_nodes.Text(text)
    cit += body
    return cit


def _make_citing_reference(
    *,
    refuri: str | None = None,
    refid: str | None = None,
    ids: tuple[str, ...] = (),
    text: str = "",
) -> docutils_nodes.reference:
    """
    Build a ``nodes.reference`` with ``refuri``/``refid``/``ids`` written
    directly onto the node's attribute dict via the docutils node API --
    never parsed from RST. Added by plan ``40.1-03`` for WR-03's Route B.

    The shape this helper must be able to produce is one a REAL
    ``sphinx-build`` never emits: a node carrying BOTH a populated own
    ``ids`` AND a ``refuri`` pointing at a document the (now-deleted,
    Phase 48 D-09) build-time union excluded. This deliberately violated a
    real-build invariant -- recorded here rather than left implicit -- per
    two facts independently reproduced that session (``40.1-RESEARCH.md``
    "WR-03 -- the two eligibility routes", carried into
    ``40.1-GATE-EVIDENCE-03.md`` §2's D-08 attempt list):

    1. A same-document citing reference (the only kind that ever appears
       in a citation's ``backrefs`` list, since ``_find_citing_reference``
       matches on a node's own ``ids``) always carries ``refid`` and never
       ``refuri`` -- Sphinx's citation domain resolves same-document
       citing sites via ``refid`` and cross-document ones via ``refuri``,
       mutually exclusively on one node.
    2. ``backrefs`` never contains a cross-document citing site's id -- a
       cross-document citing reference's own id is never appended to the
       target citation's ``backrefs`` list, only a same-document one's is.

    Reachable through ``_find_citing_reference`` requires (1) to be false
    (a ``refuri`` present) and (2) to be false (the id present in
    ``backrefs``) simultaneously -- a combination no real
    ``sphinx-build``/docutils transform chain ever produces, hence this
    helper writes both attributes directly rather than parsing RST.
    """
    attrs: dict[str, str] = {}
    if refuri is not None:
        attrs["refuri"] = refuri
    if refid is not None:
        attrs["refid"] = refid
    ref = docutils_nodes.reference("", "", **attrs)
    ref["ids"] = list(ids)
    if text:
        ref += docutils_nodes.Text(text)
    return ref


def _render_with_translator(
    doc: docutils_nodes.document,
) -> tuple[str, TypstTranslator]:
    """
    Instantiate a ``TypstTranslator`` over ``doc`` with a fresh
    ``_StubBuilder``, walk the tree, and return BOTH the joined emitted
    body (``translator.astext()``) AND the translator instance itself.
    Added by plan ``40.1-03`` so the WR-03 invariant backstop tests can
    call ``translator._reference_anchor_decision(ref)`` directly against
    the SAME translator/builder state the render used, rather than
    constructing a second translator that could silently diverge from the
    one that actually emitted ``body``.
    """
    translator = TypstTranslator(doc, _StubBuilder())
    doc.walkabout(translator)
    return translator.astext(), translator


def _render_body(doc: docutils_nodes.document) -> str:
    """
    Instantiate a ``TypstTranslator`` over ``doc`` with a fresh
    ``_StubBuilder``, walk the tree, and return the joined emitted body
    (``translator.astext()``). The single entry point every WR-02/WR-03
    assembled-doctree test uses to go from a hand-built tree to emitted
    Typst markup. Delegates to ``_render_with_translator`` (plan
    ``40.1-03``), discarding the translator instance for callers that
    only need the body.
    """
    body, _translator = _render_with_translator(doc)
    return body


def _compile_body(body: str, tmp_path: Path) -> None:
    """
    Wrap ``body`` exactly the way ``TypstWriter.translate()`` wraps a
    non-master document's body (``typsphinx/writer.py:138-141``): prepend
    ``"#{\\n"`` unless already present, append ``"}\\n"`` unless already
    present. Write the wrapped body to a ``.typ`` file under ``tmp_path``
    and compile it via ``typst.compile()``. No template and no
    ``@preview`` imports are needed here -- citation output uses no
    package function.

    Not exercised by any ``test_wr02_*`` test (WR-02 compiles cleanly by
    construction, D-04 -- its RED is the structural ``grid(`` count
    instead); written here because it belongs to the shared harness, and
    plan ``40.1-03`` uses it for WR-03's classic compile-fatal RED/GREEN.
    Callers must guard on ``TYPST_AVAILABLE`` themselves.
    """
    if not body.startswith("#{"):
        body = "#{\n" + body
    if not body.endswith("}\n"):
        body = body + "}\n"
    typ_path = tmp_path / "probe.typ"
    typ_path.write_text(body, encoding="utf-8")
    import typst

    typst.compile(str(typ_path))


class TestWr02RunNeighbourSkipList:
    """
    WR-02: ``_citation_run_neighbour``'s inert-sibling skip list must treat
    an ids-less ``nodes.target`` the same as ``nodes.comment``/
    ``nodes.system_message`` -- it emits zero bytes into the body
    (``visit_target``'s "ids falsy" branch) and must not break a run of
    citation definitions into two independently-aligned grids.
    """

    def test_wr02_idsless_target_between_citations_keeps_one_grid(self):
        """
        The structural RED/GREEN. A ``nodes.section`` containing, in
        order: citation ``a2020``, a bare ``nodes.target()`` with
        ``ids=[]``, citation ``b2020``. RESEARCH verified this emits
        ``grid(`` twice against the unfixed helper (Pattern 3,
        ``40.1-RESEARCH.md``) -- that is the RED; the fix must make it 1.
        """
        doc = _make_document()
        section = docutils_nodes.section()
        section += _make_citation("a2020", "First entry.")
        tgt = docutils_nodes.target()
        tgt["ids"] = []
        section += tgt
        section += _make_citation("b2020", "Second entry.")
        doc += section

        body = _render_body(doc)
        grid_count = body.count("grid(")
        assert grid_count == 1, (
            "expected exactly one grid( call across the citation run "
            "separated only by an ids-less nodes.target (WR-02, D-05 run "
            f"rule) -- found {grid_count}:\n{body}"
        )

    def test_wr02_target_with_ids_still_breaks_the_run(self):
        """
        Negative control bounding the fix: identical topology, except the
        intervening target carries ``ids=["some-target"]``. A target that
        really does emit an anchor (``visit_target``'s "ids falsy" branch
        is not taken) is still a real, run-breaking sibling -- this must
        stay GREEN (``grid(`` count of 2) both before and after the fix,
        proving the skip list widened by exactly one measured case and no
        further (G2, ``40.1-CONTEXT.md``/``40.1-02-PLAN.md``).
        """
        doc = _make_document()
        section = docutils_nodes.section()
        section += _make_citation("a2020", "First entry.")
        tgt = docutils_nodes.target()
        tgt["ids"] = ["some-target"]
        section += tgt
        section += _make_citation("b2020", "Second entry.")
        doc += section

        body = _render_body(doc)
        grid_count = body.count("grid(")
        assert grid_count == 2, (
            "an ids-carrying nodes.target really does emit an anchor and "
            "must still break the citation run into two independent "
            f"grid( calls -- found {grid_count}:\n{body}"
        )

    def test_wr02_comment_between_citations_keeps_one_grid(self):
        """
        Regression guard for the skip-list behaviour Phase 40 D-06 already
        established: a ``nodes.comment`` between two citation definitions
        must not break the run either. Green both before and after this
        plan's fix -- the shape the new disjunct must not disturb.
        """
        doc = _make_document()
        section = docutils_nodes.section()
        section += _make_citation("a2020", "First entry.")
        comment = docutils_nodes.comment()
        comment += docutils_nodes.Text("a comment between citations")
        section += comment
        section += _make_citation("b2020", "Second entry.")
        doc += section

        body = _render_body(doc)
        grid_count = body.count("grid(")
        assert grid_count == 1, (
            "a nodes.comment between two citation definitions must not "
            f"break the run (Phase 40 D-06) -- found {grid_count} grid( "
            f"calls:\n{body}"
        )


class TestWr03DegradedCitingSiteAnchor:
    """
    Phase 40.1's WR-03 Route B topology, re-scoped post-Phase-48 (D-09):
    a citing ``nodes.reference`` whose ``refuri`` resolves to a
    cross-document target used to force ``opens_wrapper`` to ``False`` via
    a build-time exclusion decision that has since been deleted. Under
    D-09, ``opens_wrapper`` is ``bool(refuri or refid)`` unconditionally,
    so this exact topology is now ALWAYS eligible for its own D-14 anchor
    -- the citing site's cross-document ``link()`` now routes through the
    D-07 compile-time guard (``48-02-PLAN.md``) instead of taking a
    build-time degrade branch, and its own same-document anchor
    (``index:id1``) is attached regardless of whether the cross-document
    target is reachable in any particular compile.

    This class's CORE invariant -- every ``link()`` target anywhere in
    the emitted body has a matching attached anchor somewhere in the same
    document -- is unchanged from Phase 40.1 and is exactly what this
    phase must preserve; it is now satisfied through the ELIGIBLE path
    instead of the historical degrade path. The topology itself, and the
    two real-build invariants it deliberately violates to become
    constructible, are unchanged from Phase 40.1 -- see
    ``_make_citing_reference``'s own docstring and
    ``40.1-GATE-EVIDENCE-03.md`` §2/§4 for that history.
    """

    def _build_degraded_doctree(self) -> docutils_nodes.document:
        """
        A ``nodes.section`` containing, in order: a ``nodes.paragraph``
        wrapping a citing reference with
        ``refuri="second.typ#krizhevsky2012"``, ``ids=["id1"]`` and a
        ``[Krizhevsky2012]`` ``Text`` child; then a ``nodes.citation`` with
        ``ids=["krizhevsky2012"]``, ``docname="index"``,
        ``backrefs=["id1"]``. Rendered with ``_StubBuilder`` (Pattern 4,
        ``40.1-RESEARCH.md``). The method name is kept from Phase 40.1 for
        continuity even though, post-D-09, the citing site's own anchor no
        longer degrades -- only the cross-document ``link()`` it opens is
        now guarded at Typst compile time.
        """
        doc = _make_document()
        section = docutils_nodes.section()
        para = docutils_nodes.paragraph()
        ref = _make_citing_reference(
            refuri="second.typ#krizhevsky2012",
            ids=("id1",),
            text="[Krizhevsky2012]",
        )
        para += ref
        section += para
        cit = _make_citation(
            "krizhevsky2012", "Krizhevsky, A. et al.", backrefs=["id1"]
        )
        section += cit
        doc += section
        return doc

    def test_wr03_degraded_citing_site_emits_no_dangling_backref(self):
        """
        The core id-agnostic WR-03 assertion, mirroring WR-01's own
        (``TestWr01DanglingLinkTargets``): every ``link()`` target
        anywhere in the emitted body must have a matching attached anchor
        somewhere in the same document. Phase 40.1 satisfied this
        trivially (the body contained ZERO ``link()`` calls at all, since
        the citing reference degraded to plain text and the ineligible
        backref appended no marker). Post-Phase-48 (D-09) this is
        satisfied NON-trivially: the body carries the D-07 guarded
        cross-document expression PLUS a real ``link(<index:id1>, ...)``
        in the citation definition's grid row, targeting the citing
        site's own now-attached anchor (``index:id1``) -- a real link with
        a real matching anchor.
        """
        doc = self._build_degraded_doctree()
        body = _render_body(doc)
        dangling = _link_label_targets(body) - _attached_anchor_tokens(body)
        assert dangling == set(), (
            "link() target(s) with no matching attached anchor anywhere in "
            f"the document (WR-03): {sorted(dangling)}\n\n{body}"
        )

    @pytest.mark.skipif(
        not TYPST_AVAILABLE,
        reason="typst-py is required for WR-03's real-compile half",
    )
    def test_wr03_degraded_citing_site_body_compiles(self, tmp_path):
        """
        Unchanged truth value across Phase 40.1 and Phase 48, via
        different mechanisms: pre-Phase-40.1, this fataled with
        ``typst.TypstError: label `<index:id1>` does not exist in the
        document`` (verbatim, captured in ``40.1-GATE-EVIDENCE-03.md``
        §4). Phase 40.1's fix made this compile because there were no
        links to dangle; post-Phase-48 (D-09) it compiles because the D-07
        guard prevents any fatal AND the citing site's own anchor is
        correctly attached -- never a ``TypstError`` either way.
        """
        doc = self._build_degraded_doctree()
        body = _render_body(doc)
        _compile_body(body, tmp_path)

    def test_wr03_degraded_citation_renders_plain_label_shape(self):
        """
        FLIPS post-Phase-48 (D-09, ``48-EXPECTED-STRUCTURE.md``): under
        D-09 the citing site's backref is no longer filtered as
        ineligible (``decision.eligible`` is ``True``), so the citation
        definition's grid row now carries a real ``link(`` call targeting
        the citing site's own attached anchor (``index:id1``) rather than
        a plain, non-linked bracketed label.
        """
        doc = self._build_degraded_doctree()
        body = _render_body(doc)
        def_anchor = _expected_namespace_label("index", "krizhevsky2012")
        citing_anchor = _expected_namespace_label("index", "id1")
        row = _citation_row_region(body, def_anchor)
        assert "link(" in row, (
            "citation 'krizhevsky2012' has one LIVE backref (its citing "
            "site is eligible for its own anchor under D-09) but its row "
            f"carries no link() call -- expected a real, linked label "
            f"(Phase 48, D-09):\n{row}"
        )
        assert f"<{citing_anchor}>" in row, (
            f"citation 'krizhevsky2012' row's link() does not target the "
            f"citing site's own anchor {citing_anchor!r}:\n{row}"
        )
        assert f"<{def_anchor}>" in body, (
            f"citation 'krizhevsky2012' own definition anchor "
            f"{def_anchor!r} is missing from the emitted body:\n{body}"
        )


# ---------------------------------------------------------------------------
# WR-03 invariant backstops (Task 2, added WITH the fix -- these tests
# CANNOT exist before `_reference_anchor_decision` does, so they are not
# and cannot be the RED; the RED is TestWr03DegradedCitingSiteAnchor above,
# recorded pre-fix in 40.1-GATE-EVIDENCE-03.md). Per 40.1-CONTEXT.md's
# assumption-delta decision, these are a COMPANION to the refactor, not a
# substitute for it -- they exist to make a FUTURE re-introduction of a
# second, disagreeing derivation site fail loudly, not to stand in for
# doing the refactor itself.
# ---------------------------------------------------------------------------


def _wr03_case_refid_no_following_target():
    """Case (i): ``refid`` set, ``ids`` populated, no following target --
    the ONLY case expected to be eligible."""
    doc = _make_document()
    section = docutils_nodes.section()
    para = docutils_nodes.paragraph()
    ref = _make_citing_reference(refid="target-a", ids=("citer-a",), text="[A]")
    para += ref
    section += para
    doc += section
    return doc, ref


def _wr03_case_refid_followed_by_target():
    """Case (ii): ``refid`` set, ``ids`` populated, followed by a
    ``nodes.target`` that carries its OWN ``ids`` -- ``next_is_target`` is
    ``True``, so NOT eligible (the target's own label wins instead)."""
    doc = _make_document()
    section = docutils_nodes.section()
    para = docutils_nodes.paragraph()
    ref = _make_citing_reference(refid="target-b", ids=("citer-b",), text="[B]")
    para += ref
    tgt = docutils_nodes.target()
    tgt["ids"] = ["real-target-b"]
    para += tgt
    section += para
    doc += section
    return doc, ref


def _wr03_case_refuri_excluded_document():
    """Case (iii), historical NAME kept for continuity with WR-03's own
    RED topology (Route B, minus the pre-existing citation/backrefs
    half): ``refuri`` resolving to a cross-document target, ``ids``
    populated. Pre-Phase-48, a build-time exclusion decision (since
    deleted) forced ``opens_wrapper`` to ``False`` here, so this case was
    NOT eligible. Phase 48, D-09 makes ``opens_wrapper`` UNCONDITIONAL --
    whether the cross-document target is reachable in any particular
    compile is now a question the D-07 guard answers, never a reason to
    withhold the citing site's OWN same-document anchor -- so this case
    IS now eligible: same reasoning as the always-eligible case (i)
    above, this time via ``refuri`` (present) rather than ``refid``.
    Suppressing a same-document anchor because an unrelated
    cross-document target happened to be unavailable was, in hindsight, a
    category error the two questions had been conflating."""
    doc = _make_document()
    section = docutils_nodes.section()
    para = docutils_nodes.paragraph()
    ref = _make_citing_reference(
        refuri="second.typ#anchor-c", ids=("citer-c",), text="[C]"
    )
    para += ref
    section += para
    doc += section
    return doc, ref


def _wr03_case_refid_empty_ids():
    """Case (iv): ``refid`` set, ``ids`` EMPTY -- Route A's own shape
    (Pitfall 4). Not eligible; the invariant test covers it as defensive
    code, not as a demonstrated bug (no RED is built on this route,
    ``40.1-GATE-EVIDENCE-03.md`` §2)."""
    doc = _make_document()
    section = docutils_nodes.section()
    para = docutils_nodes.paragraph()
    ref = _make_citing_reference(refid="target-d", ids=(), text="[D]")
    para += ref
    section += para
    doc += section
    return doc, ref


class TestWr03EligibilityDecisionAgreesWithEmission:
    """
    The invariant backstop tying ``_reference_anchor_decision``'s own
    answer to what ``visit_reference`` ACTUALLY emitted, across every
    eligibility-affecting shape RESEARCH identified. Not a substitute for
    the refactor (D-05/D-06/D-07 already make the disagreement
    structurally impossible) -- this closes the loop by asserting the
    predicate's *contract* holds against real emitted output, so a FUTURE
    regression that reintroduces a second, disagreeing derivation site
    fails loudly here rather than silently.
    """

    @pytest.mark.parametrize(
        "case_name, build_case, expected_eligible",
        [
            ("refid_no_following_target", _wr03_case_refid_no_following_target, True),
            ("refid_followed_by_target", _wr03_case_refid_followed_by_target, False),
            ("refuri_excluded_document", _wr03_case_refuri_excluded_document, True),
            ("refid_empty_ids", _wr03_case_refid_empty_ids, False),
        ],
    )
    def test_wr03_eligibility_decision_and_emitted_anchor_agree(
        self, case_name, build_case, expected_eligible
    ):
        doc, ref = build_case()
        body, translator = _render_with_translator(doc)
        decision = translator._reference_anchor_decision(ref)

        assert decision.eligible is expected_eligible, (
            f"case {case_name!r}: decision.eligible={decision.eligible!r}, "
            f"expected {expected_eligible!r}\n\n{body}"
        )

        ref_ids = ref.get("ids") or []
        own_label = _expected_namespace_label("index", ref_ids[0]) if ref_ids else None

        if decision.eligible:
            assert (
                decision.anchor_label is not None
            ), f"case {case_name!r}: eligible but anchor_label is None"
            assert decision.anchor_label == own_label, (
                f"case {case_name!r}: anchor_label {decision.anchor_label!r} "
                f"!= expected {own_label!r}"
            )
        else:
            assert decision.anchor_label is None, (
                f"case {case_name!r}: not eligible but anchor_label is "
                f"{decision.anchor_label!r} (expected None)"
            )

        # Case (ii) is why this assertion is written against the
        # reference's OWN label rather than "no #label( anywhere in the
        # body" -- the following target legitimately attaches its own
        # (`real-target-b`), and that must NOT be confused with the
        # citing reference's own (absent) anchor.
        attached = _attached_anchor_tokens(body)
        if own_label is not None:
            if decision.eligible:
                assert own_label in attached, (
                    f"case {case_name!r}: eligible but own label "
                    f"{own_label!r} not found in attached anchors:\n{body}"
                )
            else:
                assert own_label not in attached, (
                    f"case {case_name!r}: not eligible but own label "
                    f"{own_label!r} WAS found in attached anchors -- the "
                    f"reference must not get its own anchor when "
                    f"ineligible:\n{body}"
                )


class TestWr03XrefResolutionOnceNoWarning:
    """
    Renamed from ``TestWr03XrefResolutionAndWarningFireOnce`` (Phase 48,
    D-01, ``48-EXPECTED-STRUCTURE.md``): the cross-document degrade-to-text
    warning this class used to assert fired exactly once has no subject
    after D-01 deleted that warning outright, with no diagnostic
    replacement. Half of the original Pitfall 2 guard (`40.1-RESEARCH.md`)
    still holds and is kept unchanged: the D-06 rewrite must not cause
    ``_resolve_xref_docname`` to run twice per reference (once inside the
    predicate, once again in ``visit_reference``'s own downstream
    branches). The other half is now its OWN inverse: rendering a
    cross-document reference must emit NO warning at all from the
    translator, regardless of whether its target is present or absent in
    any particular compile -- the whole question moved to Typst's
    ``query()``, which raises no Python-side warning either way.
    """

    @staticmethod
    def _build_cross_doc_reference_doctree() -> docutils_nodes.document:
        """A single citing reference whose ``refuri`` resolves to
        ``"second"``. Pre-Phase-48 this degraded to plain text via a
        build-time exclusion decision (since deleted); post-Phase-48 it
        routes through the D-07 compile-time guard instead -- the doctree
        itself is unchanged, only what the translator does with it."""
        doc = _make_document()
        section = docutils_nodes.section()
        para = docutils_nodes.paragraph()
        ref = _make_citing_reference(
            refuri="second.typ#anchor", ids=("citer-e",), text="[E]"
        )
        para += ref
        section += para
        doc += section
        return doc

    def test_wr03_xref_resolution_happens_once_per_reference(self):
        original_resolve = TypstTranslator._resolve_xref_docname
        with mock.patch.object(
            TypstTranslator,
            "_resolve_xref_docname",
            autospec=True,
            side_effect=original_resolve,
        ) as mocked_resolve:
            doc = self._build_cross_doc_reference_doctree()
            _render_body(doc)
        assert mocked_resolve.call_count == 1, (
            "expected _resolve_xref_docname to be called exactly ONCE per "
            f"reference (Pitfall 2, 40.1-RESEARCH.md) -- called "
            f"{mocked_resolve.call_count} times"
        )

    def test_wr03_cross_document_reference_emits_no_warning(self):
        """
        FLIPS post-Phase-48 (D-01, ``48-EXPECTED-STRUCTURE.md``): the
        cross-document degrade-to-text warning this test used to assert
        fired exactly once was deleted outright, with no diagnostic
        replacement. New expected value -- its own inverse: rendering a
        cross-document reference emits NO warning at all from the
        translator, regardless of whether its target is present or absent
        in any particular compile.
        """
        with mock.patch("typsphinx.translator.logger.warning") as mocked_warning:
            doc = self._build_cross_doc_reference_doctree()
            _render_body(doc)
        assert mocked_warning.call_count == 0, (
            "expected NO translator warning for a cross-document reference "
            f"(Phase 48, D-01) -- fired {mocked_warning.call_count} times: "
            f"{mocked_warning.call_args_list}"
        )
