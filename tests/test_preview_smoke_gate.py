"""
CI-02 preview-package smoke gate (Phase 9).

The existing ``tests/test_pdf_render_gate.py`` (Phase 8.1's D-04 gate) already
runs a real ``typst compile`` cross-OS inside the matrix, but its fixture only
exercises admonitions (gentle-clues). The historical ``kai`` break lived in
**mitex** -- whose ``mi()``/``mitex()`` functions are only invoked when a
``.. math::`` directive or ``:math:`` role is present in the source. That
gate's fixture has neither, so it would NOT catch a mitex regression.

This module closes that gap: it compiles ``tests/fixtures/preview_smoke``
(which exercises all four bundled ``@preview`` packages -- codly,
codly-languages, mitex, gentle-clues -- via real function calls, not just
their ``#import`` statements) with ``sphinx-build`` -> ``typst.compile()``,
and lets any ``typst.TypstError`` (e.g. ``unknown variable: kai``) propagate
and fail the test loudly with the real Typst error message.

Unlike the D-04 render gate, no PDF text-extraction is performed here --
compile success (a real ``typst.compile()`` call completing without raising)
is the signal, not the rendered text content. See 09-RESEARCH.md "CI-02:
Smoke Test Design" and 09-PATTERNS.md for the full rationale.
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
def fixtures_dir():
    """Return the path to tests/fixtures/ directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def preview_smoke_dir(fixtures_dir):
    """Return the path to the preview_smoke fixture project."""
    return fixtures_dir / "preview_smoke"


@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for build output."""
    return tmp_path / "_build"


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the CI-02 preview-package smoke gate",
)
def test_preview_smoke_all_four_packages_compile(preview_smoke_dir, temp_build_dir):
    """
    Compile the preview_smoke fixture and confirm the four bundled
    @preview packages (codly, codly-languages, mitex, gentle-clues) all
    compile successfully when actually invoked (not merely imported).

    Requirements: CI-02 (09-RESEARCH.md, 09-PATTERNS.md).
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
            str(preview_smoke_dir),
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

    # 2. Compile the emitted .typ to PDF with typst-py. No try/except
    # wrapper: an uncaught typst.TypstError (e.g. "unknown variable: kai")
    # is the intended, loudest failure signal -- it fails the test with
    # the real Typst error message in the traceback.
    pdf_output = temp_build_dir / "index.pdf"
    typst.compile(str(index_typ), output=str(pdf_output))

    assert pdf_output.exists(), "PDF file was not created"
    assert pdf_output.stat().st_size > 0, "PDF file is empty"
