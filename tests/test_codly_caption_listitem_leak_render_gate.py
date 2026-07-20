"""
Real-compile regression gate for the FID-12 markup/code-mode leak fix
(Phase 21 Plan 01, GATE-01).

The shipping bug: a ``literal_block`` with BOTH a ``:caption:`` AND nested
in a ``list_item`` leaks its codly config wrapper as visible text. Root
cause (21-RESEARCH.md D-Disc-2, verified against a real compile): a
captioned code block opens Typst MARKUP mode via
``figure(caption: [...])[``, and the list-item ``{ }`` wrapper's own
OPENING brace was unconditionally bare -- but a bare ``{`` written directly
inside Typst markup mode is parsed as LITERAL TEXT, not as a code-embed
delimiter. Only ``#{`` re-enters code mode. The existing code's own
docstring comment assumed the bare ``{`` "re-enters code mode inside the
figure's ``[...]``" -- that assumption was the bug.

Fix: in ``visit_literal_block``, the list-item wrapper's opening brace
carries a leading ``#`` iff ``self.in_captioned_code_block and
self.code_block_caption`` (i.e. exactly the combined captioned+list-item
case); otherwise it stays the bare ``{``, byte-unchanged for the
non-captioned list-item case. The existing ``in_markup_context`` /
``codly_prefix`` predicate a few lines below is already correct and stays
unchanged -- it already excludes ``self.in_list_item``, since once the
wrapper's own opening brace is fixed, code inside it is correctly back in
CODE mode (possibly ``#``-prefixed) and the per-block codly calls must stay
bare.

Confirmed this session: the structural (``.typ``-level) assert below FAILS
against the pre-fix translator (the wrapper's opening brace is bare ``{``,
not ``#{``) and PASSES with the fix applied.
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
    Real-compile regression gate proving the FID-12 fix opens the list-item
    wrapper of a captioned code block as `#{` (re-entering code mode)
    instead of leaking its codly config call as visible prose.

    Requirements: FID-12, GATE-01.
    """

    def test_typstpdf_captioned_listitem_wrapper_opens_with_hash(
        self, codly_caption_listitem_leak_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm, at the SOURCE
        (``.typ``) level:

        - the build exits cleanly and did not report a compile failure;
        - the list-item wrapper immediately following the captioned
          figure's markup open is ``#{`` (the ``#``-prefixed fix), NOT the
          pre-fix bare ``{`` -- asserted by the substring ``"])[\\n#{\\n"``,
          which is ABSENT pre-fix (pre-fix emits ``"])[\\n{\\n"`` instead);
        - ``index.pdf`` exists, is non-empty, and begins with the ``%PDF``
          magic bytes.
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

        assert "])[\n#{\n" in typ_text, (
            "Expected the list-item wrapper's opening brace immediately "
            "after the captioned figure's markup open to be '#{' (re-"
            "entering Typst code mode) -- pre-fix it is the bare '{' form "
            f"(FID-12 regression):\n{typ_text}"
        )
        assert "])[\n{\n" not in typ_text, (
            "Found the pre-fix bare '{' wrapper form immediately after the "
            "captioned figure's markup open -- a bare '{' inside markup "
            "mode is parsed as literal text, leaking the codly config call "
            f"as visible prose (FID-12 regression):\n{typ_text}"
        )

        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced:\n" f"stderr: {result.stderr}"
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

        - the leaked codly config text is ABSENT from extracted prose --
          neither ``"number-format"`` nor a bare ``"codly("`` call string
          appears;
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

        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced:\n" f"stderr: {result.stderr}"
        )

        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)

        assert "number-format" not in full_text, (
            "Found the leaked 'number-format' codly config token in "
            f"extracted PDF text (FID-12 regression):\n{full_text}"
        )
        assert "codly(" not in full_text, (
            "Found a leaked bare 'codly(' call string in extracted PDF "
            f"text (FID-12 regression):\n{full_text}"
        )
        assert "LISTITEMCAPSENTINEL" in full_text, (
            "Expected the code block's own sentinel identifier in "
            f"extracted PDF text (the executed code block itself):\n{full_text}"
        )
