"""
Real-compile regression gate for TBL-05 (Phase 43): a captioned table whose
title renders to the empty string must anchor its ids on at least one path,
so a same-document ``:ref:`` to a propagated target resolves instead of
dangling and aborting the whole ``typst.compile()``.

Root cause (43-RESEARCH.md / CONTEXT.md D-07, measured 2026-08-04):
``visit_table`` decides "is this captioned?" STRUCTURALLY --
``isinstance(node.children[0], nodes.title)`` -- and skips its own
unconditional ``_emit_id_anchors`` call when the answer is yes, deferring
anchoring entirely to ``depart_table``'s captioned branch. ``depart_table``
instead decides the same question by TRUTHINESS of the RENDERED caption
(``if self.table_caption:``). For the fixture's first table the title's only
child is a ``raw`` node -- ``title.astext()`` is ``'<span></span>'``
(non-empty), but ``visit_raw`` raises ``SkipNode`` for a non-typst format, so
the RENDERED result is the empty string. The two checks disagree: the visit
side treats the table as captioned (skips its anchor call), the depart side
treats it as caption-less (never anchors either, since that call lives only
inside the ``if self.table_caption:`` branch). The table's ids are anchored
on NEITHER path, so the propagated ``tbl-target`` id dangles and
``typst.compile()`` aborts with ``TypstError: label ... does not exist in
the document``.

Fix (D-05, matching Sphinx's own LaTeX builder measured against identical
input): anchoring switches to the STRUCTURAL decision
(``self._table_is_captioned``, stashed at visit time), independent of
whether the caption happens to render to anything -- while RENDERING keeps
gating on the truthy rendered caption, so the empty-rendered-caption table
stays a bare ``table(...)``, is NOT figure-wrapped, and consumes NO table
number (D-05's numbering control below).

D-06: no NEW warning is emitted for a caption that renders empty -- Sphinx's
own LaTeX builder emits none for the identical input, and this fixture's
build produces no warning about the empty caption on either side of the fix
(the RED failure is a Typst compile FATAL, not a Sphinx-level WARNING).

Drives the full ``-b typstpdf`` path -- NOT ``-b typst`` -- on purpose: the
fatal only aborts on the ``TypstPDFBuilder.finish()`` compile path, so a
``-b typst`` build would emit the invalid ``.typ`` but never compile it and
thus prove nothing.
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


@pytest.fixture
def table_empty_caption_anchor_render_gate_dir():
    """Return the path to the table_empty_caption_anchor_render_gate fixture."""
    return Path(__file__).parent / "fixtures" / "table_empty_caption_anchor_render_gate"


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
    not TYPST_AVAILABLE,
    reason="typst-py is required for the table-empty-caption-anchor render gate",
)
class TestTableEmptyCaptionAnchorRenderGate:
    """
    Real-compile acceptance gate for TBL-05: a captioned table whose title
    renders to the empty string anchors its ids, so a same-document
    ``:ref:`` to a propagated target resolves and the document compiles to a
    PDF, while the table itself stays neither figure-wrapped nor numbered.

    Requirements: TBL-05, GATE-01 (43-CONTEXT.md D-05/D-06/D-07,
    43-RESEARCH.md).
    """

    def test_build_exits_zero_and_anchors_the_propagated_target(
        self, table_empty_caption_anchor_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm:

        - the build exits 0 (no ``TypstError`` fatal at the label-resolution
          pass, which is what the pre-fix translator produces here);
        - the emitted ``index.typ`` contains a ``metadata(none)`` anchor
          naming the propagated ``tbl-target`` label -- proving the id
          anchoring fix is in effect, independent of the rendered-caption
          truthiness that made the pre-fix translator skip it;
        - ``index.pdf`` exists, is non-empty, and starts with the ``%PDF``
          magic bytes -- the document compiled to a real PDF instead of
          aborting at Typst's semantic label-resolution pass;
        - no NEW warning about the empty caption is emitted (D-06) -- the
          only literal ``TypstError``-class failure signature the pre-fix
          translator produces here is the compile fatal itself, never a
          Sphinx-level ``WARNING`` about the caption.
        """
        result = _run_sphinx_build_typstpdf(
            table_empty_caption_anchor_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            "sphinx-build -b typstpdf failed -- the propagated tbl-target "
            "anchor is not emitted on at least one of visit_table's "
            "structural path or depart_table's rendered-caption path:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert "label" not in result.stderr or "does not exist" not in result.stderr, (
            "A dangling-label TypstError is still present in stderr:\n"
            f"stderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")

        assert "metadata(none) <index:tbl-target>" in typ_text, (
            "Expected a metadata(none) anchor naming the propagated "
            f"tbl-target label in the emitted Typst source:\n{typ_text}"
        )

        # D-06: no new warning about the empty caption. This build produces
        # no Sphinx-level WARNING about the caption on either side of the
        # fix (the pre-fix failure is a Typst compile FATAL, not a
        # warning), so the warning output must stay unchanged.
        assert "caption" not in result.stderr.lower(), (
            "Unexpected new warning mentioning 'caption' in stderr -- D-06 "
            f"requires no new warning for an empty-rendered caption:\n"
            f"stderr: {result.stderr}"
        )

        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted, most "
            f"likely on the dangling tbl-target label:\nstderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

    @pytest.mark.skipif(
        not PYPDF_AVAILABLE,
        reason="pypdf is required for the PDF-text-extraction assertions",
    )
    def test_pdf_text_has_all_cells_and_control_table_is_numbered_one(
        self, table_empty_caption_anchor_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture and confirm, via real ``pypdf`` text extraction:

        - both tables' cell content (``TEC1A``/``TEC1B`` from the
          empty-rendered-caption table, ``TEC2A``/``TEC2B`` from the
          real-caption control) and the control's caption text
          (``TECREALCAP``) are all present in the extracted PDF text;
        - the D-05 numbering control: the real-caption control table renders
          as "Table 1", NOT "Table 2" -- proving the empty-rendered-caption
          table above it is NOT figure-wrapped and consumes NO table number.
          Typst's own ``kind: table`` numbering would shift by one if the
          empty-rendered-caption table were (incorrectly) figure-wrapped.
        """
        result = _run_sphinx_build_typstpdf(
            table_empty_caption_anchor_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), "index.pdf was not produced"

        reader = pypdf.PdfReader(str(pdf_output))
        raw_text = "\n".join(page.extract_text() for page in reader.pages)
        # Typst's default figure numbering emits a NON-BREAKING space
        # (U+00A0) between "Table" and the number (measured this session:
        # pypdf extracts "Table\xa01: TECREALCAP") -- normalize to a
        # regular space before matching so the assertion is about the
        # numbering VALUE, not this typographic detail.
        full_text = raw_text.replace("\xa0", " ")

        for sentinel in ("TEC1A", "TEC1B", "TEC2A", "TEC2B", "TECREALCAP"):
            assert sentinel in full_text, (
                f"Expected sentinel '{sentinel}' in extracted PDF text -- "
                f"content regression:\n{full_text}"
            )

        assert "Table 1: TECREALCAP" in full_text, (
            "Expected the real-caption control table to render as 'Table "
            "1' -- the empty-rendered-caption table above it must not "
            f"consume a table number:\n{full_text}"
        )
        assert "Table 2: TECREALCAP" not in full_text, (
            "The real-caption control table rendered as 'Table 2' -- the "
            "empty-rendered-caption table is figure-wrapped and "
            f"incorrectly consumed a table number (D-05 violation):\n"
            f"{full_text}"
        )
