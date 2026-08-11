"""
Phase 39's classic GATE-01 RED for the ADM-05/D-13 rubric defect.

THIS MODULE IS A DELIBERATE RED WINDOW. Every expected string below is
hand-derived from the named ``typsphinx/translator.py`` line ranges (see
each test's docstring), never copied from a candidate fix's own output. The
CONTROL tests (already GREEN against the untouched translator) must never be
converted into defect cases -- they exist specifically to catch a fix that
over-corrects (stops wrapping paragraphs after every rubric, not just the
nested-inline-child one).

D-13's defect (39-CONTEXT.md): ``visit_strong``, ``visit_rubric`` and
``visit_desc_signature`` deliberately share three single-slot save
attributes (``_strong_was_in_paragraph``, ``_strong_was_in_list_item``,
``_strong_was_list_item_needs_separator`` -- Phase 36 D-02). A rubric whose
title carries a real inline ``strong`` child re-saves those same three
attribute names when the inner ``visit_strong`` fires, clobbering the outer
rubric's own saved values. The inner ``depart_strong`` then restores from
(and deletes) those attributes, so by the time the OUTER ``depart_rubric``
runs, ``hasattr(self, "_strong_was_in_paragraph")`` is already ``False`` --
its restore block silently no-ops, and ``self.in_list_item`` stays stuck at
``True`` (the value ``visit_rubric`` forced for its own children) for the
rest of the document. ``visit_paragraph`` treats every subsequent paragraph
as if it were inside a list item, skipping the ``par({...})`` wrapper and
emitting a bare ``text("...")`` instead -- to the end of the file, not just
the next paragraph.

Both defects compile perfectly (this module's own compile-sanity leg proves
it); the RED here is structural (a missing ``par({...})`` substring), not a
``TypstError``.

Fixture layout (``tests/fixtures/rubric_strong_nesting_render_gate/``):
the CONTROL rubric (no inline markup) and its own paragraph come FIRST,
deliberately BEFORE the defect construct -- D-13's corruption is
document-wide and never resets, so the CONTROL's own paragraph-wrap
assertion is only provably unaffected by the defect if it is measured
before the defect fires. The defect rubric then sits inside its own section
so the fixture's compile-sanity leg reaches a valid PDF: a section boundary
is the one place ``depart_section`` already emits an unconditional
separator, which is what keeps the corrupted ``in_list_item`` state from
producing an invalid ``text("...")[#heading(...)]`` juxtaposition (Typst's
trailing-content-block call sugar turns that into an "unexpected argument"
fatal) at the very first heading following the defect. This section
wrapper is a fixture-authoring necessity, not part of the defect being
measured.
"""

import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False


