"""
Real-compile regression gate for the FID-12 markup/code-mode leak class
(Phase 21 Plan 01, GATE-01), re-pointed at codly 2.0 code-mode emission.

The original bug: a ``literal_block`` with BOTH a ``:caption:`` AND nested
in a ``list_item`` leaked its codly 1.3 config wrapper as visible text,
because the captioned figure opened a Typst MARKUP block and the list-item
brace wrapper inside it was read as literal text.

With codly 2.0 the whole block is one code-mode expression,
``figure(codly.new(raw(...), ...), caption: text("..."), kind: raw)``: no
markup content block, no markup fence, no list-item brace wrapper and no
state-style ``codly`` configuration call exist that could leak. This gate
builds the captioned-list-item fixture to PDF and asserts that invariant
at the ``.typ`` level and that no configuration text leaks into the PDF.
"""

import re
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
def codly_caption_listitem_leak_render_gate_dir():
    """Return the path to the codly_caption_listitem_leak_render_gate fixture project."""
    return (
        Path(__file__).parent / "fixtures" / "codly_caption_listitem_leak_render_gate"
    )


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

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``)
    so the exact interpreter/venv running this test is reused, sidestepping
    the documented NixOS-sandbox PATH-shadowing hazard.
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
    reason="typst-py is required for the codly-caption-listitem-leak render gate",
)
class TestCodlyCaptionListitemLeakRenderGate:
    """
    Real-compile regression gate proving a captioned code block inside a
    list item is one code-mode codly.new(...) figure expression and leaks
    no codly configuration text into the PDF.

    Requirements: FID-12, GATE-01.
    """

    def test_typstpdf_captioned_listitem_wrapper_opens_with_hash(
        self, codly_caption_listitem_leak_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm, at the SOURCE
        (``.typ``) level:

        - the build exits cleanly and did not report a compile failure;
        - the captioned list-item block is one code-mode
          ``figure(codly.new(raw(...)), caption: text(...), kind: raw)``
          expression, with no brace wrapper of either form;
        - no markup fence and no bare ``codly(`` call appear anywhere;
        - ``master.pdf`` exists, is non-empty, and begins with ``%PDF``.
        """
        result = _run_sphinx_build_typstpdf(
            codly_caption_listitem_leak_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")

        assert "\nfigure(codly.new(raw(" in typ_text, typ_text
        assert re.search(
            r"^figure\(codly\.new\(raw\(.*LISTITEMCAPSENTINEL.*\), "
            r'caption: text\(".*"\), kind: raw\)$',
            typ_text,
            re.M,
        ), typ_text
        assert "```" not in typ_text, typ_text
        assert not re.search(r"(^|[^.a-z-])codly\(", typ_text), typ_text
        assert "#{\ncodly" not in typ_text and "{\ncodly" not in typ_text, typ_text
        assert "figure(caption: [" not in typ_text, typ_text

        pdf_output = temp_build_dir / "master.pdf"
        assert pdf_output.exists(), (
            "master.pdf was not produced:\n" f"stderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

    @pytest.mark.skipif(
        not PYPDF_AVAILABLE,
        reason="pypdf is required for the extracted-text leak-absence adjacency assert",
    )
    def test_pdf_extracted_text_has_no_leaked_codly_config(
        self, codly_caption_listitem_leak_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf``, extract the compiled
        PDF's text with pypdf, and confirm (D-09):

        - no codly configuration text leaks into extracted prose --
          neither ``"number-format"``, ``"number-enabled"``,
          ``"codly.new"`` nor a bare ``"codly("`` call string appears;
        - the code block's own sentinel identifier IS present (the
          executed code block still rendered).
        """
        result = _run_sphinx_build_typstpdf(
            codly_caption_listitem_leak_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        pdf_output = temp_build_dir / "master.pdf"
        assert pdf_output.exists(), (
            "master.pdf was not produced:\n" f"stderr: {result.stderr}"
        )

        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)

        assert "number-format" not in full_text, (
            "Found the leaked 'number-format' codly config token in "
            f"extracted PDF text (FID-12 regression):\n{full_text}"
        )
        assert "number-enabled" not in full_text, full_text
        assert "codly.new" not in full_text, full_text
        assert "codly(" not in full_text, (
            "Found a leaked bare 'codly(' call string in extracted PDF "
            f"text (FID-12 regression):\n{full_text}"
        )
        assert "LISTITEMCAPSENTINEL" in full_text, (
            "Expected the code block's own sentinel identifier in "
            f"extracted PDF text (the executed code block itself):\n{full_text}"
        )
