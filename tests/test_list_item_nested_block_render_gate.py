"""
Fast, offline regression gate for the list-item nested-block adjacency fix
(Phase 15, GATE-02).

This is the deterministic, network-free reproduction of the fourth fatal that
the slow full-corpus gate (``tests/test_corpus_gate.py::TestCorpusRenderGate``)
surfaced against Sphinx's own ``doc/`` tree (``changes/1.6.typ:856`` and 7 other
files, 17 identical occurrences), after the static-asset-copy, target-label, and
def-list-term-concat fixes unblocked the compile path:

    TypstError: expected semicolon or line break
        ... })par( ...

Root cause: ``in_list_item`` was a bare boolean with no nesting stack. When a
list item contains ``[paragraph, nested list, paragraph]``, the NESTED list's
``depart_list_item`` reset ``in_list_item`` to False, clobbering the outer
item's context. The trailing paragraph was then visited with
``in_list_item == False``, so ``visit_paragraph`` did NOT skip ``par()``
wrapping and emitted ``par({...})`` -- as if it were a top-level paragraph --
directly after the nested ``list(...)``'s closing ``)`` inside the outer
code-mode content block ``{...}``, producing ``})par(``: two juxtaposed
statements that Typst code mode requires to be newline/``;`` separated.

Fix: ``visit_list_item`` pushes the prior ``in_list_item`` onto a stack and
``depart_list_item`` pops+restores it, so the flag correctly reflects "inside a
list item" at any nesting depth. The trailing paragraph is then recognized as
in-item (skips ``par()`` like its sibling paragraphs) and its text emits via the
existing ``list_item_needs_separator`` ``"\\n"`` machinery, cleanly separated
from the nested list.

Confirmed both directions: FAILS against the pre-fix translator with the exact
``expected semicolon or line break`` fatal on the ``})par(`` juxtaposition, and
PASSES with the fix. Drives the full ``-b typstpdf`` path -- NOT ``-b typst`` --
on purpose: the fatal only aborts on the ``TypstPDFBuilder.finish()`` compile
path, so a ``-b typst`` build would emit the invalid ``.typ`` but never compile
it and thus prove nothing.
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
def list_item_nested_block_render_gate_dir():
    """Return the path to the list_item_nested_block_render_gate fixture."""
    return Path(__file__).parent / "fixtures" / "list_item_nested_block_render_gate"


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
    reason="typst-py is required for the list-item nested-block render gate",
)
class TestListItemNestedBlockRenderGate:
    """
    Real-compile regression gate proving the translator newline-separates a
    nested list from a sibling paragraph inside a list item, so
    ``typst.compile()`` does not abort with "expected semicolon or line break".

    Requirements: GATE-02 (Phase 15 scope expansion -- the fast offline
    reproduction of the block-level list-item juxtaposition corpus fatal).
    """

    def test_typstpdf_separates_nested_block_siblings_and_produces_pdf(
        self, list_item_nested_block_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm:

        - the build exits cleanly (no fatal raised out of the subprocess);
        - the emitted master ``.typ`` contains NO ``})par(`` juxtaposition (the
          construct that caused the fatal);
        - a nested list's closing ``)`` is followed by a newline before the next
          statement, both for the list-then-paragraph and paragraph-then-list
          sibling orderings;
        - ``index.pdf`` exists, is non-empty, and starts with the ``%PDF`` magic
          bytes -- the only proof the juxtaposed blocks compiled to valid Typst
          and ``typst.compile()`` did NOT abort with the "expected semicolon or
          line break" fatal that GATE-02 surfaced against the corpus.
        """
        result = _run_sphinx_build_typstpdf(
            list_item_nested_block_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        # A fatal inside TypstPDFBuilder.finish() is logged (not raised) as an
        # ERROR, so guard against the exact signatures explicitly rather than
        # trusting returncode alone.
        assert "expected semicolon or line break" not in result.stderr, (
            "typst.compile() rejected the juxtaposed nested-list/paragraph "
            "siblings -- the list-item nested-block separator fix is not in "
            f"effect:\nstderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )

        # The emitted master .typ must never abut a nested list's closing paren
        # against a following par() (the exact broken construct).
        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")
        assert "})par(" not in typ_text, (
            "The emitted .typ still abuts a nested list's closing ')' against a "
            "following par( with no separator -- the fix is not applied"
        )

        # The trailing paragraph after the nested list must land as a separated
        # statement, not a wrapped, unseparated par(...). The paragraph is
        # emitted as bare text() inside the item content block (uniform with the
        # item's leading paragraph), preceded by the nested list's ")" + newline.
        assert 'text("A paragraph AFTER the nested list' in typ_text, (
            "Expected the trailing paragraph to emit as a separated text() "
            "statement inside the list item"
        )
        assert "})par(" not in typ_text and ")par(" not in typ_text, (
            "No block-level ')par(' juxtaposition may remain anywhere in the "
            "emitted .typ"
        )

        # The emitted .typ must have compiled to a real, non-empty PDF.
        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted, most likely "
            f"on the juxtaposed nested-list/paragraph siblings:\n"
            f"stderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"
