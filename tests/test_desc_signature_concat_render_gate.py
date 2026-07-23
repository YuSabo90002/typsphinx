"""
Fast, offline regression gate for the desc-signature concat/newline fix
(Phase 15, GATE-02).

Deterministic, network-free reproduction of the ninth fatal the slow full-corpus
gate (``tests/test_corpus_gate.py::TestCorpusRenderGate``) surfaced against
Sphinx's own ``doc/`` tree (``usage/domains/c.typ`` and ``cpp.typ``), after bugs
#1-#8 unblocked the compile path:

    TypstError: expected expression
        text("(") +
        link(<...>, text("PyTypeObject"))

Root cause: inside a ``desc_signature`` the translator delegates to
``visit_strong``, which sets ``in_list_item = True`` (children are newline
separated). ``visit_desc_parameterlist`` ALSO sets ``in_desc_parameter = True``
and appends ``text("(") + `` (a trailing concat ``+``) but leaves
``list_item_needs_separator = True``. So while emitting the FIRST parameter BOTH
``in_list_item`` AND ``in_desc_parameter`` are active. When that first parameter
leads with a cross-referenced type (a wrapper-opening ``reference`` -> a
``link(...)``), ``visit_reference`` emitted the list-item newline
UNCONDITIONALLY -- before entering the concat element -- inserting a ``\\n``
right after ``text("(") + ``. That stranded the ``+`` at end-of-line with no
right operand -> ``expected expression``.

The C parameter shape ``MyType *obj`` (type-reference LEADS the parameter) is the
trigger; the Python shape ``obj: MyType`` (name leads, type mid-parameter) does
NOT reproduce, which is why the corpus fatal was specific to the C/C++ domains.

Fix: ``visit_reference`` now upholds the same concat/newline mutual-exclusion
invariant every other inline visitor already upholds -- inside a code-mode
concat context the ``+`` operator IS the separator, so the list-item newline
must not also fire. The signature emits
``text("(") + link(...) + text("*") + ...`` on one statement.

Confirmed both directions: FAILS against the pre-fix translator with the exact
``expected expression`` fatal (a ``text("(") + `` stranded before a newline), and
PASSES with the fix. Drives the full ``-b typstpdf`` path -- NOT ``-b typst`` --
on purpose: the fatal only aborts on the ``TypstPDFBuilder.finish()`` compile
path, so a ``-b typst`` build would emit the invalid ``.typ`` but never compile
it and thus prove nothing.
"""

import re
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
def desc_signature_concat_render_gate_dir():
    """Return the path to the desc_signature_concat_render_gate fixture project."""
    return Path(__file__).parent / "fixtures" / "desc_signature_concat_render_gate"


