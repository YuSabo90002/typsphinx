"""
Fast, offline regression gate for the table-in-list-item separator fix
(Phase 15, GATE-02).

This is the deterministic, network-free reproduction of the sixteenth fatal
that the slow full-corpus gate (``tests/test_corpus_gate.py::TestCorpusRenderGate``)
surfaced against Sphinx's own ``doc/`` tree (2 occurrences, 1 file:
``latex.typ:2382``, also ``:2463``), after bugs #1-#15 unblocked the compile
path:

    TypstError: expected semicolon or line break
        ... text("Text styling commands:")table( ...

Root cause: a table (docutils ``table`` node, emitted as
``table(columns: N, table.header(...), ...)``) nested inside a bullet-list
item, immediately following the list item's lead-in text (mirrors
``latex.typ``'s "Text styling commands:" construct). ``visit_table``/
``depart_table`` had no ``in_list_item``/``list_item_needs_separator`` guard
-- the one block visitor omitted from the bug #4 sweep (``bullet_list``/
``literal_block``/``definition_list``/``block_quote``/``field_list`` all
already had it) -- so ``depart_table``'s ``table(`` juxtaposed directly
against the preceding text's closing ``)`` in the list item's code-mode
content block with no separator.

Fix: ``visit_table`` emits the standard list-item newline separator
(mirroring ``visit_block_quote``/``visit_field_list``) when
``in_list_item and list_item_needs_separator`` -- using ``self.body.append``
directly (NOT ``self.add_text``), since ``self.in_table`` is set True
immediately after and ``add_text()`` would misroute the newline into a stale
``table_cell_content`` list left over from a prior table on the translator
instance. ``depart_table`` sets ``list_item_needs_separator = True`` when
``in_list_item`` so a following sibling separates.

Confirmed both directions: FAILS against the pre-fix translator with the
exact ``expected semicolon or line break`` fatal on the juxtaposed
``text("Text styling commands:")table(``, and PASSES with the fix. Drives
the full ``-b typstpdf`` path -- NOT ``-b typst`` -- on purpose: the fatal
only aborts on the ``TypstPDFBuilder.finish()`` compile path, so a
``-b typst`` build would emit the invalid ``.typ`` but never compile it and
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
def table_in_list_item_render_gate_dir():
    """Return the path to the table_in_list_item_render_gate fixture."""
    return Path(__file__).parent / "fixtures" / "table_in_list_item_render_gate"


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
    reason="typst-py is required for the table-in-list-item render gate",
)
class TestTableInListItemRenderGate:
    """
    Real-compile regression gate proving the translator newline-separates a
    table from a preceding sibling lead-in text inside a list item, so
    ``typst.compile()`` does not abort with "expected semicolon or line
    break".

    Requirements: GATE-02 (Phase 15 scope expansion -- the fast offline
    reproduction of the table-in-list-item corpus fatal).
    """

    def test_typstpdf_separates_table_in_list_item_and_produces_pdf(
        self, table_in_list_item_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm:

        - the build exits cleanly (no fatal raised out of the subprocess);
        - the table nested in a list item newline-separates from the
          preceding lead-in text (no ``")table("`` juxtaposition);
        - a top-level table (not in a list item) stays byte-unchanged (no
          spurious leading newline);
        - no ``TypstCompilationError`` / "expected semicolon or line break"
          signature is logged;
        - ``index.pdf`` exists, is non-empty, and starts with the ``%PDF``
          magic bytes -- the only proof the table compiled to valid Typst and
          ``typst.compile()`` did NOT abort with the fatal that GATE-02
          surfaced against the corpus.
        """
        result = _run_sphinx_build_typstpdf(
            table_in_list_item_render_gate_dir, temp_build_dir
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
            "typst.compile() rejected the table nested in a list item -- "
            "the table-in-list-item separator fix is not in effect:\n"
            f"stderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")

        # The table nested in a list item must newline-separate from the
        # preceding "Text styling commands:" lead-in text -- no bare
        # juxtaposition (the exact fatal shape:
        # `text("Text styling commands:")table(` on one line).
        assert 'text("Text styling commands:")table(' not in typ_text, (
            "The table still juxtaposes 'Text styling commands:' directly "
            f"against a following table( inside a list item:\n{typ_text}"
        )
        assert 'text("Text styling commands:")\ntable(' in typ_text, (
            "Expected the table to newline-separate from the preceding "
            f"'Text styling commands:' lead-in text inside the list item:\n"
            f"{typ_text}"
        )

        # A top-level table (not nested in a list item) must stay
        # byte-unchanged: no list-item separator applies outside a list item,
        # so the table( emission must NOT gain a spurious leading newline.
        assert (
            'text("A table at the top level (not nested in a list item) '
            'must stay\\nbyte-unchanged by this fix.")})\n\ntable(\n'
            "  columns: (50fr, 50fr),\n" in typ_text
        ), (
            "The top-level table's rendering changed -- the list-item "
            f"separator fix must not touch it:\n{typ_text}"
        )

        # The emitted .typ must have compiled to a real, non-empty PDF.
        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted, most "
            f"likely on the juxtaposed table:\nstderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"
