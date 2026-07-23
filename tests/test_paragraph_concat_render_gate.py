"""
Fast, offline regression gate for the paragraph-concat block-separation fix
(Phase 19, GATE-01, FID-02).

This is the deterministic, network-free reproduction of the v0.6.1-audit
finding F1: in Typst's unified code mode, a bare source ``\\n``/``\\n\\n``
between two top-level code-mode statements is COSMETIC ONLY -- it satisfies
the parser but produces zero visual break. Consecutive paragraphs inside a
bullet ``list_item`` previously early-returned with no separator at all
(neither cosmetic newline nor block break), so their inline ``text()``
results concatenated onto one running line -- e.g. "role.For example"
instead of "role. For example" (``usage/referencing.rst``, "Suppressed
link:" item).

Fix: ``visit_paragraph`` now calls ``self._emit_forced_break("parbreak()")``
in its ``in_list_item`` branch (a no-op-safe call for the first paragraph,
since ``list_item_needs_separator`` is reset to ``False`` in
``visit_list_item``), and ``depart_paragraph`` sets
``list_item_needs_separator = True`` in its own ``in_list_item`` branch --
the piece that was previously MISSING, without which the helper never fires
a leading separator before the 2nd+ paragraph's ``parbreak()``.

Confirmed both directions: FAILS against the pre-fix translator (no
``parbreak()`` at all is emitted between the two list-item paragraphs), and
PASSES with the fix. Drives the full ``-b typstpdf`` path -- NOT
``-b typst`` -- so the emitted ``.typ`` is also proven to compile via a real
``typst.compile()``, not merely structurally correct.
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
def paragraph_concat_render_gate_dir():
    """Return the path to the paragraph_concat_render_gate fixture project."""
    return Path(__file__).parent / "fixtures" / "paragraph_concat_render_gate"


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
    reason="typst-py is required for the paragraph-concat render gate",
)
class TestParagraphConcatRenderGate:
    """
    Real-compile regression gate proving consecutive paragraphs inside a
    bullet list item render with a ``parbreak()`` separator between them,
    so ``typst.compile()`` produces a valid PDF with visible vertical
    separation between the two paragraphs.

    Requirements: FID-02 (Phase 19, GATE-01).
    """

    def test_typstpdf_list_item_paragraphs_get_parbreak_and_produce_pdf(
        self, paragraph_concat_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm:

        - the build exits cleanly;
        - the emitted ``index.typ`` contains a ``parbreak()`` statement
          separating the two paragraphs in the first bullet item (D-05
          structural assert -- this token is entirely ABSENT pre-fix, since
          the old code early-returned with no emission at all);
        - ``index.pdf`` exists, is non-empty, and starts with the ``%PDF``
          magic bytes (real ``typst.compile()`` succeeded).
        """
        result = _run_sphinx_build_typstpdf(
            paragraph_concat_render_gate_dir, temp_build_dir
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
        # parbreak() at all between the two list-item paragraphs (both
        # visit_paragraph and depart_paragraph early-return silently when
        # in_list_item), so this string is absent pre-fix and present
        # post-fix.
        assert "parbreak()" in typ_text, (
            "Expected a parbreak() separator between the two list-item "
            f"paragraphs -- the FID-02 fix is not applied:\n{typ_text}"
        )
        # The separator must sit BETWEEN the two paragraphs' own content, not
        # merely appear anywhere in the document.
        first_para_idx = typ_text.find("Suppressed link")
        second_para_idx = typ_text.find("For example, writing")
        parbreak_idx = typ_text.find("parbreak()", first_para_idx)
        assert (
            first_para_idx != -1 and second_para_idx != -1
        ), "Expected fixture text not found in emitted .typ"
        assert first_para_idx < parbreak_idx < second_para_idx, (
            "Expected a parbreak() strictly between the first and second "
            f"list-item paragraphs:\n{typ_text}"
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
