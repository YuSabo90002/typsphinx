"""
Fast, offline regression gate for the body-less-desc block-separation fix
(Phase 19, GATE-01, FID-06).

This is the deterministic, network-free reproduction of the v0.6.1-audit
finding F15: back-to-back ``confval`` directives with only
``:type:``/``:default:`` fields (no body paragraph) render entirely inline
(no ``par()`` anywhere, since there is no body text), so consecutive such
``desc`` siblings concatenate with zero separation -- mirroring
``usage/extensions/coverage.rst``'s four back-to-back confvals, which merge
into one blob:
"coverage_c_pathType:Sequence[str]Default:()coverage_c_regexesType:dict[str,
str]Default:{}".

Fix: ``depart_desc`` now calls ``self._emit_forced_break("parbreak()")``
unconditionally, replacing the old cosmetic-only
``self.body.append("\\n\\n")``. Verified idempotent/harmless on the
with-body-content case (a confval whose last content already ends in a
``par()``) -- no double-gap artifact -- so no body-less-detection guard is
needed; the fix applies at EVERY ``depart_desc``.

Confirmed both directions: FAILS against the pre-fix translator (no
``parbreak()`` at all is emitted between the two confval ``desc`` siblings),
and PASSES with the fix. Drives the full ``-b typstpdf`` path -- NOT
``-b typst`` -- so the emitted ``.typ`` is also proven to compile via a real
``typst.compile()``.
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
def desc_bodyless_concat_render_gate_dir():
    """Return the path to the desc_bodyless_concat_render_gate fixture project."""
    return Path(__file__).parent / "fixtures" / "desc_bodyless_concat_render_gate"


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
    reason="typst-py is required for the desc-bodyless-concat render gate",
)
class TestDescBodylessConcatRenderGate:
    """
    Real-compile regression gate proving back-to-back body-less confval
    ``desc`` siblings render as visually distinct blocks separated by a
    ``parbreak()``, so ``typst.compile()`` produces a valid PDF.

    Requirements: FID-06 (Phase 19, GATE-01).
    """

    def test_typstpdf_bodyless_desc_siblings_get_parbreak_and_produce_pdf(
        self, desc_bodyless_concat_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm:

        - the build exits cleanly;
        - the emitted ``index.typ`` contains a ``parbreak()`` statement
          separating the two confval ``desc`` siblings (D-05 structural
          assert -- this token is entirely ABSENT pre-fix, since the old
          code only appended a cosmetic ``"\\n\\n"``);
        - ``index.pdf`` exists, is non-empty, and starts with the ``%PDF``
          magic bytes (real ``typst.compile()`` succeeded).
        """
        result = _run_sphinx_build_typstpdf(
            desc_bodyless_concat_render_gate_dir, temp_build_dir
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

        # D-05: structural assert -- the pre-fix translator emits NO
        # parbreak() at all between the two body-less confval desc siblings
        # (depart_desc only appended a cosmetic "\n\n"), so this string is
        # absent pre-fix and present post-fix.
        assert "parbreak()" in typ_text, (
            "Expected a parbreak() separator between the two body-less "
            f"confval desc siblings -- the FID-06 fix is not applied:\n{typ_text}"
        )
        # The separator must sit BETWEEN the two confvals' own content, not
        # merely appear anywhere in the document.
        first_confval_idx = typ_text.find("coverage_c_path")
        second_confval_idx = typ_text.find("coverage_c_regexes")
        parbreak_idx = typ_text.find("parbreak()", first_confval_idx)
        assert (
            first_confval_idx != -1 and second_confval_idx != -1
        ), "Expected fixture confval names not found in emitted .typ"
        assert first_confval_idx < parbreak_idx < second_confval_idx, (
            "Expected a parbreak() strictly between the two body-less "
            f"confval desc siblings:\n{typ_text}"
        )

        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted:\n"
            f"stderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"
