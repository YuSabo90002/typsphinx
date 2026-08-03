"""
Phase 38, the folded buffer-swap todo: ``_desc_break_marker`` (SIG-08,
``depart_desc``) compares ``self._desc_break_marker == len(self.body)``
across two ``desc`` departures, but ``self.body`` is reassigned at five
sites -- ``in_table`` (guarded) plus ``visit_term`` / ``visit_definition``
(via ``_saved_body_stack``), the admonition title, and the figure caption
(all unguarded). This module builds the fixture the folded todo's own
binding instruction requires
(``.planning/todos/pending/2026-08-01-desc-break-marker-stale-across-body-buffer-swaps.md``):
build the fixture FIRST, record the measured behaviour against the
current tree SECOND, and only THEN choose the fix.

**Measured outcome (2026-08-01, against the untouched translator): GREEN,
not RED.** Every assertion below PASSES against the pre-phase tree. This
is a verbatim, honest measurement, not a presumption -- the todo's own
prose predicted RED, but the fixture's actual reachable shape does not
reproduce a genuine cross-buffer marker comparison. Here is why, read
directly from the emitted ``.typ`` (see
``38-GATE-EVIDENCE-03.md`` for the full build):

For a nested ``desc`` pair (a ``py:class::`` containing a ``py:method::``)
placed entirely inside ONE glossary definition's body, BOTH ``depart_desc``
calls the SIG-08 marker compares -- the inner method's and the outer
class's -- run while ``self.body`` points at the SAME swapped
``current_definition_buffer`` list. ``visit_definition`` swaps the buffer
in ONCE, before either desc is entered, and ``depart_definition`` swaps it
back OUT only after both have departed. The pair's own two departures
never straddle a live buffer reassignment, so the marker's
buffer-agnostic ``len(...)`` comparison stays internally consistent for
this shape, exactly as it would at document top level. This is a
DECLARED NON-REGRESSION CONTROL, not proof the hazard is unreachable in
general -- the todo's own suggested fix (making the marker
buffer-identifying via ``(id(self.body), len(self.body))``, rather than a
sixth per-site guard) is still adopted by a later plan in this phase,
because Phase 38's own body wrapper (38-EMISSION-CONTRACT.md section 2)
changes what the marker sees at every desc boundary, which changes the
hazard's reachability. This fixture must be RE-RUN once the wrapper
lands, per the folded todo's own honest-measurement instruction.
"""

import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False


@pytest.fixture
def desc_break_marker_buffer_swap_gate_dir():
    """Return the path to the desc_break_marker_buffer_swap_gate fixture."""
    return Path(__file__).parent / "fixtures" / "desc_break_marker_buffer_swap_gate"


