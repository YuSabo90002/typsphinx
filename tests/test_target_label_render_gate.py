"""
Fast, offline regression gate for the target-anchor emission fix
(Phase 15, GATE-02).

This is the deterministic, network-free reproduction of the fatal that the slow
full-corpus gate (``tests/test_corpus_gate.py::TestCorpusRenderGate``) surfaced
against Sphinx's own ``doc/`` tree (``usage/installation.typ``), after the
static-asset-copy fix unblocked the compile path:

    TypstError: expected semicolon or line break
        label("id1")label("id2")

Root cause: ``TypstTranslator.visit_target`` emitted a bare code-mode
``label("id")``. Two consecutive ``target`` nodes -- e.g. the two anonymous
hyperlink targets (``__ https://...``) that close a ``.. tip::`` block --
then produced ``label("id1")label("id2")`` with no separator, which is a Typst
syntax error inside a ``{...}`` content block. A bare label is additionally a
raw label *value* that "cannot join content with label" even singly, and a
single anchor directly followed by a paragraph produced the sibling ``]par(``
adjacency.

Fix: emit a metadata-carrying markup anchor ``[#metadata(none) <id>]`` wrapped
in newlines (matching the extra-id anchors ``visit_title`` already emits) --
genuine content with the label attached, which joins/concatenates cleanly,
works singly and consecutively, and stays reachable via ``link(<id>)``.

Confirmed both directions: FAILS against the pre-fix translator with the exact
``expected semicolon or line break`` fatal on ``label("id1")label("id2")``, and
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
def target_label_render_gate_dir():
    """Return the path to the target_label_render_gate fixture project."""
    return Path(__file__).parent / "fixtures" / "target_label_render_gate"


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
    reason="typst-py is required for the target-label render gate",
)
class TestTargetLabelRenderGate:
    """
    Real-compile regression gate proving the translator emits a valid,
    referenceable Typst anchor for consecutive target nodes (and for an anchor
    directly followed by a paragraph), so ``typst.compile()`` does not abort
    with "expected semicolon or line break".

    Requirements: GATE-02 (Phase 15 scope expansion -- the fast offline
    reproduction of the adjacent-label corpus fatal).
    """

    def test_typstpdf_emits_valid_anchors_and_produces_pdf(
        self, target_label_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm:

        - the build exits cleanly (no fatal raised out of the subprocess);
        - the emitted master ``.typ`` contains NO bare ``label("...")`` anchor
          and instead uses the ``[#metadata(none) <id>]`` markup form;
        - ``index.pdf`` exists, is non-empty, and starts with the ``%PDF`` magic
          bytes -- the only proof the two adjacent anchors emitted valid Typst
          and ``typst.compile()`` did NOT abort with the "expected semicolon or
          line break" fatal that GATE-02 surfaced against the corpus.
        """
        result = _run_sphinx_build_typstpdf(
            target_label_render_gate_dir, temp_build_dir
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
            "typst.compile() rejected adjacent anchors -- the target-anchor fix "
            f"is not in effect:\nstderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )

        # The emitted master .typ must use the metadata-label anchor form, never
        # a bare code-mode label("...") (the construct that caused the fatal).
        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")
        assert (
            "[#metadata(none) <" in typ_text
        ), "Expected the target to emit a [#metadata(none) <id>] markup anchor"
        assert 'label("id1")label("id2")' not in typ_text, (
            "The emitted .typ still contains adjacent bare label() anchors -- "
            "the fix is not applied"
        )

        # The emitted .typ must have compiled to a real, non-empty PDF.
        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted, most likely "
            f"on adjacent bare label() anchors:\nstderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"
