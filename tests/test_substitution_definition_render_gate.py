"""
Fast, offline regression gate for the substitution_definition SkipNode fix
(Phase 15, GATE-02).

This is the deterministic, network-free reproduction of the fatal that the
slow full-corpus gate (``tests/test_corpus_gate.py::TestCorpusRenderGate``)
surfaced against Sphinx's own ``doc/`` tree (``usage/restructuredtext/...``
-> ``latex.typ:1507``, source ``latex.rst:1131+``), after bugs #1-#5 (asset
copy, target label, def-list-term concat, list-item nested-block adjacency,
string-literal escape) were fixed and the compile path advanced further:

    error: expected comma
       |-- latex.typ:1507   (source: latex.rst:1131+)

Root cause: ``TypstTranslator`` had no ``visit_substitution_definition``
handler. A ``substitution_definition`` node (from rST
``.. |name| replace:: <content>``) fell through to ``unknown_visit``, which
logs a warning but does NOT raise ``SkipNode`` -- so the translator kept
descending into the node's inline ``literal``/``text`` children and emitted
them via the normal visitor paths at document top level. A definition with
several adjacent inline children (e.g. three ``literal`` nodes joined by
``text`` separators) produced juxtaposed top-level code-mode expressions with
no separator -- ``raw("a")text(", ")raw("b")...`` -- a Typst syntax error.

Fix: add ``visit_substitution_definition`` raising ``nodes.SkipNode``,
matching docutils/Sphinx's own HTML and LaTeX writers (both skip this node
entirely -- its content is injected at ``substitution_reference`` use sites
by a docutils transform that runs BEFORE the writer, so the definition node
itself must produce no output).

Confirmed both directions: FAILS against the pre-fix translator with the
exact top-level juxtaposition leak (and, in the corpus, the "expected comma"/
"expected semicolon or line break" fatal); PASSES with the fix. Drives the
full ``-b typstpdf`` path -- NOT ``-b typst`` -- on purpose: the fatal only
aborts on the ``TypstPDFBuilder.finish()`` compile path, so a ``-b typst``
build would emit the invalid ``.typ`` but never compile it and thus prove
nothing.
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

try:
    import pypdf

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

# The definition-leak signature this test guards against: the substitution
# definition's three inline children emitted as bare juxtaposed top-level
# expressions immediately followed by the next block's par( -- exactly the
# construct that produced "expected comma"/"expected semicolon or line
# break" in the pre-fix translator.
DEFINITION_LEAK_SIGNATURE = (
    'raw("SUBSTLITERALALPHA")text(", ")raw("SUBSTLITERALBETA")'
    'text(", ")raw("SUBSTLITERALGAMMA")par('
)

SUBST_USE_SENTINEL = "SUBSTUSESENTINEL"
SUBST_LITERAL_TOKENS = (
    "SUBSTLITERALALPHA",
    "SUBSTLITERALBETA",
    "SUBSTLITERALGAMMA",
)


@pytest.fixture
def substitution_definition_render_gate_dir():
    """Return the path to the substitution_definition_render_gate fixture."""
    return Path(__file__).parent / "fixtures" / "substitution_definition_render_gate"


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
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the substitution "
    "definition render gate",
)
class TestSubstitutionDefinitionRenderGate:
    """
    Real-compile regression gate proving ``visit_substitution_definition``
    skips the definition node (no output of its own, no unknown_visit
    warning) while a ``|name|`` use elsewhere in the body still renders the
    replacement content.

    Requirements: GATE-02 (Phase 15 scope expansion -- the fast offline
    reproduction of the substitution_definition corpus fatal).
    """

    def test_typstpdf_skips_definition_and_renders_use_site(
        self, substitution_definition_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm:

        - the build exits cleanly with NO ``unknown node type`` warning for
          ``substitution_definition`` (the handler is now registered);
        - the emitted master ``.typ`` contains NO top-level juxtaposed
          ``raw(...)raw(...)`` leak from the definition (the exact
          pre-fix signature);
        - ``index.pdf`` exists, is non-empty, and starts with the ``%PDF``
          magic bytes -- proof ``typst.compile()`` did NOT abort with the
          "expected comma"/"expected semicolon or line break" fatal that
          GATE-02 surfaced against the corpus;
        - the substitution's replacement content (all three literal tokens)
          appears in the extracted PDF text, at the ``|substthings|`` use
          site, exactly once each -- proof the definition produced no output
          of its own while the use site still resolved and rendered.
        """
        result = _run_sphinx_build_typstpdf(
            substitution_definition_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        # No unknown_visit warning for substitution_definition -- the
        # handler is registered so the node no longer falls through.
        assert "substitution_definition" not in result.stderr, (
            "Expected no 'unknown node type' warning naming "
            "substitution_definition -- visit_substitution_definition is "
            f"not in effect:\nstderr: {result.stderr}"
        )

        # A fatal inside TypstPDFBuilder.finish() is logged (not raised) as
        # an ERROR, so guard against the exact signatures explicitly rather
        # than trusting returncode alone.
        for fatal_signature in (
            "expected comma",
            "expected semicolon or line break",
            "Typst compilation failed",
        ):
            assert fatal_signature not in result.stderr, (
                f"typst.compile() rejected the output ('{fatal_signature}') "
                "-- the substitution_definition SkipNode fix is not in "
                f"effect:\nstderr: {result.stderr}"
            )

        # The emitted master .typ must NOT contain the exact pre-fix
        # top-level juxtaposition leak from the definition.
        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")
        assert DEFINITION_LEAK_SIGNATURE not in typ_text, (
            "The emitted .typ still contains the substitution_definition's "
            "juxtaposed top-level expressions with no separator -- the fix "
            f"is not applied:\n{typ_text}"
        )

        # The emitted .typ must have compiled to a real, non-empty PDF.
        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted, most "
            f"likely on the substitution_definition leak:\n"
            f"stderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

        # The substitution's replacement content must have reached the
        # compiled PDF exactly once each, at the |substthings| use site --
        # proof the definition itself produced NO output (it would otherwise
        # duplicate these tokens) while the use site still resolved.
        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)

        assert SUBST_USE_SENTINEL in full_text, (
            f"Expected use-site sentinel '{SUBST_USE_SENTINEL}' in "
            "extracted PDF text"
        )
        for token in SUBST_LITERAL_TOKENS:
            assert full_text.count(token) == 1, (
                f"Expected substitution replacement token '{token}' to "
                "appear exactly once in extracted PDF text (at the "
                "|substthings| use site) -- a count of 0 means the use site "
                "did not resolve; a count > 1 means the definition itself "
                "also emitted output"
            )