@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for build output."""
    return tmp_path / "_build"


def _run_sphinx_build_typst(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typst`` as a subprocess and return the completed
    process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``)
    so the exact interpreter/venv already running this test is reused,
    sidestepping the documented NixOS-sandbox PATH-shadowing hazard --
    the pattern ``tests/test_signature_break_and_arrow_gate.py`` and
    ``tests/test_pdf_render_gate.py`` both use, cloned here.
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


def _build_typ(fixture_dir: Path, build_dir: Path) -> str:
    """Build the fixture through ``-b typst`` and return the emitted ``.typ``."""
    result = _run_sphinx_build_typst(fixture_dir, build_dir)
    assert result.returncode == 0, (
        f"sphinx-build -b typst failed:\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )
    index_typ = build_dir / "index.typ"
    assert index_typ.exists(), "index.typ was not generated"
    return index_typ.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Structural assertions on the emitted .typ -- no typst-py skip needed;
# these only require `-b typst`.
# ---------------------------------------------------------------------------


class TestDescBreakMarkerBufferSwapStructuralGate:
    """
    Structural break-count and adjacency assertions per construct.

    Requirements: IND-01 (break-bookkeeping view), the folded buffer-swap
    todo. Every count below is hand-derived from this fixture's own
    doctree shape (one desc per non-nested construct, one nested pair per
    nested construct), never from running the translator.
    """

    def test_glossary_single_desc_gets_exactly_one_break(
        self, desc_break_marker_buffer_swap_gate_dir, temp_build_dir
    ):
        """
        Construct 1: a single, non-nested desc inside a glossary
        definition. Not itself a marker-suppression case (nothing
        precedes it that the marker could match against within this
        buffer), but it establishes the region boundary construct 2's
        test below relies on, and it must build and contain exactly one
        parbreak() for its own departure.

        Measured (2026-08-01, pre-phase): PASSES. GREEN, recorded
        verbatim per this module's docstring.
        """
        typ_text = _build_typ(desc_break_marker_buffer_swap_gate_dir, temp_build_dir)
        construct_start = typ_text.index("buffer-swap-term-one")
        construct_end = typ_text.index("buffer-swap-term-two")
        region = typ_text[construct_start:construct_end]
        assert region.count("parbreak()") == 1, (
            "Expected exactly one parbreak() for construct 1's single "
            f"glossary-nested desc -- got {region.count('parbreak()')}:"
            f"\n{region}"
        )

    def test_glossary_nested_pair_gets_exactly_one_break(
        self, desc_break_marker_buffer_swap_gate_dir, temp_build_dir
    ):
        """
        Construct 2: a nested desc pair (py:class:: + py:method::) whose
        entire pair lives inside a glossary definition's body -- the
        buffer-swap-plus-nesting case the folded todo names as
        concretely reachable.

        Measured (2026-08-01, pre-phase): PASSES -- exactly one
        parbreak() is emitted for the pair, matching the correct
        (non-buggy) SIG-08 outcome. See this module's docstring for why:
        both depart_desc calls being compared run while self.body points
        at the SAME swapped definition buffer, so no genuine cross-buffer
        marker comparison occurs for this shape. GREEN, recorded
        verbatim -- not retro-fitted into a RED it did not produce.
        """
        typ_text = _build_typ(desc_break_marker_buffer_swap_gate_dir, temp_build_dir)
        construct_start = typ_text.index("buffer-swap-term-two")
        construct_end = typ_text.index("Nested Desc At Top Level", construct_start)
        region = typ_text[construct_start:construct_end]
        assert region.count("parbreak()") == 1, (
            "Expected exactly one parbreak() for construct 2's "
            "glossary-nested desc pair (buffer swap AND nesting at once) "
            f"-- got {region.count('parbreak()')}:\n{region}"
        )

    def test_top_level_control_matches_glossary_nested_pair_count(
        self, desc_break_marker_buffer_swap_gate_dir, temp_build_dir
    ):
        """
        CONTROL: the identical nested-desc shape (py:class:: containing
        py:method::) at document top level, outside any definition -- no
        self.body reassignment occurs anywhere in this construct's
        processing. Distinguishes "the buffer swap broke it" from
        "nesting broke it": this control's own break count must match
        construct 2's (both must be exactly one), or nesting itself --
        not the buffer swap -- would be the variable.

        Measured (2026-08-01, pre-phase): PASSES, and matches construct
        2 exactly (both 1), which is itself part of this fixture's
        honest GREEN measurement.
        """
        typ_text = _build_typ(desc_break_marker_buffer_swap_gate_dir, temp_build_dir)
        construct_start = typ_text.index("DescBreakTopLevelOuterClass")
        construct_end = typ_text.index("Desc Inside A Figure Caption", construct_start)
        region = typ_text[construct_start:construct_end]
        assert region.count("parbreak()") == 1, (
            "CONTROL: expected exactly one parbreak() for the top-level "
            "nested-desc control (no buffer swap) -- got "
            f"{region.count('parbreak()')}, which must match construct "
            f"2's glossary-nested count for the buffer-swap-vs-nesting "
            f"distinction to hold:\n{region}"
        )

    def test_no_adjacent_break_statements_anywhere(
        self, desc_break_marker_buffer_swap_gate_dir, temp_build_dir
    ):
        """
        No two parbreak() statements may appear adjacent with only
        whitespace between them anywhere in the emitted .typ -- the
        SIG-08 doubled-break defect's textual shape
        (37-EMISSION-CONTRACT.md section 8), checked across every
        construct in this fixture including the buffer-swapped ones.

        Measured (2026-08-01, pre-phase): PASSES.
        """
        typ_text = _build_typ(desc_break_marker_buffer_swap_gate_dir, temp_build_dir)
        lines = typ_text.splitlines()
        adjacent_positions = [
            i
            for i in range(len(lines) - 1)
            if lines[i].strip() == "parbreak()" and lines[i + 1].strip() == "parbreak()"
        ]
        assert adjacent_positions == [], (
            "Found adjacent parbreak() statements with nothing but "
            f"whitespace between them at line(s) {adjacent_positions}:"
            f"\n{typ_text}"
        )


# ---------------------------------------------------------------------------
# Real-compile acceptance: the fixture must not merely build, it must
# compile through a real typst.compile() call.
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the compile-acceptance gate",
)
class TestDescBreakMarkerBufferSwapCompileGate:
    """
    Real-compile acceptance for the buffer-swap fixture. No
    ``TypstCompilationError`` may propagate -- milestone invariant #4
    requires every node-handler-adjacent fixture in this phase to compile
    successfully both before and after any translator edit, since the
    RED/GREEN split in this phase is structural, never a compile fatal
    (Phase 40's citation work is the sole exception).
    """

    def test_fixture_compiles_via_real_typst_compile(
        self, desc_break_marker_buffer_swap_gate_dir, temp_build_dir
    ):
        """
        Measured (2026-08-01, pre-phase): compiles with exit status 0 --
        no exception raised, the output PDF exists and is non-empty. See
        this module's docstring and ``38-GATE-EVIDENCE-03.md`` for the
        verbatim exit status quoted alongside the structural gate's.
        """
        _build_typ(desc_break_marker_buffer_swap_gate_dir, temp_build_dir)
        typ_path = temp_build_dir / "index.typ"
        pdf_output = temp_build_dir / "index.pdf"
        typst.compile(str(typ_path), output=str(pdf_output))
        assert pdf_output.exists(), "PDF file was not created"
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
