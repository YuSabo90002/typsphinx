"""
Real-compile regression gate for the FID-10 margin-overflow fix (Phase 21
Plan 01, GATE-01).

The shipping bug: a long run of colon-leading inline ``literal`` role
tokens (e.g. ``:cpp:any:`` ``:cpp:class:`` ...) overflows the page's right
margin and clips mid-token instead of wrapping at the space between tokens.
Root cause (21-RESEARCH.md Pattern 1 / Pitfall 1, verified against a real
compile): the space between two adjacent inline elements in the emitted
``.typ`` IS a real, breakable ``text(" ")`` content token, but Typst's
Unicode line-breaking algorithm honors UAX14 rule LB13 ("do not break
before class CL/CP/EX/IS/SY, even after a space") for a colon-leading
literal token -- suppressing the break opportunity that would otherwise
exist right before the token.

Fix: in ``visit_literal``'s non-``in_table`` branch, when the literal's own
text starts with a character in the narrow UAX14 no-break-before class
(``":;,)]}!?"``), prepend a zero-width space (U+200B) to the ``raw()``
content before escaping. This gives Typst's line-breaker an explicit break
opportunity at the token boundary without touching a single visible glyph
of the token (ZWSP is zero-width and invisible). The existing
``self.in_table`` ZWSP primitive (a different mechanism, gated on being
inside a table cell) is left completely isolated (D-05) -- this is a new,
independent ``elif`` sibling branch.

Confirmed this session: the structural (``.typ``-level) assert below FAILS
against the pre-fix translator (no leading ZWSP is inserted) and PASSES with
the fix applied.
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


@pytest.fixture
def inline_literal_overflow_render_gate_dir():
    """Return the path to the inline_literal_overflow_render_gate fixture project."""
    return Path(__file__).parent / "fixtures" / "inline_literal_overflow_render_gate"


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


# The complete set of colon-leading role tokens used in the fixture, in
# emitted order. Kept here (rather than typed into assertions below) so the
# adjacency assert can iterate every token, including the last-placed one.
_ROLE_TOKENS = [
    ":cpp:any:",
    ":cpp:class:",
    ":cpp:enumerator:",
    ":cpp:expr:",
    ":cpp:func:",
    ":cpp:member:",
    ":cpp:texpr:",
    ":cpp:type:",
    ":cpp:union:",
    ":cpp:var:",
]


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the inline-literal-overflow render gate",
)
class TestInlineLiteralOverflowRenderGate:
    """
    Real-compile regression gate proving the FID-10 conditional leading-ZWSP
    fix gives Typst's line-breaker a break opportunity before a colon-leading
    inline literal token, without any content loss.

    Requirements: FID-10, GATE-01.
    """

    def test_typstpdf_inline_literal_overflow_produces_pdf_with_leading_zwsp(
        self, inline_literal_overflow_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm, at the SOURCE
        (``.typ``) level:

        - the build exits cleanly and did not report a compile failure;
        - the emitted ``raw(...)`` content for the colon-leading role tokens
          begins with a U+200B zero-width space immediately before the
          leading colon (the break-opportunity fix, FID-10);
        - ``index.pdf`` exists, is non-empty, and begins with the ``%PDF``
          magic bytes.

        This structural assert is the FAIL-PRE-FIX gate for FID-10 (see
        Pitfall 4: pypdf's ``extract_text()`` returns the full text of a
        visually-clipped line, so pypdf alone cannot prove the pre-fix
        failure -- only this structural ZWSP assert can).
        """
        result = _run_sphinx_build_typstpdf(
            inline_literal_overflow_render_gate_dir, temp_build_dir
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

        # Build the expected needle in Python -- never type a literal ZWSP
        # into the test source. Confirms the ZWSP is inserted BEFORE the
        # leading colon, inside the raw() string content.
        zwsp = chr(0x200B)
        needle = 'raw("' + zwsp + ":cpp"
        assert needle in typ_text, (
            "Expected a leading U+200B zero-width space immediately before "
            "the first colon of a colon-leading inline literal role token "
            f"(FID-10 regression):\n{typ_text}"
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
        not PYPDF_AVAILABLE,
        reason="pypdf is required for the extracted-text content-loss adjacency assert",
    )
    def test_pdf_extracted_text_has_no_content_loss(
        self, inline_literal_overflow_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf``, extract the compiled
        PDF's text with pypdf, and confirm every colon-leading role-token
        string (including the last-placed one) is present in the extracted
        text -- a no-content-loss sanity check (D-09).

        NOTE (Pitfall 4): this assert alone cannot prove the pre-fix bug,
        because pypdf's ``extract_text()`` returns the FULL text of a
        visually-clipped line even when the rendered page shows content
        clipped at the margin. The structural ``.typ``-level ZWSP assert in
        ``test_typstpdf_inline_literal_overflow_produces_pdf_with_leading_zwsp``
        is the actual fail-pre-fix gate for FID-10; this test is a
        supplementary no-content-loss sanity check only.

        With the fix applied, Typst's own line-breaking layout embeds
        additional invisible U+200B markers into the PDF text stream at
        every UAX14 break-class boundary within the now-breakable ``raw()``
        run (confirmed empirically this session -- e.g. the single leading
        ZWSP on ``:cpp:any:`` causes Typst to also emit invisible ZWSP
        markers before the internal ``:any:`` colons in the exported PDF
        text, even though the ``.typ`` source contains exactly one leading
        ZWSP per token, verified by inspecting the emitted ``.typ`` file
        directly). These are zero-width and do not represent content loss,
        so they are stripped before the substring comparison below.
        """
        result = _run_sphinx_build_typstpdf(
            inline_literal_overflow_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced:\n" f"stderr: {result.stderr}"
        )

        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)
        # Strip zero-width spaces Typst's line-breaker embeds at UAX14
        # break-class boundaries -- invisible, not a content-loss signal.
        visible_text = full_text.replace(chr(0x200B), "")

        for token in _ROLE_TOKENS:
            assert token in visible_text, (
                f"Expected role-token {token!r} in extracted PDF text -- "
                f"content loss regression (FID-10):\n{full_text}"
            )
