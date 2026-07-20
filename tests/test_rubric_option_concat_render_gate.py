"""
Fast, offline regression gate for the rubric/option-heading concat/newline
fix (Phase 19, FID-04).

Deterministic, network-free reproduction of the corpus symptom seen at
``man/sphinx-quickstart.typ`` ("Structure Options" rubric directly followed
by the ``--sep`` option's ``strong({...})``) and
``usage/restructuredtext/directives.typ`` ("Options" rubric directly
followed by the ``:class:`` field's ``strong({...})``): both render via
``strong()`` delegation, and a bare cosmetic ``"\\n"`` between them produces
NO visual break in Typst's unified code-mode block, so the rubric heading
merges onto the same line as the first following option/field.

Fix: ``depart_rubric`` now emits a real Typst ``linebreak()`` (via the
shared ``_emit_forced_break`` helper from Plan 01) unconditionally after
the rubric's own ``strong({...})`` closes -- a rubric always needs
separation from what follows. One fix at ``depart_rubric`` covers both
corpus sub-cases, since both render the following construct via
``strong()`` as well.

Confirmed both directions: FAILS against the pre-fix translator (no
``linebreak()`` between the rubric and the following option in
``index.typ``), PASSES with the fix. Drives the full ``-b typstpdf`` path
-- NOT ``-b typst`` -- so the fixture also proves the emitted markup
compiles to a real ``%PDF`` (D-05/D-06).
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
def rubric_option_concat_render_gate_dir():
    """Return the path to the rubric_option_concat_render_gate fixture project."""
    return Path(__file__).parent / "fixtures" / "rubric_option_concat_render_gate"


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
    reason="typst-py is required for the rubric-option-concat render gate",
)
class TestRubricOptionConcatRenderGate:
    """
    Real-compile regression gate proving a rubric option-group heading
    (FID-04) renders separated from the immediately-following option/field
    instead of merging onto the same line, and that a rubric at true
    end-of-document still compiles cleanly.

    Requirements: FID-04.
    """

    def test_typstpdf_rubric_option_produces_pdf(
        self, rubric_option_concat_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm:

        - the build exits cleanly and the compile did not fail (this alone
          proves the true end-of-document rubric -- "Trailing Heading",
          which has nothing after its own trailing linebreak() -- compiles
          without error);
        - the emitted ``index.typ`` contains a ``linebreak()`` token between
          the "Structure Options" rubric's ``strong({...})`` and the
          following ``--sep`` option's ``strong({...})`` (D-05: pre-fix the
          translator emits NO ``linebreak()`` at this site at all);
        - ``index.pdf`` exists, is non-empty, and starts with the ``%PDF``
          magic bytes (real ``typst.compile()`` succeeded, including the
          trailing end-of-document rubric).
        """
        result = _run_sphinx_build_typstpdf(
            rubric_option_concat_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure -- likely "
            "the rubric's linebreak() abutted an adjacent statement with no "
            f"separator (Pitfall 1):\nstderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")

        # D-05: structural assert -- the rubric's strong({...}) must be
        # followed by a linebreak() token BEFORE the next option's own
        # strong({...}), on the path between the two.
        rubric_idx = typ_text.index('strong({text("Structure Options")})')
        option_idx = typ_text.index('strong({text("--sep")})')
        assert option_idx > rubric_idx, (
            "Expected the '--sep' option signature to follow the rubric "
            f"heading in document order:\n{typ_text}"
        )
        between = typ_text[rubric_idx:option_idx]
        assert "linebreak()" in between, (
            "Expected a linebreak() separator between the rubric heading "
            "and the following option -- the FID-04 fix is not applied:\n"
            f"{between}"
        )

        # The true end-of-document rubric ("Trailing Heading") must also
        # emit its own trailing linebreak() (unconditional, per RESEARCH
        # Site 3) with nothing after it -- and the build above already
        # proved this compiles cleanly.
        trailing_idx = typ_text.index('strong({text("Trailing Heading")})')
        trailing_region = typ_text[trailing_idx : trailing_idx + 120]
        assert "linebreak()" in trailing_region, (
            "Expected the end-of-document rubric to also emit its own "
            f"trailing linebreak():\n{trailing_region}"
        )

        # The emitted .typ must have compiled to a real, non-empty PDF.
        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() likely aborted "
            f"on a stranded statement boundary:\nstderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"
