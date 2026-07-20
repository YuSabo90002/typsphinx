"""
Real-compile regression gate for the paragraph soft-newline reflow fix
(FID-11, Phase 21 Plan 02, GATE-01).

The shipping bug: a paragraph authored with reST soft/semantic source line
breaks (no inline markup interrupting the wrap point) is merged by docutils
into a SINGLE ``Text`` node carrying a literal ``\\n`` character where the
source line wrapped. ``visit_Text`` passed that ``\\n`` straight into
``escape_typst_string``, which turns it into the two-character escape
sequence ``\\n`` inside the emitted ``text("...")`` string literal -- Typst
decodes that escape back into a literal control character, forcing a HARD
line break in the compiled PDF (a short, ragged line with a large
right-margin gap) instead of the single space HTML/docutils/print
conventionally collapse a soft wrap to.

Fix: ``visit_Text`` now collapses ``\\n`` -> ``" "`` in the paragraph text
BEFORE calling ``escape_typst_string``, so no intra-paragraph newline escape
ever reaches the emitted ``text("...")`` call.

Confirmed against the pre-fix translator this session: ``index.typ``
contained ``text("SOFTWRAPALPHASENTINEL is a term that continues on the\\n
SOFTWRAPBETASENTINEL line ...")`` (the two-char ``\\n`` escape, embedded) and
``text(" or\\n")`` (soft break immediately adjacent to an inline literal,
matching the ``adding_domain``/``autodoc_ext`` occurrence from the audit
catalogue) -- both fail the structural assert below pre-fix.

Verification is structural ``.typ`` assert ONLY (D-08, Phase-19 family): the
hard-break symptom is a non-extractable vertical-layout property that pypdf
text extraction cannot reliably distinguish from a single collapsed space
(pypdf's ``extract_text()`` reads glyph runs left-to-right regardless of
whether a hard break or a reflow produced the line boundary), so no pypdf
assert is added for this finding.
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
def paragraph_soft_newline_render_gate_dir():
    """Return the path to the paragraph_soft_newline_render_gate fixture."""
    return Path(__file__).parent / "fixtures" / "paragraph_soft_newline_render_gate"


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

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``)
    so the exact interpreter/venv running this test is reused, sidestepping
    the documented NixOS-sandbox PATH-shadowing hazard.
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
    reason="typst-py is required for the paragraph-soft-newline render gate",
)
class TestParagraphSoftNewlineRenderGate:
    """
    Real-compile regression gate proving a soft/semantic-wrapped paragraph
    collapses its intra-paragraph source newline to a single space instead
    of forcing a Typst hard break.

    Requirements: FID-11, GATE-01.
    """

    def test_typstpdf_soft_newline_produces_pdf_with_no_intra_paragraph_break(
        self, paragraph_soft_newline_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm, at the
        SOURCE (``.typ``) level:

        - the build exits cleanly and did not report a compile failure;
        - the plain soft-wrapped paragraph's ``text("...")`` call contains
          NO intra-paragraph newline escape (the two-char sequence
          backslash+``n``) between the two sentinel tokens -- the source
          break collapsed to a single space, not a hard break;
        - the soft break immediately adjacent to an inline literal (between
          ``raw("MethodDocumenter")`` and ``raw("AttributeDocumenter")``)
          also collapses to a single-space ``text(" or ")`` statement with
          no embedded newline escape;
        - ``index.pdf`` exists, is non-empty, and begins with the ``%PDF``
          magic bytes (real ``typst.compile()`` succeeded).
        """
        result = _run_sphinx_build_typstpdf(
            paragraph_soft_newline_render_gate_dir, temp_build_dir
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

        # Build the needle in Python (not a literal in the source) so the
        # two-character escape sequence is unambiguous: backslash + 'n'.
        newline_escape = chr(92) + "n"

        # Case 1: the plain soft-wrapped paragraph (single merged Text node,
        # no inline markup at the break point). Locate its emitted
        # statement via the two sentinel tokens and assert the escape
        # sequence is absent between them -- pre-fix this assert FAILS
        # because escape_typst_string turns the embedded '\n' into this
        # exact two-char escape.
        alpha_idx = typ_text.index("SOFTWRAPALPHASENTINEL")
        beta_idx = typ_text.index("SOFTWRAPBETASENTINEL")
        assert beta_idx > alpha_idx, (
            "Expected SOFTWRAPBETASENTINEL to follow SOFTWRAPALPHASENTINEL "
            f"in the emitted .typ:\n{typ_text}"
        )
        plain_paragraph_span = typ_text[alpha_idx:beta_idx]
        assert newline_escape not in plain_paragraph_span, (
            "Found an intra-paragraph newline escape between "
            "SOFTWRAPALPHASENTINEL and SOFTWRAPBETASENTINEL -- the soft "
            "source line break was NOT collapsed to a space (FID-11 "
            f"regression):\n{plain_paragraph_span!r}"
        )
        # The collapse must join the two sentinels with exactly one space,
        # not merge them together or leave any other whitespace artifact.
        assert "the SOFTWRAPBETASENTINEL" in typ_text, (
            "Expected the collapsed paragraph to read 'the "
            "SOFTWRAPBETASENTINEL' (single space, no hard break) in the "
            f"emitted .typ:\n{typ_text}"
        )

        # Case 2: the soft break sits immediately adjacent to an inline
        # literal (matching the audit's adding_domain/autodoc_ext
        # occurrence). Locate the span between the two raw() calls and
        # assert no newline escape survives there either.
        method_idx = typ_text.index('raw("MethodDocumenter")')
        attribute_idx = typ_text.index('raw("AttributeDocumenter")')
        assert attribute_idx > method_idx, (
            "Expected raw(\"AttributeDocumenter\") to follow "
            f"raw(\"MethodDocumenter\") in the emitted .typ:\n{typ_text}"
        )
        between_literals_span = typ_text[method_idx:attribute_idx]
        assert newline_escape not in between_literals_span, (
            "Found an intra-paragraph newline escape between the two "
            "inline literals -- the soft source line break adjacent to an "
            f"inline literal was NOT collapsed to a space:\n"
            f"{between_literals_span!r}"
        )
        assert 'text(" or ")' in between_literals_span, (
            "Expected the collapsed soft break between the two inline "
            'literals to emit text(" or ") (single leading and trailing '
            f"space, no embedded newline):\n{between_literals_span!r}"
        )

        # The emitted .typ must have compiled to a real, non-empty PDF.
        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced:\n" f"stderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"
