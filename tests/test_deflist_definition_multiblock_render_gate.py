"""
Fast, offline regression gate for the def-list multi-block-definition fix
(Phase 15, GATE-02).

This is the deterministic, network-free reproduction of the seventh fatal that
the slow full-corpus gate (``tests/test_corpus_gate.py::TestCorpusRenderGate``)
surfaced against Sphinx's own ``doc/`` tree
(``usage/restructuredtext/directives.typ:1718`` plus ~16 other compiled ``.typ``
files), after the static-asset-copy, target-label, def-list-term-concat,
list-item nested-block, def-list-term inline-concat, and
substitution-definition fixes (bugs #1-#6) unblocked the compile path:

    TypstError: expected comma
        ... terms.item(TERM, par({...})<blank line>codly(...) ...) ...

Root cause: ``depart_definition`` ``''.join()``s a definition's block-level
children (``par({...})`` + blank line + ``codly(...)`` + a backtick fence +
blank line + ``list({...})``) into a bare, blank-line-separated statement blob
and passed it UNWRAPPED as ``terms.item``'s 2nd argument. Blank-line separation
of sequential content is valid only at document top level; as a function
argument Typst reads the first statement ``par({...})`` as the WHOLE argument
and then expects a comma at the next bare statement (``codly(...)``/a fence/
``list({...})``) -> "expected comma".

Fix: the ``terms.item`` assembly (``depart_definition_list``) wraps the
definition (2nd) arg in a ``{ ... }`` content block, so Typst auto-joins the
block statements into one content value -- a valid single argument. A
single-block definition wraps to ``{par({...})}`` and renders identically. The
TERM (1st arg) ``+``-concat path and the list-item block-separation path are
untouched.

Confirmed both directions: FAILS against the pre-fix translator with the exact
``expected comma`` fatal on the unwrapped multi-block definition, and PASSES
with the fix. Drives the full ``-b typstpdf`` path -- NOT ``-b typst`` -- on
purpose: the fatal only aborts on the ``TypstPDFBuilder.finish()`` compile path,
so a ``-b typst`` build would emit the invalid ``.typ`` but never compile it and
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


@pytest.fixture
def deflist_definition_multiblock_render_gate_dir():
    """Return the path to the deflist_definition_multiblock_render_gate fixture."""
    return (
        Path(__file__).parent / "fixtures" / "deflist_definition_multiblock_render_gate"
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
    reason="typst-py is required for the def-list multi-block definition gate",
)
class TestDeflistDefinitionMultiblockRenderGate:
    """
    Real-compile regression gate proving the translator wraps a definition with
    multiple block children in a single ``{ ... }`` content block, so
    ``typst.compile()`` does not abort with "expected comma".

    Requirements: GATE-02 (Phase 15 scope expansion -- the fast offline
    reproduction of the multi-block-definition corpus fatal).
    """

    def test_typstpdf_wraps_multiblock_definition_and_produces_pdf(
        self, deflist_definition_multiblock_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm:

        - the build exits cleanly (no fatal raised out of the subprocess);
        - the emitted master ``.typ`` passes the multi-block definition as a
          single ``{ ... }``-wrapped 2nd argument to ``terms.item(`` (so the
          paragraph + code fence + list join into one content value);
        - no ``TypstCompilationError`` / "expected comma" signature is logged;
        - ``index.pdf`` exists, is non-empty, and starts with the ``%PDF`` magic
          bytes -- the only proof the multi-block definition compiled to valid
          Typst and ``typst.compile()`` did NOT abort with the "expected comma"
          fatal that GATE-02 surfaced against the corpus.
        """
        result = _run_sphinx_build_typstpdf(
            deflist_definition_multiblock_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        # A fatal inside TypstPDFBuilder.finish() is logged (not raised) as an
        # ERROR, so guard against the exact signatures explicitly rather than
        # trusting returncode alone.
        assert "expected comma" not in result.stderr, (
            "typst.compile() rejected the multi-block definition -- the "
            "definition-arg wrap fix is not in effect:\n"
            f"stderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")

        # The definition must be passed as a single {...}-wrapped argument, i.e.
        # terms.item(<term>, {par(...) ... codly(...) ... list(...) }). Assert
        # the wrapped-arg boundary directly, and that the paragraph, code fence,
        # and list all live inside that one content block.
        assert ", {par(" in typ_text, (
            "Expected the definition to be passed as a single "
            "'{ ... }'-wrapped 2nd argument to terms.item( -- the wrap fix is "
            f"not applied:\n{typ_text}"
        )
        assert "codly(" in typ_text and "list({" in typ_text, (
            "The multi-block definition should still emit its code fence and "
            "bullet list inside the wrapped content block"
        )

        # The emitted .typ must have compiled to a real, non-empty PDF.
        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted, most likely "
            f"on the unwrapped multi-block definition:\n"
            f"stderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"
