"""
Real-compile regression gate for the inline-image-separator fix
(Phase 62, IMG-08, IMG-09, IMG-10, TEST-05).

An image node preceded by any sibling content in its container was emitted
adjacent to the preceding code-mode expression -- no separator at all --
so Typst refused the whole document with ``expected semicolon or line
break`` and ``TypstPDFBuilder.finish()`` raised ``ExtensionError``,
writing NO PDF for any master (including image-free masters that only
``#include()`` the poisoned content file transitively).

This is the tracer slice of the phase (62-01-PLAN.md): one failing shape
(``fail_01_sub_mid_sentence``, FEATURES.md Q1 row 1) and one
must-keep-passing shape (``pass_a_standalone_block_image``, FEATURES.md
Q2 row A), plus the image-free ``index`` root master that proves the
``#include()`` blast radius is closed. The full 16 FAIL / 9 PASS matrix
is completed in plan 02.

Drives the full ``-b typstpdf`` path via a real ``typst.compile()`` --
NOT merely a structural/string check on the emitted ``.typ`` -- text-mode
reads with an explicit utf-8 encoding on both sides, never a binary read,
so a build's Windows CR-newline write-mode translation cannot spuriously
fail this gate.
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


@pytest.fixture
def inline_image_separator_render_gate_dir():
    """Return the path to the inline_image_separator_render_gate fixture project."""
    return Path(__file__).parent / "fixtures" / "inline_image_separator_render_gate"


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


# Module constants (62-01 tracer subset; extended to the full 16/9 matrix in
# plan 02).
FAIL_DOCNAMES = ["fail_01_sub_mid_sentence"]
PASS_DOCNAMES = ["pass_a_standalone_block_image"]
ALL_MASTER_DOCNAMES = ["index"] + FAIL_DOCNAMES + ["pass_parent"]


def _wrapper_pdf_path(build_dir: Path, docname: str) -> Path:
    """Return the expected wrapper PDF path for a master docname."""
    return build_dir / f"{docname}-out.pdf"


def _assert_pdf_magic(path: Path) -> None:
    """Assert ``path`` is a non-empty file starting with the PDF magic bytes."""
    assert path.exists(), f"{path} was not produced"
    assert path.stat().st_size > 0, f"{path} is empty"
    with open(path, "rb") as f:
        magic = f.read(4)
        assert magic == b"%PDF", f"{path} is not a valid PDF (magic: {magic!r})"


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the inline-image-separator render gate",
)
class TestInlineImageSeparatorFullMatrix:
    """
    Proves every master in the tracer fixture -- including the image-free
    ``index`` root master -- writes a valid PDF post-fix (IMG-08, IMG-09).
    """

    def test_full_matrix_every_master_writes_a_pdf(
        self, inline_image_separator_render_gate_dir, temp_build_dir
    ):
        result = _run_sphinx_build_typstpdf(
            inline_image_separator_render_gate_dir, temp_build_dir
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

        for docname in ALL_MASTER_DOCNAMES:
            pdf_path = _wrapper_pdf_path(temp_build_dir, docname)
            _assert_pdf_magic(pdf_path)


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the inline-image-separator render gate",
)
class TestInlineImageSeparatorFailShapes:
    """
    Structural proof that the FAIL shape's emitted content no longer
    juxtaposes a closing paren directly against ``image(`` -- the exact
    unseparated-expression shape the pre-fix defect produced.
    """

    def test_fail_shape_emits_a_separator_before_image(
        self, inline_image_separator_render_gate_dir, temp_build_dir
    ):
        result = _run_sphinx_build_typstpdf(
            inline_image_separator_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        content_typ = temp_build_dir / "fail_01_sub_mid_sentence.typ"
        assert content_typ.exists(), "fail_01_sub_mid_sentence.typ was not emitted"
        body = content_typ.read_text(encoding="utf-8")

        assert ")image(" not in body, (
            "Found an unseparated closing-paren-then-image( juxtaposition -- "
            f"the IMG-08 fix is not applied:\n{body}"
        )
