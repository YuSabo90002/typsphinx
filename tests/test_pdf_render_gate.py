"""
D-04 real-render acceptance gate for the admonition rendering fix (Phase 08.1).

This is the only place the original bug was ever visible: the translator's
loose in-process substring asserts (e.g. ``"info[" in output``) passed even
while the admonition body rendered as literal Typst source once compiled to
PDF. This module closes that gap by running the full pipeline for real:

    sphinx-build -b typst  ->  typst.compile()  ->  pypdf text-extraction

and asserting that none of the literal-source leak signatures (the
paragraph-call / text-call / raw-call open-paren forms) appear in the
extracted PDF prose.
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

try:
    import pypdf

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

# The literal-source-leak signatures from the Phase 7 deferred-items.md
# symptom (see 08.1-RESEARCH.md "D-04: PDF text-extraction acceptance gate").
# These three token strings appear only as this test's own negative-search
# literals -- they are NOT expected in any source file's body prose.
LEAK_SIGNATURES = ("par({", 'text("', 'raw("')


@pytest.fixture
def fixtures_dir():
    """Return the path to tests/fixtures/ directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def admonition_render_gate_dir(fixtures_dir):
    """Return the path to the admonition_render_gate fixture project."""
    return fixtures_dir / "admonition_render_gate"


@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for build output."""
    return tmp_path / "_build"


@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the D-04 render gate",
)
class TestAdmonitionPdfRenderGate:
    """
    Real-compile acceptance gate for the admonition markup/code-mode fix.

    Requirements: D-04 (08.1-RESEARCH.md, 08.1-VALIDATION.md).
    """

    def test_admonition_pdf_has_no_literal_source_leak(
        self, admonition_render_gate_dir, temp_build_dir
    ):
        """
        Compile the admonition render-gate fixture to PDF and confirm the
        extracted text contains typeset prose, not literal Typst source.
        """
        # 1. sphinx-build -b typst on the fixture.
        #
        # Invoked as `sys.executable -m sphinx` (the sphinx-build console
        # entry point's module form) rather than shelling out to `uv run
        # sphinx-build`: this guarantees the exact interpreter/venv already
        # running this test is reused, with no dependency on external PATH
        # resolution of a `uv` executable. This matters in this project's
        # dev sandbox specifically -- a stray non-Nix `uv` binary installed
        # into `.venv/bin` (shadowing the correct Nix-provided `uv` earlier
        # on PATH for subprocess children) makes `["uv", "run", ...]` exit
        # 127 ("Could not start dynamically linked executable") when invoked
        # from inside a pytest-launched subprocess, even though the same
        # command succeeds when run directly in a shell. `sys.executable -m
        # sphinx` sidesteps that PATH-shadowing hazard entirely.
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "sphinx",
                "-b",
                "typst",
                str(admonition_render_gate_dir),
                str(temp_build_dir),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"sphinx-build failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        index_typ = temp_build_dir / "index.typ"
        assert index_typ.exists(), "index.typ was not generated"

        # 2. Compile the emitted .typ to PDF with typst-py.
        pdf_output = temp_build_dir / "index.pdf"
        typst.compile(str(index_typ), output=str(pdf_output))

        assert pdf_output.exists(), "PDF file was not created"
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

        # 3. Extract text with pypdf and assert no literal-source leak.
        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)

        for leaked_token in LEAK_SIGNATURES:
            assert leaked_token not in full_text, (
                f"Literal Typst source '{leaked_token}' leaked into rendered "
                "PDF text -- admonition markup/code-mode mismatch regression"
            )
