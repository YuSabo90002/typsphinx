"""
Fast, offline regression gate for the confval field-body inline-concat fix
(Phase 15, GATE-02).

This is the deterministic, network-free reproduction of the eighth fatal that
the slow full-corpus gate (``tests/test_corpus_gate.py::TestCorpusRenderGate``)
surfaced against Sphinx's own ``doc/`` tree (16 occurrences, ALL in
``usage/configuration.typ``), after the static-asset-copy, target-label,
def-list-term-concat, list-item nested-block, def-list-term inline-concat,
substitution-definition, and def-list multi-block-definition fixes (bugs #1-#7)
unblocked the compile path:

    TypstError: expected semicolon or line break
        ... text("The value of ")strong({text("html_title")}) ...

Root cause (A): a confval ``:type:``/``:default:`` field body written inline on
its field line (e.g. ``:default: The value of **html_title**``) is COLLAPSED by
docutils to inline children (``Text``/``strong``/``literal``) DIRECTLY under
``field_body``, with no wrapping ``paragraph``. ``visit_field_body`` set no
concat context, so the adjacent inline expressions juxtaposed
(``text("The value of ")strong({...})``) in the code-mode content block -- two
statements with no separator -> "expected semicolon or line break".

Root cause (B): a ``definition_list`` nested in a bullet-list item, following a
paragraph, emitted ``terms(...)`` with no leading list-item separator, abutting
the preceding ``text(...)`` (``configuration.typ:2009``) -> the same fatal.

Fix: ``visit_field_body`` activates the shared inline-concat context (bug #5
machinery) for an ALL-inline field body so its children ``+``-separate into one
valid content value; a block field body (real ``paragraph`` children) keeps the
``par({...})`` path untouched. ``visit_definition_list`` emits the standard
list-item newline separator so a def-list newline-separates from a preceding
sibling inside a list item.

Confirmed both directions: FAILS against the pre-fix translator with the exact
``expected semicolon or line break`` fatal on the juxtaposed field-body inline
children, and PASSES with the fix. Drives the full ``-b typstpdf`` path -- NOT
``-b typst`` -- on purpose: the fatal only aborts on the
``TypstPDFBuilder.finish()`` compile path, so a ``-b typst`` build would emit
the invalid ``.typ`` but never compile it and thus prove nothing.
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
def confval_field_body_render_gate_dir():
    """Return the path to the confval_field_body_render_gate fixture."""
    return Path(__file__).parent / "fixtures" / "confval_field_body_render_gate"


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
    reason="typst-py is required for the confval field-body render gate",
)
class TestConfvalFieldBodyRenderGate:
    """
    Real-compile regression gate proving the translator emits a collapsed
    field body's inline children as one valid content value (``+`` separated)
    and newline-separates a def-list from a preceding sibling in a list item,
    so ``typst.compile()`` does not abort with "expected semicolon or line
    break".

    Requirements: GATE-02 (Phase 15 scope expansion -- the fast offline
    reproduction of the confval field-body corpus fatal).
    """

    def test_typstpdf_concats_collapsed_field_body_and_produces_pdf(
        self, confval_field_body_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm:

        - the build exits cleanly (no fatal raised out of the subprocess);
        - the collapsed ``:default:`` field body emits its inline children as a
          single ``+``-separated content value (no bare ``text(...)strong(``
          juxtaposition);
        - the def-list nested in a list item newline-separates from the
          preceding paragraph (no ``)terms(`` / ``")terms(`` juxtaposition);
        - a block/normal paragraph stays wrapped in ``par({...})``;
        - no ``TypstCompilationError`` / "expected semicolon or line break"
          signature is logged;
        - ``index.pdf`` exists, is non-empty, and starts with the ``%PDF`` magic
          bytes -- the only proof the field body compiled to valid Typst and
          ``typst.compile()`` did NOT abort with the fatal that GATE-02
          surfaced against the corpus.
        """
        result = _run_sphinx_build_typstpdf(
            confval_field_body_render_gate_dir, temp_build_dir
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
            "typst.compile() rejected the collapsed field body -- the "
            "field-body inline-concat fix is not in effect:\n"
            f"stderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")

        # (A) The collapsed field body must join its inline children with ' + '
        # into one content value -- and must NOT juxtapose them.
        assert 'text("The value of ") + strong({text("html_title")})' in typ_text, (
            "Expected the collapsed :default: field body to '+'-concat its "
            "inline children into one content value -- the field-body concat "
            f"fix is not applied:\n{typ_text}"
        )
        assert ")strong({text" not in typ_text, (
            "The field body still juxtaposes an inline expression against a "
            f"following strong( -- the concat fix is not in effect:\n{typ_text}"
        )

        # (B) The def-list nested in a list item must newline-separate from the
        # preceding paragraph (no text(...) directly abutting terms(...)).
        assert '")terms(' not in typ_text, (
            "A def-list still abuts a preceding paragraph inside a list item "
            f"with no separator:\n{typ_text}"
        )

        # A block/normal paragraph must stay wrapped in par({...}).
        assert "par({" in typ_text, (
            "Normal paragraphs must still be wrapped in par({...}) -- the fix "
            "must not drop par() where it is required"
        )

        # The emitted .typ must have compiled to a real, non-empty PDF.
        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted, most likely "
            f"on the juxtaposed collapsed field body:\n"
            f"stderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"