def _run_sphinx_build_typst(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typst`` as a subprocess and return the completed
    process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never a bare ``sphinx-build``
    and never ``uv run sphinx-build``) so the exact interpreter/venv already
    running this test is reused, sidestepping the documented NixOS-sandbox
    PATH-shadowing hazard (project memory: "NixOS sandbox test env").
    """
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            "typst",
            str(source_dir),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
    )


@pytest.fixture(scope="session")
def rubric_strong_nesting_build(tmp_path_factory):
    """
    Session-scoped: run ``-b typst`` once for the whole module and return
    ``(build_dir, typ_text)`` -- the directory containing the emitted
    ``index.typ`` plus its decoded text, so the compile-sanity leg below can
    compile the SAME build output without re-invoking Sphinx.
    """
    source_dir = (
        Path(__file__).parent / "fixtures" / "rubric_strong_nesting_render_gate"
    )
    build_dir = tmp_path_factory.mktemp("rubric_strong_nesting_render_gate")
    result = _run_sphinx_build_typst(source_dir, build_dir)
    assert result.returncode == 0, (
        f"sphinx-build -b typst failed:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    typ_path = build_dir / "index.typ"
    assert typ_path.exists(), "index.typ was not emitted"
    return build_dir, typ_path.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def rubric_strong_nesting_typ_text(rubric_strong_nesting_build):
    """The emitted ``index.typ`` text, decoded once for the whole module."""
    return rubric_strong_nesting_build[1]


class TestRubricStrongNestingRenderGate:
    """
    This phase's classic GATE-01 RED (D-13): a rubric with a real inline
    ``strong`` child clobbers the shared save-slot attributes and every
    paragraph after it, to the end of the document, loses its ``par()``
    wrapper.

    Requirements: ADM-05.
    """

    def test_paragraph_immediately_after_defect_rubric_loses_par_wrapper(
        self, rubric_strong_nesting_typ_text
    ):
        """
        RED today. Hand-derived expected string: ``visit_paragraph``'s
        non-list-item branch (``typsphinx/translator.py:896-899``) opens
        ``par({``, and ``visit_Text`` (``typsphinx/translator.py:1300-1301``)
        wraps the prose in ``text("...")`` with no leading separator (first
        child of the ``par``), and ``depart_paragraph``
        (``typsphinx/translator.py:938-941``) closes with ``})``. The full
        nested expected string is therefore
        ``par({text("...")})`` around the fixture's Alpha prose.

        Pre-fix, ``visit_paragraph`` instead takes the ``in_list_item``
        branch (``typsphinx/translator.py:891-894``) because D-13 left
        ``self.in_list_item`` stuck ``True``, so this substring is absent
        and the paragraph emits as a bare ``text("...")`` call.
        """
        expected = (
            'par({text("Alpha prose sits directly after the defect rubric '
            'and must render inside a wrapped block.")})'
        )
        assert expected in rubric_strong_nesting_typ_text, (
            "D-13: the paragraph immediately after the inline-markup rubric "
            "did not emit the par({text(...)}) wrapper -- the shared "
            "_strong_was_* save-slot clobbering (Phase 36 D-02) is still "
            f"leaving in_list_item stuck True:\n{rubric_strong_nesting_typ_text}"
        )

    def test_second_later_paragraph_still_loses_par_wrapper(
        self, rubric_strong_nesting_typ_text
    ):
        """
        RED today, and the point of this test (paired with the next one) is
        that D-13's defect is DOCUMENT-WIDE: it must fail for a paragraph
        separated from the defect rubric by an intervening section heading,
        not just the immediately adjacent one. Same hand derivation as
        ``test_paragraph_immediately_after_defect_rubric_loses_par_wrapper``.
        """
        expected = (
            'par({text("Bravo prose sits after an intervening section '
            'heading and must also render inside a wrapped block.")})'
        )
        assert expected in rubric_strong_nesting_typ_text, (
            "D-13 document-wide: a paragraph separated from the defect "
            "rubric by an intervening section heading still did not emit "
            f"the par({{text(...)}}) wrapper:\n{rubric_strong_nesting_typ_text}"
        )

    def test_third_later_paragraph_still_loses_par_wrapper(
        self, rubric_strong_nesting_typ_text
    ):
        """
        RED today. The second of the document-wide pair: a paragraph
        separated from the defect rubric by TWO intervening section
        headings still fails, proving the defect runs to the end of the
        file rather than only the next paragraph or two (the
        ``must_haves.prohibitions`` bar this gate must clear).
        """
        expected = (
            'par({text("Charlie prose sits deep in the document and must '
            'also render inside a wrapped block.")})'
        )
        assert expected in rubric_strong_nesting_typ_text, (
            "D-13 document-wide: a paragraph separated from the defect "
            "rubric by two intervening section headings still did not emit "
            f"the par({{text(...)}}) wrapper:\n{rubric_strong_nesting_typ_text}"
        )

    def test_control_paragraph_after_markup_free_rubric_stays_wrapped(
        self, rubric_strong_nesting_typ_text
    ):
        """
        CONTROL. GREEN today and must stay GREEN after the fix. The control
        rubric carries no inline markup, so it never touches the shared
        ``_strong_was_*`` slots and never corrupts ``in_list_item`` --
        placed BEFORE the defect construct in the fixture so this assertion
        is measured against genuinely unbroken state, isolating the defect
        to the nested-inline-child case. A fix that indiscriminately stops
        wrapping paragraphs after every rubric (rather than fixing the
        shared-slot clobbering) would break this assertion.
        """
        expected = (
            'par({text("Delta prose sits after the markup free control '
            'rubric and must render inside a wrapped block.")})'
        )
        assert expected in rubric_strong_nesting_typ_text, (
            "CONTROL regression: the paragraph after the markup-free "
            "control rubric lost its par({text(...)}) wrapper -- this "
            "construct must stay GREEN both before and after the D-13 fix:"
            f"\n{rubric_strong_nesting_typ_text}"
        )

    def test_control_defect_rubrics_own_emission_is_unchanged(
        self, rubric_strong_nesting_typ_text
    ):
        """
        CONTROL. GREEN today and must stay GREEN after the fix. Derived
        directly from ``visit_rubric``'s and ``depart_rubric``'s own
        emission lines (``typsphinx/translator.py:5825`` -- the
        ``strong({`` open, ``typsphinx/translator.py:5856`` -- the ``})``
        close), NOT from the state-restoration bookkeeping D-13 is about. A
        fix that alters the rubric's OWN bold-wrapper emission instead of
        its state bookkeeping would fail this assertion. The open bytes
        include the rubric's own first text child ("A Nested ") and the
        close bytes include its own last text child (" Rubric") so the
        match is unambiguous against the fixture's other rubric.
        """
        open_bytes = 'strong({text("A Nested ")'
        close_bytes = 'text(" Rubric")})'
        assert open_bytes in rubric_strong_nesting_typ_text, (
            "CONTROL regression: the defect rubric's own bold-wrapper open "
            f"bytes are missing or changed:\n{rubric_strong_nesting_typ_text}"
        )
        assert close_bytes in rubric_strong_nesting_typ_text, (
            "CONTROL regression: the defect rubric's own bold-wrapper close "
            f"bytes are missing or changed:\n{rubric_strong_nesting_typ_text}"
        )

    @pytest.mark.skipif(
        not TYPST_AVAILABLE,
        reason="typst-py is required for the compile-sanity leg",
    )
    def test_fixture_compiles_to_valid_typst(self, rubric_strong_nesting_build):
        """
        Compile-sanity leg (not marked ``slow`` -- that marker is reserved
        in this repo for the network-dependent full-corpus gate). Both
        defects this fixture proves compile perfectly; this confirms the
        RED above is structural, never a build or compile error.
        """
        # Phase 47 (R3): only the WRAPPER file (this fixture's
        # typst_documents target, "master.typ") is a complete,
        # self-contained document -- the content file ("index.typ")
        # carries no template application.
        build_dir, _ = rubric_strong_nesting_build
        typ_path = build_dir / "master.typ"
        try:
            typst.compile(str(typ_path))
        except Exception as exc:
            pytest.fail(
                f"typst.compile() rejected the fixture -- both D-13 and "
                f"its CONTROL are expected to compile perfectly:\n{exc}"
            )
