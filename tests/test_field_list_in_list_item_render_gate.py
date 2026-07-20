"""
Fast, offline regression gate for the field-list-in-list-item separator fix
(Phase 15, GATE-02).

This is the deterministic, network-free reproduction of the twelfth fatal
that the slow full-corpus gate (``tests/test_corpus_gate.py::TestCorpusRenderGate``)
surfaced against Sphinx's own ``doc/`` tree (1 occurrence, 1 file:
``usage/advanced/intl.typ:391``), after bugs #1-#11 unblocked the compile
path:

    TypstError: expected semicolon or line break
        ... text("For example:")strong( ...

Root cause: a field list (``:Organization ID:``/``:Project ID:``/
``:Project URL:``) nested inside an enumerated-list item, following a "For
example:" paragraph (mirrors ``usage/advanced/intl.rst:245-256``).
``visit_field_list`` was a bare ``pass`` with no ``in_list_item``/
``list_item_needs_separator`` guard -- the one block visitor omitted from the
bug #4 sweep (``bullet_list``/``literal_block``/``definition_list``/
``block_quote`` all already had it) -- so ``visit_field_name``'s ``strong(``
juxtaposed directly against the preceding paragraph's closing ``)`` in the
list item's code-mode content block with no separator.

Fix: ``visit_field_list`` emits the standard list-item newline separator
(mirroring ``visit_block_quote``/``visit_definition_list``) when
``in_list_item and list_item_needs_separator``; ``depart_field_list`` sets
``list_item_needs_separator = True`` when ``in_list_item`` so a following
sibling separates. ``visit_field_name``/``visit_field_body`` (bug #8's
collapsed-inline-field-body machinery) are untouched.

Confirmed both directions: FAILS against the pre-fix translator with the
exact ``expected semicolon or line break`` fatal on the juxtaposed
``text("For example:")strong(``, and PASSES with the fix. Drives the full
``-b typstpdf`` path -- NOT ``-b typst`` -- on purpose: the fatal only aborts
on the ``TypstPDFBuilder.finish()`` compile path, so a ``-b typst`` build
would emit the invalid ``.typ`` but never compile it and thus prove nothing.
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
def field_list_in_list_item_render_gate_dir():
    """Return the path to the field_list_in_list_item_render_gate fixture."""
    return Path(__file__).parent / "fixtures" / "field_list_in_list_item_render_gate"


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
    reason="typst-py is required for the field-list-in-list-item render gate",
)
class TestFieldListInListItemRenderGate:
    """
    Real-compile regression gate proving the translator newline-separates a
    field list from a preceding sibling paragraph inside a list item, so
    ``typst.compile()`` does not abort with "expected semicolon or line
    break".

    Requirements: GATE-02 (Phase 15 scope expansion -- the fast offline
    reproduction of the field-list-in-list-item corpus fatal).
    """

    def test_typstpdf_separates_field_list_in_list_item_and_produces_pdf(
        self, field_list_in_list_item_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm:

        - the build exits cleanly (no fatal raised out of the subprocess);
        - the field list nested in a list item newline-separates from the
          preceding paragraph (no ``")strong("`` juxtaposition);
        - a top-level field list (not in a list item) stays byte-unchanged
          (no spurious leading newline);
        - no ``TypstCompilationError`` / "expected semicolon or line break"
          signature is logged;
        - ``index.pdf`` exists, is non-empty, and starts with the ``%PDF``
          magic bytes -- the only proof the field list compiled to valid
          Typst and ``typst.compile()`` did NOT abort with the fatal that
          GATE-02 surfaced against the corpus.
        """
        result = _run_sphinx_build_typstpdf(
            field_list_in_list_item_render_gate_dir, temp_build_dir
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
            "typst.compile() rejected the field list nested in a list item -- "
            "the field-list-in-list-item separator fix is not in effect:\n"
            f"stderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")

        # The field list nested in a list item must newline-separate from the
        # preceding "For example:" paragraph -- no bare juxtaposition (the
        # exact fatal shape: `text("For example:")strong(` on one line).
        assert 'text("For example:")strong(' not in typ_text, (
            "The field list still juxtaposes 'For example:' directly against "
            f"a following strong( inside a list item:\n{typ_text}"
        )
        assert 'text("For example:")\nstrong(text("Organization ID")' in typ_text, (
            "Expected the field list to newline-separate from the preceding "
            f"'For example:' paragraph inside the list item:\n{typ_text}"
        )

        # A top-level field list (not nested in a list item) must stay
        # unchanged with respect to the LIST-ITEM SEPARATOR fix under test
        # here: no list-item separator applies outside a list item, so
        # field_name's strong( must NOT gain a spurious leading newline.
        # The trailing colon form below is intentionally the FID-09
        # colon-space form (a space after the colon inside text(...)),
        # not the old no-space colon -- that change is a deliberate,
        # codebase-wide edit to depart_field_name (Phase 20 Plan 02), not a
        # regression of the list-item separator this test actually verifies.
        assert 'strong(text("Author") + text(": "))' in typ_text, (
            "The top-level field list's field-name rendering changed -- the "
            f"list-item separator fix must not touch it:\n{typ_text}"
        )

        # The emitted .typ must have compiled to a real, non-empty PDF.
        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted, most "
            f"likely on the juxtaposed field list:\nstderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"