@pytest.fixture
def desc_signature_siblings_render_gate_dir():
    """Return the path to the desc_signature_siblings_render_gate fixture project."""
    return Path(__file__).parent / "fixtures" / "desc_signature_siblings_render_gate"


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
    reason="typst-py is required for the desc-signature-concat render gate",
)
class TestDescSignatureConcatRenderGate:
    """
    Real-compile regression gate proving a C-domain function signature whose
    first parameter leads with a cross-reference no longer strands a ``+`` at
    end-of-line, so ``typst.compile()`` does not abort with "expected
    expression".

    Requirements: GATE-02 (Phase 15 scope expansion -- the fast offline
    reproduction of the desc-signature concat/newline corpus fatal).
    """

    def test_typstpdf_signature_reference_first_param_produces_pdf(
        self, desc_signature_concat_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm:

        - the build exits cleanly (no fatal raised out of the subprocess);
        - the emitted signature does NOT strand a ``+`` at a line boundary:
          no trailing ``+`` immediately before a newline and no leading ``+``
          at the start of a statement/line;
        - the leading-reference parameter emits ``text("(") + link(`` on ONE
          line (the concat ``+`` keeps its right operand);
        - ``index.pdf`` exists, is non-empty, and starts with the ``%PDF`` magic
          bytes -- the only proof the signature compiled to valid Typst and
          ``typst.compile()`` did NOT abort with the "expected expression"
          fatal that GATE-02 surfaced against the corpus.
        """
        result = _run_sphinx_build_typstpdf(
            desc_signature_concat_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        # A fatal inside TypstPDFBuilder.finish() is logged (not raised) as an
        # ERROR, so guard against the exact signatures explicitly rather than
        # trusting returncode alone.
        assert "expected expression" not in result.stderr, (
            "typst.compile() rejected the signature -- the desc-signature "
            f"concat/newline fix is not in effect:\nstderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")

        # The leading-reference parameter must keep the concat '+' and its right
        # operand on ONE statement: 'text("(") + link(' -- pre-fix the newline
        # split the '+' from the link, so NO single line contains this substring
        # (an empty match list here IS the pre-fix failure).
        #
        # A whole-file '+\\n' grep would false-positive on the template's own
        # Typst (a trailing binary operator legitimately continues an expression
        # in some grouping contexts), so scope the stray-operator check to the
        # parameter-list line, where a stranded '+' is unambiguously the bug.
        param_lines = [ln for ln in typ_text.splitlines() if 'text("(") + link(' in ln]
        assert param_lines, (
            "Expected a parameter-list line emitting 'text(\"(\") + link(' on "
            "one statement -- the '+' was split from its link operand by a "
            f"stray newline (the fix is not applied):\n{typ_text}"
        )
        param_line = param_lines[0]

        # The whole parameter list is on this one line (closing paren present),
        # and the line strands no '+' at either boundary (no leading '+' at the
        # start of the statement, no trailing '+' before its end).
        assert 'text(")")' in param_line, (
            "The parameter list was split across lines (closing paren not on the "
            "same statement as the opening) -- the concat/newline collision is "
            f"not fixed:\n{param_line!r}"
        )
        assert (
            re.match(r"^\s*\+", param_line) is None
        ), f"The parameter-list line leads with a stray '+':\n{param_line!r}"
        assert (
            re.search(r"\+\s*$", param_line) is None
        ), f"The parameter-list line strands a trailing '+':\n{param_line!r}"

        # The emitted .typ must have compiled to a real, non-empty PDF.
        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted, most likely "
            f"on the stranded '+' in the signature:\nstderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the sibling desc-signature render gate",
)
class TestDescSignatureSiblingsRenderGate:
    """
    Real-compile regression gate proving sibling ``desc_signature``s (FID-03)
    render ``linebreak()``-stacked on separate lines instead of concatenating
    onto one running line, and that a lone signature stays byte-unchanged
    (no spurious ``linebreak()`` for the cardinality-1 case).

    Requirements: FID-03.
    """

    def test_typstpdf_sibling_signatures_produce_pdf(
        self, desc_signature_siblings_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm:

        - the build exits cleanly and the compile did not fail;
        - the emitted ``index.typ`` contains exactly TWO ``linebreak()``
          tokens -- one between each of the three sibling ``compile(...)``
          signatures (D-05: structural token assert; pre-fix the translator
          emits ZERO ``linebreak()`` tokens here at all);
        - the lone ``solo(source)`` signature emits no extra ``linebreak()``
          (covered by the exact total-count assertion above -- the fixture's
          own prose is worded to avoid any incidental ``linebreak()``
          substring elsewhere in the document, so a total count of 2 proves
          both the sibling-stacking behavior AND the lone-signature
          byte-unchanged guarantee in one assertion);
        - ``index.pdf`` exists, is non-empty, and starts with the ``%PDF``
          magic bytes (real ``typst.compile()`` succeeded).
        """
        result = _run_sphinx_build_typstpdf(
            desc_signature_siblings_render_gate_dir, temp_build_dir
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

        # D-05: structural assert. Pre-fix the translator emits ZERO
        # linebreak() tokens between sibling desc_signatures -- three
        # sibling signatures require exactly two separators.
        linebreak_count = typ_text.count("linebreak()")
        assert linebreak_count == 2, (
            "Expected exactly 2 linebreak() tokens (one between each of the "
            "3 sibling compile(...) signatures, none around the lone "
            f"solo(source) signature) -- found {linebreak_count}. The "
            f"FID-03 fix is not applied or over-applied:\n{typ_text}"
        )

        # Sanity: the linebreak() tokens sit strictly between the sibling
        # strong({...}) signature blocks, not before the first or after the
        # last.
        first_sig_idx = typ_text.index('strong({text("compile")')
        last_sig_close_idx = typ_text.rindex(
            'text("(") + text("source") + text(", ") + text("filename") + '
            'text(", ") + text("symbol") + text(")")'
        )
        siblings_span = typ_text[first_sig_idx:last_sig_close_idx]
        assert siblings_span.count("linebreak()") == 2, (
            "Both linebreak() separators must sit strictly between the "
            f"sibling signature blocks:\n{siblings_span}"
        )

        # The lone-signature construct (solo(source)) must emit no
        # linebreak() at all around it.
        solo_idx = typ_text.index('strong({text("solo")')
        solo_region = typ_text[solo_idx : solo_idx + 200]
        assert "linebreak()" not in solo_region, (
            "The lone solo(source) signature must stay byte-unchanged -- "
            f"no linebreak() expected around it:\n{solo_region}"
        )

        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced:\n" f"stderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"
