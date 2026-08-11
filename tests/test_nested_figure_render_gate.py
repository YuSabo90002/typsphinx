"""
Real-compile regression gate for FIG-01 (Phase 43): a figure nested inside
another figure's ``legend`` (docutils' name for a figure's body content
beyond its first caption paragraph) currently aborts the WHOLE
``typst.compile()`` with a classic ``TypstError``.

Root cause (43-RESEARCH.md Pitfall 4): ``visit_legend``/``depart_legend`` do
not exist, so docutils' ``unknown_visit`` fires (warns and continues -- it
does NOT skip children), and the legend's children stream unwrapped straight
after the outer ``image(...)`` call. Typst parses ``image(...)`` followed by
any expression as an unwanted second argument/trailing content block --
``TypstError: expected comma`` -- aborting the entire compile, not merely
dropping the outer caption (though the outer caption is ALSO dropped, since
``self.figure_caption`` is a bare scalar clobbered by the nested figure's own
``visit_figure`` reset).

Even a PLAIN-TEXT legend with NO nested figure at all is already broken
today -- the root cause is the missing ``legend`` handler, not the nesting,
so this gate's fixture also covers that case (measured RED in
43-GATE-EVIDENCE-03.md).

Fix: ``visit_legend``/``depart_legend`` plus a figure-state save/restore
stack (``_push_figure_state``/``_pop_figure_state``, mirroring plan 43-01's
``_push_table_state``/``_pop_table_state``) so a nested figure's own state
does not clobber the enclosing figure's caption/ids/width when the inner
figure departs.

Drives the full ``-b typstpdf`` path -- NOT ``-b typst`` -- on purpose: the
fatal only aborts on the ``TypstPDFBuilder.finish()`` compile path.
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

try:
    import pypdf

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


# Sentinel tokens embedded in nested_figure_render_gate/index.rst.
NF1_OUTER_CAPTION = "NF1OUTERCAP"
NF1_INNER_CAPTION = "NF1INNERCAP"
NF2_CAPTION = "NF2CAP"
NF2_LEGEND_TEXT = "NF2LEGENDTEXT"
NF3_CONTROL_CAPTION = "NF3CTRLCAP"
NF4_LEGEND_ONLY = "NF4LEGENDONLY"
NF5_OUTER_CAPTION = "NF5OUTERCAP"
NF5_OUTER_LEGEND = "NF5OUTERLEGEND"
NF5_INNER_CAPTION = "NF5INNERCAP"
NF5_INNER_LEGEND = "NF5INNERLEGEND"
NF5_TRAILING_PARA = "NF5TRAILINGPARA"


@pytest.fixture
def nested_figure_render_gate_dir():
    """Return the path to the nested_figure_render_gate fixture."""
    return Path(__file__).parent / "fixtures" / "nested_figure_render_gate"


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

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``) so
    the exact interpreter/venv running this test is reused, sidestepping the
    documented NixOS-sandbox PATH-shadowing hazard.
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


@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the FIG-01 render gate",
)
class TestNestedFigureRenderGate:
    """
    Real-compile acceptance gate for FIG-01: a ``legend`` handler plus
    figure-state save/restore so a figure nested inside another figure's
    legend compiles, both figures render with both captions, the plain-text
    legend case (no nesting) also compiles, and an image-only control figure
    stays byte-unchanged.

    Requirements: FIG-01, GATE-01 (43-CONTEXT.md D-02/D-03, 43-RESEARCH.md
    Pattern 2/Pitfall 4).
    """

    def test_build_exits_zero(self, nested_figure_render_gate_dir, temp_build_dir):
        """The full fixture -- all four legend shapes -- compiles cleanly."""
        result = _run_sphinx_build_typstpdf(
            nested_figure_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_no_unknown_node_type_warning_for_legend(
        self, nested_figure_render_gate_dir, temp_build_dir
    ):
        """
        ``sphinx-build`` must emit no ``unknown node type`` warning naming a
        ``legend`` node -- proof that ``visit_legend``/``depart_legend`` now
        exist and handle it (as opposed to docutils' warn-and-continue
        ``unknown_visit`` fallback).
        """
        result = _run_sphinx_build_typstpdf(
            nested_figure_render_gate_dir, temp_build_dir
        )
        assert "unknown node type" not in result.stderr, (
            "Expected no unhandled-node-type warning for the legend node -- "
            f"visit_legend/depart_legend are missing or incomplete:\n"
            f"stderr: {result.stderr}"
        )

    def test_pdf_produced_with_both_captions_for_nested_figure(
        self, nested_figure_render_gate_dir, temp_build_dir
    ):
        """
        Section 1 (figure nested in a figure's legend): a real, non-empty
        PDF is produced, and BOTH the outer and inner figure captions are
        present in the extracted PDF text -- the outer figure's caption/ids/
        state survive the inner figure's departure (FIG-01, SC#6).
        """
        result = _run_sphinx_build_typstpdf(
            nested_figure_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        # Phase 47 (R4): the PDF is the WRAPPER's own output ("master.pdf",
        # this fixture's typst_documents target after de-collision).
        pdf_output = temp_build_dir / "master.pdf"
        assert pdf_output.exists(), (
            "master.pdf was not produced -- typst.compile() aborted, most "
            f"likely on the nested-figure-in-legend shape:\n"
            f"stderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)

        assert NF1_OUTER_CAPTION in full_text, (
            f"Expected the OUTER figure's caption sentinel "
            f"'{NF1_OUTER_CAPTION}' in extracted PDF text -- the outer "
            f"figure's caption was clobbered by the nested figure's own "
            f"state reset:\n{full_text}"
        )
        assert NF1_INNER_CAPTION in full_text, (
            f"Expected the INNER figure's caption sentinel "
            f"'{NF1_INNER_CAPTION}' in extracted PDF text:\n{full_text}"
        )

    def test_plain_text_legend_with_no_nesting_compiles(
        self, nested_figure_render_gate_dir, temp_build_dir
    ):
        """
        Section 2 (plain-text legend, no nested figure at all): this shape
        is already broken today with no nesting involved -- the root cause
        is the missing ``legend`` handler, not the nesting. Both the
        caption and the legend text must appear in the extracted PDF text.
        """
        result = _run_sphinx_build_typstpdf(
            nested_figure_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        # Phase 47 (R4): the PDF is the WRAPPER's own output ("master.pdf",
        # this fixture's typst_documents target after de-collision).
        pdf_output = temp_build_dir / "master.pdf"
        assert pdf_output.exists(), (
            "master.pdf was not produced -- typst.compile() aborted on the "
            f"plain-text legend shape:\nstderr: {result.stderr}"
        )

        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)

        assert NF2_CAPTION in full_text, (
            f"Expected caption sentinel '{NF2_CAPTION}' in extracted PDF "
            f"text:\n{full_text}"
        )
        assert NF2_LEGEND_TEXT in full_text, (
            f"Expected plain-text legend sentinel '{NF2_LEGEND_TEXT}' in "
            f"extracted PDF text -- the fix must not be narrowed to only "
            f"legends that contain a nested figure:\n{full_text}"
        )

    def test_image_only_control_is_byte_unchanged(
        self, nested_figure_render_gate_dir, temp_build_dir
    ):
        """
        Section 3 (image-only control, no legend child): the FIG-01 fix
        must not change this figure's emitted ``.typ`` bytes at all -- no
        ``{...}`` body wrap is added when there is no legend (SC#4). This
        is the byte-invariance control the fix's Task 2 diffs against the
        pre-fix bytes recorded in 43-GATE-EVIDENCE-03.md.
        """
        result = _run_sphinx_build_typstpdf(
            nested_figure_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")

        expected_control_figure = (
            "[#figure(\n"
            '  image("img.png"),\n'
            f'  caption: {{text("{NF3_CONTROL_CAPTION}")}}\n'
            ") <index:id4>]"
        )
        assert expected_control_figure in typ_text, (
            "The image-only control figure's emitted bytes changed -- the "
            f"FIG-01 legend fix must not touch a figure with no legend "
            f"child:\n{typ_text}"
        )

    def test_legend_with_no_caption_compiles(
        self, nested_figure_render_gate_dir, temp_build_dir
    ):
        """
        Section 4 (legend with no caption -- an empty comment stands in for
        the caption slot, per the docutils measurement recorded in
        43-GATE-EVIDENCE-03.md; there is no ``.. legend::`` RST directive).
        Must compile and the legend text must appear in the extracted PDF
        text even though the figure carries no caption at all.
        """
        result = _run_sphinx_build_typstpdf(
            nested_figure_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        # Phase 47 (R4): the PDF is the WRAPPER's own output ("master.pdf",
        # this fixture's typst_documents target after de-collision).
        pdf_output = temp_build_dir / "master.pdf"
        assert pdf_output.exists(), (
            "master.pdf was not produced -- typst.compile() aborted on the "
            f"no-caption legend shape:\nstderr: {result.stderr}"
        )

        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)

        assert NF4_LEGEND_ONLY in full_text, (
            f"Expected no-caption legend sentinel '{NF4_LEGEND_ONLY}' in "
            f"extracted PDF text:\n{full_text}"
        )

    def test_legend_in_legend_does_not_leak_list_item_state(
        self, nested_figure_render_gate_dir, temp_build_dir
    ):
        """
        Section 5 (43-REVIEW.md CR-01): the outer figure's legend contains
        an INNER figure that itself has BOTH a caption and its own legend.
        Pre-fix, ``visit_legend``/``depart_legend`` saved
        ``in_list_item``/``list_item_needs_separator`` into two flat
        instance attributes instead of a real stack, so the inner legend's
        ``visit_legend`` clobbers the outer legend's saved values with its
        own already-mutated ``True``/``True`` -- the outer
        ``depart_legend`` then restores the WRONG value, leaking
        ``in_list_item = True`` into every sibling for the rest of the
        document.

        Asserts on the RENDERED result, in the same style as
        ``test_image_only_control_is_byte_unchanged`` above: the top-level
        paragraph immediately after the outer figure must render through
        the NORMAL top-level paragraph path (``par({...})``), not the
        list-item/legend path (a bare ``parbreak()`` followed by an
        unwrapped ``text(...)``). Also asserts both captions and both
        legend sentinels appear in the extracted PDF text, so this test
        cannot pass by breaking the nesting it is meant to protect.
        """
        result = _run_sphinx_build_typstpdf(
            nested_figure_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")

        expected_trailing_para = f'par({{text("{NF5_TRAILING_PARA} sentinel text.")}})'
        assert expected_trailing_para in typ_text, (
            "The trailing top-level paragraph after the legend-in-legend "
            "figure did not render through the normal paragraph path -- "
            "in_list_item leaked as True past the outer figure's "
            f"depart_legend (43-REVIEW.md CR-01):\n{typ_text}"
        )

        leaked_form = f'parbreak()\n\ntext("{NF5_TRAILING_PARA} sentinel text.")'
        assert leaked_form not in typ_text, (
            "The trailing paragraph emitted the LEAKED list-item form "
            f"(parbreak() + bare text(...)) instead of par({{...}}):\n{typ_text}"
        )

        # Phase 47 (R4): the PDF is the WRAPPER's own output ("master.pdf",
        # this fixture's typst_documents target after de-collision).
        pdf_output = temp_build_dir / "master.pdf"
        assert pdf_output.exists(), (
            "master.pdf was not produced -- typst.compile() aborted on the "
            f"legend-in-legend shape:\nstderr: {result.stderr}"
        )
        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)

        for sentinel in (
            NF5_OUTER_CAPTION,
            NF5_OUTER_LEGEND,
            NF5_INNER_CAPTION,
            NF5_INNER_LEGEND,
            NF5_TRAILING_PARA,
        ):
            assert sentinel in full_text, (
                f"Expected sentinel '{sentinel}' in extracted PDF text -- "
                f"a test that passes by dropping content is not a valid "
                f"regression gate:\n{full_text}"
            )
