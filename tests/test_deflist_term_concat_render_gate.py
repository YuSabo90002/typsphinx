"""
Fast, offline regression gate for the def-list-term inline-concatenation fix
(Phase 15, GATE-02).

This is the deterministic, network-free reproduction of the third fatal that the
slow full-corpus gate (``tests/test_corpus_gate.py::TestCorpusRenderGate``)
surfaced against Sphinx's own ``doc/`` tree (``tutorial/getting-started.typ``),
after the static-asset-copy and target-label fixes unblocked the compile path:

    TypstError: expected comma
        terms.item(raw("make.bat")text(" and ")raw("Makefile"), par({...}))

Root cause: a def-list TERM buffers its inline children into
``current_term_buffer`` and ``depart_term`` does a bare ``"".join``. Adjacent
top-level inline code-mode expressions (a ``literal`` -> ``Text`` -> ``literal``
= ``raw("make.bat") text(" and ") raw("Makefile")``) are therefore concatenated
with NO separator. In Typst code mode -- the first argument of
``terms.item(TERM, DEFINITION)`` -- two juxtaposed function-call expressions are
a syntax error: the parser reads the first as the term argument then expects a
comma but finds the next expression.

Fix: an ``_in_term`` concat context (mirroring the existing ``_in_link`` /
``in_desc_parameter`` mechanism) makes ``visit_Text`` and ``visit_literal``
insert ``" + "`` between adjacent term expressions -- none before the first nor
after the last -- so the term emits
``raw("make.bat") + text(" and ") + raw("Makefile")``.

Confirmed both directions: FAILS against the pre-fix translator with the exact
``expected comma`` fatal on the juxtaposed term expressions, and PASSES with the
fix. Drives the full ``-b typstpdf`` path -- NOT ``-b typst`` -- on purpose: the
fatal only aborts on the ``TypstPDFBuilder.finish()`` compile path, so a
``-b typst`` build would emit the invalid ``.typ`` but never compile it and thus
prove nothing.
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
def deflist_term_concat_render_gate_dir():
    """Return the path to the deflist_term_concat_render_gate fixture project."""
    return Path(__file__).parent / "fixtures" / "deflist_term_concat_render_gate"


@pytest.fixture
def deflist_term_in_listitem_render_gate_dir():
    """Return the path to the deflist_term_in_listitem_render_gate fixture project."""
    return Path(__file__).parent / "fixtures" / "deflist_term_in_listitem_render_gate"


@pytest.fixture
def deflist_term_nested_list_render_gate_dir():
    """Return the path to the deflist_term_nested_list_render_gate fixture project."""
    return Path(__file__).parent / "fixtures" / "deflist_term_nested_list_render_gate"


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
    reason="typst-py is required for the def-list-term-concat render gate",
)
class TestDeflistTermConcatRenderGate:
    """
    Real-compile regression gate proving the translator ``+`` concatenates the
    adjacent inline expressions of a definition-list term, so
    ``typst.compile()`` does not abort with "expected comma".

    Requirements: GATE-02 (Phase 15 scope expansion -- the fast offline
    reproduction of the def-list-term juxtaposition corpus fatal).
    """

    def test_typstpdf_concatenates_term_expressions_and_produces_pdf(
        self, deflist_term_concat_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm:

        - the build exits cleanly (no fatal raised out of the subprocess);
        - the emitted master ``.typ`` ``+`` concatenates the adjacent term
          expressions (``raw("make.bat") + text(" and ") + raw("Makefile")``)
          and contains NO juxtaposed ``raw("make.bat")text(`` form;
        - a single-inline-node term still emits cleanly with no leading/trailing
          ``+`` (``terms.item(text("SingleTerm")``);
        - ``index.pdf`` exists, is non-empty, and starts with the ``%PDF`` magic
          bytes -- the only proof the juxtaposed term compiled to valid Typst
          and ``typst.compile()`` did NOT abort with the "expected comma" fatal
          that GATE-02 surfaced against the corpus.
        """
        result = _run_sphinx_build_typstpdf(
            deflist_term_concat_render_gate_dir, temp_build_dir
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
            "typst.compile() rejected the juxtaposed term expressions -- the "
            f"def-list-term concat fix is not in effect:\nstderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )

        # The emitted master .typ must + concatenate the adjacent term
        # expressions, never juxtapose them (the construct that caused the
        # fatal).
        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")
        assert 'raw("make.bat") + text(" and ") + raw("Makefile")' in typ_text, (
            "Expected the term to + concatenate its adjacent inline " "expressions"
        )
        assert 'raw("make.bat")text(' not in typ_text, (
            "The emitted .typ still juxtaposes the term expressions with no "
            "'+' separator -- the fix is not applied"
        )
        # A single-inline-node term must not gain a spurious leading/trailing +.
        assert (
            'terms.item(text("SingleTerm")' in typ_text
        ), "A single-inline-node term must emit cleanly with no leading '+'"

        # The emitted .typ must have compiled to a real, non-empty PDF.
        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted, most likely "
            f"on the juxtaposed term expressions:\nstderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the FID-05 deflist-term-separator render gate",
)
class TestDeflistTermInListitemRenderGate:
    """
    Real-compile regression gate proving FID-05 sub-case (a): a definition
    list nested inside a bullet ``list_item`` emits
    ``terms(separator: linebreak(), ...)`` so its term renders on its own
    line, separated from its (bare-inline, un-``par()``-wrapped) definition.

    Requirements: FID-05 (D-05 / GATE-01).
    """

    def test_typstpdf_term_in_listitem_separates_from_definition(
        self, deflist_term_in_listitem_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm:

        - the build exits cleanly and typst compiles without error;
        - the emitted ``.typ`` ``terms(...)`` call carries
          ``separator: linebreak()`` (D-05 -- absent pre-fix, present
          post-fix), which is what forces the term onto its own line even
          though the nested-in-a-list-item definition's first content is
          bare inline text;
        - ``index.pdf`` exists, is non-empty, and starts with the ``%PDF``
          magic bytes.
        """
        result = _run_sphinx_build_typstpdf(
            deflist_term_in_listitem_render_gate_dir, temp_build_dir
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
        assert "terms(separator: linebreak()" in typ_text, (
            "Expected the terms() call to carry separator: linebreak() -- "
            f"the FID-05 fix is not applied:\n{typ_text}"
        )

        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced:\n" f"stderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the FID-05 deflist-term-separator render gate",
)
class TestDeflistTermNestedListRenderGate:
    """
    Real-compile regression gate proving FID-05 sub-case (b): a definition
    list term whose definition body OPENS with a nested list emits
    ``terms(separator: linebreak(), ...)`` so the OUTER term renders on its
    own line, separated from its definition.

    Requirements: FID-05 (D-05 / GATE-01).
    """

    def test_typstpdf_term_before_nested_list_separates_from_definition(
        self, deflist_term_nested_list_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm:

        - the build exits cleanly and typst compiles without error;
        - the emitted ``.typ`` ``terms(...)`` call carries
          ``separator: linebreak()`` (D-05 -- absent pre-fix, present
          post-fix), which is what forces the OUTER term onto its own line
          even though its definition's first rendered content is the ALSO
          inline first term of a nested ``terms(...)`` list;
        - ``index.pdf`` exists, is non-empty, and starts with the ``%PDF``
          magic bytes.
        """
        result = _run_sphinx_build_typstpdf(
            deflist_term_nested_list_render_gate_dir, temp_build_dir
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
        assert "terms(separator: linebreak()" in typ_text, (
            "Expected the terms() call to carry separator: linebreak() -- "
            f"the FID-05 fix is not applied:\n{typ_text}"
        )

        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced:\n" f"stderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"
